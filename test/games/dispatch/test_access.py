import pytest

from gchar.games import get_character


@pytest.mark.unittest
class TestGamesDispatchAccess:
    def test_get_character(self):
        assert get_character('blaze') == '煌'
        assert get_character('blazer') is None
        assert get_character('blazer', allow_fuzzy=True) == '煌'

        assert get_character('CEO') == '彭忒西勒亚'
        assert get_character('CEOx') is None
        assert get_character('CEOx', allow_fuzzy=True) == "X毛"

        assert get_character('ak47', allow_fuzzy=True) == 'ak-47'
        assert get_character('ar15', allow_fuzzy=True) == 'st ar-15'
