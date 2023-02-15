import re

from unidecode import unidecode

from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName

WORD_PATTERN = re.compile('\\b\\w+\\b')


def _text_only(text: str, split: bool = False):
    return ('_' if split else '').join(WORD_PATTERN.findall(text))


class ChineseName(_GenericChineseName):
    @classmethod
    def _preprocess(cls, name: str) -> str:
        return re.sub(r'\s+', '', _GenericChineseName._preprocess(name))

    def _eqprocess(cls, name: str) -> str:
        return _text_only(_GenericChineseName._eqprocess(name)).lower()


class ChineseAliasName(_GenericChineseName):
    @classmethod
    def _preprocess(cls, name: str) -> str:
        return re.sub(r'\s+', '', _GenericChineseName._preprocess(name))

    def _eqprocess(cls, name: str) -> str:
        return _text_only(_GenericChineseName._eqprocess(name)).lower()


class JapaneseName(_GenericJapaneseName):
    @classmethod
    def _preprocess(cls, name: str) -> str:
        return re.sub(r'\s+', '', _GenericJapaneseName._preprocess(name))

    def _eqprocess(cls, name: str) -> str:
        return _text_only(_GenericJapaneseName._eqprocess(name)).lower()


class EnglishName(_GenericEnglishName):
    @classmethod
    def _word_trans(cls, text: str):
        return ' '.join(re.findall('[a-zA-Z0-9]+', unidecode(text.lower())))
