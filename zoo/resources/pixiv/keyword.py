import json
import re
import time
from contextlib import contextmanager
from itertools import chain
from typing import Type, List, Union, Dict, Tuple, Iterable, Optional, Callable, Mapping, Any
from unittest import mock
from urllib.parse import quote

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from tqdm.auto import tqdm

from .session import get_pixiv_sessions
from ditk import logging
from gchar.games.base import Character
from gchar.utils import sget
from gchar.resources.pixiv.tag import get_pixiv_keywords
from gchar.resources.pixiv.keyword import _load_pixiv_alias_for_game, _parse_pixiv_names_file


def _native_pixiv_illustration_info(keyword, session=None, order='popular_d', mode='all', **kwargs) \
        -> Tuple[int, List[List[str]]]:
    """
    mode: all, safe, r18
    """
    session = session or get_pixiv_sessions(**kwargs)
    url = f'https://www.pixiv.net/ajax/search/artworks/{quote(keyword, safe="()")}?' \
          f'word={quote(keyword, safe="")}' \
          f'&order={order}&mode={mode}&p=1&s_mode=s_tag&type=all&lang=zh' \
          f'&version=9c834eede9446d61102731a4be356cd0f1090e84'

    resp = sget(session, url, headers={
        'Referer': f'https://www.pixiv.net/tags/{quote(keyword, safe="()")}/artworks?s_mode=s_tag',
    })
    resp.raise_for_status()
    data = resp.json()
    body = data['body']

    total_count = body["illustManga"]["total"]
    all_tags = [px['tags'] for px in body["illustManga"]['data']]
    return total_count, all_tags


def _process_name_search_item(keyword: Union[str, Tuple[str, Mapping[str, Any]]]) -> Tuple[str, Mapping[str, Any]]:
    if isinstance(keyword, str):
        return keyword, {}
    elif isinstance(keyword, tuple):
        return keyword
    else:
        raise TypeError(f'Invalid keyword format - {keyword!r}.')


def _names_search_count(keywords: Iterable[str], session=None,
                        interval: Union[float, Callable[[], float]] = 0.2,
                        sleep_every: int = 70, sleep_time: float = 20,
                        ensure_times: int = 2, **kwargs) -> List[Tuple[int, List[List[str]]]]:
    session = session or get_pixiv_sessions(**kwargs)
    # noinspection PyTypeChecker
    all_keywords: List[Tuple[int, Tuple[str, Mapping[str, Any]]]] = \
        list(enumerate(map(_process_name_search_item, keywords)))
    total = len(all_keywords)

    records: Dict[int, Tuple[int, List[List[str]]]] = {}
    last_sizes = tuple((*([None] * (ensure_times - 1)), total))
    round = 0
    while all_keywords:
        new_round_names: List[Tuple[int, Tuple[str, Mapping[str, Any]]]] = []
        all_names_tqdm = tqdm(all_keywords)
        for i, (kid, (keyword, info_kwargs)) in enumerate(all_names_tqdm):
            all_names_tqdm.set_description(f'R{round + 1}/{i + 1} - {keyword} - {info_kwargs!r}')
            count, all_tags = _native_pixiv_illustration_info(keyword, session, **info_kwargs)
            if count:
                records[kid] = (count, all_tags)
            else:
                new_round_names.append((kid, (keyword, info_kwargs)))

            if (i + 1) % sleep_every == 0:
                time.sleep(sleep_time)
            else:
                if isinstance(interval, (int, float)):
                    time.sleep(interval)
                else:
                    time.sleep(interval())

        need_sleep = len(all_keywords) % sleep_every != 0
        all_keywords = new_round_names
        round += 1
        last_sizes = tuple((*last_sizes[1:], len(all_keywords)))
        if not all_keywords or all([last_sizes[i] == last_sizes[i + 1] for i in range(ensure_times - 1)]):
            break

        if need_sleep:
            time.sleep(sleep_time)

    final_retval = []
    for i in range(total):
        if i in records:
            final_retval.append(records[i])
        else:
            final_retval.append((0, []))

    return final_retval


def _get_interval_func(interval: float, min_interval: float):
    import numpy as np
    mean, std = interval, 0.4 * interval
    lower_bound, upper_bound = min_interval, interval * 2

    def _interval_func():
        v = np.random.normal(mean, std)
        while not (lower_bound <= v <= upper_bound):
            v = np.random.normal(mean, std)

        return float(v)

    return _interval_func


