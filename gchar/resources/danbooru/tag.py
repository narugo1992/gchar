import re
from typing import Iterator, Optional, List

import editdistance
from thefuzz import fuzz
from thefuzz import process as fp

from .index import _trim_name_to_ascii, get_lookup
from ...games import get_character
from ...games.base import Character


def _ascii_only(name: str) -> str:
    return ''.join(re.findall(r'[\x00-\xff]+', name))


def _get_ascii_names(ch: Character, rdis: float = 0.15, adis=2) -> Iterator[str]:
    tags = [
        (editdistance.eval(_ascii_only(name), name), i, name)
        for i, name in enumerate(map(lambda x: str(x).lower(), ch.names))
    ]

    for distance, _, name in tags:
        r_distance = distance / len(name)
        if (distance <= adis and r_distance <= rdis * 2) or r_distance <= rdis:
            yield name


def list_danbooru_tags(char, allow_fuzzy: bool = True, fuzzy_threshold: int = 70, ed_ratio: float = 1.05,
                       limit: int = 5, **kwargs) -> List[str]:
    original_char = char
    if not isinstance(char, Character):
        char = get_character(char, allow_fuzzy, fuzzy_threshold, **kwargs)
    if not char:
        raise ValueError(f'Unknown character - {original_char!r}.')

    tags, lookup = get_lookup(type(char))
    findings = []
    for name in _get_ascii_names(char):
        _trimed = _trim_name_to_ascii(name)
        findings.extend([
            (_trimed, mx, editdistance.eval(_trimed, mx) / min(len(_trimed), len(mx)), score,)
            for mx, score in fp.extractBests(
                _trimed, lookup.keys(),
                scorer=fuzz.WRatio,
                score_cutoff=fuzzy_threshold if allow_fuzzy else 100,
                limit=limit,
            )
        ])

    findings = list(filter(lambda x: x[2] <= ed_ratio, findings))
    findings = sorted(findings, key=lambda x: (x[2], -x[3]))
    if limit is not None:
        findings = findings[:limit]
    tag_list = []
    for i, (_, mx, *_) in enumerate(findings):
        for oid in lookup[mx]:
            data = tags[oid]
            tag = data['tag']
            posts = data['posts']
            tag_list.append((i, posts, tag))

    tag_list = sorted(tag_list, key=lambda x: (x[0], -x[1]))
    if limit is not None:
        tag_list = tag_list[:limit]
    return [tag for _, _, tag in tag_list]


def get_danbooru_tag(char, allow_fuzzy: bool = True, fuzzy_threshold: int = 80, ed_ratio: float = 0.7,
                     **kwargs) -> Optional[str]:
    lists = list_danbooru_tags(char, allow_fuzzy, fuzzy_threshold, ed_ratio, limit=1, **kwargs)
    if lists:
        return lists[0]
    else:
        return None
