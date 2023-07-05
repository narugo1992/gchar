import json
import sqlite3
from typing import Optional, List, Mapping, Any

import pandas as pd

from gchar.utils import get_requests_session, srequest
from ..base.tags import ParallelTagCrawler


class SankakuTagCrawler(ParallelTagCrawler):
    __init_page__ = 1
    __id_key__ = 'id'
    __max_workers__ = 8

    def __init__(self, site_url: str = 'https://capi-v2.sankakucomplex.com', limit: int = 100):
        session = get_requests_session(headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.1996 "
                "Yowser/2.5 Safari/537.36"
            ),
            "Content-Type": "application/json; charset=utf-8",
            "X-Requested-With": "com.android.browser",
            "Accept-Encoding": "gzip, deflate, br",
            "Host": "capi-v2.sankakucomplex.com"
        })
        ParallelTagCrawler.__init__(self, site_url, session)
        self.limit = limit

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        resp = srequest(self.session, 'GET', f'{self.site_url}/tags', params={
            'lang': 'en',
            'page': str(p),
            'limit': str(self.limit),
        })
        resp.raise_for_status()

        data = []
        for item in resp.json():
            item_data = {
                'id': item['id'],
                'name': item['name'],
                'type': item['type'],
                'post_count': item['post_count'],
                'pool_count': item['pool_count'],
                'series_count': item['series_count'],
                'rating': item['rating'],
                'version': item['version'],
                'parent_ids': [v['id'] for v in item['parent_tags']],
                'child_ids': [v['id'] for v in item['child_tags']],
                'related_ids': [v['id'] for v in item['related_tags']],
            }
            for trans in item['translations']:
                item_data[f'trans_{trans["lang"]}'] = trans['translation']

            data.append(item_data)

        return data

    __sqlite_indices__ = ['id', 'name', 'type', 'post_count', 'pool_count', 'series_count', 'rating']

    def json_save_to_sqlite(self, tags, tags_aliases, sqlite_file) -> str:
        sql = sqlite3.connect(sqlite_file)
        df = self.tags_json_to_df(tags)
        df['parent_ids'] = df['parent_ids'].apply(json.dumps).astype(str)
        df['child_ids'] = df['child_ids'].apply(json.dumps).astype(str)
        df['related_ids'] = df['related_ids'].apply(json.dumps).astype(str)
        df.to_sql('tags', sql)
        for column in self.__sqlite_indices__:
            sql.execute(f"CREATE INDEX tags_index_{column} ON tags ({column});").fetchall()

        parent_items = []
        child_items = []
        related_items = []
        for item in tags:
            for parent_id in item['parent_ids']:
                parent_items.append({'tag_id': item['id'], 'parent_id': parent_id})
            for child_id in item['child_ids']:
                child_items.append({'tag_id': item['id'], 'child_id': child_id})
            for related_id in item['related_ids']:
                related_items.append({'tag_id': item['id'], 'related_id': related_id})
        pd.DataFrame(data=parent_items, columns=['tag_id', 'parent_id']).to_sql('parents', sql)
        for column in ['tag_id', 'parent_id']:
            sql.execute(f"CREATE INDEX parents_index_{column} ON parents ({column});").fetchall()

        pd.DataFrame(data=child_items, columns=['tag_id', 'child_id']).to_sql('children', sql)
        for column in ['tag_id', 'child_id']:
            sql.execute(f"CREATE INDEX children_index_{column} ON children ({column});").fetchall()

        pd.DataFrame(data=related_items, columns=['tag_id', 'related_id']).to_sql('relations', sql)
        for column in ['tag_id', 'related_id']:
            sql.execute(f"CREATE INDEX relateds_index_{column} ON relations ({column});").fetchall()

        sql.close()
        return sqlite_file
