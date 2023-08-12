import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory

from huggingface_hub import hf_hub_download, HfApi
from orator import DatabaseManager
from tqdm.auto import tqdm

from gchar.utils import get_requests_session
from .session import get_zerochan_session
from .tag_aliases import get_info_of_keyword


def list_parent_tags(min_strict: int = 3, min_character_count: int = 5, max_workers: int = 4):
    db_file = hf_hub_download(
        'deepghs/site_tags',
        filename='zerochan.net/tags.sqlite',
        repo_type='dataset'
    )
    db = DatabaseManager({
        'sqlite': {
            'driver': 'sqlite',
            'database': db_file,
        }
    })
    db.connection().enable_query_log()

    all_parents = list(db.table('tags').where_in('type', ['game', 'series']).select('tag', 'type').get())
    all_values = [item['tag'] for item in all_parents]
    all_types = {item['tag']: item['type'] for item in all_parents}

    if 'ZEROCHAN_USERNAME' in os.environ and 'ZEROCHAN_PASSWORD' in os.environ:
        session = get_zerochan_session(
            os.environ['ZEROCHAN_USERNAME'],
            os.environ['ZEROCHAN_PASSWORD'],
        )
    else:
        session = get_requests_session()
    all_items = db.table('tags') \
        .where('type', 'character') \
        .where('strict', '>=', min_strict) \
        .where_in('parent', all_values) \
        .group_by('parent') \
        .select(db.raw('parent as tag, count(*) as character_count, sum(strict) as total_strict')) \
        .having('character_count', '>=', min_character_count) \
        .order_by('character_count', 'desc').get()
    all_items = list(all_items)
    retval = []
    pg = tqdm(total=len(all_items))

    def _get_info(item_):
        alias_items, tags_items, desc_md = get_info_of_keyword(item_['tag'], session)
        item_['alias'] = [
            {'type': type_, 'name': alias_name}
            for type_, alias_name in alias_items
        ]
        item_['tags'] = [
            {'type': type_, 'name': tag}
            for type_, tag in tags_items
        ]
        item_['desc_md'] = desc_md
        retval.append(item_)
        pg.update()

    tp = ThreadPoolExecutor(max_workers=max_workers)
    for item in all_items:
        item['type'] = all_types[item['tag']]
        tp.submit(_get_info, item)

    tp.shutdown()
    retval = sorted(retval, key=lambda x: (-x['character_count'], x['tag']))
    return retval


def deploy_generic_character_ds_parent(repository: str = 'deepghs/generic_character_ds',
                                       filename: str = 'zerochan.net_parent.json',
                                       min_strict: int = 3, min_character_count: int = 5,
                                       max_workers: int = 4):
    logging.info(f'Initializing repository {repository!r} ...')
    hf_client = HfApi(token=os.environ['HF_TOKEN'])
    hf_client.create_repo(repo_id=repository, repo_type='dataset', exist_ok=True)

    with TemporaryDirectory() as td:
        logging.info('Getting character parents information ...')
        data = list_parent_tags(min_strict, min_character_count, max_workers)
        json_file = os.path.join(td, 'zerochan.net_parent.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'data': data,
                'last_updated': time.time(),
            }, f, sort_keys=True, indent=4, ensure_ascii=False)

        logging.info(f'Uploading file {json_file!r} to {repository!r} ({filename!r}) ...')
        hf_client.upload_file(
            repo_id=repository,
            repo_type='dataset',
            path_or_fileobj=json_file,
            path_in_repo=filename,
        )
