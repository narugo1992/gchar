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

    @skipUnless(OS.linux, 'Linux required.')
    @pytest.mark.parametrize(['game', 'cnt'], [
        ('arknights', 878),
        ('fgo', 2011),
        ('azurlane', 1799),
        ('genshin', 472),
        ('girlsfrontline', 1113),
    ])
    def test_update(self, no_tags_json, game, cnt):
        result = simulate_entry(cli, ['gchar.resources.danbooru', 'update', '-g', game])
        assert result.exitcode == 0, f'Exitcode is {result.exitcode}.{os.linesep}' \
                                     f'This is stdout:{os.linesep}{result.stdout}{os.linesep}' \
                                     f'This is stderr:{os.linesep}{result.stderr}{os.linesep}'
        assert os.path.exists(os.path.join(no_tags_json, game, 'danbooru_tags.json'))
        with open(os.path.join(no_tags_json, game, 'danbooru_tags.json'), 'r') as f:
            data = json.load(f)
            assert 'tags' in data
            assert isinstance(data['tags'], list)
            assert len(data['tags']) >= cnt

    @skipUnless(OS.linux, 'Linux required.')
    @pytest.mark.parametrize(['game', 'cnt'], [
        ('arknights', 878),
        ('fgo', 2011),
        ('azurlane', 1799),
        ('genshin', 472),
        ('girlsfrontline', 1113),
    ])
    def test_download(self, no_tags_json, game, cnt):
        result = simulate_entry(cli, ['gchar.resources.danbooru', 'download', '-g', game])
        assert result.exitcode == 0, f'Exitcode is {result.exitcode}.{os.linesep}' \
                                     f'This is stdout:{os.linesep}{result.stdout}{os.linesep}' \
                                     f'This is stderr:{os.linesep}{result.stderr}{os.linesep}'
        assert os.path.exists(os.path.join(no_tags_json, game, 'danbooru_tags.json'))
        with open(os.path.join(no_tags_json, game, 'danbooru_tags.json'), 'r') as f:
            data = json.load(f)
            assert 'tags' in data
            assert isinstance(data['tags'], list)
            assert len(data['tags']) >= cnt
