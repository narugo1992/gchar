import json
import sqlite3

import pandas as pd
from tqdm.auto import tqdm

from gchar.utils import get_requests_session, srequest


def crawl_tags_to_json(site_root: str = 'https://konachan.com', direct: bool = False):
    session = get_requests_session(timeout=60)
    data, exist_ids = [], set()
    if direct:
        resp = srequest(session, 'GET', f'{site_root}/tag.json', params={
            'limit': '0',
        })
        resp.raise_for_status()
        data.extend(json.loads(resp.text))

    else:
        pg = tqdm()
        page_no = 1
        while True:
            resp = srequest(session, 'GET', f'{site_root}/tag.json', params={
                'limit': '100',
                'page': str(page_no),
            })
            resp.raise_for_status()

            tags = json.loads(resp.text)
            if not tags:
                break

            for item in tags:
                if item['id'] in exist_ids:
                    continue

                data.append(item)
                exist_ids.add(item['id'])

            page_no += 1
            pg.update()

    data = sorted(data, key=lambda x: -x['id'])
    return data


def json_to_df(json_):
    df = pd.DataFrame(json_).astype({})
    return df


def json_save_to_csv(json_, csv_file):
    df = json_to_df(json_)
    df.to_csv(csv_file, index=False)
    return csv_file


def json_save_to_sqlite(json_, sqlite_file):
    sql = sqlite3.connect(sqlite_file)
    df = json_to_df(json_)
    df.to_sql('tags', sql)

    index_columns = ['id', 'name', 'type', 'count', 'ambiguous']
    for column in index_columns:
        sql.execute(f"CREATE INDEX tags_index_{column} ON tags ({column});").fetchall()

    sql.close()
    return sqlite_file
