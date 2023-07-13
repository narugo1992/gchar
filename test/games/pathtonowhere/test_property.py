import pytest

from gchar.games.pathtonowhere import Rarity


@pytest.mark.unittest
class TestGamesPathtonowhereProperty:
    def test_rarity(self):
        assert Rarity.loads('普') == Rarity.R
        assert Rarity.loads(1) == Rarity.R
        assert Rarity.loads('R') == Rarity.R
        assert Rarity.loads(Rarity.R) == '普'
        assert Rarity.loads(Rarity.R) == 1
        assert Rarity.loads('危') == Rarity.SR
        assert Rarity.loads(2) == Rarity.SR
        assert Rarity.loads('SR') == Rarity.SR
        assert Rarity.loads(Rarity.SR) == '危'
        assert Rarity.loads(Rarity.SR) == 2
        assert Rarity.loads('狂') == Rarity.SSR
        assert Rarity.loads(3) == Rarity.SSR
        assert Rarity.loads('SSR') == Rarity.SSR
        assert Rarity.loads(Rarity.SSR) == '狂'
        assert Rarity.loads(Rarity.SSR) == 3

        with pytest.raises(KeyError):
            _ = Rarity.loads('skdjflsdf')
        with pytest.raises(ValueError):
            _ = Rarity.loads(-10)
        with pytest.raises(TypeError):
            _ = Rarity.loads([1, 2, 3])

        assert not (Rarity.SSR == [1, 2])
