import json
import re
from datetime import datetime
from typing import Iterator, Optional, List, Any, Mapping, Tuple
from urllib.parse import quote

import requests
from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from ..base import BaseIndexer
from ...utils import sget

_KNOWN_DATA_FIELDS = [
    'data-adapt', 'data-atk', 'data-birth_place', 'data-block', 'data-cost', 'data-def', 'data-en',
    'data-flex', 'data-group', 'data-hp', 'data-id', 'data-interval', 'data-ja', 'data-logo',
    'data-nation', 'data-obtain_method', 'data-phy', 'data-plan', 'data-position', 'data-potential',
    'data-profession', 'data-race', 'data-rarity', 'data-re_deploy', 'data-res', 'data-sex',
    'data-skill', 'data-sortid', 'data-subprofession', 'data-tag', 'data-team', 'data-tolerance',
    'data-trust', 'data-zh'
]

_UNQUOTE_NEEDED_FIELDS = {
    'data-feature',
}


# 20220607, the data format is changed, here are the known maps
# data-cn --> data-zh
# data-jp --> data-ja


class Indexer(BaseIndexer):
    __game_name__ = 'arknights'
    __official_name__ = 'arknights'
    __root_website__ = 'https://prts.wiki/'

    def _get_alias_of_op(self, op, session: requests.Session, names: List[str]) -> List[str]:
        response = sget(
            session,
            f'{self.__root_website__}/api.php?action=query&prop=redirects&titles={quote(op)}&format=json',
        )
        response.raise_for_status()

        alias_names = []
        pages = response.json()['query']['pages']
        for _, data in pages.items():
            for item in (data.get('redirects') or []):
                if item['title'] not in names:
                    alias_names.append(item['title'])

        return alias_names

    def _get_skins_of_op(self, op, page_url, session: requests.Session):
        p_resp = sget(session, page_url)
        skins_data = []
        _exist_names = set()
        for tag, type_, index_, data in \
                re.findall(r'\"(?P<tag>(skin|elite)(\d+))\"\s*:\s*(?P<data>{[^\r\n]+?})', p_resp.text):
            index_ = int(index_)
            if tag in _exist_names:
                continue

            data = json.loads(data)
            if type_ == 'elite':
                if data['introduce'] != f'精英{index_}介绍':
                    filename = f"立绘_{op}_{['1', '1+', '2'][index_]}.png"
                    suffix = ['精英零', '精英一', '精英二'][index_]
                    skins_data.append((f"{data['introduce_name']} - {suffix}", filename))
                    _exist_names.add(tag)
            elif type_ == 'skin':
                if data['name']:
                    filename = f"立绘_{op}_{tag}.png"
                    skins_data.append((data['name'], filename))
                    _exist_names.add(tag)
            else:
                assert False, f'Invalid type - {type_}.'

        skins_data_tqdm = tqdm(skins_data)
        skins = []
        for name, filename in skins_data_tqdm:
            skins_data_tqdm.set_description(name)
            resp = sget(session, f'{self.__root_website__}/w/文件:{filename}')
            page = pq(resp.text)
            media_url = f"{self.__root_website__}/{page('.fullMedia a').attr('href')}"

            skins.append({
                'name': name,
                'url': media_url,
            })

        return skins

    def _crawl_release_index(self, session: requests.Session) -> Mapping[str, Tuple[int, float]]:
        response = sget(
            session,
            f'{self.__root_website__}/w/%E5%B9%B2%E5%91%98%E4%B8%8A%E7%BA%BF%E6%97%B6%E9%97%B4%E4%B8%80%E8%A7%88'
        )
        response.raise_for_status()

        full_page = pq(response.text)
        main_table = full_page('.wikitable')
        retval = {}
        for i, row in enumerate(main_table('tbody tr').items()):
            cnname = row('td:nth-child(1) a').attr('title')
            if not cnname:
                continue

            date_match = re.fullmatch(
                r'^\s*(?P<year>\d+)年(?P<month>\d+)月(?P<day>\d+)日\s+(?P<hour>\d+):(?P<minute>\d+)\s*$',
                row('td:nth-child(3)').text()
            )
            assert date_match, f'Release date invalid - {(cnname, row("td:nth-child(3)").text())}.'

            release_time = datetime.strptime(
                f'{date_match.group("year")}/{date_match.group("month")}/{date_match.group("day")} '
                f'{date_match.group("hour")}:{date_match.group("minute")}:00 +0800',
                '%Y/%m/%d %H:%M:%S %z'
            )
            retval[cnname] = (i, release_time.timestamp())

        return retval

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        response = sget(
            session,
            f'{self.__root_website__}/w/CHAR?filter=AAAAAAAggAAAAAAAAAAAAAAAAAAAAAAA',
        )
        text = response.content.decode()
        _release_date_index = self._crawl_release_index(session)
        tqs = tqdm(list(pq(text)('#filter-data > div').items()))
        retval = []
        for item in tqs:
            data = {key: item.attr(key) for key in _KNOWN_DATA_FIELDS}

            cnname = data.get('data-cn') or data.get('data-zh')
            tqs.set_description(cnname)

            skins = self._get_skins_of_op(cnname, f'{self.__root_website__}/w/{quote(cnname)}', session)
            assert skins

            _release_info = _release_date_index.get(cnname, None)
            if _release_info:
                release_index, release_time = _release_info
            else:
                release_index, release_time = None, None
            retval.append({
                'data': data,
                'alias': self._get_alias_of_op(
                    cnname, session,
                    [
                        cnname,
                        data.get('data-en'),
                        data.get('data-jp') or data.get('data-ja'),
                    ]
                ),
                'release': {
                    'index': release_index,
                    'time': release_time,
                },
                'skins': skins,
            })
            if maxcnt is not None and len(retval) >= maxcnt:
                break

        return retval


INDEXER = Indexer()
