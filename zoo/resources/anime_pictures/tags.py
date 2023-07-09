from typing import List, Mapping, Any

import pandas as pd
from tqdm.auto import tqdm

from gchar.utils import get_requests_session, srequest
from ..base import TagCrawler


class AnimePicturesTagCrawler(TagCrawler):
    __site_url__ = 'https://anime-pictures.net'

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        session = get_requests_session()
        offset = 0
        retval = []
        pg = tqdm(desc='Tag Crawl')
        exist_ids = set()
        while True:
            resp = srequest(
                session, 'GET', f'{self.__site_url__}/api/v3/tags',
                params={
                    'lang': 'en',
                    'offset': str(offset),
                    'limit': '100',
                }
            )
            resp.raise_for_status()

            tags = resp.json()['tags']
            if not tags:
                break

            for tag in tags:
                if tag['id'] in exist_ids:
                    continue

                retval.append(tag)
                exist_ids.add(tag['id'])

            offset += len(tags)
            pg.update()

        pg.close()
        return retval

    def tags_json_to_df(self, json_) -> pd.DataFrame:
        return TagCrawler.tags_json_to_df(self, json_).astype({
            "parent": pd.Int64Dtype(),
            "alias": pd.Int64Dtype(),
        })

    __sqlite_indices__ = ['id', 'parent', 'type', 'num', 'num_pub', 'views', 'tag', 'tag_jp', 'tag_ru', 'alias']
