from functools import lru_cache
from typing import List, Optional

from .index import _refresh_index, get_index
from .name import EnglishName, JapaneseName, ChineseName
from .property import Gender, Rarity, Weapon, Element
from ..base import Character as _BaseCharacter
from ..base import Skin


class Character(_BaseCharacter):
    __cnname_class__ = ChineseName
    __enname_class__ = EnglishName
    __jpname_class__ = JapaneseName
    __index_func__ = lru_cache()(get_index)

    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data

    def _index(self) -> str:
        return str(self.enname)

    @property
    def gender(self) -> Gender:
        return Gender.loads(self.__raw_data['gender'])

    def _cnname(self):
        return self.__raw_data['cnname']

    def _enname(self):
        return self.__raw_data['enname']

    def _jpname(self):
        _jpnames = self._jpnames()
        if _jpnames:
            return _jpnames[0]
        else:
            return None  # pragma: no cover

    def _jpnames(self):
        return self.__raw_data['jpnames']

    @property
    def rarity(self) -> Rarity:
        return Rarity.loads(self.__raw_data['rarity'])

    @property
    def weapon(self) -> Weapon:
        return Weapon.loads(self.__raw_data['weapon'])

    @property
    def element(self) -> Optional[Element]:
        element = self.__raw_data['element']
        if element:
            return Element.loads(element)
        else:
            return None

    @property
    def skins(self) -> List[Skin]:
        return [Skin(item['name'], item['url']) for item in self.__raw_data['skins']]

    def __repr__(self):
        return f'<{type(self).__name__} {"/".join(map(str, self._names()))}, ' \
               f'{self.gender.name.lower()}, {self.rarity}{"*" * self.rarity}, ' \
               f'weapon: {self.weapon}, element: {self.element}>'

    @classmethod
    def refresh_index(cls, timeout: int = 5):
        _refresh_index(timeout)
