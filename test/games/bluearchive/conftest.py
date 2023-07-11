import pytest

from gchar.games.bluearchive import Character


@pytest.fixture()
def ba_yuuka():
    return Character.get('yuuka')


@pytest.fixture()
def ba_toki():
    return Character.get('toki')
