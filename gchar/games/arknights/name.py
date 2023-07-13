from transliterate import translit

from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName


class ChineseName(_GenericChineseName):
    """
    A class for modeling Chinese names of characters in the Arknights game.
    """

    @classmethod
    def _preprocess(cls, name: str) -> str:
        """
        Preprocess the Chinese name by replacing '・' with '·'.

        :param name: The input Chinese name.
        :type name: str
        :returns: The preprocessed Chinese name.
        :rtype: str
        """
        return _GenericChineseName._preprocess(name).replace('・', '·')


class ChineseAliasName(_GenericChineseName):
    """
    A class for modeling Chinese alias names of characters in the Arknights game.
    """

    @classmethod
    def _preprocess(cls, name: str) -> str:
        """
        Preprocess the Chinese alias name by replacing '・' with '·'.

        :param name: The input Chinese alias name.
        :type name: str
        :returns: The preprocessed Chinese alias name.
        :rtype: str
        """
        return _GenericChineseName._preprocess(name).replace('・', '·')


class JapaneseName(_GenericJapaneseName):
    """
    A class for modeling Japanese names of characters in the Arknights game.
    """


class EnglishName(_GenericEnglishName):
    """
    A class for modeling English names of characters in the Arknights game.
    """

    @classmethod
    def _word_trans(cls, text: str):
        """
        Transliterate the English name using the 'ru' transliteration scheme.

        :param text: The input English name.
        :type text: str
        :returns: The transliterated English name.
        :rtype: str
        """
        return translit(text, 'ru', reversed=True)
