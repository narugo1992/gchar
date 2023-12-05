import logging
import os
import re
import warnings
from datetime import datetime
from functools import wraps
from typing import List, Optional, Iterator, Any
from urllib.parse import quote, urljoin

import requests
from PIL import Image
from hbutils.system import TemporaryDirectory, urlsplit
from imgutils.data import load_image
from imgutils.metrics import lpips_extract_feature, lpips_difference, ccip_extract_feature, ccip_batch_differences, \
    ccip_default_threshold
from imgutils.operate import squeeze_with_transparency
from pyquery import PyQuery as pq
from tqdm.auto import tqdm
from waifuc.action import PaddingAlignAction
from waifuc.model import ImageItem

from gchar.utils import download_file
from gchar.utils import sget as _origin_sget
from .base import GameIndexer


@wraps(_origin_sget)
def sget(*args, **kwargs):
    kwargs = {**dict(verify=False), **kwargs}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return _origin_sget(*args, **kwargs)


def _rgba_to_pil(image: Image.Image) -> Image.Image:
    image = load_image(squeeze_with_transparency(image), force_background='white', mode='RGB')
    action = PaddingAlignAction((512, 512))
    image = action.process(ImageItem(image, {})).image
    return image


def _url_to_pil(url) -> Image.Image:
    with TemporaryDirectory() as td:
        file = os.path.join(td, urlsplit(url).filename)
        download_file(url, file, silent=True)
        return _rgba_to_pil(Image.open(file))


_DATA_ITEMS = [
    'data-time-stamp', 'data-id', 'data-name', 'data-rarity', 'data-career-cn', 'data-career',
    'data-obtain-method', 'data-hp', 'data-pow', 'data-skill-intensity', 'data-def', 'data-avatar',
    'data-camp-cn', 'data-faction', 'data-filename', 'data-has-npic', 'data-has-icon'
]

_PRE_GENDERS = {
    1074: '女性',
    1032: '男性',
    1056: '男性',
}


