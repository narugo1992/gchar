import pytest

from gchar.games.starrail import Character


@pytest.fixture()
def sr_silverwolf():
    return Character.get('银狼')


@pytest.fixture()
def sr_luocha():
    return Character.get('luocha')


@pytest.fixture()
def sr_bronya():
    return Character.get('ブローニャ')
