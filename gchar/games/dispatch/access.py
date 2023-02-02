from functools import lru_cache
from typing import Iterator, Tuple, Optional, List

from thefuzz import fuzz

from gchar.games.arknights import Character as ArknightsCharacter
from gchar.games.azurlane import Character as AzurLaneCharacter
from gchar.games.base import Character
from gchar.games.fgo import Character as FateGrandOrderCharacter
from gchar.games.genshin import Character as GenshinImpactCharacter
from gchar.games.girlsfrontline import Character as GirlsFrontLineCharacter

CHARS = [
    ArknightsCharacter,
    FateGrandOrderCharacter,
    AzurLaneCharacter,
    GenshinImpactCharacter,
    GirlsFrontLineCharacter
]


def _all_characters(**kwargs) -> Iterator[Character]:
    for _ch_set in CHARS:
        yield from _ch_set.all(**kwargs)


# NAME SIMILAR: 101-200
# ALIAS SIMILAR: 1-100
_ALIAS_MATCH = 300
_NAME_MATCH = 400


def _name_trim(name: str) -> str:
    return name.replace(' ', '').replace('-', '').replace('_', '').replace(chr(160), '').replace('\t', '')


def _yield_characters(name: str, allow_fuzzy: bool = False, fuzzy_threshold: int = 80, **kwargs) \
        -> Iterator[Tuple[Character, int]]:
    for ch in _all_characters(**kwargs):
        if any([_name == name for _name in ch._names()]):
            yield ch, _NAME_MATCH
        elif any([_name == name for _name in ch.alias_names]):
            yield ch, _ALIAS_MATCH
        elif allow_fuzzy:
            @lru_cache()
            def _get_formatted_name(cls) -> str:
                return str(cls(name))

            name_fuzzs = [
                fuzz.WRatio(
                    _name_trim(_get_formatted_name(type(_name))),
                    _name_trim(str(_name)),
                    force_ascii=False
                )
                for _name in ch._names()
            ]
            if name_fuzzs and max(name_fuzzs) >= fuzzy_threshold:
                yield ch, max(name_fuzzs) + 100
                continue

            alias_fuzzs = [
                fuzz.WRatio(
                    _name_trim(_get_formatted_name(type(_name))),
                    _name_trim(str(_name)),
                    force_ascii=False
                )
                for _name in ch.alias_names
            ]
            if alias_fuzzs and max(alias_fuzzs) >= fuzzy_threshold:
                yield ch, max(alias_fuzzs)
                continue


def list_character(name: str, limit: Optional[int] = None, allow_fuzzy: bool = False,
                   fuzzy_threshold: int = 80, **kwargs) -> List[Character]:
    ordered = sorted(_yield_characters(name, allow_fuzzy, fuzzy_threshold, **kwargs),
                     key=lambda x: (-x[1], str(x[0])))
    if limit is not None:
        ordered = ordered[:limit]

    ordered = [ch for ch, _ in ordered]
    return ordered


def get_character(name: str, allow_fuzzy: bool = False, fuzzy_threshold: int = 80,
                  contains_extra: bool = False, **kwargs) -> Optional[Character]:
    _items = list_character(name, limit=1, allow_fuzzy=allow_fuzzy, fuzzy_threshold=fuzzy_threshold,
                            contains_extra=contains_extra, **kwargs)
    if _items:
        return _items[0]
    else:
        return None
