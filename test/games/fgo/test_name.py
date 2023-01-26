import pytest

from gchar.games.base import EnglishName as _BaseEnglishName
from gchar.games.fgo import ChineseName, ChineseAliasName, EnglishName


@pytest.fixture()
def fgo_mashu_cnname(fgo_mashu):
    return fgo_mashu.cnname


@pytest.fixture()
def fgo_mashu_alias1(fgo_mashu):
    return fgo_mashu.alias_names[0]


@pytest.fixture()
def fgo_mashu_alias2(fgo_mashu):
    return fgo_mashu.alias_names[1]


@pytest.fixture()
def fgo_mashu_enname(fgo_mashu):
    return fgo_mashu.enname


@pytest.fixture()
def fgo_saber_enname(fgo_saber):
    return fgo_saber.enname


@pytest.mark.unittest
class TestGamesFgoName:
    def test_chinese_name(self, fgo_mashu_cnname: ChineseName):
        assert fgo_mashu_cnname == '玛修·基列莱特'
        assert fgo_mashu_cnname == '玛修・基列莱特'
        assert fgo_mashu_cnname != '玛修 基列莱特'

    def test_chinese_alias_name(self, fgo_mashu_alias1: ChineseAliasName, fgo_mashu_alias2: ChineseAliasName):
        assert fgo_mashu_alias1 == '盾娘'
        assert fgo_mashu_alias1 != '学妹'
        assert fgo_mashu_alias2 == '学妹'
        assert fgo_mashu_alias2 != '盾娘'

    def test_english_name(self, fgo_mashu_enname: EnglishName, fgo_mashu_cnname: ChineseName,
                          fgo_saber_enname: EnglishName):
        assert fgo_mashu_enname == 'mash_kyrielight'
        assert fgo_mashu_enname == 'Mash Kyrielight'
        assert fgo_mashu_enname == ['Mash', 'Kyrielight']
        assert fgo_mashu_enname != 'Mash Kyrieligh'
        assert fgo_mashu_enname == fgo_mashu_enname
        assert fgo_mashu_enname != fgo_mashu_cnname
        assert fgo_mashu_enname != fgo_saber_enname
        assert fgo_mashu_enname == _BaseEnglishName('mash Kyrielight')
        assert fgo_mashu_enname != _BaseEnglishName('mash Kyrieligh')

        with pytest.raises(TypeError):
            _ = EnglishName(None)
        with pytest.raises(TypeError):
            _ = None in fgo_mashu_enname
