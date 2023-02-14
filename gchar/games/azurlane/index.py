import re
from itertools import islice
from typing import Optional, Tuple, Iterator, Any

import requests
from pyquery import PyQuery as pq
from tqdm import tqdm

from ..base import BaseIndexer
from ...utils import sget

_VALID_TYPES = ['前排先锋', '后排主力', '驱逐', '轻巡', '重巡', '超巡', '战巡', '战列', '航战', '航母', '轻航', '重炮',
                '维修', '潜艇', '潜母', '运输', '风帆']

CNNAME_PATTERN = re.compile(r'^(?P<name>[^(]+)(\((?P<alias>[^)]+)\))?(?P<suffix>.改|)$')
CNNAME_MU_PATTERN = re.compile(r'^(?P<name>[^(]+\(\S+兵装\))(\((?P<alias>[^(]+\(\S+兵装\))\))?$')


def _no_big_curve(s: str) -> str:
    return s.replace('（', '(').replace('）', ')').replace('・', '·')


def _process_cnname(s: str) -> Tuple[str, str, str]:
    if '兵装' not in s:
        matching = CNNAME_PATTERN.fullmatch(s)
        return matching.group('name'), matching.group('alias'), matching.group('suffix')
    else:
        matching = CNNAME_MU_PATTERN.fullmatch(s)
        return matching.group('name'), matching.group('alias'), ''


class Indexer(BaseIndexer):
    __game_name__ = 'azurlane'
    __official_name__ = 'azur lane'
    __root_website__ = 'https://wiki.biligame.com/'

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        response = sget(session, f'{self.__root_website__}/blhx/%E8%88%B0%E8%88%B9%E5%9B%BE%E9%89%B4')

        items = list(pq(response.text)('.jntj-1').items())
        items_tqdm = tqdm(items, total=maxcnt)
        retval = []
        exist_cnnames = []
        for item in items_tqdm:
            cnname = _no_big_curve(item('span a').text())
            items_tqdm.set_description(cnname)
            p_cnname, cn_alias, cn_suffix = _process_cnname(cnname)
            short_cnname = f'{p_cnname}{cn_suffix}'
            alias = []
            if cn_alias:
                cn_alias = f'{cn_alias}{cn_suffix}'
                alias.append(cn_alias)

            types_ = item.attr('data-param1').split(',')
            rarity = item.attr('data-param2')
            group, *_ = [g.strip() for g in item.attr('data-param3').split(',') if g]
            page_url = f"{self.__root_website__}{item('.jntj-4 a').attr('href')}"

            resp = sget(session, page_url)
            full = pq(resp.text)
            table = full('table.wikitable.sv-general')
            target, l2 = islice(table('tr').items(), 2)
            ch_id = l2('#PNN').text()
            type_ = l2('#PNshiptype').text()
            enname, jpname = map(lambda x: x.text(), target('span').items())
            enname_full = enname.replace(chr(160), ' ')
            if re.fullmatch('^[A-Z]{2,}$', enname_full.split(' ')[0]):
                enname = ' '.join(enname_full.split(' ')[1:])
            else:
                enname = enname_full
            jpnames = jpname.split(' ') if jpname else []

            target.remove('span')
            full_cnname = target.text()

            image_tab = full('#characters .TabContainer')
            skins = []
            for li, con in zip(image_tab('ul .tab_li').items(), image_tab('.Contentbox2 .tab_con').items()):
                skin_name = li.text().strip()
                if con('img'):
                    skin_url, skin_scale = con('img').attr('src'), 1.0
                    srcset = con('img').attr('srcset')
                    if srcset:
                        skin_url_items = re.findall(r'(?P<url>http\S+) (?P<scale>[\d.]+)x', srcset)
                        for single_url, _str_scale in skin_url_items:
                            if float(_str_scale) > skin_scale:
                                skin_url = single_url
                                skin_scale = float(_str_scale)
                    skins.append({
                        'name': skin_name,
                        'url': skin_url,
                    })

            retval.append({
                'id': ch_id,
                'cnname': {
                    'full': full_cnname,
                    'label': cnname,
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
