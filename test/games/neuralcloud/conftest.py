import pytest

from gchar.games.neuralcloud import Character


@pytest.fixture()
def nc_daiyan():
    return Character.get('黛烟')


@pytest.fixture()
def nc_suer():
    return Character.get('苏尔')


@pytest.fixture()
def nc_wlns():
    return Character.get('乌拉诺斯')
