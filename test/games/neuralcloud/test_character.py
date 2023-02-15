import pytest

from gchar.games.neuralcloud import Character


@pytest.mark.unittest
class TestGamesNeuralcloudCharacter:
    def test_basics(self, nc_daiyan: Character, nc_suer: Character, nc_wlns: Character):
        assert nc_daiyan.index == 1046
        assert nc_daiyan == '黛烟'
        assert nc_daiyan == '95式'
        assert nc_daiyan.cnname == '黛烟'
        assert nc_daiyan.jpname is None
        assert nc_daiyan == 'type95'
        assert nc_daiyan.enname == 'daiyan'
        assert nc_daiyan.gender == 'female'
        assert nc_daiyan.clazz == '射手'
        assert nc_daiyan.company == '赛博传媒'
        assert repr(nc_daiyan) == '<Character 1046 - 黛烟/95式/daiyan/type95/95式, rarity: 3***, clazz: SHOOTER>'

        assert nc_suer.index == 1003
        assert nc_suer == '苏尔'
        assert nc_suer.cnname == '苏尔'
        assert nc_suer.jpname is None
        assert nc_suer == 'sol'
        assert nc_suer.enname == 'sol'
        assert nc_suer.gender == 'female'
        assert nc_suer.clazz == '战士'
        assert nc_suer.company == '42LAB'
        assert repr(nc_suer) == '<Character 1003 - 苏尔/sol, rarity: 2**, clazz: WARRIOR>'

        assert nc_wlns.index == 1056
        assert nc_wlns == '乌拉诺斯'
        assert nc_wlns.cnname == '乌拉诺斯'
        assert nc_wlns.jpname is None
        assert nc_wlns == 'uranus'
        assert nc_wlns.enname == 'uranus'
        assert nc_wlns.gender == 'male'
        assert nc_wlns.clazz == '射手'
        assert nc_wlns.company == '火神重工'
        assert repr(nc_wlns) == '<Character 1056 - 乌拉诺斯/uranus, rarity: 2**, clazz: SHOOTER>'
