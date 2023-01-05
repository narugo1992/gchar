from collections import namedtuple
from typing import List, Optional

from .index import get_index, _refresh_index
from .name import EnglishName, JapaneseName, ChineseName
from .property import Gender, Level
from ..base import Character as _BaseCharacter
from ..base.name import _BaseName

Skin = namedtuple('Skin', ['name', 'url'])


class Character(_BaseCharacter):
    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data

    def _index(self) -> str:
        return str(self.enname)

    def __getattr__(self, item):
        return self.__raw_data[item]

    @property
    def gender(self) -> Gender:
        return Gender.loads(self.__raw_data['gender'])

    @property
    def cnname(self) -> ChineseName:
        return ChineseName(self.__raw_data['cnname'])

    @property
    def enname(self) -> EnglishName:
        return EnglishName(self.__raw_data['enname'])

    @property
    def jpnames(self) -> List[JapaneseName]:
        return [JapaneseName(name) for name in self.__raw_data['jpnames']]

    @property
    def jpname(self) -> Optional[JapaneseName]:
        return JapaneseName(self.__raw_data['jpnames'][0])

    @property
    def level(self) -> Level:
        return Level.loads(self.__raw_data['rarity'])

    @property
    def skins(self) -> List[Skin]:
        return [Skin(item['name'], item['url']) for item in self.__raw_data['skins']]

    def _names(self) -> List[_BaseName]:
        return [self.cnname, self.enname, *self.jpnames]

    def __repr__(self):
        return f'<{type(self).__name__} {"/".join(map(str, self._names()))}, ' \
               f'{self.level}{"*" * self.level}, weapon: {self.weapon}, element: {self.element}>'

    def __eq__(self, other):
        if isinstance(other, Character):
            return self.index == other.index
        else:
            return (self.cnname and self.cnname == other) or \
                (self.enname and self.enname == other) or \
                any([jp == other for jp in self.jpnames])

    @classmethod
    def all(cls, timeout: int = 5, **kwargs) -> List['Character']:
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
