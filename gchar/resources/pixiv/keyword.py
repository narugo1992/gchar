import json
import os.path
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


def get_pixiv_illustration_count(keyword, session=None, **kwargs) -> int:
    session = session or get_pixiv_session(**kwargs)
    url = f'https://www.pixiv.net/ajax/search/artworks/{quote(keyword, safe="()")}?' \
          f'word={quote(keyword, safe="")}' \
          f'&order=date_d&mode=all&p=1&s_mode=s_tag&type=all&lang=zh&version=9c834eede9446d61102731a4be356cd0f1090e84'

    resp = session.get(url, headers={
        'Referer': f'https://www.pixiv.net/tags/{quote(keyword, safe="()")}/artworks?s_mode=s_tag',
    })
    resp.raise_for_status()
    data = resp.json()
    body = data['body']
    return body["illustManga"]["total"]


def _names_search_count(keywords: Iterable[str], session=None,
                        interval: float = 0.2, sleep_every: int = 70, sleep_time: float = 20,
                        ensure_times: int = 3, **kwargs) -> List[int]:
    session = session or get_pixiv_session(**kwargs)
    # noinspection PyTypeChecker
    all_keywords: List[Tuple[int, str]] = list(enumerate(keywords))
    total = len(all_keywords)

    ret_counts = {}
    last_sizes = tuple((*([None] * (ensure_times - 1)), total))
    round = 0
    while all_keywords:
        new_round_names: List[Tuple[int, str]] = []
        all_names_tqdm = tqdm(all_keywords)
        for i, (kid, keyword) in enumerate(all_names_tqdm):
            all_names_tqdm.set_description(f'R{round + 1}/{i + 1} - {keyword}')
            count = get_pixiv_illustration_count(keyword, session)
            if count:
                ret_counts[kid] = count
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

    return [ret_counts.get(i, 0) for i in range(total)]


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
    all_keywords = [f'{base_tag} {name}' for name in all_names]
    all_counts = _names_search_count(all_keywords, session, interval, sleep_every, sleep_time, ensure_times, **kwargs)

    return sorted([(name, count) for name, count in zip(all_names, all_counts) if count > 0])


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
    for ch, count, unsafe_count in zip(all_characters, all_counts, all_unsafe_counts):
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


def get_character_pixiv_illustration_count(char, allow_fuzzy: bool = True, fuzzy_threshold: int = 70,
                                           **kwargs) -> Optional[Tuple[int, int]]:
    kwargs = {**kwargs, 'contains_extra': False}
    original_char = char
    if not isinstance(char, Character):
        char = get_character(char, allow_fuzzy, fuzzy_threshold, **kwargs)
    if not char:
        raise ValueError(f'Unknown character - {original_char!r}.')

    all_data = _load_pixiv_characters_for_game(type(char))
    return all_data.get(char.index, None)
