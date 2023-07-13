import pytest

from gchar.games.starrail import Character


@pytest.mark.unittest
class TestGamesStarrailCharacter:
    def test_character(self, sr_silverwolf: Character):
        assert sr_silverwolf.index == 'silverwolf'
        assert sr_silverwolf.cnname == '银狼'
        assert sr_silverwolf.enname == 'silver_wolf'
        assert sr_silverwolf.jpname == '銀狼'
        assert sr_silverwolf.krname == '은랑'
        assert sr_silverwolf.krnames == ['은랑']
        assert sr_silverwolf.gender == 'female'
        assert sr_silverwolf.rarity == 5
        assert sr_silverwolf.destiny == '虚无'
        assert sr_silverwolf.element == '量子'
        assert sr_silverwolf.group == '星核猎手'
        assert len(sr_silverwolf.skins) >= 2
        assert sr_silverwolf.release_time == pytest.approx(1686096000.0)
        assert repr(sr_silverwolf) == '<Character 银狼/silver_wolf/銀狼/은랑, SSR(5*****), element: 量子, destiny: 虚无>'

    def test_character_order(self, sr_silverwolf, sr_bronya, sr_luocha):
        assert sorted([sr_silverwolf, sr_bronya, sr_luocha]) == \
               [sr_bronya, sr_silverwolf, sr_luocha]
