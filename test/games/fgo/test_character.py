import pytest

from gchar.games.base import Gender
from gchar.games.fgo import Character


@pytest.mark.unittest
class TestGamesFgoCharacter:
    def test_basic(self, fgo_saber: Character, fgo_mashu: Character, fgo_shihuangdi):
        assert fgo_mashu == "玛修·基列莱特"
        assert fgo_mashu.index == 1
        assert fgo_mashu == '盾娘'
        assert fgo_mashu == "マシュ・キリエライト"
        assert fgo_mashu == "Mash Kyrielight"
        assert fgo_mashu.rarity == 4
        assert fgo_mashu.clazz == 'shielder'
        assert fgo_mashu.gender == 'female'
        assert repr(fgo_mashu) == '<Character 1 - 玛修·基列莱特/mash_kyrielight/マシュ・キリエライト, female, 4****>'
        assert fgo_mashu != fgo_saber

        assert fgo_saber == 'saber'
        assert fgo_saber == '呆毛'
        assert fgo_saber.index == 2
        assert fgo_saber == '阿尔托莉雅·潘德拉贡'
        assert fgo_saber.cnname == '阿尔托莉雅·潘德拉贡'
        assert fgo_saber == 'アルトリア・ペンドラゴン'
        assert fgo_saber.jpname == 'アルトリア・ペンドラゴン'
        assert fgo_saber == "Altria Pendragon"
        assert fgo_saber.enname == "Altria Pendragon"
        assert fgo_saber.gender == '女性'
        assert fgo_saber.rarity == 5
        assert fgo_saber.accessible
        assert fgo_saber.clazz == 'saber'
        assert not fgo_saber.is_extra
        assert repr(fgo_saber) == '<Character 2 - 阿尔托莉雅·潘德拉贡/altria_pendragon/' \
                                  'アルトリア・ペンドラゴン, female, 5*****>'
        assert fgo_saber == fgo_saber

        assert fgo_shihuangdi == '始皇帝'
        assert fgo_shihuangdi.gender == Gender.OTHER

    def test_extra(self, fgo_saber, fgo_mashu, fgo_saber_l, fgo_saber_a, fgo_altria_caster,
                   fgo_elf_gawain, fgo_elf_tristan, fgo_elf_lancelot):
        assert not fgo_saber.is_extra
        assert not fgo_mashu.is_extra
        assert fgo_saber_a.is_extra
        assert fgo_saber_l.is_extra
        assert not fgo_altria_caster.is_extra
        assert not fgo_elf_gawain.is_extra
        assert not fgo_elf_tristan.is_extra
        assert not fgo_elf_lancelot.is_extra
