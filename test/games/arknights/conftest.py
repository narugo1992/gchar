import os.path
from shutil import copy
from unittest.mock import patch

import pytest

from ...testings import LocalTemporaryDirectory


@pytest.fixture
def no_index_json():
    with LocalTemporaryDirectory() as td:
        with patch('gchar.games.arknights.index._INDEX_FILE', os.path.join(td, 'index.json')):
            yield


@pytest.fixture
def exist_index_json():
    with LocalTemporaryDirectory() as td:
        dstfile = os.path.join(td, 'index.json')
        from gchar.games.arknights.index import _INDEX_FILE
        if os.path.exists(_INDEX_FILE):
            copy(_INDEX_FILE, dstfile)
        with patch('gchar.games.arknights.index._INDEX_FILE', dstfile):
            yield
