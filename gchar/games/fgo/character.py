from collections import namedtuple
from typing import List, Optional, Union

from .index import get_index, _refresh_index
from .name import EnglishName, JapaneseName, ChineseName
from .property import Gender, Level, Clazz
from ..base import Character as _BaseCharacter

Skin = namedtuple('Skin', ['name', 'url'])


class Character(_BaseCharacter):
    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data

    @property
    def raw_data(self) -> dict:
        return dict(self.__raw_data)

    def _index(self) -> int:
        return self.__raw_data['id']

    @property
    def gender(self) -> Gender:
        return Gender.loads(self.__raw_data['gender'])

    @property
    def level(self) -> Level:
        return Level.loads(int(self.__raw_data['rarity']))

    @property
    def accessible(self) -> bool:
        return self.__raw_data['accessible']

    @property
    def clazz(self) -> Clazz:
        return Clazz.loads(self.__raw_data['class'])

    @property
    def cnname(self) -> ChineseName:
        return ChineseName(self.__raw_data['cnname'])

    @property
    def enname(self) -> Optional[EnglishName]:
        return EnglishName(self.__raw_data['enname']) if self.__raw_data['enname'] else None

    @property
    def jpname(self) -> Optional[JapaneseName]:
        return JapaneseName(self.__raw_data['jpname']) if self.__raw_data['jpname'] else None

    def _names(self) -> List[Union[EnglishName, ChineseName, JapaneseName]]:
        return [name for name in [self.cnname, self.enname, self.jpname] if name]

    def __repr__(self):
        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'{self.gender.name.lower()}, {self.level}{"*" * self.level}>'

    def __eq__(self, other):
        if isinstance(other, Character):
            return self.index == other.index
        else:
            return (self.cnname and self.cnname == other) or \
                   (self.enname and self.enname == other) or \
                   (self.jpname and self.jpname == other)

    @property
    def skins(self) -> List[Skin]:
        return [Skin(item['name'], item['url']) for item in self.__raw_data['skins']]

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
