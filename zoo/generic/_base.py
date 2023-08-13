import json
import logging
from functools import lru_cache
from typing import Optional, Iterator, Any

import requests
from huggingface_hub import hf_hub_download
from requests import JSONDecodeError
from tqdm.auto import tqdm
from waifuc.action import NoMonochromeAction, FaceCountAction, ClassFilterAction
from waifuc.source import ZerochanSource

from ..games.base import GameIndexer


@lru_cache()
def _get_all_characters_data():
    with open(hf_hub_download(
            repo_id='deepghs/generic_character_ds',
            filename='zerochan.net.json',
            repo_type='dataset',
    ), 'r', encoding='utf-8') as f:
        return json.load(f)['data']


class ZerochanBasedIndexer(GameIndexer):
    __game_name__ = 'default'
    __official_name__ = 'Default Character'  # Name from zerochan
    __root_website__ = 'https://zerochan.net'  # Game main page from zerochan
    __repository__ = 'deepghs/generic_characters'
    __max_skins__: int = 5
    __gender_check__: bool = True

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
        all_items = [
            item for item in _get_all_characters_data()
            if item['parent'] == self.__official_name__
        ]
        if self.__gender_check__:
            all_items = [item for item in all_items if item['gender'] in {'male', 'female'}]
        if maxcnt is not None:
            all_items = all_items[:maxcnt]

        for item in tqdm(all_items, desc=self.__official_name__):
            try:
                skins = list(self._get_skin(item['name']))
            except JSONDecodeError as err:
                logging.warning(repr(err))
                continue

            if skins:
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
            else:
                logging.warning(f'No skin found for {item!r}, skipped.')
