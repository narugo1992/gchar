from collections import namedtuple
from typing import List, Optional, Union

from .index import get_index, _refresh_index
from .name import EnglishName, JapaneseName, ChineseName
from .property import BasicLevel, ResearchLevel, Group
from ..base import Character as _BaseCharacter
from ..base.name import _BaseName

Skin = namedtuple('Skin', ['name', 'url'])


class Character(_BaseCharacter):
    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data

    def _index(self) -> str:
        return self.__raw_data['id']

    @property
    def cnname(self) -> ChineseName:
        return ChineseName(self.__raw_data['cnname']['short'])

    @property
    def enname(self) -> EnglishName:
        raw = EnglishName(self.__raw_data['enname'])
        if self.group:
            return EnglishName(raw[1:])
        else:
            return raw

    @property
    def jpnames(self) -> List[JapaneseName]:
        return [JapaneseName(name) for name in self.__raw_data['jpnames']]

    @property
    def jpname(self) -> Optional[JapaneseName]:
        jpnames = self.jpnames
        if jpnames:
            return jpnames[0]
        else:
            return None

    @property
    def level(self) -> Optional[Union[BasicLevel, ResearchLevel]]:
        val = self.__raw_data['rarity']
        try:
            return BasicLevel.loads(val)
        except (ValueError, TypeError):
            try:
                return ResearchLevel.loads(val)
            except (ValueError, TypeError):
                return None

    @property
    def group(self) -> Optional[Group]:
        try:
            return Group.loads(self.__raw_data['group'])
        except (TypeError, ValueError):
            return None

    @property
    def skins(self) -> List[Skin]:
        return [Skin(item['name'], item['url']) for item in self.__raw_data['skins']]

    def _names(self) -> List[_BaseName]:
        return [self.cnname, self.enname, *self.jpnames]

    def __repr__(self):
        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'{self.level}{"*" * self.level}, group: {self.group.name if self.group else "<none>"}>'

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
