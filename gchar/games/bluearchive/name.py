import re

from unidecode import unidecode

from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName


class ChineseName(_GenericChineseName):
    pass


class ChineseAliasName(_GenericChineseName):
    pass


class JapaneseName(_GenericJapaneseName):
    pass


class EnglishName(_GenericEnglishName):
    @classmethod
    def _word_trans(cls, text: str):
        return ' '.join(re.findall('[a-zA-Z0-9]+', unidecode(text.lower())))
