import re
import warnings
from functools import lru_cache
from typing import Iterable, Iterator, Union, List, Tuple, Type

from .games import _GAMES
from ...games import get_character
from ...games.base import Character


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
    def __init__(self, chars: Iterable[Character]):
        self.__chars = list(chars)

    def _iter_dup_names(self, name: str) -> Iterator[str]:
        for ch in self.__chars:
            for sname in map(str, ch.names):
                if name != sname and name in sname:
                    yield sname

    def get_tag(self, char: Character, use_english: bool = False, positive=None, negative=None,
                max_exclude_per_word: int = 20):
        if not isinstance(char, Character):
            raise TypeError(f'Invalid character type - {char!r}.')  # pragma: no cover

        char_names = [*char.cnnames, *char.jpnames]
        if use_english:
            char_names.extend(char.ennames)

        positive = set(_yield_tags(positive or []))
        negative = set(_yield_tags(negative or [])) - positive
        or_clause = set()

        for chname in char_names:
            all_exnames = list(self._iter_dup_names(str(chname)))
            if len(all_exnames) >= max_exclude_per_word:
                continue

            or_clause.add(str(chname))
            for exname in all_exnames:
                if exname not in positive and exname not in or_clause:
                    negative.add(exname)

        return _format_tags(positive, negative, or_clause)

    def _iter_end_dup_names(self, name: str) -> Iterator[str]:
        for ch in self.__chars:
            for sname in map(str, ch.names):
                if name != sname and sname.endswith(name):
                    yield sname

    def get_simple_tag(self, char: Character, base_tag: str):
        if not isinstance(char, Character):
            raise TypeError(f'Invalid character type - {char!r}.')  # pragma: no cover

        positive = set()
        negative = set()
        or_clause = set()
        if char.jpnames:
            for jpname in char.jpnames:
                positive.add(f'{jpname}({base_tag})')
                for exname in self._iter_end_dup_names(str(jpname)):
                    negative.add(exname)

        else:
            raise ValueError(f'Japanese name not found for character - {char!r}.')

        return _format_tags(positive, negative, or_clause)


@lru_cache()
def _get_items(cls: Type[Character]) -> Tuple[str, str]:
    for item in _GAMES:
        if len(item) == 2:
            _cls, game_tag = item
            base_tag = game_tag
        elif len(item) == 3:
            _cls, game_tag, base_tag = item
        else:
            assert False, f'Invalid games item - {item!r}.'  # pragma: no cover

        if cls == _cls:
            return game_tag, base_tag

    raise TypeError(f'Unknown character type - {cls}.')  # pragma: no cover


@lru_cache()
def _get_char_pool(cls: Type[Character], **kwargs):
    return PixivCharPool(cls.all(**kwargs))


def get_pixiv_keywords(char, simple: bool = False, use_english: bool = True, includes=None, exclude=None,
                       allow_fuzzy: bool = True, fuzzy_threshold: int = 70, **kwargs):
    kwargs = {**kwargs, 'contains_extra': False}
    original_char = char
    if not isinstance(char, Character):
        char = get_character(char, allow_fuzzy, fuzzy_threshold, **kwargs)
    if not char:
        raise ValueError(f'Unknown character - {original_char!r}.')

    pool = _get_char_pool(type(char), **kwargs)
    game_tag, base_tag = _get_items(type(char))

    try:
        if simple:
            return pool.get_simple_tag(char, base_tag)
    except ValueError:
        warnings.warn(UserWarning(f'No japanese name for {char!r}, falling back to full tag.'), stacklevel=2)

    return pool.get_tag(char, use_english, positive=[includes, game_tag], negative=exclude)
