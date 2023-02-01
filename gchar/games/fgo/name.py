import re

from unidecode import unidecode

from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName


class ChineseName(_GenericChineseName):
    @classmethod
    def _preprocess(cls, name: str) -> str:
        return _GenericChineseName._preprocess(name).replace('・', '·')


class ChineseAliasName(_GenericChineseName):
    @classmethod
    def _preprocess(cls, name: str) -> str:
        return _GenericChineseName._preprocess(name).replace('・', '·')


class JapaneseName(_GenericJapaneseName):
    pass


class EnglishName(_GenericEnglishName):
    @classmethod
    def _word_trans(cls, name: str) -> str:
        return ' '.join(re.findall('[a-zA-Z0-9]+', unidecode(name.lower())))
