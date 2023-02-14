import os.path
from shutil import copy
from unittest.mock import patch

import pytest

from gchar.games.azurlane import Character
from ...testings import LocalTemporaryDirectory


@pytest.fixture
def no_index_json():
    with LocalTemporaryDirectory() as td:
        json_file = os.path.join(td, 'index.json')
        with patch('gchar.games.azurlane.index.Indexer.__INDEX_FILE__', json_file):
            yield json_file


@pytest.fixture
def exist_index_json():
    with LocalTemporaryDirectory() as td:
        dstfile = os.path.join(td, 'index.json')
        from gchar.games.azurlane.index import INDEXER
        if os.path.exists(INDEXER.__class__.index_file):
            copy(INDEXER.__class__.index_file, dstfile)
        with patch('gchar.games.azurlane.index.Indexer.__INDEX_FILE__', dstfile):
            yield


@pytest.fixture()
def azl_new_jersey():
    return Character.get('068')


@pytest.fixture()
def azl_maury():
    return Character.get('010')


@pytest.fixture()
def azl_fuso_meta():
    return Character.get('META005')


@pytest.fixture()
def azl_san_diego_refit():
    return Character.get('圣地亚哥.改')


@pytest.fixture()
def azl_gascogne_mu():
    return Character.get('418')


@pytest.fixture()
def azl_hiei_chan():
    return Character.get('383')


@pytest.fixture()
def azl_u556():
    return Character.get('386')


@pytest.fixture()
def azl_azuma():
    return Character.get('Plan010')
