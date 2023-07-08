import os
from unittest import skipUnless

import pytest

from gchar.resources.pixiv import get_pixiv_posts, get_pixiv_illustration_count_by_keyword
from gchar.resources.pixiv.session import REMOTE_PIXIV_SESSION_INDEX_URL


@pytest.mark.unittest
class TestResourcesPixivKeyword:
    def test_query_by_character(self, ch_amiya, ch_slzd):
        all_cnt, r18_cnt = get_pixiv_posts(ch_amiya)
        assert 12000 <= all_cnt <= 20000
        assert 900 <= r18_cnt <= 1500

        all_cnt, r18_cnt = get_pixiv_posts('amiya')
        assert 12000 <= all_cnt <= 20000
        assert 900 <= r18_cnt <= 1500

        all_cnt, r18_cnt = get_pixiv_posts(ch_slzd)
        assert 1000 <= all_cnt <= 2000
        assert 250 <= r18_cnt <= 500

        with pytest.raises(ValueError):
            _ = get_pixiv_posts('character_not_exist' * 20)

    # @pytest.mark.flaky(reruns=40, reruns_delay=15)
    @skipUnless(os.environ.get(REMOTE_PIXIV_SESSION_INDEX_URL, None), 'Pixiv token required.')
    def test_get_by_keyword(self, ch_amiya, ch_slzd, pixiv_mock):
        with pytest.warns(UserWarning):
            _ = get_pixiv_illustration_count_by_keyword(ch_amiya)
        _ = get_pixiv_illustration_count_by_keyword('アークナイツ')
