from unittest.mock import patch

import pytest

from gchar.games import get_character
from ...testings import LocalTemporaryDirectory


@pytest.fixture
def no_tags_json():
    with LocalTemporaryDirectory() as td:
        with patch('gchar.resources.pixiv.games._GAMES_DIRECTORY', td):
            yield td


@pytest.fixture()
def ch_amiya():
    return get_character('amiya')


@pytest.fixture()
def ch_slzd():
    return get_character('山鲁佐德')
