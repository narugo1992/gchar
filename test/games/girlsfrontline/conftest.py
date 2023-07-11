import pytest

from gchar.games.girlsfrontline import Character


@pytest.fixture()
def gfl_grizzly():
    return Character.get(96)


@pytest.fixture()
def gfl_a416():
    return Character.get(1029)


@pytest.fixture()
def gfl_bronya():
    return Character.get(1005)
