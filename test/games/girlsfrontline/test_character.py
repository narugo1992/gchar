import pytest

from gchar.games.girlsfrontline import Character


@pytest.mark.unittest
class TestGamesGirlsfrontlineCharacter:
    def test_basic(self, gfl_grizzly: Character, gfl_a416: Character, gfl_bronya: Character):
        assert gfl_grizzly == 96
        assert gfl_grizzly == "灰熊MKV"
        assert gfl_grizzly.cnname == "灰熊MKV"
        assert gfl_grizzly == "Grizzly"
        assert gfl_grizzly.enname == "Grizzly"
        assert gfl_grizzly == "グリズリー"
        assert gfl_grizzly.jpname == "グリズリー"
        assert gfl_grizzly.gender == 'female'
        assert gfl_grizzly.rarity == 5
        assert gfl_grizzly.clazz == 'HG'
        assert repr(gfl_grizzly) == '<Character 96 - 灰熊MKV/grizzly/グリズリー, 5*****, clazz: Clazz.HG>'

        assert gfl_a416 == 1029
        assert gfl_a416 == "特工416"
        assert gfl_a416.cnname == "特工416"
        assert gfl_a416 == "Agent 416"
        assert gfl_a416.enname == "Agent 416"
        assert gfl_a416 == "エージェント416"
        assert gfl_a416.jpname == "エージェント416"
        assert gfl_a416.gender == 'female'
        assert gfl_a416.rarity == 'extra'
        assert gfl_a416.clazz == 'ar'
        assert repr(gfl_a416) == '<Character 1029 - 特工416/agent_416/エージェント416, EXTRA, clazz: Clazz.AR>'

        assert gfl_bronya == 1005
        assert gfl_bronya == "布洛妮娅·扎伊切克"
        assert gfl_bronya.cnname == "布洛妮娅·扎伊切克"
        assert gfl_bronya.enname is None
        assert gfl_bronya.jpname is None
        assert gfl_bronya.gender == 'female'
        assert gfl_bronya.rarity == 'extra'
        assert gfl_bronya.clazz == 'rf'
        assert repr(gfl_bronya) == '<Character 1005 - 布洛妮娅·扎伊切克, EXTRA, clazz: Clazz.RF>'
