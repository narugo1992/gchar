import re
from typing import Optional, Iterator, Any
from urllib.parse import urljoin

import dateparser
import requests
import unicodedata
from ditk import logging
from hbutils.system import urlsplit
from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from gchar.utils import srequest
from .base import GameIndexer


class StarRailIndexer(GameIndexer):
    __game_name__ = 'starrail'
    __root_website__ = 'https://starrailstation.com'
    __root_website_cn__ = 'https://wiki.biligame.com'

    def _get_cn_index(self, session: requests.Session):
        resp = srequest(session, 'GET', f'{self.__root_website_cn__}/sr/%E8%A7%92%E8%89%B2%E5%9B%BE%E9%89%B4')
        page = pq(resp.text)

        _exist_names = set()
        for item in page('#CardSelectTr > div').items():
            link = item('div:nth-child(2) > a')
            name = link.text().strip()
            url = urljoin(resp.request.url, link.attr('href'))
            if name not in _exist_names:
                yield name, url
                _exist_names.add(name)

    def _get_info_from_cnsite(self, session: requests.Session, url: str):
        resp = srequest(session, 'GET', url)
        page = pq(resp.text)

        wikitable, *_ = page('table.wikitable').items()
        assert wikitable('tr:nth-child(1) th').text().strip() == '性别'
        gender = wikitable('tr:nth-child(1) td').text().strip()
        assert wikitable('tr:nth-child(3) th').text().strip() == '稀有度'
        rarity = int(wikitable('tr:nth-child(3) td img').attr('alt')[0])
        assert wikitable('tr:nth-child(4) th').text().strip() == '命途'
        wikitable('tr:nth-child(4) td').remove('span')
        destiny = wikitable('tr:nth-child(4) td').text().strip()
        assert wikitable('tr:nth-child(5) th').text().strip() == '战斗属性'
        wikitable('tr:nth-child(5) td').remove('span')
        element = wikitable('tr:nth-child(5) td').text().strip()
        assert wikitable('tr:nth-child(6) th').text().strip() == '阵营'
        group = wikitable('tr:nth-child(6) td').text().strip()
        assert wikitable('tr:nth-child(8) th').text().strip() == '实装日期'
        release_time = dateparser.parse(re.sub(r'\([^)]+\)', '', unicodedata.normalize('NFKC', wikitable(
            'tr:nth-child(8) td').text().strip()))).timestamp()

        tabs1, *_ = page('.resp-tabs').items()
        names = [item.text().strip() for item in tabs1('ul > li').items()]
        urls = [item('.floatnone img').attr('src') for item in
                tabs1('.resp-tabs-container .resp-tab-content').items()]
        assert len(names) == len(urls), f'Names ({names!r}) not match with urls ({urls!r})'

        skins = []
        for name, url in zip(names, urls):
            if url and '动作' not in name:
                skins.append({'name': name, 'url': urljoin(resp.request.url, url)})

        return {
            'gender': gender,
            'rarity': rarity,
            'destiny': destiny,
            'element': element,
            'group': group,
            'release': {
                'time': release_time,
            },
            'skins': skins,
        }

    def _get_en_index(self, session: requests.Session):
        resp = srequest(session, 'GET', f'{self.__root_website__}/cn/characters')
        page = pq(resp.text.replace('\x00', '')) 
        for item in page(".page-margins.page-margins-top > div:nth-child(2) > div:nth-child(3) > a").items():
            name = item.text().strip()
            url = urljoin(resp.request.url, item.attr('href'))
            keyword = urlsplit(url).path_segments[-1]
            yield name, keyword

    def _get_name_from_en(self, session: requests, keyword: str):
        langs = ['cn', 'en', 'jp', 'kr']
        retval = {}
        for lang in langs:
            r = srequest(session, 'GET', f'https://starrailstation.com/{lang}/character/{keyword}')
            p = pq(r.text)
            h1, *_ = p('h1').items()
            retval[f'{lang}name'] = h1.text().strip()

        return retval

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        logging.info(f'Grabbing names from {self.__root_website__} ...')
        en_site_page = tqdm(list(self._get_en_index(session)))
        _exist_names, _n_dict = set(), {}
        for name, keyword in en_site_page:
            en_site_page.set_description(name)
            if name not in _exist_names:
                names = self._get_name_from_en(session, keyword)
                _n_dict[name] = {'id': keyword, **names}
                _exist_names.add(name)

        logging.info(f'Grabbing from {self.__root_website_cn__} ...')
        cn_site_pg = tqdm(list(self._get_cn_index(session)))
        for name, url in cn_site_pg:
            tk = '开拓者' if '开拓者' in name else name
            if tk not in _n_dict:
                continue

            item = self._get_info_from_cnsite(session, url)
            yield {**_n_dict[tk], 'cnname': name, **item}


INDEXER = StarRailIndexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
