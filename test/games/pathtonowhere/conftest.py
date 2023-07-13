import pytest

from gchar.games.pathtonowhere import Character


@pytest.fixture()
def ptw_langley():
    return Character.get('MBCC-S-006')


@pytest.fixture()
def ptw_ignis():
    return Character.get('MBCC-S-051')


@pytest.fixture()
def ptw_adela():
    return Character.get('MBCC-S-706')
