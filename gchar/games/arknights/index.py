import os.path
import os.path
import re
from typing import Iterator, Optional, List, Any
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

    def _get_skins_of_op(self, op, session: requests.Session):
        search_content = quote(f"立绘 \"{op}\"")
        response = sget(
            session,
            f'{self.__root_website__}/index.php?title=%E7%89%B9%E6%AE%8A:%E6%90%9C%E7%B4%A2&profile=images'
            f'&search={search_content}&fulltext=1'
        )

        text = response.content.decode()
        full = pq(text)
        result_list = full('li.mw-search-result')

        skins = []
        exist_names = set()
        tqs = tqdm(list(result_list.items()))
        for item in tqs:
            url = item('td > a')
            title = url.text().strip()
            resource_url = f"{self.__root_website__}/{url.attr('href')}"
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

            resp = sget(session, resource_url)
            page = pq(resp.text)
            media_url = f"{self.__root_website__}/{page('.fullMedia a').attr('href')}"

            skins.append({
                'name': ctitle,
                'url': media_url,
            })
            exist_names.add(ctitle)

        return skins

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        response = sget(
            session,
            f'{self.__root_website__}/w/CHAR?filter=AAAAAAAggAAAAAAAAAAAAAAAAAAAAAAA',
        )
        text = response.content.decode()
        tqs = tqdm(list(pq(text)('.smwdata').items()))
        retval = []
        for item in tqs:
            data = {}
            for name in _KNOWN_DATA_FIELDS:
                val = item.attr(name)
                if name in _UNQUOTE_NEEDED_FIELDS:
                    val = pq(val).text()
                data[name] = val

            tqs.set_description(data['data-cn'])

            skins = self._get_skins_of_op(data['data-cn'], session)
            assert skins
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
                'skins': skins,
            })
            if maxcnt is not None and len(retval) >= maxcnt:
                break

        return retval


INDEXER = Indexer()
