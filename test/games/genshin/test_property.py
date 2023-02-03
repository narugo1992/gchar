import pytest

from gchar.games.genshin import Rarity, Element, Weapon


@pytest.mark.unittest
class TestGamesGenshinProperty:
    def test_rarity(self):
        assert Rarity.loads(4) == Rarity.FOUR
        assert Rarity.loads(5) == Rarity.FIVE
        assert Rarity.loads(Rarity.FOUR) == 4
        assert Rarity.loads(Rarity.FIVE) == 5
        with pytest.raises(ValueError):
            _ = Rarity.loads(3)
        with pytest.raises(ValueError):
            _ = Rarity.loads(6)
        with pytest.raises(TypeError):
            _ = Rarity.loads(None)

    def test_weapon(self):
        assert Weapon.loads('CATALYST') == Weapon.CATALYST
        assert Weapon.loads(Weapon.CATALYST) == 'CATALYST'
        assert Weapon.loads('CLAYMORE') == Weapon.CLAYMORE
        assert Weapon.loads(Weapon.CLAYMORE) == 'CLAYMORE'
        assert Weapon.loads('SWORD') == Weapon.SWORD
        assert Weapon.loads(Weapon.SWORD) == 'SWORD'
        assert Weapon.loads('BOW') == Weapon.BOW
        assert Weapon.loads(Weapon.BOW) == 'BOW'
        assert Weapon.loads('POLEARM') == Weapon.POLEARM
        assert Weapon.loads(Weapon.POLEARM) == 'POLEARM'
        assert Weapon.POLEARM != 'xxx'
        assert Weapon.POLEARM != None
        with pytest.raises(ValueError):
            _ = Weapon.loads('xxx')
        with pytest.raises(TypeError):
            _ = Weapon.loads(None)

        assert Weapon.loads('单手剑') == Weapon.SWORD
        assert Weapon.SWORD == '单手剑'
        assert Weapon.loads('双手剑') == Weapon.CLAYMORE
        assert Weapon.CLAYMORE == '双手剑'
        assert Weapon.loads('长柄武器') == Weapon.POLEARM
        assert Weapon.POLEARM == '长柄武器'
        assert Weapon.loads('法器') == Weapon.CATALYST
        assert Weapon.CATALYST == '法器'
        assert Weapon.loads('弓') == Weapon.BOW
        assert Weapon.BOW == '弓'

    def test_element(self):
        assert Element.loads('pyro') == Element.PYRO
        assert Element.loads('ANEMO') == Element.ANEMO
        assert Element.loads('Cryo') == Element.CRYO
        assert Element.loads('ELECTRO') == Element.ELECTRO
        assert Element.loads('DENDRO') == Element.DENDRO
        assert Element.loads('GEO') == Element.GEO
        assert Element.loads('HYDRO') == Element.HYDRO
        with pytest.raises(ValueError):
            _ = Element.loads('xxx')
        with pytest.raises(TypeError):
            _ = Element.loads(None)

        assert Element.loads(Element.PYRO) == 'pyro'
        assert Element.loads(Element.ANEMO) == 'ANEMO'
        assert Element.loads(Element.CRYO) == 'Cryo'
        assert Element.loads(Element.ELECTRO) == 'ELECTRO'
        assert Element.loads(Element.DENDRO) == 'DENDRO'
        assert Element.loads(Element.GEO) == 'GEO'
        assert Element.loads(Element.HYDRO) == 'HYDRO'
        assert Element.HYDRO != 'xxx'
        assert Element.HYDRO != None

        assert Element.loads('火') == Element.PYRO
        assert Element.PYRO == '火'
        assert Element.loads('风') == Element.ANEMO
        assert Element.ANEMO == '风'
        assert Element.loads('冰') == Element.CRYO
        assert Element.CRYO == '冰'
        assert Element.loads('雷') == Element.ELECTRO
        assert Element.ELECTRO == '雷'
        assert Element.loads('草') == Element.DENDRO
        assert Element.DENDRO == '草'
        assert Element.loads('岩') == Element.GEO
        assert Element.GEO == '岩'
        assert Element.loads('水') == Element.HYDRO
        assert Element.HYDRO == '水'
