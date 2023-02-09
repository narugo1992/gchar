import re
import warnings
from typing import Iterable, Iterator, Union, List, Tuple, Type, Mapping, Optional

from .games import _get_items_from_ch_type
from .keyword import _load_pixiv_names_for_game
from ...games import get_character
from ...games.base import Character
from ...utils import optional_lru_cache


def _yield_tags(tags: Union[Tuple[str], List[str], str]) -> Iterator[str]:
    if isinstance(tags, str):
        for item in re.split(r'\s+', tags):
            if item:
                yield item
    elif isinstance(tags, (list, tuple, set)):
        for item in tags:
            yield from _yield_tags(item)


def _format_tags(positive, negative, or_clause=None):
    positive_tags = list(_yield_tags(positive))
    negative_tags = list(_yield_tags(negative))
    or_clause_tags = list(_yield_tags(or_clause or ''))
    if len(or_clause_tags) == 1:
        or_tag = or_clause_tags[0]
        if or_tag not in positive_tags:
            positive_tags.append(or_tag)
        or_clause_tags = []

    positive_tags = set(positive_tags)
    or_clause_tags = set(or_clause_tags)
    negative_tags = set(negative_tags) - positive_tags - or_clause_tags
    positive_tags = sorted(positive_tags)
    negative_tags = sorted(negative_tags)
    or_clause_tags = sorted(or_clause_tags)

    all_phrases = [*positive_tags]
    if or_clause_tags:
        all_phrases.append(f'({" OR ".join(or_clause_tags)})')
    if negative_tags:
        all_phrases.extend((f'-{x}' for x in negative_tags))

    return ' '.join(all_phrases)


class PixivCharPool:
    def __init__(self, chars: Iterable[Character], names_dict: Mapping[str, Tuple[int, float, List[Tuple[str, int]]]]):
        self.__chars = list(chars)
        self.__names_dict = names_dict

    def __get_name_item(self, name) -> Optional[Tuple[int, float, List[Tuple[str, int]]]]:
        return self.__names_dict.get(name, None)

    def __get_name_count(self, name) -> int:
        tpl = self.__get_name_item(name)
        if tpl:
            count, _, _ = tpl
            return count
        else:
            return 0

    def __get_name_pollution_ratio(self, name) -> float:
        tpl = self.__get_name_item(name)
        if tpl:
            _, ratio, _ = tpl
            return ratio
        else:
            return 0.0

    def __get_name_pollution_words(self, name) -> List[Tuple[str, int]]:
        tpl = self.__get_name_item(name)
        if tpl:
            _, _, pollution = tpl
            return pollution
        else:
            return []

    def _iter_dup_names(self, name: str) -> Iterator[str]:
        for sname in self.__names_dict.keys():
            if name != sname and name in sname:
                yield sname

    def get_tag(self, char: Character, use_english: bool = False, positive=None, negative=None,
                max_exclude_per_word: int = 20, max_exclude: int = 20, max_pollution_ratio: float = 0.65):
        if not isinstance(char, Character):
            raise TypeError(f'Invalid character type - {char!r}.')  # pragma: no cover

        char_names = [*char.cnnames, *char.jpnames]
        if use_english:
            char_names.extend(char.ennames)

        positive = set(_yield_tags(positive or []))
        negative = set(_yield_tags(negative or [])) - positive
        or_clause = set()

        exclude_names = set()
        exclude_name_pairs = []
        min_pollution = 1.0
        for chname in char_names:
            s_chname = str(chname)
            name_pollution_ratio = self.__get_name_pollution_ratio(s_chname)
            min_pollution = min(name_pollution_ratio, min_pollution)
            if name_pollution_ratio <= max_pollution_ratio:
                or_clause.add(s_chname)

                for pword, pcnt in self.__get_name_pollution_words(s_chname):
                    if pword not in positive and pword not in or_clause and \
                            pword != char and pword not in exclude_names:
                        exclude_names.add(pword)
                        exclude_name_pairs.append((pword, pcnt, 1))

                all_exnames = list(self._iter_dup_names(s_chname))
                if len(all_exnames) >= max_exclude_per_word:
                    continue

                for exname in all_exnames:
                    if exname not in positive and exname not in or_clause and \
                            exname != char and exname not in exclude_names:
                        exclude_names.add(exname)
                        exclude_name_pairs.append((exname, self.__get_name_count(exname), 0))

        for exname, _, _ in sorted(exclude_name_pairs, key=lambda x: (x[2], -x[1], x[0]))[:max_exclude]:
            negative.add(exname)

        if or_clause:
            return _format_tags(positive, negative, or_clause)
        else:
            return self.get_tag(char, use_english, positive, negative,
                                max_exclude_per_word, max_exclude, max_pollution_ratio=min_pollution + 0.015)

    def _iter_end_dup_names(self, name: str) -> Iterator[str]:
        for sname in self.__names_dict.keys():
            if name != sname and sname.endswith(name):
                yield sname

    def get_simple_tag(self, char: Character, base_tag: str, max_exclude: int = 20):
        if not isinstance(char, Character):
            raise TypeError(f'Invalid character type - {char!r}.')  # pragma: no cover

        positive = set()
        negative = set()
        or_clause = set()
        if char.jpnames:
            exclude_names = set()
            for jpname in char.jpnames:
                positive.add(f'{jpname}({base_tag})')
                for exname in self._iter_end_dup_names(str(jpname)):
                    exclude_names.add(exname)

            for exname in sorted(exclude_names, key=lambda x: self.__get_name_count(x), reverse=True)[:max_exclude]:
                negative.add(exname)

        else:
            raise ValueError(f'Japanese name not found for character - {char!r}.')

        return _format_tags(positive, negative, or_clause)


@optional_lru_cache()
def _get_char_pool(cls: Type[Character], **kwargs):
    names_dict = _load_pixiv_names_for_game(cls)
    return PixivCharPool(cls.all(**kwargs), names_dict)


def get_pixiv_keywords(char, simple: bool = False, use_english: bool = True, includes=None, exclude=None,
                       allow_fuzzy: bool = True, fuzzy_threshold: int = 70, max_exclude: int = 20, **kwargs):
    original_char = char
    if not isinstance(char, Character):
        char = get_character(char, allow_fuzzy, fuzzy_threshold, **kwargs)
    if not char:
        raise ValueError(f'Unknown character - {original_char!r}.')

    pool = _get_char_pool(type(char), **kwargs)
    _, game_tag, base_tag = _get_items_from_ch_type(type(char))

    try:
        if simple:
            return pool.get_simple_tag(char, base_tag, max_exclude=max_exclude)
    except ValueError:
        warnings.warn(UserWarning(f'No japanese name for {char!r}, falling back to full tag.'), stacklevel=2)

    return pool.get_tag(char, use_english, positive=[includes, game_tag], negative=exclude, max_exclude=max_exclude)
