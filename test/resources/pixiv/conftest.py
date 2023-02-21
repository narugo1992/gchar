import json
import random
import re
from contextlib import contextmanager
from functools import lru_cache
from unittest.mock import patch

import pytest
import responses
from hbutils.random import random_hex_digits
from responses.matchers import query_string_matcher

from gchar.games import get_character
from ...testings import LocalTemporaryDirectory


@pytest.fixture
def no_tags_json():
    with LocalTemporaryDirectory() as td:
        with patch('gchar.resources.pixiv.games._GAMES_DIRECTORY', td):
            yield td


@pytest.fixture()
def ch_amiya():
    return get_character('amiya')


@pytest.fixture()
def ch_slzd():
    return get_character('山鲁佐德')


@contextmanager
def mock_pixiv_site(total_count: int = None, zero_probability: float = 0.15):
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add_passthru(re.compile(r'[\S\s]+'))
        rsps.get(
            'https://www.pixiv.net/rpc/notify_count.php',
            status=200,
            json={'popboard': 0},
            match=[
                query_string_matcher('op=count_unread&lang=zh&version=9c834eede9446d61102731a4be356cd0f1090e84'),
            ]
        )

        @lru_cache()
        def _query_for_word(word, **kwargs):
            splitted_words = list(filter(bool, re.split(r'([()\s]+|[()\s]+OR[()\s]+)', word)))

            def _create_tags():
                matched_word = [
                    wd if random.randint(0, 100) < 90 else
                    f'{random_hex_digits(random.randint(0, 5))}{wd}{random_hex_digits(random.randint(0, 5))}'
                    for wd in splitted_words
                ]
                tags = [random_hex_digits(random.randint(3, 18)) for _ in range(random.randint(5, 13))]
                tags.extend(matched_word)
                random.shuffle(tags)
                while (len(tags) > 10 or random.randint(0, 100) < 50) and len(tags) > 1:
                    first, second, *remains = tags
                    tags = [random.choice('()[]|/, `').join((first, second)), *remains]
                    random.shuffle(tags)

                return tags

            if total_count is not None:
                cnt = total_count
            else:
                cnt = 0 if random.random() < zero_probability else random.randint(20, 6000)
            return {
                'body': {
                    "illustManga": {
                        'total': cnt,
                        'data': [{
                            'tags': _create_tags(),
                        } for _ in range(min(cnt, 60))]
                    }
                }
            }

        def _list_query(request):
            return 200, {}, json.dumps(_query_for_word(**request.params))

        rsps.add_callback(
            responses.GET,
            re.compile(r'^https://www.pixiv.net/ajax/search/artworks/[^/]+?$'),
            callback=_list_query,
        )

        yield rsps


@pytest.fixture(scope="module")
def pixiv_mock():
    with mock_pixiv_site() as rsps:
        yield rsps
