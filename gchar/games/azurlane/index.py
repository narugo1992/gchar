import re
from datetime import datetime
from itertools import islice
from typing import Optional, Tuple, Iterator, Any, List
from urllib.parse import urljoin

import requests
from pyquery import PyQuery as pq
from tqdm import tqdm

from ..base import BaseIndexer
from ...utils import sget

_VALID_TYPES = ['前排先锋', '后排主力', '驱逐', '轻巡', '重巡', '超巡', '战巡', '战列', '航战', '航母', '轻航', '重炮',
                '维修', '潜艇', '潜母', '运输', '风帆']

CNNAME_PATTERN = re.compile(r'^(?P<name>[^(]+)(?P<suffix>.改|)$')
CNNAME_MU_PATTERN = re.compile(r'^(?P<name>[^(]+\(\S+兵装\))$')


def _no_big_curve(s: str) -> str:
    return s.replace('（', '(').replace('）', ')').replace('・', '·')


def _process_cnname(s: str) -> Tuple[str, List[str], str]:
    lines = s.splitlines(keepends=False)
    if '兵装' not in lines[0]:
        name, alias, suffix = None, [], None
        for line in lines:
            matching = CNNAME_PATTERN.fullmatch(line)
            if name is None:
                name, suffix = matching.group('name'), matching.group('suffix')
            else:
                alias.append(matching.group('name'))

        return name, alias, suffix

    else:
        name, alias = None, []
        for line in lines:
            matching = CNNAME_MU_PATTERN.fullmatch(line)
            if name is None:
                name = matching.group('name')
            else:
                alias.append(matching.group('name'))

        return name, alias, ''


