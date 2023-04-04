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
    "data-cn", "data-position", "data-en", "data-sex", "data-tag", "data-race", "data-rarity", "data-class",
    "data-approach", "data-camp", "data-team", "data-des", "data-feature", "data-str", "data-flex", "data-tolerance",
    "data-plan", "data-skill", "data-adapt", "data-moredes", "data-icon", "data-half", "data-ori-hp", "data-ori-atk",
    "data-ori-def", "data-ori-res", "data-ori-dt", "data-ori-dc", "data-ori-block", "data-ori-cd", "data-index",
    "data-jp", "data-birthplace", "data-nation", "data-group"
]

_UNQUOTE_NEEDED_FIELDS = {
    'data-feature',
}


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
            for item in data['redirects']:
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
        tqs = tqdm(list(pq(text)('.smwdata').items()))
        retval = []
        for item in tqs:
            data = {}
            for name in _KNOWN_DATA_FIELDS:
                val = item.attr(name)
                if name in _UNQUOTE_NEEDED_FIELDS:
                    val = pq(val).text()
                data[name] = val

            cnname = data['data-cn']
            tqs.set_description(cnname)

            skins = self._get_skins_of_op(cnname, f'{self.__root_website__}/w/{quote(cnname)}', session)
            assert skins

            release_index, release_time = _release_date_index[cnname]
            retval.append({
                'data': data,
                'alias': self._get_alias_of_op(
                    data['data-cn'], session,
                    [
                        data['data-cn'],
                        data.get('data-en', None),
                        data.get('data-jp', None),
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
