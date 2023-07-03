import json
import sqlite3

import pandas as pd
from tqdm.auto import tqdm

from gchar.config.meta import __TITLE__, __VERSION__
from gchar.utils import get_requests_session, srequest


def crawl_tags_to_json():
    session = get_requests_session(headers={
        "User-Agent": f"{__TITLE__}/{__VERSION__}",
        'Content-Type': 'application/json; charset=utf-8',
    })
    page_no = 1
    data, exist_ids = [], set()
    pg = tqdm()

    while True:
        resp = srequest(session, 'GET', 'https://danbooru.donmai.us/tags.json', params={
            'limit': '1000',
            'page': str(page_no),
        })
        resp.raise_for_status()

        if not resp.json():
            break

        for item in resp.json():
            if item['id'] in exist_ids:
                continue

            data.append(item)
            exist_ids.add(item['id'])

        page_no += 1
        pg.update()

    return data


def json_to_df(json_):
    df = pd.DataFrame(json_).astype({})
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    return df


def json_save_to_csv(json_, csv_file):
    df = json_to_df(json_)
    df.to_csv(csv_file, index=False)
    return csv_file


def json_save_to_sqlite(json_, sqlite_file):
    sql = sqlite3.connect(sqlite_file)
    df = json_to_df(json_)
    df['words'] = df['words'].apply(json.dumps).astype(str)
    df.to_sql('tags', sql, )

    index_columns = ['id', 'name', 'post_count', 'category', "created_at", "updated_at", "is_deprecated"]
    for column in index_columns:
        sql.execute(f"CREATE INDEX tags_index_{column} ON tags ({column});").fetchall()

    sql.close()
    return sqlite_file
