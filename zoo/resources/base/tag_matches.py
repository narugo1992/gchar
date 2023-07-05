import itertools
import json
import logging
import os.path
import re
import time
from contextlib import contextmanager
from enum import Enum
from typing import Type, List, ContextManager, Iterator

import click
import numpy as np
from ditk import logging
from hbutils.system import TemporaryDirectory
from huggingface_hub import hf_hub_download
from imgutils.metrics import ccip_batch_same
from orator import DatabaseManager
from thefuzz import fuzz
from tqdm.auto import tqdm

from gchar.games import get_character_class, list_available_game_names
from gchar.games.base import Character
from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from .base import HuggingfaceDeployable
from .character import get_ccip_features_of_character, TagFeatureExtract

GAME_KEYWORDS = {
    'arknights': ['arknights'],
    'fgo': ['fate/grand_order', 'fate'],
    'azurlane': ['azur_lane'],
    'genshin': ['genshin_impact'],
    'girlsfrontline': ['girls\'_frontline'],
    'neuralcloud': ['girls\'_frontline_nc', 'girls\'_frontline'],
    'bluearchive': ['blue_archive'],
}


class ValidationStatus(str, Enum):
    YES = 'yes'
    UNCERTAIN = 'uncertain'
    NO = 'no'

    @property
    def order(self):
        if self == self.YES:
            return 1
        elif self == self.UNCERTAIN:
            return 2
        elif self == self.NO:
            return 3


def remove_curves(text) -> str:
    return re.sub(r'\([\s\S]+?\)', '', text)


def split_words(text) -> List[str]:
    return [word for word in re.split(r'[\W_]+', text) if word]


