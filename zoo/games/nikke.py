import os.path
import re
import warnings
from typing import Optional, Iterator, Any, Tuple
from urllib.parse import urljoin

import dateparser
import numpy as np
import requests
from PIL import Image
from ditk import logging
from hbutils.system import TemporaryDirectory, urlsplit
from imgutils.data import load_image, istack
from imgutils.metrics import lpips_extract_feature, lpips_difference, ccip_batch_differences, ccip_extract_feature, \
    ccip_default_threshold
from imgutils.operate import squeeze_with_transparency
from pyquery import PyQuery as pq
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import min_weight_full_bipartite_matching
from tqdm.auto import tqdm
from waifuc.action import PaddingAlignAction
from waifuc.model import ImageItem

from gchar.utils import srequest, download_file
from .base import GameIndexer


def _rgba_to_pil(image: Image.Image) -> Image.Image:
    image = load_image(squeeze_with_transparency(image), force_background='white', mode='RGB')
    action = PaddingAlignAction((512, 512))
    image = action.process(ImageItem(image, {})).image
    return image


def _ensite_url_to_pil(url) -> Image.Image:
    with TemporaryDirectory() as td:
        file = os.path.join(td, urlsplit(url).filename)
        download_file(url, file, silent=True)
        return _rgba_to_pil(Image.open(file))


def _cnsite_url_to_pil(url) -> Image.Image:
    with TemporaryDirectory() as td:
        file = os.path.join(td, urlsplit(url).filename)
        download_file(url, file, silent=True)

        image = Image.open(file)
        assert image.is_animated, f'Gif required but {url!r} found.'
        image.seek(0)
        new_image = image.copy().convert('RGB')

        mask = np.array(new_image.convert('L')) < 254
        new_image = istack((new_image, mask))
        return _rgba_to_pil(new_image)


