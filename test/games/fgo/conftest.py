import os.path
from shutil import copy
from unittest.mock import patch

import pytest

from gchar.games.fgo import Character
from ...testings import LocalTemporaryDirectory


@pytest.fixture
def no_index_json():
    with LocalTemporaryDirectory() as td:
        json_file = os.path.join(td, 'index.json')
        with patch('gchar.games.fgo.index._INDEX_FILE', json_file):
            yield json_file


@pytest.fixture
def exist_index_json():
    with LocalTemporaryDirectory() as td:
        dstfile = os.path.join(td, 'index.json')
        from gchar.games.fgo.index import _INDEX_FILE
        if os.path.exists(_INDEX_FILE):
            copy(_INDEX_FILE, dstfile)
        with patch('gchar.games.fgo.index._INDEX_FILE', dstfile):
            yield


@pytest.fixture()
def fgo_mashu():
    return Character.get('学妹')


@pytest.fixture()
def fgo_saber():
    return Character.get(2)


@pytest.fixture()
def fgo_altria_caster():
    return Character.get(284)


@pytest.fixture()
def fgo_saber_l():
    return Character.get(119)


@pytest.fixture()
def fgo_saber_a():
    return Character.get(129)


@pytest.fixture()
def fgo_elf_gawain():
    return Character.get(310)


@pytest.fixture()
def fgo_elf_tristan():
    return Character.get(311)


@pytest.fixture()
def fgo_elf_lancelot():
    return Character.get(312)


@pytest.fixture()
def fgo_shihuangdi():
    return Character.get('始皇帝')
