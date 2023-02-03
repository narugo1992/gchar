import pytest

from gchar.games.arknights import Level, Clazz


@pytest.mark.unittest
class TestGamesArknightsProperty:
    def test_level(self):
        assert Level.loads(6) == 6
        assert Level.loads(Level.FOUR) == 4
        with pytest.raises(TypeError):
            _ = Level.loads(None)
        with pytest.raises(ValueError):
            _ = Level.loads(20)

        assert Level.SIX == 6
        assert Level.ONE == 1
        assert 3 < Level.FOUR < 5

    def test_clazz(self):
        assert Clazz.VANGUARD == 'vanguard'
        assert Clazz.VANGUARD == '先锋'
        assert Clazz.VANGUARD == Clazz.VANGUARD
        assert Clazz.VANGUARD != Clazz.GUARD
        assert Clazz.VANGUARD != None

        assert Clazz.DEFENDER == 'defender'
        assert Clazz.DEFENDER == '重装'
        assert Clazz.DEFENDER == Clazz.DEFENDER
        assert Clazz.DEFENDER != Clazz.SNIPER
        assert Clazz.DEFENDER != 'sniper'

        assert Clazz.SUPPORTER == 'supporter'
        assert Clazz.SUPPORTER == '辅助'
        assert Clazz.SUPPORTER == Clazz.SUPPORTER
        assert Clazz.SUPPORTER != Clazz.SNIPER
        assert Clazz.SUPPORTER != 'sniper'

        assert Clazz.MEDIC == 'medic'
        assert Clazz.MEDIC == '医疗'
        assert Clazz.MEDIC == Clazz.MEDIC
        assert Clazz.MEDIC != Clazz.SNIPER
        assert Clazz.MEDIC != 'sniper'

        assert Clazz.loads(Clazz.DEFENDER) == Clazz.DEFENDER
        assert Clazz.loads(Clazz.SNIPER) == Clazz.SNIPER
        with pytest.raises(ValueError):
            _ = Clazz.loads('fff')
        with pytest.raises(TypeError):
            _ = Clazz.loads([1, 2, 3])
