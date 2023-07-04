import json
from typing import Optional, List, Mapping, Any

import pandas as pd

from gchar.config.meta import __TITLE__, __VERSION__
from gchar.utils import srequest
from ..base import HeaderParallelTagCrawler


class DanbooruTagCrawler(HeaderParallelTagCrawler):
    __init_page__ = 1
    __id_key__ = 'id'
    __max_workers__ = 4

    def __init__(self, site_url: str = 'https://danbooru.donmai.us'):
        HeaderParallelTagCrawler.__init__(self, site_url)
        self.session.headers.update({
            "User-Agent": f"{__TITLE__}/{__VERSION__}",
            'Content-Type': 'application/json; charset=utf-8',
        })

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        name_pattern = kwargs['name_pattern']
        resp = srequest(self.session, 'GET', f'{self.site_url}/tags.json', params={
            'limit': '1000',
            'page': str(p),
            'search[name_matches]': name_pattern,
        })
        resp.raise_for_status()

        return resp.json()

    def json_to_df(self, json_) -> pd.DataFrame:
        df = HeaderParallelTagCrawler.json_to_df(self, json_)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df['words'] = df['words'].apply(json.dumps).astype(str)
        return df

    __sqlite_indices__ = ['id', 'name', 'post_count', 'category', "created_at", "updated_at", "is_deprecated"]
