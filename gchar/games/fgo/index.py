import os
import re
import unicodedata
from typing import List, Optional, Iterator, Any
from urllib.parse import quote

import requests
from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from ..base import BaseIndexer
from ...utils import get_requests_session, sget

SERVANT_ALT_PATTERN = re.compile(r'Servant (?P<id>\d+)\.[a-zA-Z\d]+')
PAGE_REL_PATTERN = re.compile(r'var data_list\s*=\"(?P<ids>[\d,\s]*)\"')


class Indexer(BaseIndexer):
    __game_name__ = 'fgo'
    __official_name__ = 'fate/grand order'
    __root_website__ = 'https://fgo.wiki/'

    def _get_alias_of_op(self, op, session: requests.Session, names: List[str]) -> List[str]:
        response = sget(
            session,
            f'{self.__root_website__}/api.php?action=query&prop=redirects&titles={quote(op)}&format=json',
        )
        response.raise_for_status()

        alias_names = []
        pages = response.json()['query']['pages']
        for _, data in pages.items():
            for item in (data.get('redirects', None) or []):
                if item['title'] not in names:
                    alias_names.append(item['title'])

        return alias_names

    def _get_similar_lists(self, current_id: int, sim_table: pq, session: requests.Session = None) -> List[int]:
        session = session or get_requests_session()
        content_box = sim_table('td')
        ids = []
        if content_box('td a img'):
            for image in content_box('td a img').items():
                sid = int(SERVANT_ALT_PATTERN.fullmatch(image.attr('alt')).group('id').lstrip('0'))
                ids.append(sid)

        elif content_box('td a'):
            sim_page_url = f"{self.__root_website__}/{content_box('td a').attr('href')}"
            resp = sget(session, sim_page_url)

            for reltext in PAGE_REL_PATTERN.findall(resp.content.decode()):
                for id_ in [int(item.strip()) for item in reltext.split(',')]:
                    ids.append(id_)

        else:
            raise ValueError(f'Unknown similar table content:{os.linesep}{content_box}.')  # pragma: no cover

        return sorted(set([id_ for id_ in ids if current_id != id_]))

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        response = sget(session, f'{self.__root_website__}/w/SVT')
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
        retval = []
        for item in fulllist:
            id_ = int(item['id'])
            cnname = item['name_cn'].replace('・', '·')
            jpname = item['name_jp']
            enname = item['name_en']
            fulllist.set_description(cnname)

            alias = [name.strip() for name in item['name_other'].split('&') if name.strip()]
            get_method = item['method']

            resp = sget(session, f'{self.__root_website__}/w/{quote(item["name_link"])}')
            page = pq(resp.text)
            main_table, *_other_tables = page('table.wikitable').items()
            if not main_table('tr:nth-child(7)'):
                sim_table = main_table
                assert '快速跳转' in sim_table('th').text().strip()

                simlist = self._get_similar_lists(id_, sim_table, session)
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
            skin_title_raw = re.findall(r'var\s+arrayTitle\s*=\s*new\s+Array\((?P<text>[\s\S]*?)\);', resp.text)
            if skin_title_raw:  # normal servants
                skin_title_items = re.split(r'\s*,\s*', unicodedata.normalize('NFKC', skin_title_raw[0]))
                skin_titles = [eval(item) for item in skin_title_items if eval(item)]
                skin_items = list(graphbox('.graphpicker a.image').items())
            else:
                graphbox = main_table("tbody tr:nth-child(4) th:nth-child(3)")
                if list(graphbox('article.tabber__panel a.image').items()):  # solomon
                    skin_items = list(graphbox('article.tabber__panel a.image').items())
                    skin_titles = [eitem.parents('article.tabber__panel').attr('title') for eitem in skin_items]
                else:  # other beasts
                    skin_items = list(graphbox('a.image').items())
                    assert len(skin_items) == 1
                    skin_titles = ['普通']

            assert len(skin_items) == len(skin_items), \
                f"The quantity ({len(skin_items)}) of skin items should " \
                f"be consistent with the quantity ({len(skin_titles)}) of skin titles, " \
                f"but in reality they are different. The current servant number is {id_}."
            img_items = tqdm(list(zip(skin_titles, skin_items)))
            for skin_title, img in img_items:
                img_items.set_description(skin_title)
                sp = sget(session, f'{self.__root_website__}/{img.attr("href")}')
                sp_page = pq(sp.text)
                heading = sp_page('#firstHeading').text()

                _, resource_filename = heading.split(':', maxsplit=1)
                image_url = f"{self.__root_website__}/{sp_page('.fullMedia a').attr('href')}"

                skins.append({
                    'name': skin_title,
                    'url': image_url
                })

            alias.extend(
                self._get_alias_of_op(item["name_link"], session, [*all_cnnames, *all_ennames, *all_jpnames, *alias]))
            retval.append({
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
            })
            if maxcnt is not None and len(retval) >= maxcnt:
                break

        return retval


INDEXER = Indexer()
