import logging
import os.path
import re
import warnings
from datetime import datetime
from functools import wraps
from typing import Optional, List, Dict, Iterator, Any
from urllib.parse import quote, urljoin

import requests
from hbutils.system import urlsplit
from pyquery import PyQuery as pq
from tqdm import tqdm

from gchar.utils import sget as _origin_sget
from .base import GameIndexer


@wraps(_origin_sget)
def sget(*args, **kwargs):
    kwargs = {**dict(verify=False), **kwargs}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return _origin_sget(*args, **kwargs)


_STAR_PATTERN = re.compile(r'(?P<rarity>\d|EXTRA)star\.png')
_CLASS_PATTERN = re.compile(r'_(?P<class>SMG|MG|RF|HG|AR|SG)_')

_CN_SITE_ATTRS = [
    'data-mod', 'data-time-stamp', 'data-tile-effect1', 'data-tile-effect1-time', 'data-tile-effect2',
    'data-tile-effect2-time', 'data-id', 'data-name-ingame', 'data-url', 'data-rarity',
    'data-tdoll-class', 'data-tiles', 'data-obtain-method', 'data-tiles-affect', 'data-base-hp',
    'data-base-atk', 'data-base-rate', 'data-base-acc', 'data-skill1', 'data-base-eva', 'data-base-armor',
    'data-production-time', 'data-avatar', 'data-type-img', 'data-type', 'data-skill2',
    'data-modtile-effect1-time', 'data-modtile-effect2-time', 'data-tiles-affect-mod', 'data-avatar-mod',
    'data-mod-rarity', 'data-tiles-mod', 'data-mod-hp', 'data-mod-atk', 'data-mod-rate', 'data-mod-acc',
    'data-mod-eva', 'data-mod-armor'
]


