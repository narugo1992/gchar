from itertools import chain
from typing import List, Union, Type, Iterator, Optional, Callable

from .name import _BaseName, ChineseName, EnglishName, JapaneseName


class Character:
    __cnname_class__: Type[ChineseName] = ChineseName
    __enname_class__: Type[EnglishName] = EnglishName
    __jpname_class__: Type[JapaneseName] = JapaneseName
    __alias_name_class__: Optional[Type[ChineseName]] = None
    __index_func__: Optional[Callable] = None

    def _index(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def index(self):
        return self._index()

    def _cnname(self):
        raise NotImplementedError  # pragma: no cover

    def _cnnames(self):
        cnname = self._cnname()
        return [cnname] if cnname else []

    @property
    def cnname(self):
        cnname = self._cnname()
        return self.__cnname_class__(cnname) if cnname else None

    @property
    def cnnames(self):
        return [self.__cnname_class__(name) for name in self._cnnames() if name]

    def _jpname(self):
        raise NotImplementedError  # pragma: no cover

    def _jpnames(self):
        jpname = self._jpname()
        return [jpname] if jpname else []

    @property
    def jpname(self):
        jpname = self._jpname()
        return self.__jpname_class__(jpname) if jpname else None

    @property
    def jpnames(self):
        return [self.__jpname_class__(name) for name in self._jpnames() if name]

    def _enname(self):
        raise NotImplementedError  # pragma: no cover

    def _ennames(self):
        enname = self._enname()
        return [enname] if enname else []

    @property
    def enname(self):
        enname = self._enname()
        return self.__enname_class__(enname) if enname else None

    @property
    def ennames(self):
        return [self.__enname_class__(name) for name in self._ennames() if name]

    def _alias_names(self):
        return []

    @property
    def alias_names(self):
        return [self.__alias_name_class__(name) for name in self._alias_names()]

    def _names(self) -> List[_BaseName]:
        return [*self.cnnames, *self.ennames, *self.jpnames]

    @property
    def names(self) -> List[str]:
        return sorted(set(map(str, self._names())))

    def _is_extra(self) -> bool:
        return False

    @property
    def is_extra(self) -> bool:
        return bool(self._is_extra())

    def __eq__(self, other) -> bool:
        if type(other) == type(self):
            return self.index == other.index
        else:
            if self.index is not None and self.index == other:
                return True
            for name in chain(self._names(), self.alias_names):
                if name == other:
                    return True

            return False

    @classmethod
    def all(cls, timeout: int = 5, contains_extra: bool = True, **kwargs):
        all_chs = [cls(data) for data in cls.__index_func__(timeout=timeout)]
        chs = [ch for ch in all_chs if contains_extra or not ch.is_extra]
        return chs

    @classmethod
    def get(cls, name, **kwargs):
        for item in cls.all(**kwargs):
            if item == name:
                return item

        return None


def _yield_all_characters(ch: Union[Character, list, tuple, Type[Character]], **kwargs) -> Iterator[Character]:
    if isinstance(ch, Character):
        yield ch
    elif isinstance(ch, type) and issubclass(ch, Character):
        yield from ch.all(**kwargs)
    elif isinstance(ch, (list, tuple)):
        for item in ch:
            yield from _yield_all_characters(item, **kwargs)


def list_all_characters(*chs: Union[Character, list, tuple, Type[Character]], **kwargs) -> List[Character]:
    return list(_yield_all_characters(chs, **kwargs))