class Indexer(BaseIndexer):
    __game_name__ = 'azurlane'
    __official_name__ = 'azur lane'
    __root_website__ = 'https://wiki.biligame.com/'
    __root_website_en__ = 'https://azurlane.koumakan.jp/'

    def _crawl_index_from_ensite(self, session: requests.Session):
        response = sget(session, f'{self.__root_website_en__}/wiki/List_of_Ships')
        records = {}
        page = pq(response.text)
        base_table, plan_table, meta_table, collab_table, _ = page('.wikitable').items()

        for row in base_table('tbody tr').items():
            link = row('td:nth-child(1) a')
            if link.text().strip():
                index = link.text().strip()
                url = f"{self.__root_website_en__}/{link.attr('href')}"
                records[index] = url

        for row in plan_table('tbody tr').items():
            link = row('td:nth-child(1) a')
            if link.text().strip():
                index = f'Plan{link.text().strip()[-3:]}'
                url = f"{self.__root_website_en__}/{link.attr('href')}"
                records[index] = url

        for row in meta_table('tbody tr').items():
            link = row('td:nth-child(1) a')
            if link.text().strip():
                index = f'META{link.text().strip()[-3:]}'
                url = f"{self.__root_website_en__}/{link.attr('href')}"
                records[index] = url

        for row in collab_table('tbody tr').items():
            link = row('td:nth-child(1) a')
            if link.text().strip():
                index = f'Collab{link.text().strip()[-3:]}'
                url = f"{self.__root_website_en__}/{link.attr('href')}"
                records[index] = url

        return records

    def _get_skins_resources_from_enwiki_page(self, session: requests.Session, wiki_url: str):
        response = sget(session, f'{wiki_url}/Gallery')
        page = pq(response.text)

        records = []
        for link in page('.shipskin-image a').items():
            title = ' - '.join([item.attr('data-title') for item in
                                islice(link.parents('article.tabber__panel').items(), 2)])
            url = f"{self.__root_website_en__}/{link.attr('href')}"
            records.append((title, url))

        chibi_items = list(page('.shipskin-chibi a').items())
        if chibi_items:
            link = chibi_items[0]
            title = 'chibi'
            url = f"{self.__root_website_en__}/{link.attr('href')}"
            records.append((title, url))

        return records

    def _get_skins_from_enwiki_page(self, session: requests.Session, wiki_url: str):
        tqdm_list = tqdm(self._get_skins_resources_from_enwiki_page(session, wiki_url))
        skins = []
        _exist_names = set()
        duplicate_names = set()
        for title, url in tqdm_list:
            tqdm_list.set_description(title)

            resp = sget(session, url)
            page = pq(resp.text)
            media_url = urljoin(url, page('.fullMedia a').attr('href'))
            skins.append({'name': title, 'url': media_url})
            if title in _exist_names:
                duplicate_names.add(title)
            _exist_names.add(title)

        _max_index = {}
        retval = []
        for item in skins:
            title, download_url = item['name'], item['url']
            if title in duplicate_names:
                _max_index[title] = _max_index.get(title, 0) + 1
                title = f'{title} #{_max_index[title]}'

            retval.append({'name': title, 'url': download_url})

        return retval

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        response = sget(session, f'{self.__root_website__}/blhx/%E8%88%B0%E8%88%B9%E5%9B%BE%E9%89%B4')
        _en_wiki_index = self._crawl_index_from_ensite(session)

        items = list(pq(response.text)('.jntj-1').items())
        items_tqdm = tqdm(items, total=maxcnt)
        retval = []
        exist_cnnames = []
        for item in items_tqdm:
            cnname = _no_big_curve(item('span a').text())
            items_tqdm.set_description(cnname.splitlines(keepends=False)[0])
            p_cnname, cn_alias, cn_suffix = _process_cnname(cnname)
            short_cnname = f'{p_cnname}{cn_suffix}'
            alias = [f'{cn_alias_item}{cn_suffix}' for cn_alias_item in cn_alias]

            types_ = item.attr('data-param1').split(',')
            rarity = item.attr('data-param2')
            group, *_ = [g.strip() for g in item.attr('data-param3').split(',') if g]
            page_url = f"{self.__root_website__}{item('.jntj-4 a').attr('href')}"

            resp = sget(session, page_url)
            full = pq(resp.text)
            table = full('table.wikitable.sv-general')
            target, l2, l3, l4 = islice(table('tr').items(), 4)
            ch_id = l2('#PNN').text()
            type_ = l2('#PNshiptype').text()
            date_match = re.fullmatch(
                r'^\s*(?P<year>\d+)年(?P<month>\d+)月((?P<day>\d+)日)?\s*$',
                l4('td:nth-child(2)').text()
            )
            release_time = datetime.strptime(
                f'{date_match.group("year")}/{date_match.group("month")}/{date_match.group("day") or "15"} '
                f'17:00:00 +0800',
                '%Y/%m/%d %H:%M:%S %z'
            )

            enname, jpname = map(lambda x: x.text(), target('span').items())
            enname_full = enname.replace(chr(160), ' ')
            if re.fullmatch('^[A-Z]{2,}$', enname_full.split(' ')[0]):
                enname = ' '.join(enname_full.split(' ')[1:])
            else:
                enname = enname_full
            jpnames = jpname.split(' ') if jpname else []

            target.remove('span')
            full_cnname = target.text()

            skins = self._get_skins_from_enwiki_page(session, _en_wiki_index[ch_id])
            retval.append({
                'id': ch_id,
                'cnname': {
                    'full': full_cnname,
                    'label': cnname.splitlines(keepends=False)[0],
                    'short': short_cnname,
                },
                'enname': {
                    'full': enname_full,
                    'short': enname,
                },
                'jpnames': jpnames,
                'alias': alias,
                'type': type_,
                'types': types_,
                'rarity': rarity,
                'is_meta': 'META' in ch_id,
                'is_refit': '.改' in cnname,
                'is_mu': '兵装' in cnname,
                'is_chibi': False,
                'group': group,
                'release': {
                    'time': release_time.timestamp(),
                },
                'skins': skins,
            })
            exist_cnnames.append(short_cnname)
            if maxcnt is not None and len(retval) >= maxcnt:
                break

        exist_cnnames_set = set(exist_cnnames)
        for data, cnname in zip(retval, exist_cnnames):
            data['is_chibi'] = cnname.startswith('小') and cnname[1:] in exist_cnnames_set

        return retval


INDEXER = Indexer()
