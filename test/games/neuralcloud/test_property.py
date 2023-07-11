import pytest

from gchar.games.neuralcloud import Rarity, Clazz


@pytest.mark.unittest
class TestGamesFgoProperty:
    def test_rarity(self):
        assert Rarity.loads(1) == Rarity.ONE
        assert Rarity.loads(2) == Rarity.TWO
        assert Rarity.loads(3) == Rarity.THREE
        assert Rarity.loads(Rarity.ONE) == 1
        assert Rarity.loads(Rarity.TWO) == 2
        assert Rarity.loads(Rarity.THREE) == 3
        with pytest.raises(ValueError):
            _ = Rarity.loads(0)
        with pytest.raises(ValueError):
            _ = Rarity.loads(4)
        with pytest.raises(TypeError):
            _ = Rarity.loads(None)

    def test_clazz(self):
        assert Clazz.loads('守卫') == Clazz.GUARD
        assert Clazz.loads(Clazz.GUARD) == '守卫'
        assert Clazz.loads('射手') == Clazz.SHOOTER
        assert Clazz.loads(Clazz.SHOOTER) == '射手'
        assert Clazz.loads('战士') == Clazz.WARRIOR
        assert Clazz.loads(Clazz.WARRIOR) == '战士'
        assert Clazz.loads('特种') == Clazz.SPECIALIST
        assert Clazz.loads(Clazz.SPECIALIST) == '特种'
        assert Clazz.loads('医师') == Clazz.MEDIC
        assert Clazz.loads(Clazz.MEDIC) == '医师'

        assert Clazz.loads(1) == Clazz.GUARD
        assert Clazz.loads(Clazz.GUARD) == 1
        assert Clazz.loads(2) == Clazz.SHOOTER
        assert Clazz.loads(Clazz.SHOOTER) == 2
        assert Clazz.loads(3) == Clazz.WARRIOR
        assert Clazz.loads(Clazz.WARRIOR) == 3
        assert Clazz.loads(4) == Clazz.SPECIALIST
        assert Clazz.loads(Clazz.SPECIALIST) == 4
        assert Clazz.loads(5) == Clazz.MEDIC
        assert Clazz.loads(Clazz.MEDIC) == 5

        assert Clazz.loads('guard') == Clazz.GUARD

        with pytest.raises(ValueError):
            _ = Clazz.loads(10)
        with pytest.raises(ValueError):
            _ = Clazz.loads('10')
        with pytest.raises(TypeError):
            _ = Clazz.loads(None)
        assert Clazz.GUARD != 10
        assert Clazz.GUARD != '10'
        assert Clazz.GUARD != None
        assert Clazz.GUARD != []
