import pytest

from gchar.games.nikke import Character


@pytest.fixture()
def nikke_admi():
    return Character.get('admi')


@pytest.fixture()
def nikke_helm():
    return Character.get('helm')


@pytest.fixture()
def nikke_quency():
    return Character.get('quency')


@pytest.fixture()
def nikke_neon_blue_ocean():
    return Character.get('neon_blue_ocean')