class NikkeIndexer(GameIndexer):
    __game_name__ = 'nikke'
    __root_website__ = 'https://nikke-goddess-of-victory-international.fandom.com'
    __root_website_cn__ = 'https://nikke.gamekee.com'

    def _get_index_from_ensite(self, session: requests.Session) -> Iterator[Tuple[str, str]]:
        resp = srequest(session, 'GET', f'{self.__root_website__}/wiki/Home')
        page = pq(resp.text)

        for ix in page('#content div').items():
            divs = list(ix.children())
            if len(divs) == 2 and pq(divs[0]).text().strip() == 'Nikkes':
                for item in pq(divs[1]).children():
                    item = pq(item)
                    url = urljoin(resp.request.url, item('div:nth-child(1) a').attr('href'))
                    name = item('div:nth-child(2)').text().strip()
                    yield name, url

                break

    def _get_info_from_ensite(self, session: requests.Session, url: str):
        resp = srequest(session, 'GET', url)
        page = pq(resp.text)

        names = {}
        for item in page('aside.pi-theme-wikia > section:nth-child(3) > .pi-item[data-source]').items():
            text = item.text().strip().replace('(', '(').replace(')', ')')
            native = re.sub(r'\([^)]+\)', '', text).strip()
            inners = re.findall(r'\(([^)]+)\)', text)
            exist_names, current_names = set(), []
            for name in [native, *inners]:
                name = re.sub(r'\s+', ' ', name.strip())
                if name not in exist_names:
                    exist_names.add(name)
                    current_names.append(name)
            names[item.attr('data-source')] = current_names

        info = {}
        for item in page('aside.pi-theme-wikia > section:nth-child(5) td[data-source]').items():
            info[item.attr('data-source')] = item('a').attr('title').lower().replace('category:', '').strip()
        for item in page('aside.pi-theme-wikia > section:nth-child(6) td[data-source]').items():
            info[item.attr('data-source')] = item('a').attr('title').lower().replace('category:', '').strip()

        extra = {}
        for item in page('aside.pi-theme-wikia > section:nth-child(8) div[data-source]').items():
            extra[item.attr('data-source')] = item('.pi-data-value').text().strip()
        if 'releaseDate' in extra:
            release_time = dateparser.parse(extra['releaseDate']).timestamp()
        else:
            release_time = None

        skins = []
        skin_resp = srequest(session, 'GET', f'{url}/Gallery')
        skin_page = pq(skin_resp.text)
        images_box = skin_page('#gallery-0')
        for item in images_box('.wikia-gallery-item').items():
            name_box = item('.lightbox-caption')
            name_box.remove('span')
            name = name_box.text().strip() or 'Default'
            thumb_page_url = urljoin(skin_resp.url, item('.thumb a img').attr('src'))
            skin_url = re.sub(r'/revision[\s\S]+?$', '', thumb_page_url)
            if skin_url and srequest(session, 'HEAD', skin_url).ok:
                skins.append({'name': name, 'url': skin_url})

        return {
            'info': info,
            'names': names,
            'skins': skins,
            'release': {
                'time': release_time,
            }
        }

    def _get_index_from_cnsite(self, session: requests.Session) -> Iterator[Tuple[str, int]]:
        resp = srequest(session, 'GET', f'{self.__root_website_cn__}/v1/wiki/entry', headers={
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "referrer": f"{self.__root_website_cn__}/",
            "game-alias": "nikke",
            "game-id": "0",
        })
        data = resp.json()
        entries = data['data']['entry_list']

        for entry in entries:
            if entry['name'] == '游戏图鉴':
                game_tj = entry
                break
        else:
            raise ValueError('Game index not found!')

        for entry in game_tj['child']:
            if entry['name'] == '角色图鉴':
                ch_index = entry['child']
                break
        else:
            raise ValueError('Character index not found!')

        for item in ch_index:
            if item['content_id']:
                yield item['name'], item["content_id"]

    def _get_info_from_cnsite(self, session: requests.Session, content_id: int):
        resp = srequest(session, 'GET', f'{self.__root_website_cn__}/v1/content/detail/{content_id}', headers={
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "referrer": f"{self.__root_website_cn__}/{content_id}.html",
            "game-alias": "nikke",
            "game-id": "0",
        })
        data = resp.json()

        page = pq(data['data']['content'])
        first_table, *_ = page('table.mould-table').items()
        gif_img_url = urljoin(resp.request.url, first_table('tr:nth-child(2) td:nth-child(3) img').attr('src'))

        bottom = page('.selectItem.slide-model-container')
        name_mapping = {
            item.text().strip(): item.attr('data-index')
            for item in bottom('.slide-nav-wrapper > [data-index]').items()
        }
        block_mapping = {
            item.attr('data-index'): item
            for item in bottom('.slide-content-group > [data-index]').items()
        }
        img_element = block_mapping[name_mapping.get('立绘', name_mapping.get('立绘（新）'))]('img')
        url = urljoin(resp.request.url, img_element.attr('data-real') or img_element.attr('src'))

        return {
            'name': data['data']['title'],
            'skin_url': gif_img_url,
        }

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        logging.info(f'Grabbing from {self.__root_website__} ...')
        en_site_pg = tqdm(list(self._get_index_from_ensite(session)))
        en_site_items = []
        en_lpips_feats, en_ccip_feats = [], []
        for name, url in en_site_pg:
            en_site_pg.set_description(name)
            item_data = self._get_info_from_ensite(session, url)
            en_site_items.append(item_data)
            sq_skin_img = _ensite_url_to_pil(item_data['skins'][0]['url'])
            en_lpips_feats.append(lpips_extract_feature(sq_skin_img))
            en_ccip_feats.append(ccip_extract_feature(sq_skin_img))

        logging.info(f'Grabbing from {self.__root_website_cn__} ...')
        cn_site_pg = tqdm(list(self._get_index_from_cnsite(session)))
        cn_site_items = []
        cn_lpips_feats, cn_ccip_feats = [], []
        for name, content_id in cn_site_pg:
            cn_site_pg.set_description(name)
            data_item = self._get_info_from_cnsite(session, content_id)
            cn_site_items.append(data_item)
            sq_skin_img = _cnsite_url_to_pil(data_item['skin_url'])
            cn_lpips_feats.append(lpips_extract_feature(sq_skin_img))
            cn_ccip_feats.append(ccip_extract_feature(sq_skin_img))

        # lpips matching
        lpips_pairs = []
        lpips_matrix = np.zeros((len(en_site_items), len(cn_site_items)), dtype=np.float32)
        for i, en_feat in enumerate(en_lpips_feats):
            for j, cn_feat in enumerate(cn_lpips_feats):
                diff = lpips_difference(en_feat, cn_feat)
                lpips_pairs.append((i, j, diff))
                lpips_matrix[i, j] = diff

        cmatrix = csr_matrix(lpips_matrix)
        row_ind, col_ind = min_weight_full_bipartite_matching(cmatrix)

        _exist_i, _exist_j, matched_pairs = set(), set(), []
        for i, j in zip(row_ind, col_ind):
            if i == -1 or j == -1:
                continue

            diff = lpips_matrix[i, j].item()
            if diff > 0.2:
                continue

            en_item, cn_item = en_site_items[i], cn_site_items[j]
            cnname = cn_item['name']
            ennames = list(en_item['names'].get('name_en') or [])
            logging.info(f'{cnname!r} and {ennames!r} matched with lpips, with diff of {diff!r}.')
            matched_pairs.append((i, j, 'lpips', diff))
            _exist_i.add(i)
            _exist_j.add(j)

        # ccip matching
        ccip_diffs = ccip_batch_differences([*en_ccip_feats, *cn_ccip_feats])
        ccip_diffs = ccip_diffs[0:len(en_ccip_feats), len(en_ccip_feats): len(en_ccip_feats) + len(cn_ccip_feats)]
        ccip_pairs = [
            (i, j, ccip_diffs[i, j].item())
            for i in range(len(en_ccip_feats))
            for j in range(len(cn_ccip_feats))
        ]
        for i, j, diff in sorted(ccip_pairs, key=lambda x: x[2]):
            if i in _exist_i or j in _exist_j or diff > ccip_default_threshold():
                continue

            en_item, cn_item = en_site_items[i], cn_site_items[j]
            cnname = cn_item['name']
            ennames = list(en_item['names'].get('name_en') or [])
            logging.info(f'{cnname!r} and {ennames!r} matched with ccip, with diff of {diff!r}.')
            matched_pairs.append((i, j, 'ccip', diff))
            _exist_i.add(i)
            _exist_j.add(j)

        _non_match_en_ids = set(range(len(en_site_items))) - _exist_i
        for i in sorted(_non_match_en_ids):
            en_item = en_site_items[i]
            ennames = list(en_item['names'].get('name_en') or [])
            warnings.warn(f'{ennames!r} not matched with chinese wiki, no chinese name will be used.')
            matched_pairs.append((i, None, None, None))

        _non_match_cn_ids = set(range(len(cn_site_items))) - _exist_j
        for j in sorted(_non_match_cn_ids):
            cn_item = cn_site_items[j]
            cnname = cn_item['name']
            warnings.warn(f'{cnname!r} not matched with english wiki, it will be ignored.')

        for i, j, diff_type, diff_value in matched_pairs:
            en_item = en_site_items[i]
            cn_item = cn_site_items[j] if j is not None else None
            skins = list(en_item['skins'])
            if cn_item:
                skins.append({
                    'name': 'Animated',
                    'url': cn_item['skin_url'],
                })

            yield {
                'cnname': cn_item['name'] if cn_item else None,
                'jpname': list(en_item['names'].get('name_jp') or []),
                'enname': list(en_item['names'].get('name_en') or []),
                'krname': list(en_item['names'].get('name_kr') or []),
                **en_item['info'],
                'skins': skins,
                'release': en_item['release'],
                'diff': {
                    'type': diff_type,
                    'value': diff_value,
                } if cn_item else None,
            }


INDEXER = NikkeIndexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
