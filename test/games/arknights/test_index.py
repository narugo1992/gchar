import os
from unittest import skipUnless

import pytest

from gchar.games.arknights.index import get_index, _local_is_ready


@pytest.mark.unittest
class TestGamesArknightsIndex:
    def test_get_index(self):
        index = get_index()
        cnnames = [item['data']['data-cn'] for item in index]
        assert '阿米娅' in cnnames
        assert '凯尔希' in cnnames
        assert '龙舌兰' in cnnames
        assert '银灰' in cnnames

    @skipUnless(os.environ.get('RUN_INDEX'), 'Env \'RUN_INDEX\' required.')
    @pytest.mark.timeout(900)
    def test_get_index_with_refresh(self, no_index_json):
        index = get_index()
        cnnames = [item['data']['data-cn'] for item in index]
        assert '阿米娅' in cnnames
        assert '凯尔希' in cnnames
        assert '龙舌兰' in cnnames
        assert '银灰' in cnnames

    def test_get_index_last_updated_at_no_index_json(self, no_index_json):
        assert not _local_is_ready()
