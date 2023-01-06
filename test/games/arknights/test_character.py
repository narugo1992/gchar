import pytest

from gchar.games.arknights import Character
from gchar.games.base import list_all_characters


@pytest.fixture(scope='module')
def all_characters():
    return Character.all()


@pytest.fixture(scope='module')
def fang():
    return Character.get('fang')


@pytest.fixture(scope='module')
def amiya():
    return Character.get('amiya')


@pytest.fixture(scope='module')
def amiya_guard():
    return Character.get('阿米娅(近卫)')


@pytest.fixture(scope='module')
def specter():
    return Character.get('specter')


@pytest.fixture(scope='module')
def specter_extra():
    return Character.get('归溟幽灵鲨')


@pytest.fixture(scope='module')
def silverash():
    return Character.get('silverash')


@pytest.fixture(scope='module')
def chen():
    return Character.get('陈')


@pytest.fixture(scope='module')
def chen_extra():
    return Character.get('假日威龙陈')


@pytest.mark.unittest
class TestGamesArknightsCharacter:
    def test_chars(self, no_index_json, amiya, amiya_guard, specter, specter_extra, silverash, chen, chen_extra, fang):
        assert amiya == 'amiya'
        assert amiya_guard == 'amiya'
        assert amiya == amiya_guard
        assert amiya.gender == 'female'
        assert not amiya.is_extra
        assert amiya.cnname == '阿米娅'
        assert amiya.cnnames == ['阿米娅']
        assert amiya.enname == 'amiya'
        assert amiya.ennames == ['amiya']
        assert amiya.jpname == 'アーミヤ'
        assert amiya.jpnames == ['アーミヤ']
        assert amiya.names == ['amiya', 'アーミヤ', '阿米娅']

        assert amiya.level == 5
        assert amiya.clazz == 'caster'
        assert amiya.clazz != 'guard'
        assert amiya.clazz != 'specialist'
        assert repr(amiya) == '<Character R001 - 阿米娅/amiya/アーミヤ, female, 5*****>'

        assert amiya_guard.level == 5
        assert amiya_guard.clazz == 'guard'
        assert amiya_guard.clazz != 'caster'
        assert amiya_guard.is_extra
        assert repr(amiya_guard) == '<Character R001 - 阿米娅(近卫)/amiya/アーミヤ, female, 5*****>'

        assert amiya.approach == '主线剧情'
        assert amiya_guard.approach == '主线剧情'
        with pytest.raises(AttributeError):
            _ = amiya.what_the_fxxk

        assert specter == '幽灵鲨'
        assert not specter.is_extra
        assert repr(specter) == '<Character AA02 - 幽灵鲨/specter/スペクター, female, 5*****>'
        assert specter_extra == '归溟幽灵鲨'
        assert specter_extra.is_extra
        assert repr(specter_extra) == '<Character CR02 - 归溟幽灵鲨/specter_the_unchained/帰溟スペクター, female, 6******>'

        assert silverash == '银灰'
        assert silverash.level == 6
        assert silverash.gender == '男性'
        assert not silverash.is_extra
        assert repr(silverash) == '<Character JC01 - 银灰/silverash/シルバーアッシュ, male, 6******>'

        assert chen == 'chen'
        assert chen == '陈'
        assert chen.level == 6
        assert chen.gender == 'female'
        assert chen.clazz == 'guard'
        assert not chen.is_extra
        assert repr(chen) == '<Character LM04 - 陈/chen/チェン, female, 6******>'

        assert chen_extra == 'chen_the_holungday'
        assert chen_extra == '假日威龙陈'
        assert chen_extra.level == 6
        assert chen_extra.gender == 'female'
        assert chen_extra.clazz == 'sniper'
        assert chen_extra.is_extra
        assert repr(chen_extra) == '<Character R112 - 假日威龙陈/chen_the_holungday/遊龍チェン, female, 6******>'

        assert fang == 'fang'
        assert fang == '芬'
        assert fang == 'フェン'
        assert fang.level == 3
        assert fang.gender == 'female'
        assert fang.clazz == 'vanguard'
        assert not fang.is_extra
        assert len(fang.skins) == 2
        assert fang.skins[0].name == '立绘 芬 1'
        assert fang.skins[1].name == '立绘 芬 skin1'

    def test_chars_get(self):
        assert Character.get('what_the_fxxk') is None

    def test_list_all_characters(self):
        actual_all = list_all_characters(Character)
        standalone_all = list_all_characters(Character, contains_extra=False)
        assert len(actual_all) > len(standalone_all)
        assert all([not ch.is_extra for ch in standalone_all])
        assert not all([not ch.is_extra for ch in actual_all])
