import re

from unidecode import unidecode

from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName


class ChineseName(_GenericChineseName):
    @classmethod
    def _preprocess(cls, name: str) -> str:
        return re.sub(r'\s+', '', name.strip())


class JapaneseName(_GenericJapaneseName):
    @classmethod
    def _preprocess(cls, name: str) -> str:
        return re.sub(r'\s+', '', name.strip())


class EnglishName(_GenericEnglishName):
    @classmethod
    def _word_trans(cls, text: str):
        return ' '.join(re.findall('[a-zA-Z0-9]+', unidecode(text.lower())))
