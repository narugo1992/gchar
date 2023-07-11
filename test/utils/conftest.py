import pytest
from hbutils.testing import TextAligner

from ..testings import start_http_server_to_testfile


@pytest.fixture()
def text_align():
    return TextAligner().multiple_lines()


@pytest.fixture(scope='session')
def url_to_testfile():
    with start_http_server_to_testfile() as url:
        yield url


@pytest.fixture(scope='session')
def url_to_game_characters():
    yield 'https://huggingface.co/datasets/deepghs/game_characters/resolve/main'


@pytest.fixture(scope='session')
def url_to_game_character_skins():
    yield 'https://huggingface.co/datasets/deepghs/game_character_skins/resolve/main'
