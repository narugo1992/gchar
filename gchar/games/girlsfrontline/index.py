import json
import os.path
import re
import time
from typing import Optional, List, Dict
from urllib.parse import quote

import requests
from pyquery import PyQuery as pq
from tqdm import tqdm

from ...utils import download_file, get_requests_session, sget

_LOCAL_DIR, _ = os.path.split(os.path.abspath(__file__))
_INDEX_FILE = os.path.join(_LOCAL_DIR, 'index.json')

_WEBSITE_ROOT = 'https://iopwiki.com'
_CN_WEBSITE_ROOT = 'https://www.gfwiki.org'

_STAR_PATTERN = re.compile(r'(?P<rarity>\d|EXTRA)star\.png')
_CLASS_PATTERN = re.compile(r'_(?P<class>SMG|MG|RF|HG|AR|SG)_')

_CN_SITE_ATTRS = [
    'data-mod', 'data-time-stamp', 'data-tile-effect1', 'data-tile-effect1-time', 'data-tile-effect2',
    'data-tile-effect2-time', 'data-id', 'data-name-ingame', 'data-url', 'data-rarity',
    'data-tdoll-class', 'data-tiles', 'data-obtain-method', 'data-tiles-affect', 'data-base-hp',
    'data-base-atk', 'data-base-rate', 'data-base-acc', 'data-skill1', 'data-base-eva', 'data-base-armor',
    'data-production-time', 'data-avatar', 'data-type-img', 'data-type', 'data-skill2',
    'data-modtile-effect1-time', 'data-modtile-effect2-time', 'data-tiles-affect-mod', 'data-avatar-mod',
    'data-mod-rarity', 'data-tiles-mod', 'data-mod-hp', 'data-mod-atk', 'data-mod-rate', 'data-mod-acc',
    'data-mod-eva', 'data-mod-armor'
]


def _get_alias_of_op(op, session: requests.Session, website_root: str, names: List[str]) -> List[str]:
    response = sget(
        session,
        f'{website_root}/api.php?action=query&prop=redirects&titles={quote(op)}&format=json',
    )
    response.raise_for_status()

    alias_names = []
    pages = response.json()['query']['pages']
    for _, data in pages.items():
        for item in (data.get('redirects', None) or []):
            if item['title'] not in names:
                alias_names.append(item['title'])

    return alias_names


def _get_only_index_from_cnsite(session: requests.Session) -> Dict[int, str]:
    response = sget(session, f'{_CN_WEBSITE_ROOT}/w/%E6%88%98%E6%9C%AF%E4%BA%BA%E5%BD%A2%E5%9B%BE%E9%89%B4')
    response.raise_for_status()

    query = pq(response.text)
    return {
        int(item.attr('data-id')): item.attr('data-name-ingame')
        for item in query('.dolldata').items()
    }


def _get_index_from_iopwiki(timeout: int = 5, maxcnt: Optional[int] = None):
    session = get_requests_session(timeout=timeout)

    def _get_media_url(purl: str) -> str:
        resp_ = sget(session, purl)
        return pq(resp_.text)(".fullMedia a").attr("href")

    response = sget(session, f'{_WEBSITE_ROOT}/wiki/T-Doll_Index')
    full = pq(response.text)

    _cn_index = _get_only_index_from_cnsite(session)

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

        if id_ in _cn_index and _cn_index[id_] != cnname:
            cnnames = [_cn_index[id_], cnname]
            cnname, cnname_en = _cn_index[id_], cnname
        else:
            cnnames = [cnname]
            cnname_en = cnname

        alias_names = []
        alias_names.extend(_get_alias_of_op((enname or cnname_en or jpname).replace(' ', '_'), session, _WEBSITE_ROOT,
                                            [*cnnames, enname, jpname]))
        if id_ in _cn_index:
            alias_names.extend(_get_alias_of_op(_cn_index[id_], session, _CN_WEBSITE_ROOT,
                                                [*alias_names, *cnnames, enname, jpname]))

        resp = sget(session, f"{_WEBSITE_ROOT}/{item('.pad a').attr('href')}")
        ch_page = pq(resp.text)
        _first, *_ = ch_page('a.image').parents('ul').items()
        img_items = list(_first('li').items())
        skins = []
        img_items_tqdm = tqdm(img_items)
        for fn in img_items_tqdm:
            img_name = fn('.gallerytext').text()
            img_items_tqdm.set_description(img_name)
            img_url = _get_media_url(f"{_WEBSITE_ROOT}/{fn('a.image').attr('href')}")
            skins.append({
                'desc': img_name,
                'url': f"{_WEBSITE_ROOT}/{img_url}",
            })

        retval.append({
            'id': id_,
            'rarity': rarity,
            'class': clazz,
            'cnname': cnname,
            'cnnames': cnnames,
            'enname': enname,
            'jpname': jpname,
            'alias': alias_names,
            'twname': _get_name_with_lang('TW'),
            'krname': _get_name_with_lang('KR'),
            'skins': skins
        })
        if maxcnt is not None and len(retval) >= maxcnt:
            break

    return retval


def _refresh_index(timeout: int = 5, maxcnt: Optional[int] = None, index_file: Optional[str] = None):
    data = _get_index_from_iopwiki(timeout, maxcnt)
    with open(index_file or _INDEX_FILE, 'w', encoding='utf-8') as f:
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


ONLINE_INDEX_URL = 'https://huggingface.co/datasets/deepghs/game_characters/resolve/main/girlsfrontline/index.json'


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
