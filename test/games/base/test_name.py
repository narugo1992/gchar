import pytest

from gchar.games.base import ChineseName, JapaneseName, EnglishName


@pytest.fixture(scope='module')
def cn_amiya():
    return ChineseName('阿米娅')


@pytest.fixture(scope='module')
def jp_amiya():
    return JapaneseName('アーミヤ')


@pytest.fixture(scope='module')
def en_amiya():
    return EnglishName('Amiya')


@pytest.fixture(scope='module')
def en_blue_poison():
    return EnglishName('Blue Poison')


@pytest.mark.unittest
class TestGamesBaseName:
    def test_chinese_name(self, cn_amiya):
        assert cn_amiya == cn_amiya
        assert cn_amiya == '阿米娅'
        assert cn_amiya != '阿米驴'
        assert cn_amiya != None
        assert cn_amiya != []

        with pytest.raises(TypeError):
            _ = ChineseName(None)

        assert '阿' in cn_amiya
        assert '驴' not in cn_amiya

        assert len(cn_amiya) == 3

        assert cn_amiya[0] == '阿'
        assert cn_amiya[-1] == '娅'
        assert cn_amiya[::-1] == '娅米阿'

        assert repr(cn_amiya) == '<ChineseName \'阿米娅\'>'
        assert str(cn_amiya) == '阿米娅'

    def test_japanese_name(self, jp_amiya):
        assert jp_amiya == jp_amiya
        assert jp_amiya == 'アーミヤ'
        assert jp_amiya != 'amiya'
        assert jp_amiya != '阿米娅'
        assert jp_amiya != None
        assert jp_amiya != []

        with pytest.raises(TypeError):
            _ = JapaneseName(None)

        assert 'アーミヤ' in jp_amiya
        assert 'ミヤ' in jp_amiya

        assert len(jp_amiya) == 4

        assert jp_amiya[0] == 'ア'
        assert jp_amiya[-1] == 'ヤ'
        assert jp_amiya[::-1] == 'ヤミーア'

        assert repr(jp_amiya) == '<JapaneseName \'アーミヤ\'>'
        assert str(jp_amiya) == 'アーミヤ'

    def test_english_name(self, en_amiya, en_blue_poison):
        assert en_amiya == en_amiya
        assert en_amiya == 'amiya'
        assert en_amiya == 'Amiya'
        assert en_amiya == ['Amiya']
        assert en_amiya == ['Amiya', '']
        assert en_amiya != en_blue_poison
        assert en_blue_poison == en_blue_poison
        assert en_blue_poison == 'blue   poison'
        assert en_blue_poison == ' Blue_Poison'
        assert en_blue_poison == 'blue____poison'
        assert en_blue_poison == ['blue', 'poison']
        assert en_blue_poison == ['Blue', '', 'Poison']

        with pytest.raises(TypeError):
            _ = EnglishName(None)

        assert 'ami' not in en_amiya
        assert 'Amiya' in en_amiya
        assert ' amiya' in en_amiya
        assert 'blue' in en_blue_poison
        assert 'poi' not in en_blue_poison
        assert 'poison' in en_blue_poison
        assert 'blue poison' in en_blue_poison
        assert 'poison blue ' not in en_blue_poison

        assert len(en_amiya) == 1
        assert len(str(en_amiya)) == 5
        assert len(en_blue_poison) == 2
        assert len(str(en_blue_poison)) == 11

        assert en_amiya[::] == ['amiya']
        assert en_blue_poison[::-1] == ['poison', 'blue']
        assert en_blue_poison[1] == 'poison'

        assert str(en_amiya) == 'amiya'
        assert str(en_blue_poison) == 'blue_poison'
        assert repr(en_amiya) == '<EnglishName \'amiya\'>'
        assert repr(en_blue_poison) == '<EnglishName \'blue_poison\'>'
