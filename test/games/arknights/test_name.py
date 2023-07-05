import pytest

from gchar.games.arknights import ChineseName, EnglishName, JapaneseName


@pytest.fixture
def cn_amiya():
    return ChineseName('阿米娅')


@pytest.fixture(scope='module')
def jp_amiya():
    return JapaneseName('アーミヤ')


@pytest.fixture(scope='module')
def en_amiya():
    return EnglishName('amiya')


@pytest.fixture(scope='module')
def en_kaltsit():
    return EnglishName('Kal\'tsit')


@pytest.fixture(scope='module')
def en_chen():
    return EnglishName('Ch\'en')


@pytest.fixture(scope='module')
def en_blue_poison():
    return EnglishName('BLUE POISON')


@pytest.fixture(scope='module')
def en_rosa():
    return EnglishName('роса')


@pytest.mark.unittest
class TestGamesArknightsName:
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

    def test_en_name(self, en_amiya, en_rosa, cn_amiya, en_blue_poison, en_chen, en_kaltsit):
        assert en_amiya == 'amiya'
        assert en_amiya == 'AMIYA'
        assert en_amiya == ['amiya']
        assert en_amiya != 'a miya'
        assert en_amiya == en_amiya
        assert en_amiya != en_rosa
        assert en_amiya != cn_amiya
        assert en_amiya != None
        assert en_amiya in en_amiya
        assert ChineseName('amiya') in en_amiya

        assert en_rosa == 'rosa'
        assert en_rosa == '  роса '
        assert en_rosa != 'poca'

        assert en_blue_poison == 'blue poison'
        assert en_blue_poison == ['blue', 'poison']
        assert en_blue_poison != 'bluepoison'

        assert en_kaltsit == 'kal\'tsit'
        assert en_chen == 'ch\'en'

        with pytest.raises(TypeError):
            _ = EnglishName(None)
        with pytest.raises(TypeError):
            _ = None in en_amiya
