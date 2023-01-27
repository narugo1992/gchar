import pytest

from gchar.games.girlsfrontline import Rarity, Clazz


@pytest.mark.unittest
class TestGamesGrilsfrontlineProperty:
    def test_rarity(self):
        assert Rarity.loads(1) == Rarity.ONE
        assert Rarity.loads(Rarity.ONE) == 1
        assert Rarity.loads(2) == Rarity.TWO
        assert Rarity.loads(Rarity.TWO) == 2
        assert Rarity.loads(3) == Rarity.THREE
        assert Rarity.loads(Rarity.THREE) == 3
        assert Rarity.loads(4) == Rarity.FOUR
        assert Rarity.loads(Rarity.FOUR) == 4
        assert Rarity.loads(5) == Rarity.FIVE
        assert Rarity.loads(Rarity.FIVE) == 5
        assert Rarity.loads('Extra') == Rarity.EXTRA
        assert Rarity.loads(Rarity.EXTRA) == 'EXTRA'
        with pytest.raises(ValueError):
            _ = Rarity.loads(6)
        with pytest.raises(ValueError):
            _ = Rarity.loads('xxx')
        with pytest.raises(TypeError):
            _ = Rarity.loads(None)
        assert Rarity.ONE != None

    def test_clazz(self):
        assert Clazz.loads('HG') == Clazz.HG
        assert Clazz.loads('手枪') == Clazz.HG
        assert Clazz.loads('手') == Clazz.HG
        assert Clazz.loads(Clazz.HG) == 'HG'
        assert Clazz.HG == '手枪'
        assert Clazz.HG == '手'
        assert Clazz.loads('AR') == Clazz.AR
        assert Clazz.loads('突击步枪') == Clazz.AR
        assert Clazz.loads('突') == Clazz.AR
        assert Clazz.loads(Clazz.AR) == 'AR'
        assert Clazz.AR == '突击步枪'
        assert Clazz.AR == '突'
        assert Clazz.loads('RF') == Clazz.RF
        assert Clazz.loads('步枪') == Clazz.RF
        assert Clazz.loads('步') == Clazz.RF
        assert Clazz.loads(Clazz.RF) == 'RF'
        assert Clazz.RF == '步枪'
        assert Clazz.RF == '步'
        assert Clazz.loads('SMG') == Clazz.SMG
        assert Clazz.loads('冲锋枪') == Clazz.SMG
        assert Clazz.loads('冲') == Clazz.SMG
        assert Clazz.loads(Clazz.SMG) == 'SMG'
        assert Clazz.SMG == '冲锋枪'
        assert Clazz.SMG == '冲'
        assert Clazz.loads('MG') == Clazz.MG
        assert Clazz.loads('机枪') == Clazz.MG
        assert Clazz.loads('机') == Clazz.MG
        assert Clazz.loads(Clazz.MG) == 'MG'
        assert Clazz.MG == '机枪'
        assert Clazz.MG == '机'
        assert Clazz.loads('SG') == Clazz.SG
        assert Clazz.loads('霰弹枪') == Clazz.SG
        assert Clazz.loads('霰') == Clazz.SG
        assert Clazz.loads(Clazz.SG) == 'SG'
        assert Clazz.SG == '霰弹枪'
        assert Clazz.SG == '霰'

        with pytest.raises(ValueError):
            _ = Clazz.loads('xxx')
        with pytest.raises(TypeError):
            _ = Clazz.loads(None)

        assert Clazz.MG != None
        assert Clazz.MG != 'xxx'
