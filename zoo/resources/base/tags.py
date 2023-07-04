import datetime
import json
import os
import sqlite3
import string
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import List, Mapping, Any, Optional

import pandas as pd
from ditk import logging
from hbutils.system import TemporaryDirectory, urlsplit
from huggingface_hub import HfApi, CommitOperationAdd
from tqdm.auto import tqdm


class TagCrawler:
    def __init__(self, site_url: str):
        self.site_url = site_url

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        raise NotImplementedError

    def json_to_df(self, json_) -> pd.DataFrame:
        return pd.DataFrame(json_)

    def json_save_to_csv(self, json_, csv_file) -> str:
        df = self.json_to_df(json_)
        df.to_csv(csv_file, index=False)
        return csv_file

    __sqlite_indices__ = []

    def json_save_to_sqlite(self, json_, sqlite_file) -> str:
        sql = sqlite3.connect(sqlite_file)
        df = self.json_to_df(json_)
        df.to_sql('tags', sql)

        for column in self.__sqlite_indices__:
            sql.execute(f"CREATE INDEX tags_index_{column} ON tags ({column});").fetchall()

        sql.close()
        return sqlite_file

    @contextmanager
    def tags_files(self) -> List[str]:
        data = self.get_tags_json()
        with TemporaryDirectory() as td:
            files = []

            json_file = os.path.join(td, 'tags.json')
            logging.info(f'Saving data to json file {json_file!r} ...')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            files.append(json_file)

            csv_file = os.path.join(td, 'tags.csv')
            logging.info(f'Exporting data to csv file {csv_file!r} ...')
            self.json_save_to_csv(data, csv_file)
            files.append(csv_file)

            sqlite_file = os.path.join(td, 'tags.sqlite')
            logging.info(f'Exporting data to sqlite database file {sqlite_file!r} ...')
            self.json_save_to_sqlite(data, sqlite_file)
            files.append(sqlite_file)

            yield files

    def deploy_to_huggingface(self, repository: str = 'deepghs/site_tags',
                              namespace: Optional[str] = None, revision: str = 'main'):
        namespace = namespace or urlsplit(self.site_url).host
        logging.info(f'Initializing repository {repository!r} ...')
        hf_client = HfApi(token=os.environ['HF_TOKEN'])
        hf_client.create_repo(repo_id=repository, repo_type='dataset', exist_ok=True)

        with self.tags_files() as files:
            current_time = datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
            commit_message = f"Publish {namespace}\'s tags, on {current_time}"
            logging.info(f'Publishing {namespace}\'s tags to repository {repository!r} ...')
            hf_client.create_commit(
                repository,
                [
                    CommitOperationAdd(
                        path_in_repo=f'{namespace}/{os.path.basename(file)}',
                        path_or_fileobj=file,
                    ) for file in files
                ],
                commit_message=commit_message,
                repo_type='dataset',
                revision=revision,
            )


class ParallelTagCrawler(TagCrawler):
    __max_workers__ = 12
    __init_page__ = 1
    __id_key__ = 'id'

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        raise NotImplementedError

    def _get_tags_json(self, data=None, exist_ids=None,
                       pg_pages: Optional[tqdm] = None, pg_tags: Optional[tqdm] = None, **kwargs):
        logging.info(f'Finding max pages for {kwargs!r} ...')
        left, right = 1, 2
        while True:
            if self.get_tags_from_page(right, **kwargs):
                left, right = left << 1, right << 1
                logging.info(f'Left: {left}, right: {right}')
            else:
                break

        while left < right:
            middle = (left + right + 1) // 2
            if self.get_tags_from_page(middle, **kwargs):
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
            pg_pages = tqdm(desc=f'Pages {kwargs}', total=len(range(self.__init_page__, pages + 1)))

        def _process(p):
            for item in self.get_tags_from_page(p, **kwargs):
                if self.__id_key__ and item[self.__id_key__] in exist_ids:
                    continue

                data.append(item)
                if self.__id_key__:
                    exist_ids.add(item[self.__id_key__])
                pg_tags.update()

            pg_pages.update()

        tp = ThreadPoolExecutor(max_workers=self.__max_workers__)
        for i in range(self.__init_page__, pages + 1):
            tp.submit(_process, i)

        tp.shutdown()
        if self.__id_key__:
            return sorted(data, key=lambda x: x[self.__id_key__])
        else:
            return data

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
