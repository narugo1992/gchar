import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from hbutils.string import plural_word
from tqdm.auto import tqdm

from gchar.utils import get_requests_session, srequest


def crawl_tags_to_json(limit: int = 100):
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

    # username = os.environ['SANKAKU_USERNAME']
    # password = os.environ['SANKAKU_PASSWORD']
    # resp = srequest(session, 'POST', 'https://login.sankakucomplex.com/auth/token',
    #                 json={"login": username, "password": password})
    # resp.raise_for_status()
    # login_data = resp.json()
    # session.headers.update({
    #     "Authorization": f"{login_data['token_type']} {login_data['access_token']}",
    # })

    def _check_page(p):
        resp = srequest(session, 'GET', 'https://capi-v2.sankakucomplex.com/tags', params={
            'lang': 'en',
            'page': str(p),
            'limit': str(limit),
        })
        resp.raise_for_status()
        return len(resp.json()) > 0

    l, r = 1024, 2048
    while True:
        if _check_page(r):
            l, r = l << 1, r << 1
            print(f'Left: {l}, right: {r}')
        else:
            break

    while l < r:
        m = (l + r + 1) // 2
        if _check_page(m):
            l = m
        else:
            r = m - 1
        print(f'Left: {l}, right: {r}')

    pages = l
    print(f'{plural_word(pages, "page")} found in total.')

    data, _exist_ids = [], set()
    pg_page = tqdm(total=pages, desc='Pages')
    pg_tags = tqdm(desc='Tags')

    def _process_page(p):
        resp = srequest(session, 'GET', 'https://capi-v2.sankakucomplex.com/tags', params={
            'lang': 'en',
            'page': str(p),
            'limit': str(limit),
        })
        resp.raise_for_status()

        for item in resp.json():
            if item['id'] in _exist_ids:
                continue

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
            pg_tags.update()

        pg_page.update()

    tp = ThreadPoolExecutor(max_workers=12)
    for i in range(1, pages + 1):
        tp.submit(_process_page, i)

    tp.shutdown()

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
    df['parent_ids'] = df['parent_ids'].apply(json.dumps).astype(str)
    df['child_ids'] = df['child_ids'].apply(json.dumps).astype(str)
    df['related_ids'] = df['related_ids'].apply(json.dumps).astype(str)
    df.to_sql('tags', sql)
    index_columns = ['id', 'name', 'type', 'post_count', 'pool_count', 'series_count', 'rating']
    for column in index_columns:
        sql.execute(f"CREATE INDEX tags_index_{column} ON tags ({column});").fetchall()

    parent_items = []
    child_items = []
    related_items = []
    for item in json_:
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
