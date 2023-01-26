import pytest


@pytest.mark.unittest
class TestGamesGenshinCharacter:
    def test_basic(self, genshin_keqing, genshin_yoimiya, genshin_zhongli):
        assert genshin_keqing.index == 'keqing'
        assert genshin_keqing == '刻晴'
        assert genshin_keqing.cnname == '刻晴'
        assert genshin_keqing == 'keqing'
        assert genshin_keqing.enname == 'keqing'
        assert genshin_keqing == '刻晴'
        assert genshin_keqing == 'こくせい'
        assert genshin_keqing.jpname == '刻晴'
        assert genshin_keqing.gender == 'female'
        assert genshin_keqing.rarity == 5
        assert genshin_keqing.weapon == 'sword'
        assert genshin_keqing.element == 'electro'
        assert repr(genshin_keqing) == '<Character 刻晴/keqing/刻晴/こくせい, female, 5*****, ' \
                                       'weapon: Weapon.SWORD, element: Element.ELECTRO>'

        assert genshin_yoimiya == 'yoimiya'
        assert genshin_yoimiya == '宵宫'
        assert genshin_yoimiya.cnname == '宵宫'
        assert genshin_yoimiya == 'yoimiya'
        assert genshin_yoimiya.enname == 'yoimiya'
        assert genshin_yoimiya == '宵宮'
        assert genshin_yoimiya == 'よいみや'
        assert genshin_yoimiya.jpname == '宵宮'
        assert genshin_yoimiya.gender == 'female'
        assert genshin_yoimiya.rarity == 5
        assert genshin_yoimiya.weapon == 'bow'
        assert genshin_yoimiya.element == 'pyro'
        assert repr(genshin_yoimiya) == '<Character 宵宫/yoimiya/宵宮/よいみや, female, 5*****, ' \
                                        'weapon: Weapon.BOW, element: Element.PYRO>'

        assert genshin_zhongli == 'zhongli'
        assert genshin_zhongli == '钟离'
        assert genshin_zhongli.cnname == '钟离'
        assert genshin_zhongli == 'zhongli'
        assert genshin_zhongli.enname == 'zhongli'
        assert genshin_zhongli == '鍾離'
        assert genshin_zhongli == 'しょうり'
        assert genshin_zhongli.jpname == '鍾離'
        assert genshin_zhongli.gender == 'male'
        assert genshin_zhongli.rarity == 5
        assert genshin_zhongli.weapon == 'polearm'
        assert genshin_zhongli.element == 'geo'
        assert repr(genshin_zhongli) == '<Character 钟离/zhongli/鍾離/しょうり, male, 5*****, ' \
                                        'weapon: Weapon.POLEARM, element: Element.GEO>'
