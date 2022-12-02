import json
import os.path
import re
import time
from itertools import islice

import requests
from pyquery import PyQuery as pq
from tqdm import tqdm

_LOCAL_DIR, _ = os.path.split(os.path.abspath(__file__))
_INDEX_FILE = os.path.join(_LOCAL_DIR, 'index.json')

ROOT_SITE = 'https://wiki.biligame.com/'

_VALID_TYPES = ['前排先锋', '后排主力', '驱逐', '轻巡', '重巡', '超巡', '战巡', '战列', '航战', '航母', '轻航', '重炮',
                '维修', '潜艇', '潜母', '运输', '风帆']

TEXT_IN_CURVE = re.compile(r'[\(（][^\)）]+[\)）]')


def _no_big_curve(s: str) -> str:
    return s.replace('（', '(').replace('）', ')')


def _remove_curve(s: str) -> str:
    return TEXT_IN_CURVE.sub('', s)


def _get_index_from_biliwiki(timeout: int = 5):
    session = requests.Session()
    response = session.get(
        f'{ROOT_SITE}/blhx/%E8%88%B0%E8%88%B9%E5%9B%BE%E9%89%B4',
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
        },
        timeout=timeout
    )
    response.raise_for_status()

    items = list(pq(response.text)('.jntj-1').items())
    retval = []
    for item in tqdm(items):
        _generic_label = item('.jntj-4').text()
        if '.改' in _generic_label or '兵装' in _generic_label:
            continue

        cnname = _no_big_curve(item('span a').text())
        short_cname = _remove_curve(cnname)

        types_ = item.attr('data-param1').split(',')
        rarity = item.attr('data-param2')
        group = item.attr('data-param3')
        page_url = f"{ROOT_SITE}{item('.jntj-4 a').attr('href')}"

        resp = session.get(page_url)
        resp.raise_for_status()

        full = pq(resp.text)
        table = full('table.wikitable.sv-general')
        target, l2 = islice(table('tr').items(), 2)
        ch_id = l2('#PNN').text()
        type_ = l2('#PNshiptype').text()
        enname, jpname = map(lambda x: x.text(), target('span').items())
        jpnames = jpname.split(' ') if jpname else []

        target.remove('span')
        full_cnname = target.text()

        image_tab = full('#characters .TabContainer')
        skins = []
        for li, con in zip(image_tab('ul .tab_li').items(), image_tab('.Contentbox2 .tab_con').items()):
            skin_name = li.text().strip()
            if con('img'):
                skin_url = con('img').attr('src')
                skins.append({
                    'name': skin_name,
                    'url': skin_url,
                })

        retval.append({
            'id': ch_id,
            'cnname': {
                'full': full_cnname,
                'label': cnname,
                'short': short_cname,
            },
            'enname': enname,
            'jpnames': jpnames,
            'type': type_,
            'types': types_,
            'rarity': rarity,
            'group': group,
            'skins': skins,
        })

    return retval


def _refresh_index(timeout: int = 5):
    data = _get_index_from_biliwiki(timeout)
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
