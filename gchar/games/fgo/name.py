import re

import unicodedata
from unidecode import unidecode

from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName


class ChineseName(_GenericChineseName):
    @classmethod
    def _preprocess(cls, name: str) -> str:
        return _GenericChineseName._preprocess(name).replace('・', '·').replace("\"", '') \
            .replace("“", '').replace("”", '')


class ChineseAliasName(_GenericChineseName):
    @classmethod
    def _preprocess(cls, name: str) -> str:
        return unicodedata.normalize('NFKC', _GenericChineseName._preprocess(name))


class JapaneseName(_GenericJapaneseName):
    @classmethod
    def _preprocess(cls, name: str) -> str:
        return unicodedata.normalize('NFKC', _GenericJapaneseName._preprocess(name))


class EnglishName(_GenericEnglishName):
    @classmethod
    def _word_trans(cls, name: str) -> str:
        return ' '.join(re.findall('[a-zA-Z0-9]+', unidecode(name.lower())))