class TagMatcher(HuggingfaceDeployable):
    __site_name__: str
    __tag_column__: str = 'name'
    __count_column__: str = 'count'
    __extra_filters__: dict = {'type': 4}
    __case_insensitive__: bool = False
    __min_similarity__: float = 0.7
    __strict_similarity__: float = 0.9
    __yes_min_vsim__: float = 0.60
    __no_max_vsim__: float = 0.20
    __game_keywords__: dict = GAME_KEYWORDS
    __default_repository__ = 'deepghs/game_characters'
    __tag_fe__: Type[TagFeatureExtract]

    def __init__(self, game_name: str, game_keywords: List[str] = None):
        db_file = hf_hub_download(
            'deepghs/site_tags',
            filename=f'{self.__site_name__}/tags.sqlite',
            repo_type='dataset'
        )
        logging.debug(f'Opening db file {db_file!r} ...')
        self.db = DatabaseManager({
            'sqlite': {
                'driver': 'sqlite',
                'database': db_file,
            }
        })
        self.db.connection().enable_query_log()
        self.game_name = game_name
        self.game_cls: Type[Character] = get_character_class(game_name)
        self.game_keywords = list(game_keywords or self.__game_keywords__.get(game_name) or [])
        self.ch_feats = {}

    def _query_via_pattern(self, pattern, *patterns):
        query = self.db.table('tags').select('*')
        for key, value in self.__extra_filters__.items():
            query = query.where(key, '=', value)

        or_clause = self.db.query()
        for i, p in enumerate([pattern, *patterns]):
            or_clause = or_clause.or_where(
                self.db.raw(f'LOWER({self.__tag_column__})')
                if self.__case_insensitive__ else self.__tag_column__,
                'like', p.lower() if self.__case_insensitive__ else p,
            )

        query = query.where(or_clause)
        return query

    def _split_name_to_words(self, name):
        if self.__case_insensitive__:
            name = name.lower()
        return split_words(name.strip())

    def _split_tag_to_words(self, tag):
        if self.__case_insensitive__:
            tag = tag.lower()
        return split_words(remove_curves(tag.strip()))

    def _keyword_check(self, tag):
        tag_words = self._split_name_to_words(tag)
        for keyword in self.game_keywords:
            keyword_words = self._split_tag_to_words(keyword)
            for i in range(len(tag_words)):
                if tag_words[i:i + len(keyword_words)] == keyword_words:
                    return True

        return False

    def _words_cmp(self, name_words: List[str], tag_words: List[str]) -> float:
        tag = ' '.join(tag_words)
        name = ' '.join(name_words)
        tsor = fuzz.token_sort_ratio(tag, name) / 100.0
        tser = fuzz.token_set_ratio(tag, name) / 100.0
        return tsor * 0.7 + tser * 0.3

    def _get_ch_feats(self, character: Character):
        if character.index not in self.ch_feats:
            feats = get_ccip_features_of_character(character)
            self.ch_feats[character.index] = feats
        return self.ch_feats[character.index]

    def _tag_name_validate(self, character, tag, count, similarity, has_keyword: bool) -> bool:
        return has_keyword and similarity >= self.__strict_similarity__

    def _tag_validate(self, character, tag, count, similarity, has_keyword: bool) -> ValidationStatus:
        if self._tag_name_validate(character, tag, count, similarity, has_keyword):
            return ValidationStatus.YES

        ch_feats = self._get_ch_feats(character)
        tag_feats = self.__tag_fe__(tag).get_features()
        if ch_feats and tag_feats:
            feats = [*ch_feats, *tag_feats]
            smatrix = ccip_batch_same(feats)[0:len(ch_feats), len(ch_feats):len(ch_feats) + len(tag_feats)]
            ratio = smatrix.astype(np.float32).mean().item()
            logging.info(f'Visual matching of {character!r} and tag {tag!r}: {ratio}')
            if ratio >= self.__yes_min_vsim__:
                return ValidationStatus.YES
            elif ratio < self.__no_max_vsim__:
                return ValidationStatus.NO
            else:
                return ValidationStatus.UNCERTAIN
        else:
            return ValidationStatus.NO

    def _iter_patterns_by_name_words(self, name_words_sets: List[List[str]]) -> Iterator[str]:
        # name without keyword
        yield from [
            '%'.join(['', *words, ''])
            for name_words in name_words_sets
            for words in itertools.permutations(name_words)
        ]

    __pattern_batch__: int = 200

    def _batch_iter_patterns(self, name_words_sets: List[List[str]]) -> Iterator[List[str]]:
        patterns = []
        for p in self._iter_patterns_by_name_words(name_words_sets):
            patterns.append(p)
            if len(patterns) >= self.__pattern_batch__:
                yield list(patterns)
                patterns.clear()

        if patterns:
            yield list(patterns)

    def try_matching(self):
        best_sim_for_tag_words, ch_options = {}, {}
        all_chs = self.game_cls.all(contains_extra=False)

        for ch in tqdm(all_chs, desc='Name Searching'):
            name_words_sets = [self._split_name_to_words(name) for name in ch.names]
            options, exist_tags = [], set()
            for patterns in self._batch_iter_patterns(name_words_sets):
                for row in self._query_via_pattern(*patterns).get():
                    tag = row[self.__tag_column__]
                    count = row[self.__count_column__]
                    if tag in exist_tags:
                        continue

                    tag_words = self._split_tag_to_words(tag)
                    sim = max([self._words_cmp(name_words, tag_words) for name_words in name_words_sets])
                    if sim < self.__min_similarity__:
                        continue
                    kw = self._keyword_check(tag)

                    options.append((tag, count, sim, kw))
                    exist_tags.add(tag)

                    tag_tpl = tuple(tag_words)
                    if tag_tpl not in best_sim_for_tag_words:
                        best_sim_for_tag_words[tag_tpl] = 0.0
                    best_sim_for_tag_words[tag_tpl] = max(best_sim_for_tag_words[tag_tpl], sim)

            options = sorted(options, key=lambda x: (0 if x[3] else 1, -x[2], -x[1], len(x[0]), x[0]))
            ch_options[ch.index] = options

        retval = []
        for ch in tqdm(all_chs, desc='Tag Matching'):
            options = ch_options[ch.index]
            options = [
                (tag, count, sim, kw) for tag, count, sim, kw in options
                if np.isclose(sim, best_sim_for_tag_words[tuple(self._split_tag_to_words(tag))])
            ]

            if any(self._tag_name_validate(ch, tag, count, sim, kw)
                   for tag, count, sim, kw in options):
                options = [
                    (tag, count, sim, kw, ValidationStatus.YES)
                    for tag, count, sim, kw in options
                    if self._tag_name_validate(ch, tag, count, sim, kw)
                ]
            else:
                options = [
                    (tag, count, sim, kw, self._tag_validate(ch, tag, count, sim, kw))
                    for tag, count, sim, kw in options
                ]

            options = [
                (tag, count, sim, kw, status)
                for tag, count, sim, kw, status in options
                if status != ValidationStatus.NO
            ]
            options = sorted(options, key=lambda x: (x[4].order, 0 if x[3] else 1, -x[2], -x[1], len(x[0]), x[0]))
            if options:
                retval.append({
                    'index': ch.index,
                    'cnname': str(ch.cnname) if ch.cnname else None,
                    'enname': str(ch.enname) if ch.enname else None,
                    'jpname': str(ch.jpname) if ch.jpname else None,
                    'tags': [
                        {
                            'name': option[0],
                            'count': option[1],
                            'status': option[4].value,
                        } for option in options
                    ]
                })
                find_tags = [(tag, count, status.value) for tag, count, sim, kw, status in options]
                logging.info(f'Tags found for character {ch!r} - {find_tags!r}')
            else:
                logging.warning(f'No Tags found for character {ch!r}')

        return retval

    @contextmanager
    def with_files(self, **kwargs) -> ContextManager[List[str]]:
        with TemporaryDirectory() as td:
            json_file = os.path.join(td, f'tags_{self.__site_name__}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'data': self.try_matching(),
                    'time': time.time(),
                }, f, indent=4, ensure_ascii=False, sort_keys=True)

            yield [json_file]

    def get_default_namespace(self, **kwargs) -> str:
        return self.game_name

    @classmethod
    def add_commands(cls, cli):
        @cli.command('chtags', help='Match tags of characters from database.',
                     context_settings={**GLOBAL_CONTEXT_SETTINGS})
        @click.option('--repository', '-r', 'repository', type=str, default='deepghs/game_characters',
                      help='Repository to publish to.', show_default=True)
        @click.option('--namespace', '-n', 'namespace', type=str, default=None,
                      help='Namespace to publish to, default to game name.', show_default=True)
        @click.option('--revision', '-R', 'revision', type=str, default='main',
                      help='Revision for pushing the model.', show_default=True)
        @click.option('--game', '-g', 'game_name', type=click.Choice(list_available_game_names()), required=True,
                      help='Game to deploy.', show_default=True)
        def chtags(repository: str, namespace: str, revision: str, game_name: str):
            logging.try_init_root(logging.INFO)
            matcher = cls(game_name)
            matcher.deploy_to_huggingface(repository, namespace, revision)

        @cli.command('chtags_export', help='Match tags of characters from database.',
                     context_settings={**GLOBAL_CONTEXT_SETTINGS})
        @click.option('--output_directory', '-o', 'output_directory', type=str, default='.',
                      help='Output directory', show_default=True)
        @click.option('--namespace', '-n', 'namespace', type=str, default=None,
                      help='Namespace to publish to, default to game name.', show_default=True)
        @click.option('--game', '-g', 'game_name', type=click.Choice(list_available_game_names()), required=True,
                      help='Game to deploy.', show_default=True)
        def chtags_export(output_directory: str, namespace: str, game_name: str):
            logging.try_init_root(logging.INFO)
            matcher = cls(game_name)
            matcher.export_to_directory(output_directory, namespace)
