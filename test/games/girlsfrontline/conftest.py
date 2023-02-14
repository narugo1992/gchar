import os.path
from shutil import copy
from unittest.mock import patch, PropertyMock

import pytest

from gchar.games.girlsfrontline import Character
from ...testings import LocalTemporaryDirectory


@pytest.fixture
def no_index_json():
    with LocalTemporaryDirectory() as td:
        json_file = os.path.join(td, 'index.json')
        with patch('gchar.games.girlsfrontline.index.Indexer.__INDEX_FILE__',
                   new_callable=PropertyMock(return_value=json_file)):
            yield json_file


@pytest.fixture
def exist_index_json():
    with LocalTemporaryDirectory() as td:
        dstfile = os.path.join(td, 'index.json')
        from gchar.games.girlsfrontline.index import INDEXER
        if os.path.exists(INDEXER.__class__.index_file):
            copy(INDEXER.__class__.index_file, dstfile)
        with patch('gchar.games.girlsfrontline.index.Indexer.__INDEX_FILE__', dstfile):
            yield


@pytest.fixture()
def gfl_grizzly():
    return Character.get(96)


@pytest.fixture()
def gfl_a416():
    return Character.get(1029)


@pytest.fixture()
def gfl_bronya():
    return Character.get(1005)
