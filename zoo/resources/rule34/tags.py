import json
import sqlite3

import pandas as pd
import xmltodict
from tqdm.auto import tqdm

from gchar.utils import get_requests_session, srequest


def crawl_tags_to_json(site_root: str = 'https://rule34.xxx'):
    session = get_requests_session(headers={
        'Content-Type': 'application/json; charset=utf-8',
    })
    data, exist_ids = [], set()
    pg = tqdm()

    page_no = 0
    while True:
        resp = srequest(session, 'GET', f'{site_root}/index.php', params={
            'page': 'dapi',
            's': 'tag',
            'q': 'index',
            'json': '1',
            'limit': '100',
            'pid': str(page_no),
        })
        resp.raise_for_status()

        json_data = xmltodict.parse(resp.text)
        if 'tags' not in json_data or 'tag' not in json_data['tags']:
            break
        tags = json_data['tags']['tag']
        if not tags:
            break

        for item in tags:
            item = {key.lstrip('@'): value for key, value in item.items()}
            item['id'] = int(item['id'])
            item['type'] = int(item['type'])
            item['count'] = int(item['count'])
            item['ambiguous'] = json.loads(item['ambiguous'])
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
