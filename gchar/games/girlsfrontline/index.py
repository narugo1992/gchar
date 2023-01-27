import json
import os.path
import re
import time
from typing import Optional

import requests
from pyquery import PyQuery as pq
from tqdm import tqdm

from ..base import get_requests_session

_LOCAL_DIR, _ = os.path.split(os.path.abspath(__file__))
_INDEX_FILE = os.path.join(_LOCAL_DIR, 'index.json')

_ROOT_SITE = 'https://iopwiki.com'

_STAR_PATTERN = re.compile(r'(?P<rarity>\d|EXTRA)star\.png')
_CLASS_PATTERN = re.compile(r'_(?P<class>SMG|MG|RF|HG|AR|SG)_')


def _get_index_from_iopwiki(timeout: int = 5, maxcnt: Optional[int] = None):
    session = get_requests_session()

    def _get_media_url(purl: str) -> str:
        resp_ = session.get(purl, timeout=timeout)
        resp_.raise_for_status()

        return pq(resp_.text)(".fullMedia a").attr("href")

    response = session.get(f'{_ROOT_SITE}/wiki/T-Doll_Index')
    response.raise_for_status()

    full = pq(response.text)

    retval = []
    all_items = list(full('span.card-bg-small').items())
    all_items_tqdm = tqdm(all_items)
    for item in all_items_tqdm:
        id_text = item('span.index').text().strip()
        if not id_text:
            continue

        title = item('a').attr('title')
        rele, *_ = _STAR_PATTERN.findall(item('img.rarity-stars').attr('src'))
        clazz, *_ = _CLASS_PATTERN.findall(item('img.rarity-class').attr('src'))
        rarity = int(rele) if len(rele) == 1 else rele
        id_ = int(id_text)

        def _get_name_with_lang(lang: str) -> str:
            return full(f'span[data-server-doll={title!r}][data-server-released={lang!r}]') \
                .attr('data-server-releasename')

        cnname = _get_name_with_lang('CN')
        enname = _get_name_with_lang('EN')
        jpname = _get_name_with_lang('JP')
        all_items_tqdm.set_description(f'{cnname}/{enname}/{jpname}')

        resp = session.get(f"{_ROOT_SITE}/{item('.pad a').attr('href')}")
        resp.raise_for_status()

        ch_page = pq(resp.text)
        _first, *_ = ch_page('a.image').parents('ul').items()
        img_items = list(_first('li').items())
        skins = []
        img_items_tqdm = tqdm(img_items)
        for fn in img_items_tqdm:
            img_name = fn('.gallerytext').text()
            img_items_tqdm.set_description(img_name)
            img_url = _get_media_url(f"{_ROOT_SITE}/{fn('a.image').attr('href')}")
            skins.append({
                'desc': img_name,
                'url': f"{_ROOT_SITE}/{img_url}",
            })

        retval.append({
            'id': id_,
            'rarity': rarity,
            'class': clazz,
            'cnname': cnname,
            'enname': enname,
            'jpname': jpname,
            'twname': _get_name_with_lang('TW'),
            'krname': _get_name_with_lang('KR'),
            'skins': skins
        })
        if maxcnt is not None and len(retval) >= maxcnt:
            break

    return retval


def _refresh_index(timeout: int = 5, maxcnt: Optional[int] = None):
    data = _get_index_from_iopwiki(timeout, maxcnt)
    with open(_INDEX_FILE, 'w') as f:
        tagged_data = {
            'data': data,
            'last_updated': time.time(),
        }
        json.dump(tagged_data, f, indent=4, ensure_ascii=False)


def _get_index_from_local():
    with open(_INDEX_FILE, 'r') as f:
        return json.load(f)['data']


def _local_is_ready() -> bool:
    return os.path.exists(_INDEX_FILE)


def get_index(force_refresh: bool = False, timeout: int = 5):
    if force_refresh or not _local_is_ready():
        try:
            _refresh_index(timeout=timeout)
        except requests.exceptions.RequestException:
            if not _local_is_ready():
                raise FileNotFoundError('Unable to prepare for local datafile.')

    return _get_index_from_local()