import pytest

from gchar.games import get_character


@pytest.mark.unittest
class TestGamesDispatchAccess:
    def test_get_character_blaze(self):
        assert get_character('blaze') == '煌'
        assert get_character('blazer') is None
        assert get_character('blazer', allow_fuzzy=True) == '煌'

    def test_get_character_ceo(self):
        assert get_character('CEO') == '彭忒西勒亚'
        assert get_character('CEOx') is None
        assert get_character('CEOx', allow_fuzzy=True) == "X毛"

    def test_get_character_gfl(self):
        assert get_character('ak47', allow_fuzzy=True) == 'ak-47'
        assert get_character('ar15', allow_fuzzy=True) == 'st ar-15'

    def test_get_character_saber(self):
        saber = get_character('saber')
        assert saber.index == 2
        assert repr(saber) == '<Character 2 - 阿尔托莉雅·潘德拉贡/altria_pendragon/アルトリア・ペンドラゴン, female, ' \
                              '5*****, class: Clazz.SABER>'

    def test_get_character_amiya(self):
        amiya = get_character('amiya')
        assert amiya.index == 'R001'
        assert repr(amiya) == '<Character R001 - 阿米娅/amiya/アーミヤ, female, 5*****>'

    def test_get_character_cba(self):
        cba = get_character('cba')
        assert cba.index == 215
        assert repr(cba) == '<Character 215 - 斯卡哈·斯卡蒂/scathach_skadi/スカサハ=スカディ, female, ' \
                            '5*****, class: Clazz.CASTER>'

        rba = get_character('rba')
        assert rba.index == 357
        assert repr(rba) == '<Character 357 - 斯卡哈·斯卡蒂/scathach_skadi/スカサハ=スカディ, female, ' \
                            '5*****, class: Clazz.RULER>'

    def test_get_character_saber_lancer(self):
        ls = get_character('白枪呆')
        assert ls.index == 119
        assert repr(ls) == '<Character 119 - 阿尔托莉雅·潘德拉贡/altria_pendragon/アルトリア・ペンドラゴン, ' \
                           'female, 5*****, class: Clazz.LANCER>'
