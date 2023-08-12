import itertools
import json
import logging
import os.path
import re
import time
from contextlib import contextmanager
from enum import Enum
from typing import Type, List, ContextManager, Iterator, Optional, Tuple, Union, Mapping

import click
import numpy as np
from ditk import logging
from hbutils.system import TemporaryDirectory
from huggingface_hub import hf_hub_download, hf_hub_url
from imgutils.metrics import ccip_batch_same
from orator import DatabaseManager
from thefuzz import fuzz
from tqdm.auto import tqdm

from gchar.games import get_character_class, list_available_game_names
from gchar.games.base import Character
from gchar.generic import import_generic
from gchar.utils import GLOBAL_CONTEXT_SETTINGS, srequest, get_requests_session
from .base import HuggingfaceDeployable
from .character import get_ccip_features_of_character, TagFeatureExtract

import_generic()


class ValidationStatus(str, Enum):
    TRUST = 'trust'
    YES = 'yes'
    UNCERTAIN = 'uncertain'
    NO = 'no'
    BAN = 'ban'

    @property
    def order(self):
        if self == self.TRUST:
            return 1
        elif self == self.YES:
            return 1
        elif self == self.UNCERTAIN:
            return 2
        elif self == self.NO:
            return 3
        elif self == self.BAN:
            return 4

    @property
    def visible(self) -> bool:
        return self in {self.TRUST, self.YES, self.UNCERTAIN}

    @property
    def sure(self) -> bool:
        return self in {self.TRUST, self.YES}


def remove_curves(text) -> str:
    return re.sub(r'\([\s\S]+?\)', '', text)


def split_words(text) -> List[str]:
    return [word for word in re.split(r'[\W_]+', text) if word]


_SESSION = get_requests_session()


