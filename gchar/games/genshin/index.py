import json
import os
import re
import time
from typing import Optional

import requests
from pyquery import PyQuery as pq
from tqdm import tqdm

from ...utils import download_file, get_requests_session, sget

_LOCAL_DIR, _ = os.path.split(os.path.abspath(__file__))
_INDEX_FILE = os.path.join(_LOCAL_DIR, 'index.json')

_ROOT_WEBSITE = 'https://genshin-impact.fandom.com/'


def _get_index_from_fandom(timeout: int = 5, maxcnt: Optional[int] = None):
    session = get_requests_session(timeout=timeout)
    response = sget(session, f'{_ROOT_WEBSITE}/wiki/Character/List')

    full = pq(response.text)
    table, *_ = full('table.article-table').items()
    retval = []
    main_table_rows = tqdm(list(table('tbody tr').items()))
    for item in main_table_rows:
        tds = list(item('td').items())
        if not tds:
            continue

        enname = tds[1]('a').attr('title')
        main_table_rows.set_description(enname)
        page_url = f"{_ROOT_WEBSITE}/{tds[1]('a').attr('href')}"
        rarity, *_ = map(int, re.findall(r'\d', tds[2]('img').attr('title')))

        element = tds[3]('a').attr('title')
        weapon = tds[4]('a').attr('title')
        region = tds[5]('a').attr('title')
        gender, *gother = re.findall('(Male|Female)', tds[6]('a').text().strip())
        if gother:
            gender = 'Others'

        resp = sget(session, page_url)
        page = pq(resp.text)

        images_tab = page('.pi-image-collection.wds-tabber')
        skins = []
        for tab, at in zip(
                images_tab('ul li span.wds-tabs__tab-label').items(),
                images_tab('figure.pi-image a').items()
        ):
            tab_name = tab.text().strip()
            image_url = at.attr('href')
            skins.append({
                'name': tab_name,
                'url': image_url,
            })

        lang_table = None
        for tb in page('.article-table').items():
            if 'language' in tb('th').text().strip().lower():
                lang_table = tb
                break

        cnname, jpnames = None, None
        if lang_table:
            for ix in lang_table('tr').items():
                if ix('th'):
                    continue

                t_td, c_td, *_ = ix('td').items()
                s_title = t_td.text().strip()

                if s_title.lower() == 'english':
                    enname = c_td.text().strip()
                elif 'simplified' in s_title.lower():
                    cnname = c_td('[lang=zh-Hans]').text().strip()
                elif s_title.lower() == 'japanese':
                    if c_td('ruby'):
                        jpname_1 = c_td('ruby > span').text()
                        jpname_2 = c_td('ruby rt span').text()
                        jpname_1 = re.sub(r'\s+', '', jpname_1)
                        jpname_2 = re.sub(r'\s+', '', jpname_2)
                        jpnames = [jpname_1, jpname_2]
                    else:
                        jpnames = [c_td('[lang=ja]').text().strip()]

        retval.append({
            'cnname': cnname,
            'enname': enname,
            'jpnames': jpnames,
            'rarity': rarity,
            'gender': gender,
            'element': element,
            'weapon': weapon,
            'region': region,
            'skins': skins
        })
        if maxcnt is not None and len(retval) >= maxcnt:
            break

    return retval


def _refresh_index(timeout: int = 5, maxcnt: Optional[int] = None, index_file: Optional[str] = None):
    data = _get_index_from_fandom(timeout, maxcnt)
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


ONLINE_INDEX_URL = 'https://huggingface.co/datasets/deepghs/game_characters/resolve/main/genshin/index.json'


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
