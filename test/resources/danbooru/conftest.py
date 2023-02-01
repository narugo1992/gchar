from unittest.mock import patch

import pytest

from ...testings import LocalTemporaryDirectory


@pytest.fixture
def no_tags_json():
    with LocalTemporaryDirectory() as td:
        with patch('gchar.resources.danbooru.index._GAMES_DIRECTORY', td):
            yield td
