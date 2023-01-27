import os.path
from shutil import copy
from unittest.mock import patch

import pytest

from gchar.games.girlsfrontline import Character
from ...testings import LocalTemporaryDirectory


@pytest.fixture
def no_index_json():
    with LocalTemporaryDirectory() as td:
        json_file = os.path.join(td, 'index.json')
        with patch('gchar.games.girlsfrontline.index._INDEX_FILE', json_file):
            yield json_file


@pytest.fixture
def exist_index_json():
    with LocalTemporaryDirectory() as td:
        dstfile = os.path.join(td, 'index.json')
        from gchar.games.girlsfrontline.index import _INDEX_FILE
        if os.path.exists(_INDEX_FILE):
            copy(_INDEX_FILE, dstfile)
        with patch('gchar.games.girlsfrontline.index._INDEX_FILE', dstfile):
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
