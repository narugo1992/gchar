import logging
import os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus

import pandas as pd
from hbutils.system import TemporaryDirectory
from huggingface_hub import hf_hub_download, HfApi
from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from gchar.utils import get_requests_session, srequest


def get_alias_of_keyword(word: str):
    session = get_requests_session()
    resp = srequest(session, 'GET', f'https://www.zerochan.net/{quote_plus(word)}', raise_for_status=False)
    if resp.status_code == 404:
        return []
    else:
        resp.raise_for_status()
    page = pq(resp.text)

    retval = []
    for item in page('#aliases li').items():
        type_ = item('i').text().strip()
        alias_name = item('span').text().strip()
        retval.append((type_, alias_name))

    return retval


def get_alias_table(max_workers: int = 4):
    tags = pd.read_csv(hf_hub_download(
        'deepghs/site_tags',
        filename='zerochan.net/tags.csv',
        repo_type='dataset'
    ))['tag']

    columns = ['alias', 'tag', 'type']
    data = []
    pg = tqdm(total=len(tags))

    def _get_alias(wd):
        for type_, alias_name in get_alias_of_keyword(wd):
            data.append((alias_name, wd, type_))
        pg.update()

    tp = ThreadPoolExecutor(max_workers=max_workers)
    for tag in tags:
        tp.submit(_get_alias, tag)

    tp.shutdown()

    data = [(i, alias, tag, type_) for i, (alias, tag, type_) in enumerate(data)]
    data = sorted(data, key=lambda x: (x[2], x[0]))
    data = [(alias, tag, type_) for i, alias, tag, type_ in data]

    df = pd.DataFrame(columns=columns, data=data)
    return df


def deploy_alias_offline(repository: str = 'deepghs/site_tags', filename: str = 'zerochan.net/alias_offline.csv',
                         max_workers: int = 4):
    logging.info(f'Initializing repository {repository!r} ...')
    hf_client = HfApi(token=os.environ['HF_TOKEN'])
    hf_client.create_repo(repo_id=repository, repo_type='dataset', exist_ok=True)

    with TemporaryDirectory() as td:
        logging.info('Getting aliases ...')
        df = get_alias_table(max_workers)
        csv_file = os.path.join(td, 'alias_offline.csv')
        df.to_csv(csv_file)

        logging.info(f'Uploading file {csv_file!r} to {repository!r} ({filename!r}) ...')
        hf_client.upload_file(
            repo_id=repository,
            repo_type='dataset',
            path_or_fileobj=csv_file,
            path_in_repo=filename,
        )