class GirlsFrontLineIndexer(GameIndexer):
    __game_name__ = 'girlsfrontline'
    __official_name__ = 'girls\' front-line'
    __root_website__ = 'https://iopwiki.com'
    __root_website_cn__ = 'http://www.gfwiki.org'

    def _get_alias_of_op(self, op, session: requests.Session, website_root: str, names: List[str]) -> List[str]:
        response = sget(
            session,
            f'{website_root}/api.php?action=query&prop=redirects&titles={quote(op)}&format=json',
            headers={'Referer': website_root},
        )
        response.raise_for_status()

        alias_names = []
        pages = response.json()['query']['pages']
        for _, data in pages.items():
            for item in (data.get('redirects', None) or []):
                if item['title'] not in names:
                    alias_names.append(item['title'])

        return alias_names

    def _get_only_index_from_cnsite(self, session: requests.Session) -> Dict[int, str]:
        response = sget(session, f'{self.__root_website_cn__}/w/%E6%88%98%E6%9C%AF%E4%BA%BA%E5%BD%A2%E5%9B%BE%E9%89%B4')
        response.raise_for_status()

        query = pq(response.text)
        return {
            int(item.attr('data-id')): item.attr('data-name-ingame')
            for item in query('.dolldata').items()
        }

    def _get_media_url(self, session, purl: str) -> str:
        resp_ = sget(session, purl)
        return urljoin(resp_.url, pq(resp_.text)(".fullMedia a").attr("href"))

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        response = sget(session, f'{self.__root_website__}/wiki/T-Doll_Index')
        full = pq(response.text)

        _cn_index = self._get_only_index_from_cnsite(session)

        retval = []
        all_items = list(full('span.gfl-doll-card').items())
        all_items_tqdm = tqdm(all_items)
        for item in all_items_tqdm:
            id_text = item('span.index').text().strip()
            if not id_text:
                continue

            title = item('span[title]').attr('title')
            rele, *_ = _STAR_PATTERN.findall(item('span.rarity-class').attr('data-bg-lazy'))
            clazz, *_ = _CLASS_PATTERN.findall(item('span.rarity-class').attr('data-bg-lazy'))
            rarity = int(rele) if len(rele) == 1 else rele
            id_ = int(id_text)

            def _get_name_with_lang(lang: str) -> str:
                return full(f'span[data-server-doll={title!r}][data-server-released={lang!r}]') \
                    .attr('data-server-releasename')

            cnname = _get_name_with_lang('CN')
            enname = _get_name_with_lang('EN')
            jpname = _get_name_with_lang('JP')
            all_items_tqdm.set_description(f'{cnname}/{enname}/{jpname}')

            if id_ in _cn_index and _cn_index[id_] != cnname:
                cnnames = [_cn_index[id_], cnname]
                cnname, cnname_en = _cn_index[id_], cnname
            else:
                cnnames = [cnname]
                cnname_en = cnname

            alias_names = []
            alias_names.extend(
                self._get_alias_of_op((enname or cnname_en or jpname).replace(' ', '_'), session, self.__root_website__,
                                      [*cnnames, enname, jpname]))
            if id_ in _cn_index:
                alias_names.extend(self._get_alias_of_op(_cn_index[id_], session, self.__root_website_cn__,
                                                         [*alias_names, *cnnames, enname, jpname]))

            if id_ in _cn_index:
                logging.info(f'Accessing info of {title!r} from CN wiki ...')
                cn_page_resp = sget(session, f'{self.__root_website_cn__}/w/{quote(_cn_index[id_])}',
                                    headers={
                                        'Referer': f'{self.__root_website_cn__}/w/%E6%88%98%E6%9C%AF%E4%BA%BA%E5%BD%A2%E5%9B%BE%E9%89%B4'})
                cn_page = pq(cn_page_resp.text)
                all_doll_items = list(cn_page('.dollDivSplit4R table.dollTable').items())
                if all_doll_items:
                    cn_page_main_info, *_ = all_doll_items
                    date_match = re.fullmatch(
                        r'^\s*(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)\s*$',
                        cn_page_main_info('tr:nth-child(4) td').text(),
                    )
                    release_time = datetime.strptime(
                        f'{date_match.group("year")}/{date_match.group("month")}/{date_match.group("day")} '
                        f'17:00:00 +0800',
                        '%Y/%m/%d %H:%M:%S %z'
                    )
                    release_timestamp = release_time.timestamp()
                else:
                    release_timestamp = None
            else:
                release_timestamp = None

            resp = sget(session, urljoin(response.url, item('span[title] a').attr('href')))
            ch_page = pq(resp.text)
            _first, *_ = ch_page('li.gallerybox a').parents('ul').items()
            img_items = list(_first('li').items())
            skins = []
            img_items_tqdm = tqdm(img_items)
            for fn in img_items_tqdm:
                img_name = fn('.gallerytext').text()
                img_items_tqdm.set_description(img_name)
                if not re.findall(r'\bprofile\b', img_name, re.IGNORECASE):
                    wiki_url = urljoin(resp.url, fn('a.mw-file-description').attr('href'))
                    logging.info(f'Accessing skin {img_name!r} for {title!r} ...')
                    img_url = self._get_media_url(session, wiki_url)
                    img_name = img_name or os.path.splitext(urlsplit(img_url).filename)[0]
                    skins.append({
                        'desc': img_name,
                        'url': img_url,
                    })

            item = {
                'id': id_,
                'rarity': rarity,
                'class': clazz,
                'cnname': cnname,
                'cnnames': cnnames,
                'enname': enname,
                'jpname': jpname,
                'alias': alias_names,
                'twname': _get_name_with_lang('TW'),
                'krname': _get_name_with_lang('KR'),
                'release': {
                    'time': release_timestamp,
                },
                'skins': skins
            }
            retval.append(item)
            if maxcnt is not None and len(retval) >= maxcnt:
                break

        return retval


INDEXER = GirlsFrontLineIndexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
