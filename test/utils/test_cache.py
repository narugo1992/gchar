import os
from unittest.mock import patch

import pytest

from gchar.utils import optional_lru_cache


@pytest.mark.unittest
class TestUtilsCache:
    def test_optional_lru_cache(self):
        cnt = 0

        @optional_lru_cache()
        def _cache_func():
            nonlocal cnt
            cnt += 1
            return cnt

        with patch.dict(os.environ, {'NO_CACHE': '1'}):
            assert _cache_func() == 1
            assert _cache_func() == 2
            assert _cache_func() == 3

        with patch.dict(os.environ, {'NO_CACHE': ''}):
            assert _cache_func() == 4
            assert _cache_func() == 4
            assert _cache_func() == 4

        with patch.dict(os.environ, {'NO_CACHE': '1'}):
            assert _cache_func() == 5
            assert _cache_func() == 6
            assert _cache_func() == 7

        with patch.dict(os.environ, {'NO_CACHE': ''}):
            assert _cache_func() == 4
            assert _cache_func() == 4
            assert _cache_func() == 4
