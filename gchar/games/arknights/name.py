from transliterate import translit

from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName


class ChineseName(_GenericChineseName):
    pass


class JapaneseName(_GenericJapaneseName):
    pass


class EnglishName(_GenericEnglishName):
    @classmethod
    def _word_trans(cls, text: str):
        return translit(text.replace('\'', '').replace('\"', ''), 'ru', reversed=True)
