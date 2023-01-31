from functools import lru_cache
from typing import List

from .index import _refresh_index, get_index
from .name import ChineseName, JapaneseName, EnglishName, ChineseAliasName
from .property import Gender, Rarity, Clazz
from ..base import Character as _BaseCharacter
from ..base import Skin


class Character(_BaseCharacter):
    __cnname_class__ = ChineseName
    __jpname_class__ = JapaneseName
    __enname_class__ = EnglishName
    __alias_name_class__ = ChineseAliasName
    __index_func__ = lru_cache()(get_index)

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
    def rarity(self) -> Rarity:
        return Rarity.loads(int(self.__raw_data['rarity']))

    @property
    def accessible(self) -> bool:
        return self.__raw_data['accessible']

    @property
    def clazz(self) -> Clazz:
        return Clazz.loads(self.__raw_data['class'])

    def _cnname(self):
        return self._cnnames()[0]

    def _cnnames(self):
        return self.__raw_data['cnnames']

    def _jpname(self):
        return self._jpnames()[0]

    def _jpnames(self):
        return self.__raw_data['jpnames']

    def _enname(self):
        return self._ennames()[0]

    def _ennames(self):
        return self.__raw_data['ennames']

    def _alias_names(self):
        return self.__raw_data['alias']

    def _is_extra(self) -> bool:
        for ch in self.__raw_data['similar']:
            id_, name = ch['id'], ch['name']
            if id_ < self.__raw_data['id'] and name == self.cnname:
                return True

        return False

    def __repr__(self):
        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'{self.gender.name.lower()}, {self.rarity}{"*" * self.rarity}>'

    @property
    def skins(self) -> List[Skin]:
        return [Skin(item['name'], item['url']) for item in self.__raw_data['skins']]

    @classmethod
    def refresh_index(cls, timeout: int = 5):
        _refresh_index(timeout)
