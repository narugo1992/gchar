import pytest

from gchar.games import get_character


@pytest.fixture()
def ch_amiya():
    return get_character('amiya')


@pytest.fixture()
def ch_slzd():
    return get_character('山鲁佐德')
