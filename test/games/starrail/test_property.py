import pytest

from gchar.games.starrail import Rarity


@pytest.mark.unittest
class TestGamesStarrailProperty:
    def test_rarity(self):
        assert Rarity.loads(4) == Rarity.SR
        assert Rarity.loads('SR') == Rarity.SR
        assert Rarity.loads(Rarity.SR) == 4
        assert Rarity.loads(5) == Rarity.SSR
        assert Rarity.loads('SSR') == Rarity.SSR
        assert Rarity.loads(Rarity.SSR) == 5

        with pytest.raises(ValueError):
            _ = Rarity.loads(-1)
        with pytest.raises(TypeError):
            _ = Rarity.loads([123])
