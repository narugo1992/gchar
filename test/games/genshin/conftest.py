import os.path
from shutil import copy
from unittest.mock import patch, PropertyMock

import pytest

from gchar.games.genshin import Character
from ...testings import LocalTemporaryDirectory


@pytest.fixture
def no_index_json():
    with LocalTemporaryDirectory() as td:
        json_file = os.path.join(td, 'index.json')
        with patch('gchar.games.genshin.index.Indexer.__class__.index_file',
                   new_callable=PropertyMock(return_value=json_file)):
            yield json_file


@pytest.fixture
def exist_index_json():
    with LocalTemporaryDirectory() as td:
        dstfile = os.path.join(td, 'index.json')
        from gchar.games.genshin.index import INDEXER

        if os.path.exists(INDEXER.__class__.index_file):
            copy(INDEXER.__class__.index_file, dstfile)
        with patch('gchar.games.genshin.index.Indexer.__class__.index_file',
                   new_callable=PropertyMock(return_value=dstfile)):
            yield


@pytest.fixture()
def genshin_keqing() -> Character:
    return Character.get('keqing')


@pytest.fixture()
def genshin_yoimiya() -> Character:
    return Character.get('よいみや')


@pytest.fixture()
def genshin_zhongli() -> Character:
    return Character.get('鍾離')
