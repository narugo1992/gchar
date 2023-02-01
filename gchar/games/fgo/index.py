import json
import os
import re
import time
from itertools import islice
from typing import List, Optional, Iterator
from urllib.parse import quote

import requests
from pyquery import PyQuery as pq

from ...utils import import_tqdm, download_file, get_requests_session, sget

tqdm = import_tqdm()

_LOCAL_DIR, _ = os.path.split(os.path.abspath(__file__))
_INDEX_FILE = os.path.join(_LOCAL_DIR, 'index.json')

_WEBSITE_ROOT = 'https://fgo.wiki/'

SERVANT_ALT_PATTERN = re.compile(r'Servant (?P<id>\d+)\.[a-zA-Z\d]+')
PAGE_REL_PATTERN = re.compile(r'var data_list\s*=\"(?P<ids>[\d,\s]*)\"')


def _get_alias_of_op(op, session: requests.Session, names: List[str]) -> List[str]:
    response = sget(
        session,
        f'{_WEBSITE_ROOT}/api.php?action=query&prop=redirects&titles={quote(op)}&format=json',
    )
    response.raise_for_status()

    alias_names = []
    pages = response.json()['query']['pages']
    for _, data in pages.items():
        for item in data['redirects']:
            if item['title'] not in names:
                alias_names.append(item['title'])

    return alias_names


def _get_similar_lists(current_id: int, sim_table: pq, session: requests.Session = None) -> List[int]:
    session = session or get_requests_session()
    content_box = sim_table('td')
    ids = []
    if content_box('td a img'):
        for image in content_box('td a img').items():
            sid = int(SERVANT_ALT_PATTERN.fullmatch(image.attr('alt')).group('id').lstrip('0'))
            ids.append(sid)

    elif content_box('td a'):
        sim_page_url = f"{_WEBSITE_ROOT}/{content_box('td a').attr('href')}"
        resp = sget(session, sim_page_url)

        for reltext in PAGE_REL_PATTERN.findall(resp.content.decode()):
            for id_ in [int(item.strip()) for item in reltext.split(',')]:
                ids.append(id_)

    else:
        raise ValueError(f'Unknown similar table content:{os.linesep}{content_box}.')  # pragma: no cover

    return sorted(set([id_ for id_ in ids if current_id != id_]))


def _get_index_from_fgowiki(timeout: int = 5) -> Iterator[dict]:
    session = get_requests_session(timeout=timeout)

    response = sget(session, f'{_WEBSITE_ROOT}/w/SVT')
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

    _id_to_name = {int(item['id']): item['name_cn'] for item in fulllist}
    fulllist = tqdm(fulllist[::-1], leave=True)
    for item in fulllist:
        id_ = int(item['id'])
        cnname = item['name_cn'].replace('・', '·')
        jpname = item['name_jp']
        enname = item['name_en']
        fulllist.set_description(cnname)

        alias = [name.strip() for name in item['name_other'].split('&') if name.strip()]
        get_method = item['method']

        resp = sget(session, f'{_WEBSITE_ROOT}/w/{quote(item["name_link"])}')
        page = pq(resp.text)
        main_table, *_other_tables = page('table.wikitable').items()
        if not main_table('tr:nth-child(7)'):
            sim_table = main_table
            assert '快速跳转' in sim_table('th').text().strip()

            simlist = _get_similar_lists(id_, sim_table, session)
            main_table, *_other_tables = _other_tables
        else:
            simlist = []

        row1 = main_table('tr:nth-child(1)')
        row2 = main_table('tr:nth-child(2)')
        row3 = main_table('tr:nth-child(3)')
        row6 = main_table('tr:nth-child(6)')
        row7 = main_table('tr:nth-child(7)')

        CN_ALIAS_PATTERN = re.compile('^(?P<cnalias>[^（]+)（(?P<cnname>[^）]+)）$')
        if CN_ALIAS_PATTERN.fullmatch(row1('th:nth-child(1)').text()) and row1('th:nth-child(1) span'):
            matching = CN_ALIAS_PATTERN.fullmatch(row1('th:nth-child(1)').text())
            cn_alias = matching.group('cnalias')
            if cn_alias not in alias:
                alias.append(cn_alias)
            all_cnnames = [matching.group('cnname')]
            all_jpnames = [row2('td:nth-child(1)').text()]
            all_ennames = [row3('td:nth-child(1)').text()]
        else:
            s_r1 = row1('th:nth-child(1)').text()
            s_r2 = row2('td:nth-child(1)').text()
            s_r3 = row3('td:nth-child(1)').text()
            if '/' in s_r1 and '/' in s_r2 and '/' in s_r3:
                all_cnnames = s_r1.split('/')
                all_jpnames = s_r2.split('/')
                all_ennames = s_r3.split('/')
                assert len(all_cnnames) == len(all_jpnames) == len(all_ennames)
            else:
                all_cnnames = [s_r1]
                all_jpnames = [s_r2]
                all_ennames = [s_r3]

        if cnname not in all_cnnames:
            all_cnnames.append(cnname)
        if jpname not in all_jpnames:
            all_jpnames.append(jpname)
        if enname not in all_ennames:
            all_ennames.append(enname)

        if not row3('th > img').attr('alt'):
            accessible = False
            rarity, *_ = re.findall(r'\d+', row1('th:nth-child(2) a img').attr('alt'))
        else:
            accessible = True
            rarity, *_ = re.findall(r'\d+', row3('th > img').attr('alt'))
        clazz = row7('td:nth-child(1)').text().strip()
        gender = row7('td:nth-child(2)').text().strip()

        graphbox = row6('th:nth-child(7)')
        skins = []
        img_items = tqdm(list(graphbox('.graphpicker a.image').items()), leave=True)
        for img in img_items:
            sp = sget(session, f'{_WEBSITE_ROOT}/{img.attr("href")}')
            sp_page = pq(sp.text)
            heading = sp_page('#firstHeading').text()
            img_items.set_description(heading)

            _, resource_filename = heading.split(':', maxsplit=1)
            image_name, _ = os.path.splitext(resource_filename)
            image_url = f"{_WEBSITE_ROOT}/{sp_page('.fullMedia a').attr('href')}"

            skins.append({
                'name': image_name,
                'url': image_url
            })

        alias.extend(_get_alias_of_op(item["name_link"], session, [*all_cnnames, *all_ennames, *all_jpnames, *alias]))
        yield {
            'id': id_,
            'cnnames': all_cnnames,
            'jpnames': all_jpnames,
            'ennames': all_ennames,
            'alias': alias,
            'accessible': accessible,
            'rarity': rarity,
            'method': get_method,
            'class': clazz,
            'gender': gender,
            'skins': skins,
            'similar': [{'id': id_, 'name': _id_to_name[id_]} for id_ in simlist],
        }


def _refresh_index(timeout: int = 5, maxcnt: Optional[int] = None, index_file: Optional[str] = None):
    yielder = _get_index_from_fgowiki(timeout)
    if maxcnt:
        yielder = islice(yielder, maxcnt)
    data = list(yielder)
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


ONLINE_INDEX_URL = 'https://huggingface.co/datasets/deepghs/game_characters/resolve/main/fgo/index.json'


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
