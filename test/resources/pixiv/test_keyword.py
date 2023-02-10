import os
from unittest import skipUnless

import pytest

from gchar.resources.pixiv import query_pixiv_illustration_count_by_character, get_pixiv_illustration_count_by_keyword
from gchar.resources.pixiv.session import REMOTE_PIXIV_SESSION_URL


@pytest.mark.unittest
class TestResourcesPixivKeyword:
    def test_query_by_character(self, ch_amiya, ch_slzd):
        all_cnt, r18_cnt = query_pixiv_illustration_count_by_character(ch_amiya)
        assert 12000 <= all_cnt <= 20000
        assert 900 <= r18_cnt <= 1500

        all_cnt, r18_cnt = query_pixiv_illustration_count_by_character('amiya')
        assert 12000 <= all_cnt <= 20000
        assert 900 <= r18_cnt <= 1500

        all_cnt, r18_cnt = query_pixiv_illustration_count_by_character(ch_slzd)
        assert 1000 <= all_cnt <= 2000
        assert 250 <= r18_cnt <= 500

        with pytest.raises(ValueError):
            _ = query_pixiv_illustration_count_by_character('character_not_exist' * 20)

    @pytest.mark.flaky(reruns=40, reruns_delay=15)
    @skipUnless(os.environ.get(REMOTE_PIXIV_SESSION_URL, None), 'Pixiv token required.')
    def test_get_by_keyword(self, ch_amiya, ch_slzd):
        with pytest.warns(UserWarning):
            cnt = get_pixiv_illustration_count_by_keyword(ch_amiya)
        assert 12000 <= cnt <= 20000

        cnt = get_pixiv_illustration_count_by_keyword('アークナイツ')
        assert 180000 <= cnt <= 300000
