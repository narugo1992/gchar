import pytest

from gchar.games.base import Gender


@pytest.mark.unittest
class TestGamesBase:
    def test_gender(self):
        assert Gender.OTHER == '其他'
        assert Gender.OTHER == Gender.OTHER
        assert Gender.OTHER != 'male'
        assert Gender.OTHER != Gender.MALE
        assert Gender.OTHER != 'female'
        assert Gender.OTHER != Gender.FEMALE
        assert Gender.OTHER != 1
        assert Gender.OTHER != None
        assert Gender.OTHER != [1, 2, 3]

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

        assert Gender.loads('male') == Gender.MALE
        assert Gender.loads('Female') == Gender.FEMALE
        assert Gender.loads('男性') == Gender.MALE
        assert Gender.loads('女') == Gender.FEMALE
        assert Gender.loads(Gender.MALE) == Gender.MALE
        assert Gender.loads(Gender.FEMALE) == Gender.FEMALE
        assert Gender.loads('未知') == Gender.OTHER

        assert Gender.MALE == '男性'
        assert Gender.FEMALE == 'female'
        assert Gender.MALE != None
        with pytest.raises(TypeError):
            _ = Gender.loads(None)
