from functools import lru_cache
from typing import List

from .index import _refresh_index, get_index
from .name import EnglishName, JapaneseName, ChineseName
from .property import Rarity, Clazz
from ..base import Character as _BaseCharacter
from ..base import Skin


class Character(_BaseCharacter):
    __enname_class__ = EnglishName
    __cnname_class__ = ChineseName
    __jpname_class__ = JapaneseName
    __index_func__ = lru_cache()(get_index)

    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data

    def _index(self) -> int:
        return self.__raw_data['id']

    def _cnname(self):
        return self.__raw_data['cnname']

    def _enname(self):
        return self.__raw_data['enname']

    def _jpname(self):
        return self.__raw_data['jpname']

    @property
    def rarity(self) -> Rarity:
        return Rarity.loads(self.__raw_data['rarity'])

    @property
    def clazz(self) -> Clazz:
        return Clazz.loads(self.__raw_data['class'])

    @property
    def skins(self) -> List[Skin]:
        return [Skin(item['desc'], item['url']) for item in self.__raw_data['skins']]

    def __repr__(self):
        if isinstance(self.rarity.value, int):
            _rarity_repr = f'{self.rarity.value}{"*" * self.rarity.value}'
        else:
            _rarity_repr = f'{self.rarity.name}'

        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'{_rarity_repr}, clazz: {self.clazz}>'

    @classmethod
    def refresh_index(cls, timeout: int = 5):
        _refresh_index(timeout)
