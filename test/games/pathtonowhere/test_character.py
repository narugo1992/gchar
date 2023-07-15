import pytest

from gchar.games.pathtonowhere import Character


@pytest.mark.unittest
class TestGamesPathtonowhereCharacter:
    def test_character(self, ptw_langley: Character):
        assert ptw_langley.index == 'MBCC-S-006'
        assert ptw_langley.cnname == '兰利'
        assert ptw_langley.enname == 'langley'
        assert ptw_langley.jpname == 'ラングリー'
        assert ptw_langley.jpnames == ['ラングリー']
        assert ptw_langley.gender == 'female'
        assert ptw_langley.rarity == 3
        assert len(ptw_langley.skins) >= 3
        assert ptw_langley.release_time is None
        assert ptw_langley.job == '精准'
        assert ptw_langley.group == '背离'
        assert repr(ptw_langley) == '<Character MBCC-S-006 - 兰利/langley/ラングリー, SSR(3***), job: 精准, group: 背离>'
