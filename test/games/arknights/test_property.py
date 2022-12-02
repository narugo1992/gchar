import pytest

from gchar.games.arknights import Gender, Level


@pytest.mark.unittest
class TestGamesArknightsProperty:
    def test_gender(self):
        assert Gender.OTHER == '其他'
        assert Gender.OTHER == Gender.OTHER
        assert Gender.OTHER != 'male'
        assert Gender.OTHER != Gender.MALE
        assert Gender.OTHER != 'female'
        assert Gender.OTHER != Gender.FEMALE
        assert Gender.OTHER != 1
        assert Gender.OTHER != None

        assert Gender.MALE == '男性'
        assert Gender.MALE == '男'
        assert Gender.MALE == 'man'
        assert Gender.MALE == 'male'
        assert Gender.MALE == 'MALE'
        assert Gender.MALE == Gender.MALE
        assert Gender.MALE != 'others'
        assert Gender.MALE != Gender.OTHER
        assert Gender.MALE != 'female'
        assert Gender.MALE != Gender.FEMALE

        assert Gender.FEMALE == '女性'
        assert Gender.FEMALE == '女'
        assert Gender.FEMALE == 'woman'
        assert Gender.FEMALE == 'female'
        assert Gender.FEMALE == 'FeMALE'
        assert Gender.FEMALE == Gender.FEMALE
        assert Gender.FEMALE != 'others'
        assert Gender.FEMALE != Gender.OTHER
        assert Gender.FEMALE != 'male'
        assert Gender.FEMALE != Gender.MALE

        assert Gender.loads('男') == Gender.MALE
        assert Gender.loads('female') == Gender.FEMALE
        assert Gender.loads(Gender.OTHER) == Gender.OTHER

    def test_level(self):
        assert Level.loads(6) == 6
        assert Level.loads(Level.FOUR) == 4
        with pytest.raises(TypeError):
            _ = Level.loads(None)
        with pytest.raises(ValueError):
            _ = Level.loads(20)

        assert Level.SIX == 6
        assert Level.ONE == 1
        assert 3 < Level.FOUR < 5
