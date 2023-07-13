import re

from unidecode import unidecode

from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName


class ChineseName(_GenericChineseName):
    """
    A class representing Chinese names of characters in the Azur Lane game.
    Inherits from _GenericChineseName.
    """


class ChineseAliasName(_GenericChineseName):
    """
    A class representing Chinese alias names of characters in the Azur Lane game.
    Inherits from _GenericChineseName.
    """


class JapaneseName(_GenericJapaneseName):
    """
    A class representing Japanese names of characters in the Azur Lane game.
    Inherits from _GenericJapaneseName.
    """


class EnglishName(_GenericEnglishName):
    """
    A class representing English names of characters in the Azur Lane game.
    Inherits from _GenericEnglishName.
    """

    @classmethod
    def _word_trans(cls, text: str):
        """
        Perform word-based transliteration on the given text.

        :param text: The text to transliterate.
        :type text: str
        :return: The transliterated text.
        :rtype: str
        """
        return ' '.join(re.findall('[a-zA-Z0-9]+', unidecode(text.lower())))
