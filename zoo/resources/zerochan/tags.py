import sqlite3
import time

import pandas as pd
from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from gchar.utils import get_requests_session, srequest


def crawl_tags_to_json(min_timespan: float = 0.5):
    session = get_requests_session(headers={'User-Agent': 'Tag Crawler - narugo1992'})
    page_no = 1
    data, exist_names = [], set()
    pg = tqdm()
    _last_time = time.time()

    while True:
        time.sleep(max(_last_time + min_timespan - time.time(), 0.0))
        resp = srequest(session, 'GET', 'https://www.zerochan.net/tags', params={
            's': 'count',
            'm': 'details',
            'q': '',
            't': '',
            'p': str(page_no)
        })
        _last_time = time.time()
        resp.raise_for_status()
        page = pq(resp.text)
        active = False
        for row in page('table.tags tr').items():
            if len(row('td')) == 0:
                continue

            type_ = row('td:nth-child(1)').attr('class').strip()
            name = row('td:nth-child(1)').text().strip()
            parent = row('td:nth-child(2)').text().strip()
            total = int(row('td:nth-child(3)').text().replace(',', '').strip())
            strict = int(row('td:nth-child(4)').text().replace(',', '').strip())
            children_count = int(row('td:nth-child(5)').text().replace(',', '').strip())
            parent_count = int(row('td:nth-child(6)').text().replace(',', '').strip())

            if name not in exist_names:
                data.append({
                    'tag': name,
                    'type': type_,
                    'parent': parent,
                    'total': total,
                    'strict': strict,
                    'children_count': children_count,
                    'parent_count': parent_count,
                })
                exist_names.add(name)

            active = True

        if not active:
            break

        page_no += 1
        pg.update()

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
    df.to_sql('tags', sql, )

    index_columns = ['children_count', 'parent', 'parent_count', 'strict', 'tag', 'total', 'type']
    for column in index_columns:
        sql.execute(f"CREATE INDEX tags_index_{column} ON tags ({column});").fetchall()

    sql.close()
    return sqlite_file
