import json
import os.path
import re
import time
from functools import lru_cache
from typing import Type, List, Union, Dict, Tuple, Iterable, Optional
from urllib.parse import quote

from tqdm.auto import tqdm

from .games import _get_items_from_ch_type, _local_names_file, _local_characters_file
from .session import get_pixiv_session
from ...games import get_character
from ...games.base import Character
from ...utils import download_file


def get_pixiv_illustration_count_by_keyword(keyword, session=None, order='popular_d', **kwargs) \
        -> Tuple[int, List[List[str]]]:
    session = session or get_pixiv_session(**kwargs)
    url = f'https://www.pixiv.net/ajax/search/artworks/{quote(keyword, safe="()")}?' \
          f'word={quote(keyword, safe="")}' \
          f'&order={order}&mode=all&p=1&s_mode=s_tag&type=all&lang=zh&version=9c834eede9446d61102731a4be356cd0f1090e84'

    resp = session.get(url, headers={
        'Referer': f'https://www.pixiv.net/tags/{quote(keyword, safe="()")}/artworks?s_mode=s_tag',
    })
    resp.raise_for_status()
    data = resp.json()
    body = data['body']

    total_count = body["illustManga"]["total"]
    all_tags = [px['tags'] for px in body["illustManga"]['data']]
    return total_count, all_tags


def _names_search_count(keywords: Iterable[str], session=None,
                        interval: float = 0.2, sleep_every: int = 70, sleep_time: float = 20,
                        ensure_times: int = 3, **kwargs) -> List[Tuple[int, List[List[str]]]]:
    session = session or get_pixiv_session(**kwargs)
    # noinspection PyTypeChecker
    all_keywords: List[Tuple[int, str]] = list(enumerate(keywords))
    total = len(all_keywords)

    records: Dict[int, Tuple[int, List[List[str]]]] = {}
    last_sizes = tuple((*([None] * (ensure_times - 1)), total))
    round = 0
    while all_keywords:
        new_round_names: List[Tuple[int, str]] = []
        all_names_tqdm = tqdm(all_keywords)
        for i, (kid, keyword) in enumerate(all_names_tqdm):
            all_names_tqdm.set_description(f'R{round + 1}/{i + 1} - {keyword}')
            count, all_tags = get_pixiv_illustration_count_by_keyword(keyword, session)
            if count:
                records[kid] = (count, all_tags)
            else:
                new_round_names.append((kid, keyword))

            if (i + 1) % sleep_every == 0:
                time.sleep(sleep_time)
            else:
                time.sleep(interval)

        if len(all_keywords) % sleep_every != 0:
            time.sleep(sleep_time)

        all_keywords = new_round_names
        round += 1
        last_sizes = tuple((*last_sizes[1:], len(all_keywords)))
        if all([last_sizes[i] == last_sizes[i + 1] for i in range(ensure_times - 1)]):
            break

    final_retval = []
    for i in range(total):
        if i in records:
            final_retval.append(records[i])
        else:
            final_retval.append((0, []))

    return final_retval


def get_pixiv_name_search_count(cls: Type[Character], session=None,
                                interval: float = 0.2, sleep_every: int = 70, sleep_time: float = 20,
                                ensure_times: int = 3, **kwargs):
    (cls, _), base_tag, _ = _get_items_from_ch_type(cls)
    session = session or get_pixiv_session(**kwargs)

    _all_names_set = set()
    for ch in cls.all(contains_extra=True):
        for name in ch.names:
            _all_names_set.add(name)
    all_names: List[str] = sorted(_all_names_set)
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

    count_data = _names_search_count(all_keywords, session, interval, sleep_every, sleep_time, ensure_times, **kwargs)
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

        all_pollution = {name: cnt for name, cnt in all_pollution.items() if cnt >= 0}
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


def _load_pixiv_names_for_game(game: Union[Type[Character], str]) -> Dict[str, int]:
    (cls, game_name), base_tag, _ = _get_items_from_ch_type(game)
    pixiv_names_file = _local_names_file(game_name)
    if not os.path.exists(pixiv_names_file):
        _download_pixiv_names_for_game(game)

    with open(pixiv_names_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        names = data['names']

    return {item['name']: item['count'] for item in names}


def get_pixiv_character_search_count(cls: Type[Character], session=None,
                                     interval: float = 0.2, sleep_every: int = 70, sleep_time: float = 20,
                                     ensure_times: int = 3, **kwargs):
    (cls, _), base_tag, _ = _get_items_from_ch_type(cls)
    session = session or get_pixiv_session(**kwargs)

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
        all_keywords.append(get_pixiv_keywords(ch))
        all_unsafe_keywords.append(get_pixiv_keywords(ch, includes=['R-18']))

    _all = _names_search_count([*all_keywords, *all_unsafe_keywords], session,
                               interval, sleep_every, sleep_time, ensure_times, **kwargs)
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


def get_pixiv_illustration_count_by_character(char, allow_fuzzy: bool = True, fuzzy_threshold: int = 70,
                                              **kwargs) -> Optional[Tuple[int, int]]:
    original_char = char
    if not isinstance(char, Character):
        char = get_character(char, allow_fuzzy, fuzzy_threshold, **kwargs)
    if not char:
        raise ValueError(f'Unknown character - {original_char!r}.')

    all_data = _load_pixiv_characters_for_game(type(char))
    return all_data.get(char.index, None)
