import json
import os.path
import re
import time
import warnings
from functools import lru_cache
from itertools import chain
from typing import Type, List, Union, Dict, Tuple, Iterable, Optional, Callable, Mapping, Any
from urllib.parse import quote

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import yaml
from tqdm.auto import tqdm

from .games import _get_items_from_ch_type, _local_names_file, _local_characters_file, _local_alias_file
from .session import get_pixiv_sessions
from ...games import get_character
from ...games.base import Character
from ...utils import download_file, sget


def _native_pixiv_illustration_info(keyword, session=None, order='popular_d', mode='all', **kwargs) \
        -> Tuple[int, List[List[str]]]:
    """
    mode: all, safe, r18
    """
    session = session or get_pixiv_sessions(**kwargs)
    url = f'https://www.pixiv.net/ajax/search/artworks/{quote(keyword, safe="()")}?' \
          f'word={quote(keyword, safe="")}' \
          f'&order={order}&mode={mode}&p=1&s_mode=s_tag&type=all&lang=zh&version=9c834eede9446d61102731a4be356cd0f1090e84'

    resp = sget(session, url, headers={
        'Referer': f'https://www.pixiv.net/tags/{quote(keyword, safe="()")}/artworks?s_mode=s_tag',
    })
    resp.raise_for_status()
    data = resp.json()
    body = data['body']

    total_count = body["illustManga"]["total"]
    all_tags = [px['tags'] for px in body["illustManga"]['data']]
    return total_count, all_tags


def get_pixiv_illustration_count_by_keyword(keyword, session=None, order='popular_d', mode='all', **kwargs) -> int:
    if isinstance(keyword, Character):
        from .tag import get_pixiv_keywords
        char = keyword
        keyword = get_pixiv_keywords(keyword, **kwargs)
        warnings.warn(UserWarning(f'Character {char!r} detected, '
                                  f'auto-generated keyword {keyword!r} will be used.'), stacklevel=2)

    retval, _ = _native_pixiv_illustration_info(keyword, session, order=order, mode=mode, **kwargs)
    return retval


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


def _download_pixiv_alias_for_game(game: Union[Type[Character], str]):
    (cls, game_name), base_tag, _ = _get_items_from_ch_type(game)
    _alias_filename = _local_alias_file(game_name)
    download_file(
        f'https://huggingface.co/datasets/deepghs/game_characters/resolve/main/{game_name}/pixiv_alias.yaml',
        _alias_filename,
    )


def _load_pixiv_alias_for_game(cls: Type[Character]) -> Dict[Union[int, str], List[str]]:
    (_, game_name), _, _ = _get_items_from_ch_type(cls)
    _alias_filename = _local_alias_file(game_name)
    if not os.path.exists(_alias_filename):
        _download_pixiv_alias_for_game(game_name)

    with open(_alias_filename, 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader)

    alias = data['alias']
    return {item['id']: item['alias'] for item in alias}


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
    (cls, _), base_tag, _ = _get_items_from_ch_type(cls)
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
        all_keywords.append(f'{base_tag} {name} {excluded_text}')

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


def _download_pixiv_names_for_game(game: Union[Type[Character], str]):
    (cls, game_name), base_tag, _ = _get_items_from_ch_type(game)
    pixiv_names_file = _local_names_file(game_name)
    download_file(
        f'https://huggingface.co/datasets/deepghs/game_characters/resolve/main/{game_name}/pixiv_names.json',
        pixiv_names_file
    )


def _load_pixiv_names_for_game(game: Union[Type[Character], str]) \
        -> Dict[str, Tuple[int, float, List[Tuple[str, int]]]]:
    (cls, game_name), base_tag, _ = _get_items_from_ch_type(game)
    pixiv_names_file = _local_names_file(game_name)
    if not os.path.exists(pixiv_names_file):
        _download_pixiv_names_for_game(game)

    with open(pixiv_names_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        names = data['names']

    all_dict = {item['name']: item for item in names}
    all_counts = {}

    def _get_count(name):
        if name in all_counts:
            return all_counts[name]
        elif name not in all_dict:
            return 0
        else:
            item = all_dict[name]
            cnt = item['count']
            for ex in item['keyword']['excluded']:
                cnt += _get_count(ex)

            all_counts[name] = cnt
            return cnt

    retval = {}
    for item in names:
        name = item['name']
        count = _get_count(name)
        kwinfo = item['keyword']

        p_total = kwinfo['items']
        p_polluted = kwinfo['polluted']
        pollution_ratio = (p_polluted / p_total) if p_polluted else 0.0
        pollition_words = [(word, int(pcnt / p_total * count))
                           for word, pcnt in kwinfo['pollution'].items() if pcnt > 0]

        retval[name] = (count, pollution_ratio, pollition_words)

    return retval


def _get_pixiv_character_search_counts_by_game(
        cls: Type[Character], session=None,
        interval: float = 0.2, min_interval: float = 0.2,
        sleep_every: int = 70, sleep_time: float = 20,
        ensure_times: int = 2, maxcnt: Optional[int] = None, **kwargs):
    (cls, _), base_tag, _ = _get_items_from_ch_type(cls)
    session = session or get_pixiv_sessions(**kwargs)

    chs = cls.all(**kwargs)
    _all_ids = {}
    for ch in chs:
        _all_ids[ch.index] = _all_ids.get(ch.index, 0) + 1

    from .tag import get_pixiv_keywords

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
            'illustrations': {
                'all': count,
                'r18': unsafe_count,
            }
        })

    return retval


def _download_pixiv_characters_for_game(game: Union[Type[Character], str]):
    (cls, game_name), base_tag, _ = _get_items_from_ch_type(game)
    pixiv_names_file = _local_characters_file(game_name)
    download_file(
        f'https://huggingface.co/datasets/deepghs/game_characters/resolve/main/{game_name}/pixiv_characters.json',
        pixiv_names_file
    )


@lru_cache()
def _load_pixiv_characters_for_game(game: Union[Type[Character], str]) -> Dict[str, Tuple[int, int]]:
    (cls, game_name), base_tag, _ = _get_items_from_ch_type(game)
    pixiv_names_file = _local_characters_file(game_name)
    if not os.path.exists(pixiv_names_file):
        _download_pixiv_characters_for_game(game)

    with open(pixiv_names_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        chs = data['characters']

    return {item['index']: (item["illustrations"]["all"], item["illustrations"]["r18"]) for item in chs}


def query_pixiv_illustration_count_by_character(char, allow_fuzzy: bool = True, fuzzy_threshold: int = 70,
                                                **kwargs) -> Optional[Tuple[int, int]]:
    original_char = char
    if not isinstance(char, Character):
        char = get_character(char, allow_fuzzy, fuzzy_threshold, **kwargs)
    if not char:
        raise ValueError(f'Unknown character - {original_char!r}.')

    all_data = _load_pixiv_characters_for_game(type(char))
    return all_data.get(char.index, None)
