import re
from typing import Optional, Iterator, Any

import requests
from pyquery import PyQuery as pq
from tqdm import tqdm

from ..base import BaseIndexer
from ...utils import sget


class Indexer(BaseIndexer):
    __game_name__ = 'genshin'
    __official_name__ = 'genshin impact'
    __root_website__ = 'https://genshin-impact.fandom.com/'

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None,
                                 **kwargs) -> Iterator[Any]:
        response = sget(session, f'{self.__root_website__}/wiki/Character/List')

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
            page_url = f"{self.__root_website__}/{tds[1]('a').attr('href')}"
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


INDEXER = Indexer()
