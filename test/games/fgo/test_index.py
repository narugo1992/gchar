import pytest

from gchar.games.fgo import get_index
from gchar.games.fgo.index import _local_is_ready


@pytest.mark.unittest
class TestGamesFgoIndex:
    def test_get_index(self):
        index = get_index()
        cnnames = [item['cnnames'][0] for item in index]
        assert '玛修·基列莱特' in cnnames
        assert '阿尔托莉雅·卡斯特' in cnnames

    def test_get_index_last_updated_at_no_index_json(self, no_index_json):
        assert not _local_is_ready()
