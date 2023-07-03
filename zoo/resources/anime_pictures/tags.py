import sqlite3

import pandas as pd
from tqdm.auto import tqdm

from gchar.utils import get_requests_session, srequest

get_requests_session()


def crawl_tags_to_json():
    session = get_requests_session()
    offset = 0
    retval = []
    pg = tqdm(desc='Tag Crawl')
    exist_ids = set()
    while True:
        resp = srequest(session, 'GET', 'https://anime-pictures.net/api/v3/tags?offset=131000&limit=1000&lang=en',
                        params={
                            'lang': 'en',
                            'offset': str(offset),
                            'limit': '100',
                        })
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


def json_to_df(json_):
    df = pd.DataFrame(json_).astype({
        "parent": pd.Int64Dtype(),
        "alias": pd.Int64Dtype(),
    })
    return df


def json_save_to_csv(json_, csv_file):
    df = json_to_df(json_)
    df.to_csv(csv_file, index=False)
    return csv_file


def json_save_to_sqlite(json_, sqlite_file):
    sql = sqlite3.connect(sqlite_file)
    df = json_to_df(json_)
    df.to_sql('tags', sql, )

    index_columns = ['id', 'parent', 'type', 'num', 'num_pub', 'views', 'tag', 'tag_jp', 'tag_ru', 'alias']
    for column in index_columns:
        sql.execute(f"CREATE INDEX tags_index_{column} ON tags ({column});").fetchall()

    sql.close()
    return sqlite_file
