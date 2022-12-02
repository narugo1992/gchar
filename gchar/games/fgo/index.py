import json
import os
import re
import time
from urllib.parse import quote

import requests
from pyquery import PyQuery as pq
from tqdm import tqdm

_LOCAL_DIR, _ = os.path.split(os.path.abspath(__file__))
_INDEX_FILE = os.path.join(_LOCAL_DIR, 'index.json')

_ROOT_WEBSITE = 'https://fgo.wiki/'


def _get_index_from_fgowiki(timeout: int = 5):
    session = requests.session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    })

    response = session.get(f'{_ROOT_WEBSITE}/w/SVT', timeout=timeout)
    response.raise_for_status()
    (raw_text, *_), *_ = re.findall(r'override_data\s*=\s*(?P<str>"(\\"|[^"])+")', response.text)
    raw_text: str = eval(raw_text)

    fulllist, curobj = [], {}
    for line in raw_text.splitlines(keepends=False):
        line = line.strip()
        if line:
            name, content = line.split('=', maxsplit=1)
            curobj[name] = content
        else:
            fulllist.append(curobj)
            curobj = {}

    if curobj:
        fulllist.append(curobj)

    fulllist = tqdm(fulllist[::-1])
    retval = []
    for item in fulllist:
        id_ = int(item['id'])
        cnname = item['name_cn']
        jpname = item['name_jp']
        enname = item['name_en']
        fulllist.set_description(cnname)

        alias = [name.strip() for name in item['name_other'].split('&') if name.strip()]
        get_method = item['method']

        resp = session.get(f'{_ROOT_WEBSITE}/w/{quote(item["name_link"])}')
        resp.raise_for_status()
        page = pq(resp.text)
        main_table, *_other_tables = page('table.wikitable').items()
        # sim_table = None
        if not main_table('tr:nth-child(7)'):
            # sim_table = main_table
            main_table, *_other_tables = _other_tables

        row3 = main_table('tr:nth-child(3)')
        row6 = main_table('tr:nth-child(6)')
        row7 = main_table('tr:nth-child(7)')

        if not row3('th > img').attr('alt'):
            accessible = False
            row1 = main_table('tr:nth-child(1)')
            rarity, *_ = re.findall(r'\d+', row1('th:nth-child(2) a img').attr('alt'))
        else:
            accessible = True
            rarity, *_ = re.findall(r'\d+', row3('th > img').attr('alt'))
        clazz = row7('td:nth-child(1)').text().strip()
        gender = row7('td:nth-child(2)').text().strip()

        graphbox = row6('th:nth-child(7)')
        skins = []
        img_items = tqdm(list(graphbox('.graphpicker a.image').items()))
        for img in img_items:
            sp = session.get(f'{_ROOT_WEBSITE}/{img.attr("href")}')
            sp.raise_for_status()
            sp_page = pq(sp.text)
            heading = sp_page('#firstHeading').text()
            img_items.set_description(heading)

            _, resource_filename = heading.split(':', maxsplit=1)
            image_name, _ = os.path.splitext(resource_filename)
            image_url = f"{_ROOT_WEBSITE}/{sp_page('.fullMedia a').attr('href')}"

            skins.append({
                'name': image_name,
                'url': image_url
            })

        retval.append({
            'id': id_,
            'cnname': cnname,
            'jpname': jpname,
            'enname': enname,
            'alias': alias,
            'accessible': accessible,
            'rarity': rarity,
            'method': get_method,
            'class': clazz,
            'gender': gender,
            'skins': skins,
        })

    return retval


def _refresh_index(timeout: int = 5):
    data = _get_index_from_fgowiki(timeout)
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
