import json
import os
from unittest import skipUnless

import pytest
from hbutils.testing import simulate_entry, OS

from gchar.config.meta import __VERSION__
from gchar.resources.danbooru.__main__ import cli


@pytest.mark.unittest
class TestResourcesDanbooruMain:
    def test_version(self):
        result = simulate_entry(cli, ['gchar.resources.danbooru', '-v'])
        assert result.exitcode == 0
        assert __VERSION__ in result.stdout
        assert 'danbooru' in result.stdout

    @skipUnless(not OS.windows, 'Non-windows required.')
    @pytest.mark.parametrize(['game'], [
        ('fgo',),
    ])
    def test_update(self, no_tags_json, game):
        result = simulate_entry(cli, ['gchar.resources.danbooru', 'update', '-g', game])
        assert result.exitcode == 0, f'Exitcode is {result.exitcode}.{os.linesep}' \
                                     f'This is stdout:{os.linesep}{result.stdout}{os.linesep}' \
                                     f'This is stderr:{os.linesep}{result.stderr}{os.linesep}'
        assert os.path.exists(os.path.join(no_tags_json, game, 'danbooru_tags.json'))
        with open(os.path.join(no_tags_json, game, 'danbooru_tags.json'), 'r') as f:
            data = json.load(f)
            assert 'tags' in data
            assert isinstance(data['tags'], list)
            assert len(data['tags']) >= 5
