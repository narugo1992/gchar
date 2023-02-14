import os.path
from shutil import copy
from unittest.mock import patch

import pytest

from ...testings import LocalTemporaryDirectory


@pytest.fixture
def no_index_json():
    with LocalTemporaryDirectory() as td:
        json_file = os.path.join(td, 'index.json')
        with patch('gchar.games.arknights.index.Indexer.__INDEX_FILE__', json_file):
            yield json_file


@pytest.fixture
def exist_index_json():
    with LocalTemporaryDirectory() as td:
        dstfile = os.path.join(td, 'index.json')
        from gchar.games.arknights.index import INDEXER
        if os.path.exists(INDEXER.__class__.index_file):
            copy(INDEXER.__class__.index_file, dstfile)
        with patch('gchar.games.arknights.index.Indexer.__INDEX_FILE__', dstfile):
            yield
