import re
from typing import Union, List

from unidecode import unidecode

from ..base import ChineseName as _GenericChineseName
from ..base import EnglishName as _GenericEnglishName
from ..base import JapaneseName as _GenericJapaneseName
from ..base import SegmentName, TextName


class ChineseName(_GenericChineseName):
    pass


class JapaneseName(_GenericJapaneseName):
    pass


class EnglishName(_GenericEnglishName):
    @classmethod
    def _word_trans(cls, text: str):
        return ' '.join(re.findall('[a-zA-Z0-9]+', unidecode(text.lower())))

    @classmethod
    def _preprocess(cls, name: Union[str, List[str]]) -> List[str]:
        if isinstance(name, SegmentName):
            return name[:]
        elif isinstance(name, TextName):
            return cls._preprocess(str(name))
        elif isinstance(name, str):
            name = cls._word_trans(name)
        elif isinstance(name, list):
            name = [cls._word_trans(wd) for wd in name]
        else:
            raise TypeError(f'Invalid name type - {name!r}.')

        return _GenericEnglishName._preprocess(name)
