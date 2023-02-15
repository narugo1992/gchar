import re
from typing import List, Union

from ...utils import Comparable


class _BaseName(Comparable):
    def __init__(self, name):
        _ = name

    def _repr(self) -> str:
        raise NotImplementedError  # pragma: no cover

    def _check_same_type(self, other):
        if isinstance(other, _BaseName):
            return other
        else:
            return self.__class__(other)

    def _key(self):
        return self._repr()

    def __str__(self):
        return self._repr()

    def __repr__(self):
        return f'<{type(self).__name__} {self._repr()!r}>'

    def __bool__(self):
        return bool(self._repr())


class TextName(_BaseName):
    def __init__(self, name: str):
        if not isinstance(name, str):
            raise TypeError(f'Invalid name type - {name!r}.')
        _BaseName.__init__(self, name)
        self.__name = self._preprocess(name)

    def _repr(self) -> str:
        return self.__name

    def __contains__(self, item: str) -> bool:
        return item in self.__name

    def __len__(self):
        return len(self.__name)

    def __getitem__(self, item):
        return self.__name[item]

    @classmethod
    def _preprocess(cls, name: str) -> str:
        return name.strip()

    @classmethod
    def _eqprocess(cls, name: str) -> str:
        return name.lower()

    def _key(self):
        return self._eqprocess(_BaseName._key(self))


class SegmentName(_BaseName):
    __seperator__ = '_'

    def __init__(self, name: Union[str, List[str]]):
        if not isinstance(name, (str, list, tuple)):
            raise TypeError(f'Invalid name type - {name!r}.')
        _BaseName.__init__(self, name)
        self.__words = self._preprocess(name)

    def _repr(self):
        return self.__seperator__.join(self.__words)

    def __contains__(self, item: Union[str, List[str]]) -> bool:
        target = self._preprocess(item)
        n = len(target)
        for i in range(0, len(self.__words) - n + 1):
            if self.__words[i:i + n] == target:
                return True

        return False

    def __len__(self):
        return len(self.__words)

    def __getitem__(self, item) -> List[str]:
        return self.__words[item]

    _SPLITTERS = re.compile(r'[\s_,]+')

    @classmethod
    def _preprocess(cls, name: Union[str, List[str]]) -> List[str]:
        if isinstance(name, str):
            words = cls._SPLITTERS.split(name.strip().lower())
        else:
            words = name

        words = [wd.lower().strip() for wd in words]
        words = [wd for wd in words if wd]
        return words


class ChineseName(TextName):
    pass


class JapaneseName(TextName):
    pass


class EnglishName(SegmentName):
    @classmethod
    def _word_trans(cls, name: str) -> str:
        return name

    @classmethod
    def _preprocess(cls, name: Union[SegmentName, TextName, str, List[str]]) -> List[str]:
        if isinstance(name, SegmentName):
            return name[:]
        elif isinstance(name, TextName):
            return cls._preprocess(str(name))
        elif isinstance(name, str):
            name = cls._word_trans(name).replace(chr(160), ' ')
        elif isinstance(name, list):
            name = [cls._word_trans(wd) for wd in name]
        else:
            raise TypeError(f'Invalid name type - {name!r}.')

        return SegmentName._preprocess(name)
