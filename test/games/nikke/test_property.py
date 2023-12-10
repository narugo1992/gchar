import pytest

from gchar.games.nikke import Rarity, Clazz, Burst


@pytest.mark.unittest
class TestGamesNikkeProperty:
    def test_rarity(self):
        assert Rarity.loads(1) == Rarity.R
        assert Rarity.loads('R') == Rarity.R
        assert Rarity.loads(Rarity.R) == 1
        assert Rarity.loads(2) == Rarity.SR
        assert Rarity.loads('SR') == Rarity.SR
        assert Rarity.loads(Rarity.SR) == 2
        assert Rarity.loads(3) == Rarity.SSR
        assert Rarity.loads('SSR') == Rarity.SSR
        assert Rarity.loads(Rarity.SSR) == 3

        with pytest.raises(ValueError):
            _ = Rarity.loads(-1)
        with pytest.raises(TypeError):
            _ = Rarity.loads([1, 2])

    def test_clazz(self):
        assert Clazz.loads('attackers') == Clazz.ATTACKER
        assert Clazz.loads('attacker') == Clazz.ATTACKER
        assert Clazz.loads('火力型') == Clazz.ATTACKER
        assert Clazz.loads(1) == Clazz.ATTACKER
        assert Clazz.loads('ATTACKER') == Clazz.ATTACKER
        assert Clazz.loads(Clazz.ATTACKER) == 'attackers'
        assert Clazz.loads(Clazz.ATTACKER) == 1
        assert Clazz.loads('defenders') == Clazz.DEFENDER
        assert Clazz.loads('defender') == Clazz.DEFENDER
        assert Clazz.loads('防御型') == Clazz.DEFENDER
        assert Clazz.loads(2) == Clazz.DEFENDER
        assert Clazz.loads('DEFENDER') == Clazz.DEFENDER
        assert Clazz.loads(Clazz.DEFENDER) == 'defenders'
        assert Clazz.loads(Clazz.DEFENDER) == 2
        assert Clazz.loads('supporters') == Clazz.SUPPORTER
        assert Clazz.loads('supporter') == Clazz.SUPPORTER
        assert Clazz.loads('辅助型') == Clazz.SUPPORTER
        assert Clazz.loads(3) == Clazz.SUPPORTER
        assert Clazz.loads('SUPPORTER') == Clazz.SUPPORTER
        assert Clazz.loads(Clazz.SUPPORTER) == 'supporters'
        assert Clazz.loads(Clazz.SUPPORTER) == 3

        assert not (Clazz.ATTACKER == [1, 2])
        with pytest.raises(ValueError):
            _ = Clazz.loads('as' * 100)
        with pytest.raises(ValueError):
            _ = Clazz.loads(-1)
        with pytest.raises(TypeError):
            _ = Clazz.loads([1, 2, 3])

        assert sorted(Clazz.__members__.values()) == [Clazz.ATTACKER, Clazz.DEFENDER, Clazz.SUPPORTER]
        assert set(Clazz.__members__.values()) == {Clazz.ATTACKER, Clazz.DEFENDER, Clazz.SUPPORTER}

        assert repr(Clazz.ATTACKER) == '<Clazz.ATTACKER: 1>'
        assert repr(Clazz.DEFENDER) == '<Clazz.DEFENDER: 2>'
        assert repr(Clazz.SUPPORTER) == '<Clazz.SUPPORTER: 3>'

    def test_burst(self):
        assert Burst.loads('burst skill i') == Burst.I
        assert Burst.loads('i') == Burst.I
        assert Burst.loads(1) == Burst.I
        assert Burst.loads('I') == Burst.I
        assert Burst.loads(Burst.I) == 'burst skill i'
        assert Burst.loads(Burst.I) == 1
        assert Burst.loads('burst skill ii') == Burst.II
        assert Burst.loads('ii') == Burst.II
        assert Burst.loads(2) == Burst.II
        assert Burst.loads('II') == Burst.II
        assert Burst.loads(Burst.II) == 'burst skill ii'
        assert Burst.loads(Burst.II) == 2
        assert Burst.loads('burst skill iii') == Burst.III
        assert Burst.loads('iii') == Burst.III
        assert Burst.loads(3) == Burst.III
        assert Burst.loads('III') == Burst.III
        assert Burst.loads(Burst.III) == 'burst skill iii'
        assert Burst.loads(Burst.III) == 3

        assert not (Burst.I == [1, 2])
        assert not (Burst.II == None)
        assert not (Burst.III == 'skldfgj')

        with pytest.raises(ValueError):
            _ = Burst.loads('s;dklfjl' * 100)
        with pytest.raises(ValueError):
            _ = Burst.loads(-10)
        with pytest.raises(TypeError):
            _ = Burst.loads([1, 2])

        assert sorted(Burst.__members__.values()) == [Burst.I, Burst.II, Burst.III, Burst.ALL]
        assert set(Burst.__members__.values()) == {Burst.I, Burst.II, Burst.III, Burst.ALL}

        assert repr(Burst.I) == '<Burst.I: 1>'
        assert repr(Burst.II) == '<Burst.II: 2>'
        assert repr(Burst.III) == '<Burst.III: 3>'
