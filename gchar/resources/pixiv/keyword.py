import time
from typing import Type, List
from urllib.parse import quote

from tqdm.auto import tqdm

from .games import _get_items_from_ch_type
from .session import get_pixiv_session
from ...games.base import Character


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
                                **kwargs):
    cls, base_tag, _ = _get_items_from_ch_type(cls)
    session = session or get_pixiv_session(**kwargs)

    _all_names_set = set()
    for ch in cls.all(contains_extra=True):
        for name in ch.names:
            _all_names_set.add(name)
    all_names: List[str] = sorted(_all_names_set)

    retval = []
    nts = (None, None)
    cnt, round = 0, 0
    while all_names:
        new_round_names = []
        all_names_tqdm = tqdm(all_names)
        for name in all_names_tqdm:
            all_names_tqdm.set_description(f'R{round + 1}/{cnt + 1} - {name}')
            keyword = f'{base_tag} {name}'
            count = get_pixiv_illustration_count(keyword, session)
            cnt += 1
            if count:
                retval.append((name, count))
            else:
                new_round_names.append(name)

            if cnt % sleep_every == 0:
                time.sleep(sleep_time)
            else:
                time.sleep(interval)

        if cnt % sleep_every != 0:
            time.sleep(sleep_time)

        all_names = new_round_names
        round += 1
        _, *_old_nts = nts
        nts = tuple((*_old_nts, len(all_names)))
        if all([nts[i] == nts[i + 1] for i in range(len(nts) - 1)]):
            break

    return sorted(retval)
