import re
from datetime import datetime
from typing import List, Optional, Iterator, Any
from urllib.parse import quote

import requests
from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from ..base import BaseIndexer
from ...utils import sget

_DATA_ITEMS = [
    'data-time-stamp', 'data-id', 'data-name', 'data-rarity', 'data-career-cn', 'data-career',
    'data-obtain-method', 'data-hp', 'data-pow', 'data-skill-intensity', 'data-def', 'data-avatar',
    'data-camp-cn', 'data-faction', 'data-filename', 'data-has-npic', 'data-has-icon'
]

_PRE_GENDERS = {
    1032: '男性',
    1056: '男性',
}


class Indexer(BaseIndexer):
    __game_name__ = 'neuralcloud'
    __official_name__ = 'project neural cloud'
    __root_website__ = 'http://wiki.42lab.cloud'

    def _get_alias_of_op(self, op, session: requests.Session, website_root: str, names: List[str]) -> List[str]:
        response = sget(
            session,
            f'{website_root}/api.php?action=query&prop=redirects&titles={quote(op)}&format=json',
        )
        response.raise_for_status()

        alias_names = []
        pages = response.json()['query']['pages']
        for _, data in pages.items():
            for item in (data.get('redirects', None) or []):
                if item['title'] not in names:
                    alias_names.append(item['title'])

        return alias_names

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        response = sget(session, f'{self.__root_website__}/w/%E5%BF%83%E6%99%BA%E4%BA%BA%E5%BD%A2%E5%9B%BE%E9%89%B4')
        response.raise_for_status()

        index_page = pq(response.text)
        retval = []
        all_ch_items = tqdm(list(index_page('.dolldata').items()))
        for item in all_ch_items:
            full_data = {
                name: item.attr(name)
                for name in _DATA_ITEMS
            }
            id_ = int(item.attr('data-id'))
            cnname = item.attr('data-name')
            rarity = int(item.attr('data-rarity'))
            clazz = item.attr('data-career-cn')
            company = item.attr('data-camp-cn')
            all_ch_items.set_description(f'{id_} - {cnname}')

            alias_names = self._get_alias_of_op(cnname, session, self.__root_website__, [])

            wiki_url = f'{self.__root_website__}/w/{quote(cnname)}'
            page_resp = sget(session, wiki_url)
            page_resp.raise_for_status()
            one_page = pq(page_resp.text)

            date_match = re.fullmatch(
                r'^\s*(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)\s*$',
                one_page('.flexRight table tr:nth-child(7) td:nth-child(2)').text(),
            )
            release_time = datetime.strptime(
                f'{date_match.group("year")}/{date_match.group("month")}/{date_match.group("day")} '
                f'17:00:00 +0800',
                '%Y/%m/%d %H:%M:%S %z'
            )

            if one_page('#后续经历'):
                gf_char_block = one_page('#后续经历').parent('h2').next('table.dollPageCloud')
                *_, gf_char_element = gf_char_block('td > a.externalCloud').items()
                gf_char_name, gf_char_page_url = gf_char_element.text().strip(), gf_char_element.attr('href')

                gf_page = sget(session, gf_char_page_url)
                pq_gf_page = pq(gf_page.text)
                gf_doll_table = pq_gf_page('#基本信息').parent('h2').next('div > div.dollDivSplit4R table.dollTable')
                gf_first_row = gf_doll_table('tr:nth-child(1)')
                assert gf_first_row('th').text().strip() == '编号'
                gf_char_id, = re.findall(r'^\s*No\.\s*(\d+)\s*$', gf_first_row('td:nth-child(2)').text())
                gf_char_id = int(gf_char_id)
            else:
                gf_char_name, gf_char_id = None, None

            if gf_char_name:
                gender = 'female'
            elif id_ in _PRE_GENDERS:
                gender = _PRE_GENDERS[id_]
            else:
                cv_name = one_page('.flexRight table tr:nth-child(5) td:nth-child(4)').text()
                mg_resp = sget(session, f'https://zh.moegirl.org.cn/{quote(cv_name)}', raise_for_status=False)
                if mg_resp.ok:
                    gender_words = re.findall('(女性|男性)', mg_resp.text)
                    gender = gender_words[0] if gender_words else None
                else:
                    gender = None

                assert gender, f'Invalid gender - {id_} {cnname}, this should be processed in _PRE_GENDERS.'

            enname, = re.findall(r'<div\s+id="nameEN"[^>]*>(?P<name>[^<]+)</div>', page_resp.text)
            skins = []
            for skin_text in re.findall(r'pic_data\.push\((?P<content>\{[\s\S]+?})\)\s*;', page_resp.text):

                (skin_name_s1, _), = re.findall(r'name\s*:\s*"(?P<name>[\s\S]*?)"\s*(,|$)', skin_text)
                (skin_name_s2_1, _), = re.findall(r'class\s*:\s*"(?P<name>[\s\S]*?)"\s*(,|$)', skin_text)
                (skin_name_s2_2, _), = re.findall(r'line\s*:\s*"(?P<name>[\s\S]*?)"\s*(,|$)', skin_text)
                (skin_url, _), = re.findall(r'pic\s*:\s*"(?P<name>[\s\S]*?)"\s*(,|$)', skin_text)
                skin_name_s2 = skin_name_s2_1 if len(skin_name_s2_1) <= len(skin_name_s2_2) else skin_name_s2_2
                if skin_name_s2:
                    skin_name = f"{skin_name_s1} - {skin_name_s2}"
                else:
                    skin_name = skin_name_s1
                skins.append({
                    'name': skin_name,
                    'url': skin_url,
                })

            retval.append({
                'data': full_data,
                'id': id_,
                'cnname': cnname,
                'jpname': None,
                'enname': enname,
                'alias': alias_names,
                'gf': {
                    'id': gf_char_id,
                    'name': gf_char_name,
                } if gf_char_id else None,
                'gender': gender,
                'rarity': rarity,
                'class': clazz,
                'company': company,
                'wiki_url': wiki_url,
                'release': {
                    'time': release_time.timestamp(),
                },
                'skins': skins,
            })
            if maxcnt is not None and len(retval) >= maxcnt:
                break

        return retval


INDEXER = Indexer()
