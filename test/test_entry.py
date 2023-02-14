import os
from contextlib import contextmanager
from unittest.mock import patch

import pytest
from hbutils.testing import simulate_entry

from gchar.__main__ import cli, GAMES
from gchar.config.meta import __VERSION__
from .testings import LocalTemporaryDirectory


@pytest.fixture()
def no_local_data():
    def _nested_mock(layer: int = 0):
        if layer >= len(GAMES):
            yield
        else:
            json_file = os.path.join(td, GAMES[layer], 'index.json')
            with patch(f'gchar.games.{GAMES[layer]}.index.Indexer.__INDEX_FILE__', json_file):
                yield from _nested_mock(layer + 1)

    @contextmanager
    def _nested_game_character_mock():
        yield from _nested_mock(0)

    with LocalTemporaryDirectory() as td:
        for game in GAMES:
            os.makedirs(os.path.join(td, game), exist_ok=True)

        with _nested_game_character_mock(), patch('gchar.resources.danbooru.index._GAMES_DIRECTORY', td):
            yield td


@pytest.mark.unittest
class TestMain:
    def test_version(self):
        result = simulate_entry(cli, ['gchar', '-v'])
        assert result.exitcode == 0
        assert __VERSION__ in result.stdout
        assert 'gchar' in result.stdout.lower()

    @pytest.mark.parametrize(['game', ], [(item,) for item in GAMES])
    def test_update(self, no_local_data, game):
        result = simulate_entry(cli, ['gchar', 'update', '-g', game])
        assert result.exitcode == 0, f'Exitcode is {result.exitcode}.{os.linesep}' \
                                     f'This is stdout:{os.linesep}{result.stdout}{os.linesep}' \
                                     f'This is stderr:{os.linesep}{result.stderr}{os.linesep}'
        assert os.path.exists(os.path.join(no_local_data, game, 'danbooru_tags.json')), \
            f"This is the files here: {os.listdir(os.path.join(no_local_data, game))}"
        assert os.path.exists(os.path.join(no_local_data, game, 'index.json')), \
            f"This is the files here: {os.listdir(os.path.join(no_local_data, game))}"

    def test_update_all(self, no_local_data):
        result = simulate_entry(cli, ['gchar', 'update'])
        assert result.exitcode == 0, f'Exitcode is {result.exitcode}.{os.linesep}' \
                                     f'This is stdout:{os.linesep}{result.stdout}{os.linesep}' \
                                     f'This is stderr:{os.linesep}{result.stderr}{os.linesep}'
        for game in GAMES:
            assert os.path.exists(os.path.join(no_local_data, game, 'danbooru_tags.json')), \
                f"This is the files here: {os.listdir(os.path.join(no_local_data, game))}"
            assert os.path.exists(os.path.join(no_local_data, game, 'index.json')), \
                f"This is the files here: {os.listdir(os.path.join(no_local_data, game))}"