class TagMatcher(HuggingfaceDeployable):
    __site_name__: str
    __tag_column__: str = 'name'
    __count_column__: str = 'count'
    __extra_filters__: dict = {'type': 4}
    __case_insensitive__: bool = True
    __min_similarity__: float = 0.7
    __strict_similarity__: float = 0.95
    __yes_min_vsim__: float = 0.60
    __no_max_vsim__: float = 0.20
    __max_validate__: int = 10
    __sure_min_samples__: int = 8
    __default_repository__ = 'deepghs/game_characters'
    __tag_fe__: Type[TagFeatureExtract]

    def __init__(self, game_name: str, game_keywords: List[str] = None, repository: Optional[str] = None):
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
        self.game_keywords = list(game_keywords or get_character_class(game_name).__game_keywords__ or [])
        self.ch_feats = {}
        self.repository = repository or self.__default_repository__

    def get_premarked_lists(self) -> Tuple[Mapping[Union[int, str], List[str]], Mapping[Union[int, str], List[str]]]:
        file_url = hf_hub_url(
            self.repository,
            filename=f'{self.game_name}/tags_{self.__site_name__}.json',
            repo_type='dataset'
        )
        resp = srequest(_SESSION, 'GET', file_url, raise_for_status=False)
        if resp.ok:
            json_file = hf_hub_download(
                self.repository,
                filename=f'{self.game_name}/tags_{self.__site_name__}.json',
                repo_type='dataset'
            )
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)['data']

            blacklists = {
                item['index']: list(item.get('blacklist', None) or [])
                for item in data
            }
            whitelists = {
                item['index']: list(item.get('whitelist', None) or [])
                for item in data
            }
            return blacklists, whitelists

        else:
            return {}, {}

    def _query_via_pattern(self, pattern, *patterns):
        query = self.db.table('tags').select('*')
        for key, value in self.__extra_filters__.items():
            if isinstance(value, (list, tuple, set)):
                query = query.where_in(key, value)
            else:
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

    def _words_filter(self, name_words: List[str], tag_words: List[str]) -> float:
        tag = ' '.join(tag_words)
        name = ' '.join(name_words)
        if self.__case_insensitive__:
            tag, name = tag.lower(), name.lower()
        return fuzz.token_set_ratio(tag, name) / 100.0

    def _words_compare(self, name_words: List[str], tag_words: List[str]) -> float:
        tag = ' '.join(tag_words)
        name = ' '.join(name_words)
        if self.__case_insensitive__:
            tag, name = tag.lower(), name.lower()
        return fuzz.token_sort_ratio(tag, name) / 100.0

    def _get_ch_feats(self, character: Character):
        if character.index not in self.ch_feats:
            feats = get_ccip_features_of_character(character)
            self.ch_feats[character.index] = feats
        return self.ch_feats[character.index]

    def _tag_name_validate(self, character, tag, count, similarity, has_keyword: bool) -> bool:
        return has_keyword and similarity >= self.__strict_similarity__

    def _tag_validate(self, character, tag, count, similarity, has_keyword: bool) \
            -> ValidationStatus:
        if self._tag_name_validate(character, tag, count, similarity, has_keyword):
            return ValidationStatus.YES

        if self.__tag_fe__ is None:
            return ValidationStatus.UNCERTAIN
        else:
            ch_feats = self._get_ch_feats(character)
            if ch_feats:
                tag_feats = self.__tag_fe__(tag).get_features()
                if tag_feats:
                    feats = [*ch_feats, *tag_feats]
                    total = len(ch_feats) * len(tag_feats)
                    smatrix = ccip_batch_same(feats)[0:len(ch_feats), len(ch_feats):len(ch_feats) + len(tag_feats)]
                    ratio = smatrix.astype(np.float32).mean().item()
                    logging.info(f'Visual matching of {character!r} and tag {tag!r}: {ratio}')
                    if ratio >= self.__yes_min_vsim__:
                        if total < self.__sure_min_samples__:
                            return ValidationStatus.UNCERTAIN
                        else:
                            return ValidationStatus.TRUST
                    elif ratio < self.__no_max_vsim__:
                        if total < self.__sure_min_samples__:
                            return ValidationStatus.NO
                        else:
                            return ValidationStatus.BAN
                    else:
                        return ValidationStatus.UNCERTAIN
                else:
                    return ValidationStatus.NO
            else:
                return ValidationStatus.UNCERTAIN

    def _iter_patterns_by_name_words(self, name_words_sets: List[List[str]]) -> Iterator[str]:
        # name without keyword
        for name_words in name_words_sets:
            word_count = len(name_words)
            f_word_count = min(max(word_count // 2, 2), word_count)
            for word_cmbs in itertools.combinations(name_words, f_word_count):
                if sum(map(len, word_cmbs)) >= 7:
                    for words in itertools.permutations(word_cmbs):
                        origin_text = '_'.join(words)
                        for i in range(len(origin_text)):
                            new_text = ''.join([
                                ('%' if origin_text[j] == '_' else '_') if i == j else origin_text[j]
                                for j in range(len(origin_text))
                            ])
                            pattern = f'%{new_text}%'
                            yield pattern
                else:
                    yield '%'.join(['', *word_cmbs, ''])

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

    def _alias_replace(self, tag, count) -> Tuple[str, int]:
        _known_names = {tag}
        _known_tuples = [(tag, count)]
        while True:
            query = self.db.table('tag_aliases').select('*').where('alias', '=', tag)
            lst = list(query.get())
            if not lst:
                break
            else:
                new_tag = lst[0]['tag']
                if new_tag in _known_names:
                    cnts = np.array([c for _, c in _known_tuples])
                    tag, count = _known_tuples[np.argmax(cnts)]
                    break

                t_query = self.db.table('tags').select('*').where(self.__tag_column__, '=', new_tag)
                t_lst = list(t_query.get())
                if t_lst:
                    new_count = t_lst[0][self.__count_column__]
                    tag, count = new_tag, new_count
                    _known_names.add(tag)
                    _known_tuples.append((tag, count))
                else:
                    break

        return tag, count

    def _yield_mapped_tags(self, tag) -> Iterator[Tuple[str, dict]]:
        yield tag, {}

    def _get_ch_names(self, ch: Character) -> List[str]:
        return sorted(set(map(str, [*ch.names, *ch.alias_names])))

    def _yield_name_count(self, names: List[str]) -> Iterator[Tuple[str, int]]:
        name_words_sets = [self._split_name_to_words(name) for name in names]
        exist_tags = set()
        for patterns in self._batch_iter_patterns(name_words_sets):
            for row in self._query_via_pattern(*patterns).get():
                tag = row[self.__tag_column__]
                count = row[self.__count_column__]
                if tag in exist_tags:
                    continue

                origin_tag = tag
                tag, count = self._alias_replace(tag, count)
                if tag in exist_tags:
                    continue

                tag_words = self._split_tag_to_words(origin_tag)
                tag_words_n = self._split_name_to_words(origin_tag)
                filter_sim = max([
                    *(self._words_filter(name_words, tag_words) for name_words in name_words_sets),
                    *(self._words_filter(name_words, tag_words_n) for name_words in name_words_sets),
                ])
                if filter_sim < self.__min_similarity__:
                    continue

                exist_tags.add(tag)
                exist_tags.add(origin_tag)
                yield tag, count

    def try_matching(self):
        ch_options = {}
        origin_chs = self.game_cls.all(contains_extra=True)
        all_chs, _exist_chids = [], set()
        for ch in origin_chs:
            if ch.index not in _exist_chids:
                all_chs.append(ch)
                _exist_chids.add(ch.index)
        ch_blacklists, ch_whitelists = self.get_premarked_lists()

        ns_tqdm = tqdm(all_chs, desc='Name Searching')
        for ch in ns_tqdm:
            ns_tqdm.set_description(f'Name Search: {ch!r}')
            ch_names = self._get_ch_names(ch)
            name_words_sets = [self._split_name_to_words(name) for name in ch_names]
            options = []
            for tag, count in self._yield_name_count(ch_names):
                tag_words = self._split_tag_to_words(tag)
                tag_words_n = self._split_name_to_words(tag)
                sim = max([
                    *(self._words_compare(name_words, tag_words) for name_words in name_words_sets),
                    *(self._words_compare(name_words, tag_words_n) for name_words in name_words_sets),
                ])
                kw = self._keyword_check(tag)

                for mapped_tag, meta in self._yield_mapped_tags(tag):
                    options.append((mapped_tag, count, sim, kw, meta))

            options = sorted(options, key=lambda x: (0 if x[3] else 1, -x[2], -x[1], len(x[0]), x[0]))
            ch_options[ch.index] = options
            logging.info(f'Selected tags for {ch!r}: {options!r}')

        retval = []
        for ch in tqdm(all_chs, desc='Tag Matching'):
            options = ch_options[ch.index]
            blacklist = set(ch_blacklists.get(ch.index, None) or [])
            whitelist = set(ch_whitelists.get(ch.index, None) or [])
            options = sorted(options, key=lambda x: (0 if x[3] else 1, -x[1], len(x[0]), x[0]))

            # filter visual not matches
            ops, validate_cnt = [], 0
            has_kw = options and options[0][3]
            ref_status, ref_sim = None, None
            for tag, count, sim, kw, meta in options:
                # when xxx_(game) exist, tags like (xxx)_(yyy) will be dropped.
                if has_kw and not kw and ref_status and ref_status.sure and \
                        sorted(set(self._split_name_to_words(tag)) - set(self._split_tag_to_words(tag))):
                    continue

                if tag in blacklist:
                    continue
                elif tag in whitelist:
                    ops.append((tag, count, sim, kw, meta, ValidationStatus.YES))
                    ref_status = ValidationStatus.YES
                    ref_sim = sim if ref_sim is None else min(sim, ref_sim)
                else:
                    if not kw and ref_status is not None:
                        if ref_status.sure and sim < ref_sim - 0.05:
                            continue
                        if not ref_status.sure and sim < ref_sim - 0.10:
                            continue
                    if validate_cnt >= self.__max_validate__:
                        continue

                    status = self._tag_validate(ch, tag, count, sim, kw)
                    logging.info(f'Validate result of {tag!r}: {status}')

                    ops.append((tag, count, sim, kw, meta, status))
                    if status.visible:
                        if status.sure:
                            ref_status = ValidationStatus.YES
                        elif ref_status is None or not ref_status.sure:
                            ref_status = ValidationStatus.UNCERTAIN
                        ref_sim = sim if ref_sim is None else min(sim, ref_sim)

                    validate_cnt += 1

            options = ops

            # mapping tags to aliases
            ops = []
            for tag, count, sim, kw, meta, status in options:
                if status.visible:
                    ops.append((tag, count, sim, kw, meta, status))
                    if status == ValidationStatus.TRUST:
                        whitelist.add(tag)
                elif status == ValidationStatus.BAN:
                    blacklist.add(tag)

            options = sorted(ops, key=lambda x: (x[5].order, -x[1], len(x[0]), x[0]))
            retval.append({
                'index': ch.index,
                'cnname': str(ch.cnname) if ch.cnname else None,
                'enname': str(ch.enname) if ch.enname else None,
                'jpname': str(ch.jpname) if ch.jpname else None,
                'tags': [
                    {
                        'name': tag,
                        'count': count,
                        'sure': status.sure,
                        'meta': meta,
                    } for tag, count, sim, kw, meta, status in options
                ],
                'blacklist': sorted(blacklist),
                'whitelist': sorted(whitelist),
            })
            find_tags = [(tag, count, status.value) for tag, count, sim, kw, meta, status in options]
            logging.info(f'Tags found for character {ch!r} - {find_tags!r}')
            logging.info(f'Blacklisted tags of character {ch!r}: {sorted(blacklist)!r}')
            logging.info(f'Whitelisted tags of character {ch!r}: {sorted(whitelist)!r}')

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
            logging.try_init_root(logging.DEBUG)
            matcher = cls(game_name)
            matcher.export_to_directory(output_directory, namespace)
