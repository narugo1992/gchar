import json
import os
import sqlite3
import string
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import List, Mapping, Any, Optional, ContextManager, Tuple

import pandas as pd
import requests
from ditk import logging
from hbutils.system import TemporaryDirectory, urlsplit
from tqdm.auto import tqdm

from gchar.utils import get_requests_session
from .base import HuggingfaceDeployable


class NoTagAlias(Exception):
    pass


class TagCrawler(HuggingfaceDeployable):
    def __init__(self, site_url: str, session: Optional[requests.Session] = None):
        self.site_url = site_url
        self.session = session or get_requests_session()

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        raise NotImplementedError

    def get_tag_aliases_json(self) -> List[Tuple[str, str]]:
        raise NoTagAlias

    def tags_json_to_df(self, json_) -> pd.DataFrame:
        return pd.DataFrame(json_)

    def tags_json_save_to_csv(self, json_, csv_file) -> str:
        df = self.tags_json_to_df(json_)
        df.to_csv(csv_file, index=False)
        return csv_file

    def tag_aliases_json_to_df(self, list_):
        return pd.DataFrame([{'alias': alias, 'to': to_} for alias, to_ in list_])

    def tag_aliases_json_save_to_csv(self, list_, csv_file):
        df = self.tag_aliases_json_to_df(list_)
        df.to_csv(csv_file, index=False)
        return csv_file

    __sqlite_indices__ = []

    def json_save_to_sqlite(self, tags, tag_aliases, sqlite_file) -> str:
        sql = sqlite3.connect(sqlite_file)

        df_tags = self.tags_json_to_df(tags)
        df_tags.to_sql('tags', sql)
        for column in self.__sqlite_indices__:
            sql.execute(f"CREATE INDEX tags_index_{column} ON tags ({column});").fetchall()

        if tag_aliases is not None:
            df_tag_aliases = self.tag_aliases_json_to_df(tag_aliases)
            df_tag_aliases.to_sql('tag_aliases', sql)
            for column in ['alias', 'to']:
                sql.execute(f"CREATE INDEX tag_aliases_index_{column} ON tag_aliases ({column});").fetchall()

        sql.close()
        return sqlite_file

    @contextmanager
    def tags_files(self) -> List[str]:
        tags = self.get_tags_json()
        try:
            tag_aliases = self.get_tag_aliases_json()
        except NoTagAlias:
            tag_aliases = None
        with TemporaryDirectory() as td:
            files = []

            json_tags_file = os.path.join(td, 'tags.json')
            logging.info(f'Saving tags to json file {json_tags_file!r} ...')
            with open(json_tags_file, 'w', encoding='utf-8') as f:
                json.dump(tags, f)
            files.append(json_tags_file)

            csv_tags_file = os.path.join(td, 'tags.csv')
            logging.info(f'Exporting tags to csv file {csv_tags_file!r} ...')
            self.tags_json_save_to_csv(tags, csv_tags_file)
            files.append(csv_tags_file)

            if tag_aliases is not None:
                json_tag_aliases_file = os.path.join(td, 'tag_aliases.json')
                logging.info(f'Saving tags alias to json file {json_tag_aliases_file!r} ...')
                with open(json_tag_aliases_file, 'w', encoding='utf-8') as f:
                    json.dump([{'alias': alias, 'to': to_} for alias, to_ in tag_aliases], f)
                files.append(json_tag_aliases_file)

                csv_tag_aliases_file = os.path.join(td, 'tag_aliases.csv')
                logging.info(f'Exporting tag aliases to csv file {csv_tag_aliases_file!r} ...')
                self.tag_aliases_json_save_to_csv(tag_aliases, csv_tag_aliases_file)
                files.append(csv_tag_aliases_file)

            sqlite_file = os.path.join(td, 'tags.sqlite')
            logging.info(f'Exporting data to sqlite database file {sqlite_file!r} ...')
            self.json_save_to_sqlite(tags, tag_aliases, sqlite_file)
            files.append(sqlite_file)

            yield files

    @contextmanager
    def with_files(self, **kwargs) -> ContextManager[List[str]]:
        with self.tags_files() as files:
            yield files

    def get_default_namespace(self, **kwargs) -> str:
        return urlsplit(self.site_url).host


class ParallelTagCrawler(TagCrawler):
    __max_workers__ = 12
    __init_page__ = 1
    __id_key__ = 'id'

    @classmethod
    def _load_data_with_pages(cls, one_page_func, key_extract_func=None,
                              data=None, exist_ids=None, pg_pages: Optional[tqdm] = None,
                              pg_tags: Optional[tqdm] = None, **kwargs):
        left, right = 1, 2
        while True:
            if one_page_func(right, **kwargs):
                left, right = left << 1, right << 1
                logging.info(f'Left: {left}, right: {right}')
            else:
                break

        while left < right:
            middle = (left + right + 1) // 2
            if one_page_func(middle, **kwargs):
                left = middle
            else:
                right = middle - 1
            logging.info(f'Left: {left}, right: {right}')

        pages = left
        logging.info(f'Max pages for {kwargs!r} is {pages!r}.')

        if data is None:
            data = []
        if exist_ids is None:
            exist_ids = set()
        if pg_tags is None:
            pg_tags = tqdm(desc=f'Tags {kwargs!r}')
        if pg_pages is None:
            pg_pages = tqdm(desc=f'Pages {kwargs}', total=len(range(cls.__init_page__, pages + 1)))

        def _process(p):
            for item in one_page_func(p, **kwargs):
                if key_extract_func and key_extract_func(item) in exist_ids:
                    # if self.__id_key__ and item[self.__id_key__] in exist_ids:
                    continue

                data.append(item)
                if key_extract_func:
                    exist_ids.add(key_extract_func(item))

                # if self.__id_key__:
                #     exist_ids.add(item[self.__id_key__])
                pg_tags.update()

            pg_pages.update()

        tp = ThreadPoolExecutor(max_workers=cls.__max_workers__)
        for i in range(cls.__init_page__, pages + 1):
            tp.submit(_process, i)

        tp.shutdown()
        if key_extract_func:
            return sorted(data, key=key_extract_func)
        else:
            return data

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        raise NotImplementedError

    def _get_tags_json(self, data=None, exist_ids=None,
                       pg_pages: Optional[tqdm] = None, pg_tags: Optional[tqdm] = None, **kwargs):
        logging.info(f'Finding max pages for {kwargs!r} ...')
        return self._load_data_with_pages(
            self.get_tags_from_page,
            lambda x: x[self.__id_key__],
            data, exist_ids, pg_pages, pg_tags, **kwargs
        )

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        return self._get_tags_json()


class HeaderParallelTagCrawler(ParallelTagCrawler):
    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        raise NotImplementedError

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        data, exist_ids = [], set()
        pg_tags = tqdm(desc=f'Tags')
        pg_pages = tqdm(desc=f'Pages')

        for c in string.printable:
            if c == '*' or c == '?' or not c.strip():
                continue

            self._get_tags_json(data, exist_ids, pg_pages, pg_tags, name_pattern=f'{c}*')

        if self.__id_key__:
            return sorted(data, key=lambda x: x[self.__id_key__])
        else:
            return data
