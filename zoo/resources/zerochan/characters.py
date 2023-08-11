import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import zhon.cedict
from ditk import logging
from hbutils.system import TemporaryDirectory
from huggingface_hub import hf_hub_download, HfApi
from tqdm.auto import tqdm

from .session import get_zerochan_session
from .tag_aliases import get_info_of_keyword


def _find_jp_words(word):
    return re.findall(u'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]+', word)


def _find_cn_words(word):
    return re.findall(u'[{}]+'.format(zhon.cedict.simp), word)


def _words_check(word):
    _jp_word_list = _find_jp_words(word)
    _cn_word_list = _find_cn_words(word)
    if _jp_word_list and _cn_word_list:
        for _cn_word in _cn_word_list:
            if ''.join(_find_jp_words(_cn_word)) != _cn_word:
                return 'cn'
        for _jp_word in _jp_word_list:
            if ''.join(_find_cn_words(_jp_word)) != _jp_word:
                return 'jp'

        return 'cn'

    elif _jp_word_list:
        return 'jp'
    elif _cn_word_list:
        return 'cn'
    else:
        return None


def _suffix_splitter(name):
    enname_match = re.fullmatch(r'^(?P<name>[^(]+?)\s*\(\s*(?P<suffix>[^)]+?)\s*\)\s*$', name)
    if enname_match:
        return enname_match.group('name'), enname_match.group('suffix')
    else:
        return name, None


def _merge_names(main_name, names, no_space: bool = False):
    names = sorted(names, key=len)
    if main_name:
        names = [main_name, *names]

    _exists = set()
    retval, suffixes = [], []
    for name in names:
        name, suffix = _suffix_splitter(name)
        if no_space:
            name = re.sub(r'\s+', '', name)

        _m_name = re.sub(r'[\W_]+', '', name)
        if _m_name not in _exists:
            retval.append(name)
            _exists.add(_m_name)
        if suffix and suffix not in suffixes:
            suffixes.append(suffix)

    return retval, suffixes


def get_character_list(min_strict: int = 20, max_workers: int = 4):
    tags_df = pd.read_csv(hf_hub_download(
        'deepghs/site_tags',
        filename='zerochan.net/tags.csv',
        repo_type='dataset'
    ))

    session = get_zerochan_session(
        os.environ['ZEROCHAN_USERNAME'],
        os.environ['ZEROCHAN_PASSWORD'],
    )

    all_ch_tags = set(tags_df[tags_df['type'] == 'character']['tag'])
    selected_df = tags_df[(tags_df['type'] == 'character') & (tags_df['strict'] >= min_strict)]
    selected_df = selected_df.sort_values(['strict'], ascending=False)

    retval = []
    pg = tqdm(total=len(selected_df))

    def _get(item):
        if item['parent'] in all_ch_tags:
            pass
        else:
            aliases, tags, desc_md = get_info_of_keyword(item['tag'], session)
            enname, ennames = item['tag'], []
            cnname, cnnames = None, []
            jpname, jpnames = None, []
            krname, krnames = None, []
            alias_names = []
            for type_, alias_name in aliases:
                if type_ in {'cn', 'zh'}:
                    if not cnname:
                        cnname = alias_name
                    else:
                        cnnames.append(alias_name)
                elif type_ == 'jp':
                    if not jpname:
                        jpname = alias_name
                    else:
                        jpnames.append(alias_name)
                elif type_ == 'ko':
                    if not krname:
                        krname = alias_name
                    else:
                        krnames.append(alias_name)
                elif type_ in {'en', 'english'}:
                    ennames.append(alias_name)
                else:
                    _wc = _words_check(alias_name)
                    if _wc == 'cn':
                        cnnames.append(alias_name)
                    elif _wc == 'jp':
                        jpnames.append(alias_name)
                    else:
                        alias_names.append(alias_name)

            ennames, ensuffixes = _merge_names(enname, ennames, no_space=False)
            jpnames, jpsuffixes = _merge_names(jpname, jpnames, no_space=True)
            cnnames, cnsuffixes = _merge_names(cnname, cnnames, no_space=True)
            krnames, krsuffixes = _merge_names(krname, krnames, no_space=True)

            is_male, is_female = False, False
            gender = None
            for type_, tag in tags:
                if type_ == 'theme' and gender is None:
                    if tag == 'Male':
                        is_male = True
                        gender = 'male'
                    if tag == 'Female':
                        is_female = True
                        gender = 'female'
            if is_male and not is_female:
                gender = 'male'
            elif is_female and not is_male:
                gender = 'female'
            else:
                gender = 'unknown'

            retval.append({
                'name': item['tag'],
                'enname': {
                    'names': ennames,
                    'suffixes': ensuffixes,
                },
                'cnname': {
                    'names': cnnames,
                    'suffixes': cnsuffixes,
                },
                'jpname': {
                    'names': jpnames,
                    'suffixes': jpsuffixes,
                },
                'krname': {
                    'names': krnames,
                    'suffixes': krsuffixes,
                },
                'parent': item['parent'],
                'gender': gender,
                'alias': alias_names,
                'total': item['total'],
                'strict': item['strict'],
                'description': desc_md,
                'tags': [
                    {'type': type_, 'tag': tag}
                    for type_, tag in tags
                ],
            })

        pg.update()

    tp = ThreadPoolExecutor(max_workers=max_workers)
    for item in selected_df.to_dict('records'):
        tp.submit(_get, item)

    tp.shutdown()

    retval = sorted(enumerate(retval), key=lambda x: (x[1]['parent'].lower(), -x[1]['strict'], x[0]))
    retval = [item for _, item in retval]

    return retval


def deploy_generic_character_ds(repository: str = 'deepghs/generic_character_ds',
                                filename: str = 'zerochan.net.json',
                                min_strict: int = 5, max_workers: int = 4):
    logging.info(f'Initializing repository {repository!r} ...')
    hf_client = HfApi(token=os.environ['HF_TOKEN'])
    hf_client.create_repo(repo_id=repository, repo_type='dataset', exist_ok=True)

    with TemporaryDirectory() as td:
        logging.info('Getting character information ...')
        data = get_character_list(min_strict, max_workers)
        csv_file = os.path.join(td, 'zerochan.net.json')
        with open(csv_file, 'w', encoding='utf-8') as f:
            json.dump({
                'data': data,
                'last_updated': time.time(),
            }, f, sort_keys=True, indent=4, ensure_ascii=False)

        logging.info(f'Uploading file {csv_file!r} to {repository!r} ({filename!r}) ...')
        hf_client.upload_file(
            repo_id=repository,
            repo_type='dataset',
            path_or_fileobj=csv_file,
            path_in_repo=filename,
        )
