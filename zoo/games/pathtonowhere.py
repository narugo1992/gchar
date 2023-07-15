import re
from typing import Optional, Iterator, Any, Tuple
from urllib.parse import urljoin

import requests
from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from gchar.utils import srequest
from .base import GameIndexer


class PathToNowhereIndexer(GameIndexer):
    __game_name__ = 'pathtonowhere'
    __root_website__ = 'https://wiki.biligame.com/wqmt'
    __jp_website__ = 'https://wikiwiki.jp/ptn'

    def _get_index_info(self, session: requests.Session) -> Iterator[Tuple[str, str, str, str, str, str]]:
        index_page = srequest(
            session, 'GET',
            f'{self.__root_website__}/%E7%A6%81%E9%97%AD%E8%80%85'
        )
        page = pq(index_page.text)
        table = page('#CardSelectTr')

        for row in table('tr').items():
            if not list(row('td').items()):
                continue

            td0_a = row('td:nth-child(1) a')
            name = td0_a.attr('title')
            page_url = urljoin(index_page.request.url, td0_a.attr('href'))

            assert row('td:nth-child(2)').attr('data-label') == '编号'
            id_ = row('td:nth-child(2)').text().strip()

            assert row('td:nth-child(3)').attr('data-label') == '职业'
            job = row('td:nth-child(3)').text().strip()

            assert row('td:nth-child(4)').attr('data-label') == '稀有度'
            rarity = row('td:nth-child(4) img').attr('alt')[0]

            assert row('td:nth-child(5)').attr('data-label') == '阵营'
            group = row('td:nth-child(5)').text().strip()

            yield name, page_url, id_, job, rarity, group

    def _get_info_from_page(self, session: requests.Session, url: str):
        resp = srequest(session, 'GET', url)
        page = pq(resp.text)

        content = page('#mw-content-text .row')
        left_side = content('.col-sm-6:nth-child(1)')
        right_side = content('.col-sm-6:nth-child(2)')

        l_table1, *_ = left_side('table.wikitable').items()
        r_table1, r_table2, *_ = right_side('table.wikitable').items()

        lt1_row0, lt1_row1, lt1_row2 = l_table1('tr').items()
        assert lt1_row0('th:nth-child(1)').text().strip() == '姓名'
        cnname = lt1_row0('td:nth-child(2)').text().strip()
        assert lt1_row0('th:nth-child(3)').text().strip() == '编号'
        id_ = lt1_row0('td:nth-child(4)').text().strip()
        assert lt1_row1('th:nth-child(1)').text().strip() == '职业'
        job = lt1_row1('td:nth-child(2)').text().strip()
        assert lt1_row1('th:nth-child(3)').text().strip() == '危险评级'
        rarity = lt1_row1('td:nth-child(4)').text().strip()
        assert lt1_row2('th:nth-child(1)').text().strip() == '角色TAG'
        tags = re.split(r'[\W_]+', lt1_row2('td:nth-child(2)').text().strip())

        rt1_tabs = list(r_table1('.resp-tabs-list > li').items())
        rt1_contents = list(r_table1('.resp-tabs-container > .resp-tab-content').items())
        assert len(rt1_tabs) == len(rt1_contents), \
            f'Skin tabs ({len(rt1_tabs)}) and contents ({len(rt1_contents)}) not match for character {cnname!r}/{id_}.'
        skins = []
        for tab, ctx in zip(rt1_tabs, rt1_contents):
            skin_name = tab.text().strip()
            if list(ctx('.showOnImg').items()):
                skin_url = urljoin(resp.request.url, ctx('.showOnImg img').attr('src'))
            else:
                skin_url = urljoin(resp.request.url, ctx('img').attr('src'))
            skins.append({'name': skin_name, 'url': skin_url})

        rt2_row2 = list(r_table2('tr').items())[1]
        assert rt2_row2('th:nth-child(3)').text().strip() == '性别'
        gender = rt2_row2('td:nth-child(4)').text().strip()
        rt2_row4 = list(r_table2('tr').items())[3]
        assert rt2_row4('th:nth-child(3)').text().strip() == '英文名'
        enname = rt2_row4('td:nth-child(4)').text().strip()
        rt2_row5 = list(r_table2('tr').items())[4]
        assert rt2_row5('th:nth-child(1)').text().strip() == '阵营'
        group = rt2_row5('td:nth-child(2)').text().strip()

        return {
            'id': id_,
            'cnname': cnname,
            'enname': enname,
            'gender': gender,
            'job': job,
            'group': group,
            'rarity': rarity,
            'tags': tags,
            'skins': skins,
        }

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        pg = tqdm(list(self._get_index_info(session)))
        for name, page_url, id_, job, rarity, group in pg:
            pg.set_description(f'{name} - {id_}')
            yield self._get_info_from_page(session, page_url)


INDEXER = PathToNowhereIndexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
