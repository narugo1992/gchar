import json
import os.path
import re
import time
from itertools import islice
from typing import Iterator, Optional
from urllib.parse import quote

import requests
from pyquery import PyQuery as pq
from requests.adapters import HTTPAdapter

from ...utils import import_tqdm, download_file

tqdm = import_tqdm()

_LOCAL_DIR, _ = os.path.split(os.path.abspath(__file__))
_INDEX_FILE = os.path.join(_LOCAL_DIR, 'index.json')

_WEBSITE_ROOT = 'https://prts.wiki/'


def _get_skins_of_op(op, session: requests.Session):
    search_content = quote(f"立绘 \"{op}\"")
    response = session.get(
        f'{_WEBSITE_ROOT}/index.php?title=%E7%89%B9%E6%AE%8A:%E6%90%9C%E7%B4%A2&profile=images'
        f'&search={search_content}&fulltext=1'
    )
    response.raise_for_status()

    text = response.content.decode()
    full = pq(text)
    result_list = full('li.mw-search-result')

    skins = []
    exist_names = set()
    tqs = tqdm(list(result_list.items()))
    for item in tqs:
        url = item('td > a')
        title = url.text().strip()
        resource_url = f"{_WEBSITE_ROOT}/{url.attr('href')}"
        tqs.set_description(title)

        assert title.startswith('文件:')
        _, ctitle = title.split(':', maxsplit=1)
        ctitle, _ = os.path.splitext(ctitle)
        if ctitle in exist_names:
            continue

        try:
            _, name, sign = re.split(r'\s+', ctitle, maxsplit=2)
        except ValueError:
            continue

        if name != op:
            continue

        if not re.fullmatch(r'^(skin\d+|\d+|\d+\+)$', sign):
            continue

        resp = session.get(resource_url)
        resp.raise_for_status()

        page = pq(resp.text)
        media_url = f"{_WEBSITE_ROOT}/{page('.fullMedia a').attr('href')}"

        skins.append({
            'name': ctitle,
            'url': media_url,
        })
        exist_names.add(ctitle)

    return skins


_KNOWN_DATA_FIELDS = [
    "data-cn",
    "data-position",
    "data-en",
    "data-sex",
    "data-tag",
    "data-race",
    "data-rarity",
    "data-class",
    "data-approach",
    "data-camp",
    "data-team",
    "data-des",
    "data-feature",
    "data-str",
    "data-flex",
    "data-tolerance",
    "data-plan",
    "data-skill",
    "data-adapt",
    "data-moredes",
    "data-icon",
    "data-half",
    "data-ori-hp",
    "data-ori-atk",
    "data-ori-def",
    "data-ori-res",
    "data-ori-dt",
    "data-ori-dc",
    "data-ori-block",
    "data-ori-cd",
    "data-index",
    "data-jp",
    "data-birthplace",
    "data-nation",
    "data-group"
]

_UNQUOTE_NEEDED_FIELDS = {
    'data-feature',
}


def _get_index_from_prts(timeout: int = 5, max_retries: int = 3) -> Iterator[dict]:
    session = requests.session()
    session.mount('http://', HTTPAdapter(max_retries=max_retries))
    session.mount('https://', HTTPAdapter(max_retries=max_retries))
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    })

    response = session.get(
        f'{_WEBSITE_ROOT}/w/CHAR?filter=AAAAAAAggAAAAAAAAAAAAAAAAAAAAAAA',
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
        },
        timeout=timeout
    )
    response.raise_for_status()

    text = response.content.decode()
    tqs = tqdm(list(pq(text)('.smwdata').items()))
    for item in tqs:
        data = {}
        for name in _KNOWN_DATA_FIELDS:
            val = item.attr(name)
            if name in _UNQUOTE_NEEDED_FIELDS:
                val = pq(val).text()
            data[name] = val

        tqs.set_description(data['data-cn'])

        skins = _get_skins_of_op(data['data-cn'], session)
        assert skins
        yield {
            'data': data,
            'skins': skins,
        }


_MIN_REFRESH_SPAN = 3 * 24 * 60 * 60  # 3 days


def _refresh_index(timeout: int = 5, maxcnt: Optional[int] = None, index_file: Optional[str] = None):
    yielder = _get_index_from_prts(timeout)
    if maxcnt:
        yielder = islice(yielder, maxcnt)
    data = list(yielder)
    with open(index_file or _INDEX_FILE, 'w') as f:
        tagged_data = {
            'data': data,
            'last_updated': time.time(),
        }
        json.dump(tagged_data, f, indent=4, ensure_ascii=False)


def _get_index_from_local():
    with open(_INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['data']


def _local_is_ready() -> bool:
    return os.path.exists(_INDEX_FILE)


ONLINE_INDEX_URL = 'https://huggingface.co/datasets/deepghs/game_characters/resolve/main/arknights/index.json'


def _download_from_huggingface():
    download_file(ONLINE_INDEX_URL, _INDEX_FILE)


def get_index(crawl: bool = False, force_refresh: bool = False, timeout: int = 5):
    if force_refresh or not _local_is_ready():
        try:
            if crawl:
                _refresh_index(timeout=timeout)
            else:
                _download_from_huggingface()
        except requests.exceptions.RequestException:
            if not _local_is_ready():
                raise FileNotFoundError('Unable to prepare for local datafile.')

    return _get_index_from_local()