def _get_pixiv_search_count_by_name(
        cls: Type[Character], session=None, interval: float = 0.2, min_interval: float = 0.2,
        sleep_every: int = 70, sleep_time: float = 20, ensure_times: int = 2, maxcnt: Optional[int] = None, **kwargs):
    base_tag = cls.__pixiv_keyword__
    session = session or get_pixiv_sessions(**kwargs)

    _all_names_set = set()
    for ch in cls.all(contains_extra=True):
        for name in ch.names:
            _all_names_set.add(name)

    _alias_data = _load_pixiv_alias_for_game(cls)
    _all_names_set |= set(chain(*_alias_data.values()))

    all_names: List[str] = [name.lower() for name in sorted(_all_names_set)]
    if maxcnt is not None:
        all_names = all_names[-maxcnt:]
    all_keywords = []
    all_excluded = []
    for name in all_names:
        excluded_words = []
        for name_x in all_names:
            if name in name_x and name != name_x:
                excluded_words.append(name_x)

        excluded_text = ' '.join(map(lambda x: f'-{x}', sorted(excluded_words)))
        all_excluded.append(excluded_words)
        if base_tag:
            all_keywords.append(f'{base_tag} {name} {excluded_text}')
        else:
            all_keywords.append(f'{name} {excluded_text}')

    count_data = _names_search_count(all_keywords, session, _get_interval_func(interval, min_interval),
                                     sleep_every, sleep_time, ensure_times, **kwargs)
    retval = []
    for name, keyword, excluded, (count, tag_items) in zip(all_names, all_keywords, all_excluded, count_data):
        if count <= 0:
            continue

        _name_pattern = re.compile(f'\\b{re.escape(name)}\\b', re.IGNORECASE)
        _name_partial_pattern = re.compile(f'\\b(\\w*{re.escape(name)}\\w*)\\b', re.IGNORECASE)
        word_matched_cnt, word_polluted_cnt = 0, 0
        all_pollution = {}
        groups = []
        for tags in tag_items:
            matched, finded_words = False, []
            for tag in tags:
                exact_matches = _name_pattern.findall(tag.lower())
                if exact_matches:
                    matched = True

                partial_matches = sorted(set(_name_partial_pattern.findall(tag.lower())) - set(exact_matches))
                finded_words.extend(partial_matches)

            if matched:
                word_matched_cnt += 1
            elif finded_words:
                word_polluted_cnt += 1
                for word in set(finded_words):
                    all_pollution[word] = all_pollution.get(word, 0) + 1
                groups.append(tuple(set(finded_words)))

        recorded_names = set()
        while groups:
            word, cnt = sorted(all_pollution.items(),
                               key=lambda x: (1 if x[0] in recorded_names else 0, -x[1], len(x[0]), x[0]))[0]
            recorded_names.add(word)
            new_groups = []
            for group in groups:
                if word in group:
                    for item in group:
                        if item not in recorded_names:
                            all_pollution[item] -= 1
                else:
                    new_groups.append(group)
            groups = new_groups

        all_pollution = {name: cnt for name, cnt in all_pollution.items() if cnt > 0}
        assert sum(all_pollution.values()) == word_polluted_cnt
        retval.append({
            'name': name,
            'count': count,
            'keyword': {
                'text': keyword,
                'excluded': excluded,
                'items': len(tag_items),
                'matched': word_matched_cnt,
                'polluted': word_polluted_cnt,
                'pollution': dict(sorted(all_pollution.items(), key=lambda x: (-x[1], x[0]))),
            }
        })

    return retval


@contextmanager
def _try_mock_character_name_file(input_file: Optional[str]):
    if input_file is not None:
        def _load_pixiv_names_for_game(game_cls):
            _ = game_cls
            logging.info(f'Load pixiv names file from {input_file!r}.')
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                names = data['names']

            return _parse_pixiv_names_file(names)

        with mock.patch('gchar.resources.pixiv.tag._load_pixiv_names_for_game', _load_pixiv_names_for_game):
            yield

    else:
        yield


def _get_pixiv_character_search_counts_by_game(
        cls: Type[Character], session=None,
        interval: float = 0.2, min_interval: float = 0.2,
        sleep_every: int = 70, sleep_time: float = 20,
        ensure_times: int = 2, maxcnt: Optional[int] = None,
        input_file: Optional[str] = None, **kwargs):
    with _try_mock_character_name_file(input_file):
        base_tag = cls.__pixiv_keyword__
        session = session or get_pixiv_sessions(**kwargs)

        chs = cls.all(**kwargs)
        _all_ids = {}
        for ch in chs:
            _all_ids[ch.index] = _all_ids.get(ch.index, 0) + 1

        all_characters, all_keywords, all_unsafe_keywords = [], [], []
        for ch in chs:
            if ch.is_extra and _all_ids.get(ch.index, 0) > 1:
                continue

            all_characters.append(ch)
            keyword = get_pixiv_keywords(ch)
            all_keywords.append(keyword)
            all_unsafe_keywords.append((keyword, {'mode': 'r18'}))

            if maxcnt is not None and len(all_characters) >= maxcnt:
                break

        _all = _names_search_count([*all_keywords, *all_unsafe_keywords], session,
                                   _get_interval_func(interval, min_interval),
                                   sleep_every, sleep_time, ensure_times, **kwargs)
        all_counts = _all[:len(all_keywords)]
        all_unsafe_counts = _all[len(all_keywords):]

        retval = []
        for ch, (count, _), (unsafe_count, _) in zip(all_characters, all_counts, all_unsafe_counts):
            retval.append({
                'index': ch.index,
                'cnname': str(ch.cnname) if ch.cnname else None,
                'enname': str(ch.enname) if ch.enname else None,
                'jpname': str(ch.jpname) if ch.jpname else None,
                'illustrations': {
                    'all': count,
                    'r18': unsafe_count,
                }
            })

        return retval
