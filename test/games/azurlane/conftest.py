import pytest

from gchar.games.azurlane import Character


@pytest.fixture()
def azl_new_jersey():
    return Character.get('068')


@pytest.fixture()
def azl_maury():
    return Character.get('010')


@pytest.fixture()
def azl_fuso_meta():
    return Character.get('META005')


@pytest.fixture()
def azl_san_diego_refit():
    return Character.get('圣地亚哥.改')


@pytest.fixture()
def azl_gascogne_mu():
    return Character.get('418')


@pytest.fixture()
def azl_hiei_chan():
    return Character.get('383')


@pytest.fixture()
def azl_u556():
    return Character.get('386')


@pytest.fixture()
def azl_azuma():
    return Character.get('Plan010')
