import pytest

from gchar.games.genshin import Character


@pytest.fixture()
def genshin_keqing() -> Character:
    return Character.get('keqing')


@pytest.fixture()
def genshin_yoimiya() -> Character:
    return Character.get('よいみや')


@pytest.fixture()
def genshin_zhongli() -> Character:
    return Character.get('鍾離')


@pytest.fixture()
def genshin_traveller() -> Character:
    return Character.get('traveler')
