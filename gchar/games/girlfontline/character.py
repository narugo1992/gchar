from collections import namedtuple
from typing import List, Optional

from .index import get_index, _refresh_index
from .name import EnglishName, JapaneseName, ChineseName
from .property import Level, Clazz
from ..base import Character as _BaseCharacter
from ..base.name import _BaseName

Skin = namedtuple('Skin', ['name', 'url'])


class Character(_BaseCharacter):
    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data
        self.__is_extra = None

    def _index(self) -> int:
        return self.__raw_data['id']

    @property
    def cnname(self) -> Optional[ChineseName]:
        cnname = self.__raw_data['cnname']
        return ChineseName(cnname) if cnname else None

    @property
    def enname(self) -> Optional[EnglishName]:
        enname = self.__raw_data['enname']
        return EnglishName(enname) if enname else None

    @property
    def jpname(self) -> Optional[JapaneseName]:
        jpname = self.__raw_data['jpname']
        return JapaneseName(jpname) if jpname else None

    @property
    def level(self) -> Level:
        return Level.loads(self.__raw_data['rarity'])

    @property
    def clazz(self) -> Clazz:
        return Clazz.loads(self.__raw_data['class'])

    @property
    def skins(self) -> List[Skin]:
        return [Skin(item['desc'], item['url']) for item in self.__raw_data['skins']]

    def _names(self) -> List[_BaseName]:
        return [name for name in [self.cnname, self.enname, self.jpname] if name]

    def __repr__(self):
        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'{self.level}, clazz: {self.clazz}>'

    def __eq__(self, other):
        if isinstance(other, Character):
            return self.index == other.index
        else:
            return (self.cnname and self.cnname == other) or \
                   (self.enname and self.enname == other) or \
                   (self.jpname and self.jpname == other)

    @classmethod
    def all(cls, timeout: int = 5) -> List['Character']:
        return [Character(data) for data in get_index(timeout=timeout)]

    @classmethod
    def get(cls, name, timeout: int = 5) -> Optional['Character']:
        for item in cls.all(timeout):
            if item == name:
                return item

        return None

    @classmethod
    def refresh_index(cls, timeout: int = 5):
        _refresh_index(timeout)
