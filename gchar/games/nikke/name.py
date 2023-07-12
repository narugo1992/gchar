from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName
from ..base import TextName


class ChineseName(_GenericChineseName):
    pass


class JapaneseName(_GenericJapaneseName):
    pass


class KoreanName(TextName):
    pass


class EnglishName(_GenericEnglishName):
    pass