class NeuralCloudIndexer(GameIndexer):
    __game_name__ = 'neuralcloud'
    __official_name__ = 'project neural cloud'
    __root_website__ = 'http://wiki.42lab.cloud'
    __jp_website__ = 'https://neural-cloud.wikiru.jp'

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

    def _crawl_index_from_cnsite(self, session: requests.Session) -> Iterator[Any]:
        response = sget(session, f'{self.__root_website__}/w/%E5%BF%83%E6%99%BA%E4%BA%BA%E5%BD%A2%E5%9B%BE%E9%89%B4')
        response.raise_for_status()

        index_page = pq(response.text)
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
                *_, gf_char_element = gf_char_block('td > span.externalCloud a').items()
                gf_char_name, gf_char_page_url = gf_char_element.text().strip(), gf_char_element.attr('href')
                gf_char_page_url = gf_char_page_url.replace('https://', 'http://')

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

            if list(one_page('.fixed-info .ssr').items()):
                enname_item, *_ = one_page('.fixed-info .ssr').items()
            elif list(one_page('.fixed-info .sr').items()):
                enname_item, *_ = one_page('.fixed-info .sr').items()
            elif list(one_page('.fixed-info .r').items()):
                enname_item, *_ = one_page('.fixed-info .r').items()
            else:
                assert False, f'No english name element found for character {cnname!r} ({id_!r})'

            enname = enname_item.text().lower()
            # enname, = re.findall(r'<div\s+id="nameEN"[^>]*>(?P<name>[^<]+)</div>', page_resp.text)
            hero_state = one_page('.hero-state')

            skins = []
            for skin_text, skin_img in zip(
                    hero_state('.skin-list [data-npic]').items(),
                    hero_state('.skin img').items(),
            ):
                skin_url = urljoin(page_resp.url, skin_img.attr('src'))
                skin_name = skin_text('b').text().strip() + ' - ' + skin_text('span').text().strip()
                skins.append({
                    'name': skin_name,
                    'url': skin_url,
                })

            yield {
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
            }

    def _get_index_from_jpsite(self, session: requests.Session):
        resp = sget(session,
                    f'{self.__jp_website__}/?%E3%82%AD%E3%83%A3%E3%83%A9%E3%82%AF%E3%82%BF%E3%83%BC%E4%B8%80%E8%A6%A7#')
        for item in pq(resp.text)("tr td.style_td:nth-child(2) a").items():
            yield item.text().strip(), urljoin(resp.request.url, item.attr('href'))

    def _get_info_from_jpsite(self, session: requests.Session, url):
        resp = sget(session, url)
        page = pq(resp.text)

        tables = list(page('.style_table').items())
        table_1 = tables[0]
        rel_url = table_1('tr:nth-child(2) td:nth-child(1) img').attr('data-src')
        if rel_url:
            return {
                'skin_url': urljoin(resp.request.url, rel_url),
            }
        else:
            return None

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        cn_items = []
        cn_skins = []
        for i, item in enumerate(tqdm(self._crawl_index_from_cnsite(session))):
            cn_items.append(item)
            skin_url = None
            for skin in item['skins']:
                if '默认' in skin['name']:
                    skin_url = skin['url']
                    logging.info(f'Skin {skin["name"]} selected for {item["cnname"]}')
                    break
            else:
                logging.warning(f'No skin found for {item["cnname"]}')

            if skin_url is not None:
                img = _url_to_pil(skin_url)
                cn_skins.append((i, lpips_extract_feature(img), ccip_extract_feature(img)))

        jp_items = []
        jp_skins = []
        i = 0 
        for _, (jpname, jp_page_url) in enumerate(tqdm(list(self._get_index_from_jpsite(session)))):
            info = self._get_info_from_jpsite(session, jp_page_url)
            if not info:
                logging.warning(f'No skin information for {jpname!r}, skipped.')
                continue
            info['jpname'] = jpname
            jp_items.append(info)
            img = _url_to_pil(info['skin_url'])
            jp_skins.append((i, lpips_extract_feature(img), ccip_extract_feature(img)))
            i += 1

        lpips_pairs = []
        for i, cn_lpips_feat, _ in cn_skins:
            for j, jp_lpips_feat, _ in jp_skins:
                lpips_pairs.append((i, j, lpips_difference(cn_lpips_feat, jp_lpips_feat)))

        _exist_is, _exist_js, mps = set(), set(), {}
        for i, j, diff in sorted(lpips_pairs, key=lambda x: x[2]):
            if i in _exist_is or j in _exist_js or diff > 0.2:
                continue

            mps[i] = (j, 'lpips', diff)
            _exist_is.add(i)
            _exist_js.add(j)
            cnname = cn_items[i]['cnname']
            jpname = jp_items[j]['jpname']
            logging.info(f'{cnname!r} matched with {jpname!r}, lpips diff is {diff!r}')

        ccip_feats = [
            *(cn_ccip_feat for _, _, cn_ccip_feat in cn_skins),
            *(jp_ccip_feat for _, _, jp_ccip_feat in jp_skins),
        ]
        ccip_diffs = ccip_batch_differences(ccip_feats)[0:len(cn_skins), len(cn_skins):len(cn_skins) + len(jp_skins)]
        ccip_pairs = []
        for ri, (i, _, _) in enumerate(cn_skins):
            for rj, (j, _, _) in enumerate(jp_skins):
                diff = ccip_diffs[ri, rj].item()
                ccip_pairs.append((i, j, diff))

        for i, j, diff in sorted(ccip_pairs, key=lambda x: x[2]):
            if i in _exist_is or j in _exist_js or diff > ccip_default_threshold():
                continue

            mps[i] = (j, 'ccip', diff)
            _exist_is.add(i)
            _exist_js.add(j)
            cnname = cn_items[i]['cnname']
            jpname = jp_items[j]['jpname']
            logging.info(f'{cnname!r} matched with {jpname!r}, ccip diff is {diff!r}')

        retval = []
        for i, item in enumerate(cn_items):
            if i in mps:
                j, method, diff = mps[i]
                jpname = jp_items[j]['jpname']
            else:
                jpname, method, diff = None, None, None

            item['jpname'] = jpname
            item['diff'] = {
                'method': method,
                'diff': diff
            } if method else None
            retval.append(item)
            if jpname is None:
                logging.warning(f'Chinese character {item["cnname"]} not matched with jpname.')

        for j, item in enumerate(jp_items):
            if j not in _exist_js:
                logging.warning(f'Japanese character {item["jpname"]} not matched with cnname.')

        return cn_items


INDEXER = NeuralCloudIndexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
