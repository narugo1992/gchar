from itertools import chain
from typing import List, Union, Type, Iterator, Optional, Callable, Tuple

from .index import BaseIndexer
from .name import _BaseName, ChineseName, EnglishName, JapaneseName
from .property import Gender
from .skin import Skin
from ...utils import Comparable


class CharacterMeta(type):
    def __init__(cls, name, bases, dict_):
        type.__init__(cls, name, bases, dict_)
        cls.__original_names = set([name for name in dir(type) if name.startswith('__') and name.endswith('__')])
        if not hasattr(cls, '__indexer__'):
            cls.__indexer__: Optional[BaseIndexer] = None

    @property
    def __index_func__(cls) -> Optional[Callable]:
        if cls.__indexer__:
            return cls.__indexer__.get_index
        else:
            return None

    @property
    def __game_name__(cls):
        return cls.__indexer__.__game_name__


class Character(Comparable, metaclass=CharacterMeta):
    __cnname_class__: Type[ChineseName] = ChineseName
    __enname_class__: Type[EnglishName] = EnglishName
    __jpname_class__: Type[JapaneseName] = JapaneseName
    __alias_name_class__: Optional[Type[ChineseName]] = None
    __indexer__: Optional[BaseIndexer] = None

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
        names = [self.__cnname_class__(name) for name in self._cnnames() if name]
        return [name for name in names if name]

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
        names = [self.__jpname_class__(name) for name in self._jpnames() if name]
        return [name for name in names if name]

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
        names = [self.__enname_class__(name) for name in self._ennames() if name]
        return [name for name in names if name]

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

    def _gender(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def gender(self) -> Gender:
        return Gender.loads(self._gender())

    def _is_extra(self) -> bool:
        return False

    @property
    def is_extra(self) -> bool:
        return bool(self._is_extra())

    def _skins(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @property
    def skins(self) -> List[Skin]:
        return [Skin(name, url) for name, url in self._skins()]

    def _release_time(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def release_time(self) -> Optional[float]:
        return self._release_time()

    def _order(self):
        return ()

    def _key(self):
        return self._order(), self._index(), (1 if self._is_extra() else 0)

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

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def _simple_all(cls, timeout: int = 5, contains_extra: bool = True, **kwargs):
        all_chs = [cls(data) for data in cls.__index_func__(timeout=timeout)]
        chs = [ch for ch in all_chs if contains_extra or not ch.is_extra]
        return chs

    @classmethod
    def all(cls, timeout: int = 5, contains_extra: bool = True, **kwargs):
        return sorted(cls._simple_all(timeout, contains_extra, **kwargs))

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
