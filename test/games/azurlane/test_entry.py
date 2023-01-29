import json
import os
from unittest import skipUnless

import pytest
from hbutils.testing import simulate_entry

from gchar.config.meta import __VERSION__
from gchar.games.azurlane.__main__ import cli


@pytest.mark.unittest
class TestGamesAzurlaneEntry:
    def test_version(self):
        result = simulate_entry(cli, ['gchar.games.azurlane', '-v'])
        assert result.exitcode == 0
        assert __VERSION__ in result.stdout
        assert 'azurlane' in result.stdout

    def test_update_full_5(self, no_index_json):
        result = simulate_entry(cli, ['gchar.games.azurlane', 'update', '-n', '5'])
        assert result.exitcode == 0, f'Exitcode is {result.exitcode}.{os.linesep}' \
                                     f'This is stdout:{os.linesep}{result.stdout}{os.linesep}' \
                                     f'This is stderr:{os.linesep}{result.stderr}{os.linesep}'
        assert os.path.exists(no_index_json)
        with open(no_index_json, 'r') as f:
            data = json.load(f)
            assert 'data' in data
            assert isinstance(data['data'], list)
            assert len(data['data']) == 5

    @skipUnless(os.environ.get('RUN_CRAWLER'), 'Env \'RUN_CRAWLER\' required.')
    @pytest.mark.timeout(1800)
    def test_update_full(self, no_index_json):
        result = simulate_entry(cli, ['gchar.games.azurlane', 'update'])
        assert result.exitcode == 0, f'Exitcode is {result.exitcode}.{os.linesep}' \
                                     f'This is stdout:{os.linesep}{result.stdout}{os.linesep}' \
                                     f'This is stderr:{os.linesep}{result.stderr}{os.linesep}'
        assert os.path.exists(no_index_json)
        with open(no_index_json, 'r') as f:
            data = json.load(f)
            assert 'data' in data
            assert isinstance(data['data'], list)
            assert len(data['data']) > 800