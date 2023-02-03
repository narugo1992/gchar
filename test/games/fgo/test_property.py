import pytest

from gchar.games.fgo import Rarity, Clazz


@pytest.mark.unittest
class TestGamesFgoProperty:
    def test_rarity(self):
        assert Rarity.loads(0) == Rarity.ZERO
        assert Rarity.loads(1) == Rarity.ONE
        assert Rarity.loads(2) == Rarity.TWO
        assert Rarity.loads(3) == Rarity.THREE
        assert Rarity.loads(4) == Rarity.FOUR
        assert Rarity.loads(5) == Rarity.FIVE
        assert Rarity.loads(Rarity.ZERO) == 0
        assert Rarity.loads(Rarity.ONE) == 1
        assert Rarity.loads(Rarity.TWO) == 2
        assert Rarity.loads(Rarity.THREE) == 3
        assert Rarity.loads(Rarity.FOUR) == 4
        assert Rarity.loads(Rarity.FIVE) == 5
        with pytest.raises(ValueError):
            _ = Rarity.loads(-1)
        with pytest.raises(ValueError):
            _ = Rarity.loads(6)
        with pytest.raises(TypeError):
            _ = Rarity.loads(None)

    def test_clazz(self):
        assert Clazz.loads('saber') == Clazz.SABER
        assert Clazz.loads('lancer') == Clazz.LANCER
        assert Clazz.loads('archer') == Clazz.ARCHER
        assert Clazz.loads('rider') == Clazz.RIDER
        assert Clazz.loads('CASTER') == Clazz.CASTER
        assert Clazz.loads('AssAssIn') == Clazz.ASSASSIN
        assert Clazz.loads('BERSERKER') == Clazz.BERSERKER
        assert Clazz.loads('Ruler') == Clazz.RULER
        assert Clazz.loads('MOONCANCER') == Clazz.MOONCANCER
        assert Clazz.loads('avenger') == Clazz.AVENGER
        assert Clazz.loads('shielder') == Clazz.SHIELDER
        assert Clazz.loads('alterego') == Clazz.ALTEREGO
        assert Clazz.loads('Pretender') == Clazz.PRETENDER
        assert Clazz.loads('FOREIGNER') == Clazz.FOREIGNER

        with pytest.raises(ValueError):
            _ = Clazz.loads('wtf')
        with pytest.raises(TypeError):
            _ = Clazz.loads(None)

        assert Clazz.loads(Clazz.SABER) == 'saber'
        assert Clazz.loads(Clazz.LANCER) == 'lancer'
        assert Clazz.loads(Clazz.ARCHER) == 'archer'
        assert Clazz.loads(Clazz.RIDER) == 'rider'
        assert Clazz.loads(Clazz.CASTER) == 'CASTER'
        assert Clazz.loads(Clazz.ASSASSIN) == 'AssAssIn'
        assert Clazz.loads(Clazz.BERSERKER) == 'BERSERKER'
        assert Clazz.loads(Clazz.RULER) == 'Ruler'
        assert Clazz.loads(Clazz.MOONCANCER) == 'MOONCANCER'
        assert Clazz.loads(Clazz.AVENGER) == 'avenger'
        assert Clazz.loads(Clazz.SHIELDER) == 'shielder'
        assert Clazz.loads(Clazz.ALTEREGO) == 'alterego'
        assert Clazz.loads(Clazz.PRETENDER) == 'Pretender'
        assert Clazz.loads(Clazz.FOREIGNER) == 'FOREIGNER'
        assert Clazz.FOREIGNER != 'wtf'
        assert Clazz.FOREIGNER != None
