import json
import logging
from functools import lru_cache
from queue import Queue
from typing import Optional, Iterator, Any, List

import requests
from huggingface_hub import hf_hub_download
from requests import JSONDecodeError
from tqdm.auto import tqdm
from waifuc.action import NoMonochromeAction, FaceCountAction, ClassFilterAction
from waifuc.source import ZerochanSource

from gchar.games.base import Character
from ..games.base import GameIndexer


@lru_cache()
def _get_all_characters_data():
    with open(hf_hub_download(
            repo_id='deepghs/generic_character_ds',
            filename='zerochan.net.json',
            repo_type='dataset',
    ), 'r', encoding='utf-8') as f:
        return json.load(f)['data']


@lru_cache()
def _get_all_characters_parent_data():
    with open(hf_hub_download(
            repo_id='deepghs/generic_character_ds',
            filename='zerochan.net_parents.json',
            repo_type='dataset',
    ), 'r', encoding='utf-8') as f:
        return json.load(f)['data']


@lru_cache()
def _parent_tree():
    retval = {}
    for item in _get_all_characters_parent_data():
        if item['parent'] not in retval:
            retval[item['parent']] = []
        retval[item['parent']].append(item['tag'])

    return retval


class ZerochanBasedIndexer(GameIndexer):
    __game_name__ = 'default'
    __official_name__ = 'Default Character'  # Name from zerochan
    __root_website__ = 'https://zerochan.net'  # Game main page from zerochan
    __repository__ = 'deepghs/generic_characters'
    __root_names__: Optional[List[str]] = None
    __max_skins__: int = 5
    __gender_check__: bool = True
    __exclude_cls__: Optional[Character] = None

    @classmethod
    def _get_root_names(cls):
        if cls.__root_names__ is not None:
            return cls.__root_names__
        else:
            return [cls.__official_name__]

    @classmethod
    def _get_all_child_parents(cls):
        q = Queue()
        _exists = set()
        _tree = _parent_tree()
        for root in cls._get_root_names():
            q.put(root)

        while not q.empty():
            root = q.get()
            _exists.add(root)

            if root in _tree:
                for item in _tree[root]:
                    if item not in _exists:
                        q.put(item)

        return _exists

    def _get_skin(self, keyword: str) -> Iterator[dict]:
        source = ZerochanSource(keyword, strict=True, select='full')
        source = source.attach(
            NoMonochromeAction(),
            ClassFilterAction(['illustration', 'bangumi']),
            FaceCountAction(1, level='n'),
        )[:self.__max_skins__]
        for item in tqdm(source, desc=keyword):
            yield {
                'name': f'Zerochan {item.meta["zerochan"]["id"]}',
                'url': item.meta['url'],
            }

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        all_parents = self._get_all_child_parents()
        logging.info(f'All detected parents: {all_parents!r}.')
        all_items = [
            item for item in _get_all_characters_data()
            if item['parent'] in all_parents
        ]
        if self.__gender_check__:
            all_items = [item for item in all_items if item['gender'] in {'male', 'female'}]
        if maxcnt is not None:
            all_items = all_items[:maxcnt]

        for item in tqdm(all_items, desc=self.__official_name__):
            if self.__exclude_cls__ is not None:
                all_names = [
                    *item['enname']['names'],
                    *item['cnname']['names'],
                    *item['jpname']['names'],
                    *item['krname']['names'],
                    *item['alias'],
                ]
                _exists, _exist_ch = False, None
                for _name in all_names:
                    ch = self.__exclude_cls__.get(_name)
                    if ch is not None:
                        _exists, _exist_ch = True, ch
                        break

                if _exists:
                    logging.info(f'Character already exists as {_exist_ch!r}, skipped.')
                    continue

            try:
                skins = list(self._get_skin(item['name']))
            except JSONDecodeError as err:
                logging.warning(repr(err))
                continue

            if not skins:
                logging.warning(f'No skin found for {item!r}, skipped.')
                continue

            yield {
                'ennames': item['enname']['names'],
                'cnnames': item['cnname']['names'],
                'jpnames': item['jpname']['names'],
                'krnames': item['krname']['names'],
                'alias': item['alias'],
                'gender': item['gender'],
                'tags': item['tags'],
                'desc_md': item['description'],
                'skins': skins,
                'total': item['total'],
                'strict': item['strict'],
            }
