import pytest

from gchar.games.fgo import Character


@pytest.fixture()
def fgo_mashu():
    return Character.get('学妹')


@pytest.fixture()
def fgo_saber():
    return Character.get(2)


@pytest.fixture()
def fgo_solomon():
    return Character.get(83)


@pytest.fixture()
def fgo_tiamat():
    return Character.get(149)


@pytest.fixture()
def fgo_altria_caster():
    return Character.get(284)


@pytest.fixture()
def fgo_saber_l():
    return Character.get(119)


@pytest.fixture()
def fgo_saber_a():
    return Character.get(129)


@pytest.fixture()
def fgo_elf_gawain():
    return Character.get(310)


@pytest.fixture()
def fgo_elf_tristan():
    return Character.get(311)


@pytest.fixture()
def fgo_elf_lancelot():
    return Character.get(312)


@pytest.fixture()
def fgo_shihuangdi():
    return Character.get('始皇帝')


@pytest.fixture()
def fgo_okita():
    return Character.get(68)


@pytest.fixture()
def fgo_okita_extra():
    return Character.get(267)


@pytest.fixture()
def fgo_tomoe():
    return Character.get(184)


@pytest.fixture()
def fgo_tomoe_extra():
    return Character.get(290)
