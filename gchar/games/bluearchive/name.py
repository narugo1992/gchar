import re

from unidecode import unidecode

from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName


class ChineseName(_GenericChineseName):
    """
    Represents the Chinese name of a character in Blue Archive.
    Inherits from the base class _GenericChineseName.
    """
    pass


class ChineseAliasName(_GenericChineseName):
    """
    Represents the Chinese alias name of a character in Blue Archive.
    Inherits from the base class _GenericChineseName.
    """
    pass


class JapaneseName(_GenericJapaneseName):
    """
    Represents the Japanese name of a character in Blue Archive.
    Inherits from the base class _GenericJapaneseName.
    """
    pass


class EnglishName(_GenericEnglishName):
    """
    Represents the English name of a character in Blue Archive.
    Inherits from the base class _GenericEnglishName.
    """

    @classmethod
    def _word_trans(cls, text: str):
        """
        Translates the text into English words.

        :param text: The text to translate.
        :type text: str
        :return: The translated English words.
        :rtype: str
        """
        return ' '.join(re.findall('[a-zA-Z0-9]+', unidecode(text.lower())))
