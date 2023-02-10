import os
import time
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

    @skipUnless(os.environ.get(REMOTE_PIXIV_SESSION_URL, None), 'Pixiv token required.')
    def test_get_by_keyword(self, ch_amiya, ch_slzd):
        for i in range(5):
            with pytest.warns(UserWarning):
                cnt = get_pixiv_illustration_count_by_keyword(ch_amiya)
            if cnt == 0:
                time.sleep(10.0)
                continue
            else:
                assert 12000 <= cnt <= 20000
                break
        else:
            assert False, f'Max try exceed for pixiv api - {ch_amiya!r}.'

        for i in range(5):
            cnt = get_pixiv_illustration_count_by_keyword('アークナイツ')
            if cnt == 0:
                time.sleep(10.0)
                continue
            else:
                assert 180000 <= cnt <= 300000
                break
        else:
            assert False, 'Max try exceed for pixiv api - \'アークナイツ\'.'
