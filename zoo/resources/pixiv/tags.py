import re
from typing import Optional, List, Mapping, Any
from urllib.parse import urljoin

import pandas as pd
from ditk import logging
from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from gchar.utils import srequest
from ..base.tags import ParallelTagCrawler


def _parse_int(x):
    if x == 'N/A':
        return None
    else:
        return int(x)


class PixivTagCrawler(ParallelTagCrawler):
    __max_workers__ = 12
    __id_key__ = 'name'
    __init_page__ = 1

    __site_url__ = 'https://dic.pixiv.net'
    __site_name__ = 'pixiv.net'

    def __init__(self):
        ParallelTagCrawler.__init__(self)

    CATEGORY_NAME_MAP = {
        'アニメ': 'animation', 'マンガ': 'manga', 'ラノベ': 'light novel', 'ゲーム': 'game', 'フィギュア': 'figure',
        '音楽': 'music', 'アート': 'art', 'デザイン': 'design', '一般': 'general', '人物': 'person',
        'キャラクター': 'character', 'セリフ': 'dialogue', 'イベント': 'event', '同人サークル': 'doujin circle'
    }

    def get_category_index(self):
        resp = srequest(self.session, 'GET', self.__site_url__)
        page = pq(resp.text)
        return [
            (self.CATEGORY_NAME_MAP[item.text().strip()], urljoin(resp.request.url, item.attr('href')))
            for item in page('nav#categories li a').items()
        ]

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        base_url = kwargs.pop('base_url')
        category = kwargs.pop('category')
        resp = srequest(self.session, 'GET', base_url, params={'page': str(p)}, raise_for_status=False)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()

        data = []
        for item in pq(resp.text)('#main section article').items():
            name = item('.info h2 a').text().strip()
            wiki_url = urljoin(resp.request.url, item('.info h2 a').attr('href'))

            ritems = {}
            for vitem in item('ul.data li').items():
                vname, vvalue = re.split(r'\s*:\s*', vitem.text().strip(), maxsplit=1)
                ritems[vname] = vvalue

            data.append({
                'name': name,
                'category': category,
                'wiki_url': wiki_url,
                'updated_at': ritems['更新'],
                'views': _parse_int(ritems['閲覧数']),
                'posts': _parse_int(ritems['作品数']),
                'checklists': _parse_int(ritems['チェックリスト数']),
            })

        return data

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        data, exist_ids = [], set()
        pg_pages = tqdm(desc='Total pages')
        pg_tags = tqdm(desc='Total tags')
        for category, category_index_url in self.get_category_index():
            logging.info(f'Finding max pages for category {category!r} ...')
            return self._load_data_with_pages(
                self.get_tags_from_page,
                lambda x: x[self.__id_key__],
                data, exist_ids, pg_pages, pg_tags,
                base_url=category_index_url, category=category,
            )

        return data

    def tags_json_to_df(self, json_) -> pd.DataFrame:
        df = ParallelTagCrawler.tags_json_to_df(self, json_).astype({
            "views": pd.Int64Dtype(),
            "posts": pd.Int64Dtype(),
            "checklists": pd.Int64Dtype(),
        })
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        return df

    __sqlite_indices__ = ['name', 'category', 'updated_at', 'views', 'posts', 'checklists']
