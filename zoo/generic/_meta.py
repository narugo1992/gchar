import copy
import json
import logging
import re
from functools import lru_cache
from itertools import chain
from urllib.parse import quote_plus

from huggingface_hub import hf_hub_download
from orator import DatabaseManager
from unidecode import unidecode


@lru_cache()
def _get_game_all():
    with open(hf_hub_download(
            repo_id='deepghs/generic_character_ds',
            filename='zerochan.net_parents.json',
            repo_type='dataset',
    ), 'r', encoding='utf-8') as f:
        return json.load(f)['data']


@lru_cache()
def _get_character_all():
    with open(hf_hub_download(
            repo_id='deepghs/generic_character_ds',
            filename='zerochan.net.json',
            repo_type='dataset',
    ), 'r', encoding='utf-8') as f:
        return json.load(f)['data']
    pass


@lru_cache()
def _get_pixiv_db():
    db = DatabaseManager({
        'sqlite': {
            'driver': 'sqlite',
            'database': hf_hub_download(
                repo_id='deepghs/site_tags',
                filename='pixiv.net/tags.sqlite',
                repo_type='dataset',
            ),
        }
    })
    db.connection().enable_query_log()
    return db


@lru_cache()
def _get_pixiv_en_db():
    db = DatabaseManager({
        'sqlite': {
            'driver': 'sqlite',
            'database': hf_hub_download(
                repo_id='deepghs/site_tags',
                filename='en.pixiv.net/tags.sqlite',
                repo_type='dataset',
            ),
        }
    })
    db.connection().enable_query_log()
    return db


def _get_names_from_pixiv(all_names):
    logging.info(f'Querying {all_names!r} from pixiv japanese database ...')
    db = _get_pixiv_db()
    query = db.table('tags').select('*')
    or_clause = db.query()
    for p in all_names:
        wds = re.split(r'[\W_]+', p.lower())
        pattern = '%'.join(['', *(wd for wd in wds if wd), ''])
        or_clause = or_clause.or_where(db.raw(f'LOWER(name)'), 'like', pattern)

    query = query.where(or_clause)
    pixiv_names = []
    for item in query.get():
        item_name = re.sub(r'[\W_]+', '', item['name'].lower())
        for p in all_names:
            if item_name == re.sub(r'[\W_]+', '', p.lower()):
                pixiv_names.append((item['name'], item['posts']))
                break

    logging.info(f'Findings: {pixiv_names!r} ...')
    return pixiv_names


def _get_names_from_pixiv_en(all_names):
    logging.info(f'Querying {all_names!r} from pixiv english database ...')
    db = _get_pixiv_en_db()
    query = db.table('tags').select('*')
    or_clause = db.query()
    for p in all_names:
        wds = re.split(r'[\W_]+', p.lower())
        pattern = '%'.join(['', *(wd for wd in wds if wd), ''])
        or_clause = or_clause.or_where(db.raw(f'LOWER(name)'), 'like', pattern)
        or_clause = or_clause.or_where(db.raw(f'LOWER(trans_ja)'), 'like', pattern)

    query = query.where(or_clause)
    pixiv_names = []
    for item in query.get():
        item_name = re.sub(r'[\W_]+', '', item['name'].lower())
        if item['trans_ja']:
            item_name_ja = re.sub(r'[\W_]+', '', item['trans_ja'].lower())
        else:
            item_name_ja = None
        for p in all_names:
            pname = re.sub(r'[\W_]+', '', p.lower())
            if item_name == pname or item_name_ja == pname:
                pixiv_names.append((item['name'], item['trans_ja'], item['posts']))
                break

    jp_db = _get_pixiv_db()
    p_names = []
    for name, trans_ja, posts in pixiv_names:
        records = list(jp_db.table('tags').where('name', trans_ja).get())
        if records:
            posts = records[0]['posts']
        p_names.append((trans_ja, posts))

    logging.info(f'Findings: {p_names!r} ...')
    return p_names


def get_game_info(game_name):
    logging.info(f'Finding game information with name {game_name!r} ...')
    raw_game_name = game_name
    game_name = re.sub(r'[\W_]+', '', unidecode(game_name.lower()))
    for item in _get_game_all():
        names = [item['tag'], *(alias['name'] for alias in item['alias'])]
        for name in names:
            if re.sub(r'[\W_]+', '', unidecode(name.lower())) == game_name:
                return item

    raise ValueError(f'Game name not found - {raw_game_name!r}.')


@lru_cache()
def get_char_info_list(char_name):
    logging.info(f'Finding characters {char_name!r} from zerochan character database ...')
    retval = []
    for item in _get_character_all():
        if item['parent'] == char_name:
            retval.append(item)

    return retval


def get_full_info_for_datasource(game_name):
    g_info = get_game_info(game_name)
    ch_infos = get_char_info_list(g_info['tag'])

    official_name = g_info['tag']
    all_names = [official_name]
    t_names = [official_name]
    for alias in g_info['alias']:
        alias['name'] = alias['name'].strip()
        if alias['type'] in {'english', 'cn', 'ja', 'kr', 'alternative'} \
                and alias['name'] not in all_names:
            all_names.append(alias['name'])
        if alias['type'] in {'english'} and alias['name'] not in t_names:
            t_names.append(alias['name'])

    ch_suffix_records = {}
    for ch in ch_infos:
        for suffix in chain(ch['cnname']['suffixes'], ch['jpname']['suffixes'],
                            ch['krname']['suffixes'], ch['enname']['suffixes']):
            ch_suffix_records[suffix] = ch_suffix_records.get(suffix, 0) + 1

    if ch_suffix_records:
        max_suffix_cnt = max(ch_suffix_records.values())
        if max_suffix_cnt >= 15 or (max_suffix_cnt >= 3 and max_suffix_cnt >= len(ch_infos) * 0.3):
            for name, cnt in ch_suffix_records.items():
                name = name.strip()
                if cnt == max_suffix_cnt:
                    if name not in all_names:
                        all_names.append(name)
                    if name not in t_names:
                        t_names.append(name)

    t_names = [(i, unidecode(name.lower().strip())) for i, name in enumerate(t_names)]
    t_names = sorted(t_names, key=lambda x: (len(x[1]), x[0]))
    _, game_name = t_names[0]
    game_name = re.sub(r'[\W_]+', '', game_name)

    for name in copy.deepcopy(all_names):
        name = unidecode(name).strip()
        if name not in all_names:
            all_names.append(name)

    root_ws = f'https://zerochan.net/{quote_plus(official_name)}'
    all_pixiv_names = {}
    for pixiv_tag, pixiv_cnt in chain(_get_names_from_pixiv(all_names), _get_names_from_pixiv_en(all_names)):
        all_pixiv_names[pixiv_tag] = max(pixiv_cnt, all_pixiv_names.get(pixiv_tag, 0))
    if all_pixiv_names:
        pixiv_keyword, _ = sorted(all_pixiv_names.items(), key=lambda x: (-x[1], x[0]))[0]
    else:
        pixiv_keyword = None
    return game_name, official_name, root_ws, all_names, pixiv_keyword
