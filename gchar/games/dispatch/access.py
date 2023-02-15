from functools import lru_cache
from itertools import islice
from typing import Iterator, Tuple, Optional, List

from thefuzz import fuzz

from ..arknights import Character as ArknightsCharacter
from ..azurlane import Character as AzurLaneCharacter
from ..base import Character
from ..fgo import Character as FateGrandOrderCharacter
from ..genshin import Character as GenshinImpactCharacter
from ..girlsfrontline import Character as GirlsFrontLineCharacter
from ..neuralcloud import Character as NeuralCloudCharacter
from ...utils import optional_lru_cache

CHARS = [
    ArknightsCharacter,
    FateGrandOrderCharacter,
    AzurLaneCharacter,
    GenshinImpactCharacter,
    GirlsFrontLineCharacter,
    NeuralCloudCharacter,
]


@optional_lru_cache()
def _all_characters(**kwargs) -> List[Character]:
    from ...resources.pixiv import query_pixiv_illustration_count_by_character

    chs: List[Tuple[Character, int, bool, int]] = []
    cnt = 0
    for _ch_set in CHARS:
        for ch in _ch_set.all(**kwargs):
            counts = query_pixiv_illustration_count_by_character(ch)
            if counts:
                all_count, _ = counts
            else:
                all_count = 0
            chs.append((ch, all_count, ch.is_extra, cnt))
            cnt += 1

    chs = sorted(chs, key=lambda x: (0 if not x[2] else 1, -x[1], x[3]))
    return [ch for ch, _, _, _ in chs]


# NAME SIMILAR: 101-200
# ALIAS SIMILAR: 1-100
_ALIAS_MATCH = 300
_NAME_MATCH = 400


def _name_trim(name: str) -> str:
    return name.replace(' ', '').replace('-', '').replace('_', '').replace(chr(160), '').replace('\t', '')


def _yield_characters(name: str, allow_fuzzy: bool = False, fuzzy_threshold: int = 80, **kwargs) \
        -> Iterator[Tuple[Character, int]]:
    all_chs = _all_characters(**kwargs)
    for ch in all_chs:
        if any([_name == name for _name in ch._names()]):
            yield ch, _NAME_MATCH
    for ch in all_chs:
        if any([_name == name for _name in ch.alias_names]):
            yield ch, _ALIAS_MATCH

    if allow_fuzzy:
        @lru_cache()
        def _get_formatted_name(cls) -> str:
            return str(cls(name))

        items: List[Tuple[Character, int, int]] = []
        for i, ch in enumerate(all_chs):
            name_fuzzs = [
                fuzz.WRatio(
                    _name_trim(_get_formatted_name(type(_name))),
                    _name_trim(str(_name)),
                    force_ascii=False
                )
                for _name in ch._names()
            ]
            if name_fuzzs and max(name_fuzzs) >= fuzzy_threshold:
                items.append((ch, max(name_fuzzs) + 100, i))
        items = sorted(items, key=lambda x: (-x[1], x[2]))
        for ch, fuzzy, _ in items:
            yield ch, fuzzy

        items: List[Tuple[Character, int, int]] = []
        for i, ch in enumerate(all_chs):
            alias_fuzzs = [
                fuzz.WRatio(
                    _name_trim(_get_formatted_name(type(_name))),
                    _name_trim(str(_name)),
                    force_ascii=False
                )
                for _name in ch.alias_names
            ]
            if alias_fuzzs and max(alias_fuzzs) >= fuzzy_threshold:
                items.append((ch, max(alias_fuzzs), i))
        items = sorted(items, key=lambda x: (-x[1], x[2]))
        for ch, fuzzy, _ in items:
            yield ch, fuzzy


def list_character(name: str, limit: Optional[int] = None, allow_fuzzy: bool = False,
                   fuzzy_threshold: int = 80, **kwargs) -> List[Character]:
    iterator = _yield_characters(name, allow_fuzzy, fuzzy_threshold, **kwargs)
    if limit is not None:
        iterator = islice(iterator, limit)

    ordered = [ch for ch, _ in iterator]
    assert limit is None or len(ordered) <= limit
    return ordered


def get_character(name: str, allow_fuzzy: bool = False, fuzzy_threshold: int = 80,
                  contains_extra: bool = True, **kwargs) -> Optional[Character]:
    _items = list_character(name, limit=1, allow_fuzzy=allow_fuzzy, fuzzy_threshold=fuzzy_threshold,
                            contains_extra=contains_extra, **kwargs)
    if _items:
        return _items[0]
    else:
        return None
