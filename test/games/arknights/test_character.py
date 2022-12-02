import pytest

from gchar.games.arknights import Character


@pytest.fixture(scope='module')
def all_characters():
    return Character.all()


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
    def test_chars(self, no_index_json, amiya, amiya_guard, specter, specter_extra, silverash, chen, chen_extra):
        assert amiya == 'amiya'
        assert amiya_guard == 'amiya'
        assert amiya == amiya_guard
        assert amiya.gender == 'female'
        assert not amiya.is_extra

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
        assert repr(specter_extra) == '<Character CR02 - 归溟幽灵鲨/specter_the_unchained, female, 6******>'

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
