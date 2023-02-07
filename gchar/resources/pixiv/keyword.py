import json
import os.path
import time
from typing import Type, List, Union, Dict
from urllib.parse import quote

from tqdm.auto import tqdm

from .games import _get_items_from_ch_type, _local_names_file
from .session import get_pixiv_session
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

    retval = []
    nts = tuple([None] * ensure_times)
    round = 0
    while all_names:
        new_round_names = []
        all_names_tqdm = tqdm(all_names)
        for i, name in enumerate(all_names_tqdm):
            all_names_tqdm.set_description(f'R{round + 1}/{i + 1} - {name}')
            keyword = f'{base_tag} {name}'
            count = get_pixiv_illustration_count(keyword, session)
            if count:
                retval.append((name, count))
            else:
                new_round_names.append(name)

            if (i + 1) % sleep_every == 0:
                time.sleep(sleep_time)
            else:
                time.sleep(interval)

        if len(all_names) % sleep_every != 0:
            time.sleep(sleep_time)

        all_names = new_round_names
        round += 1
        _, *_old_nts = nts
        nts = tuple((*_old_nts, len(all_names)))
        if all([nts[i] == nts[i + 1] for i in range(len(nts) - 1)]):
            break

    return sorted(retval)


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
