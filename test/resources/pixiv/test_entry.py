import json
import os
from unittest import skipUnless

import pytest
from hbutils.testing import simulate_entry, OS

from gchar.config.meta import __VERSION__
from gchar.resources.pixiv.__main__ import cli
from gchar.resources.pixiv.session import REMOTE_PIXIV_SESSION_URL


@pytest.mark.unittest
class TestResourcesPixivMain:
    def test_version(self):
        result = simulate_entry(cli, ['gchar.resources.pixiv', '-v'])
        assert result.exitcode == 0
        assert __VERSION__ in result.stdout
        assert 'pixiv' in result.stdout

    @skipUnless(os.environ.get(REMOTE_PIXIV_SESSION_URL, None), 'Pixiv token required.')
    @skipUnless(not OS.windows, 'Non-windows required.')
    @pytest.mark.flaky(reruns=5, reruns_delay=10)
    @pytest.mark.parametrize(['game', 'min_cnt', 'max_cnt'], [
        ('arknights', 3, 5),
        ('fgo', 2, 5),
        ('azurlane', 3, 5),
        ('genshin', 3, 5),
        ('girlsfrontline', 2, 5),
    ])
    def test_names(self, no_tags_json, game, min_cnt, max_cnt):
        result = simulate_entry(cli, [
            'gchar.resources.pixiv', 'names', '-g', game,
            '--maxcnt', '5', '--sleep_every', '2', '--sleep_time', '1.3',
        ])
        assert result.exitcode == 0, f'Exitcode is {result.exitcode}.{os.linesep}' \
                                     f'This is stdout:{os.linesep}{result.stdout}{os.linesep}' \
                                     f'This is stderr:{os.linesep}{result.stderr}{os.linesep}'

        json_file = os.path.join(no_tags_json, game, 'pixiv_names.json')
        assert os.path.exists(json_file)
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert min_cnt <= len(data['names']) <= max_cnt

    @skipUnless(os.environ.get(REMOTE_PIXIV_SESSION_URL, None), 'Pixiv token required.')
    @skipUnless(not OS.windows, 'Non-windows required.')
    @pytest.mark.parametrize(['game'], [
        ('arknights',),
        ('fgo',),
        ('azurlane',),
        ('genshin',),
        ('girlsfrontline',),
    ])
    def test_characters(self, no_tags_json, game):
        result = simulate_entry(cli, [
            'gchar.resources.pixiv', 'characters', '-g', game,
            '--maxcnt', '5', '--sleep_every', '2', '--sleep_time', '1.3',
        ])
        assert result.exitcode == 0, f'Exitcode is {result.exitcode}.{os.linesep}' \
                                     f'This is stdout:{os.linesep}{result.stdout}{os.linesep}' \
                                     f'This is stderr:{os.linesep}{result.stderr}{os.linesep}'

        json_file = os.path.join(no_tags_json, game, 'pixiv_characters.json')
        assert os.path.exists(json_file)
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data['characters']) == 5
