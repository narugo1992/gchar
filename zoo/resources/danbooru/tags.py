import json
import string
from typing import Optional, List, Mapping, Any, Tuple

import pandas as pd
from ditk import logging
from tqdm.auto import tqdm

from gchar.config.meta import __TITLE__, __VERSION__
from gchar.utils import srequest
from ..base import HeaderParallelTagCrawler


class DanbooruTagCrawler(HeaderParallelTagCrawler):
    __init_page__ = 1
    __id_key__ = 'id'
    __max_workers__ = 4

    __site_url__: str = 'https://danbooru.donmai.us'

    def __init__(self):
        HeaderParallelTagCrawler.__init__(self)
        self.session.headers.update({
            "User-Agent": f"{__TITLE__}/{__VERSION__}",
            'Content-Type': 'application/json; charset=utf-8',
        })

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        name_pattern = kwargs['name_pattern']
        resp = srequest(self.session, 'GET', f'{self.__site_url__}/tags.json', params={
            'limit': '1000',
            'page': str(p),
            'search[name_matches]': name_pattern,
        })
        resp.raise_for_status()

        return resp.json()

    def get_tag_aliases_from_page(self, p, **kwargs) -> List[Tuple[str, str]]:
        name_pattern = kwargs['name_pattern']
        resp = srequest(self.session, 'GET', f'{self.__site_url__}/tag_aliases.json', params={
            'limit': '1000',
            'page': str(p),
            'search[name_matches]': name_pattern,
        })
        resp.raise_for_status()

        return [
            (item["antecedent_name"], item["consequent_name"])
            for item in resp.json()
        ]

    def _get_tag_aliases_json(self, data=None, exist_ids=None,
                              pg_pages: Optional[tqdm] = None, pg_tags: Optional[tqdm] = None, **kwargs):
        logging.info(f'Finding max pages for {kwargs!r} ...')
        self._load_data_with_pages(
            self.get_tag_aliases_from_page,
            lambda x: x[0],
            data, exist_ids, pg_pages, pg_tags, **kwargs
        )

    def get_tag_aliases_json(self) -> List[Tuple[str, str]]:
        data, exist_ids = [], set()
        pg_tags = tqdm(desc=f'Tag Aliases')
        pg_pages = tqdm(desc=f'Pages')

        for c in sorted(set(string.printable.lower())):
            if c == '*' or c == '?' or not c.strip():
                continue

            self._get_tag_aliases_json(data, exist_ids, pg_pages, pg_tags, name_pattern=f'{c}*')

        if self.__id_key__:
            return sorted(data, key=lambda x: x[0])
        else:
            return data

    def tags_json_to_df(self, json_) -> pd.DataFrame:
        df = HeaderParallelTagCrawler.tags_json_to_df(self, json_)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df['words'] = df['words'].apply(json.dumps).astype(str)
        return df

    __sqlite_indices__ = ['id', 'name', 'post_count', 'category', "created_at", "updated_at", "is_deprecated"]
