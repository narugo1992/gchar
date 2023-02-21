from typing import List, Optional, Tuple

from .index import INDEXER
from .name import EnglishName, JapaneseName, ChineseName
from .property import Rarity, Weapon, Element
from ..base import Character as _BaseCharacter


class Character(_BaseCharacter):
    __cnname_class__ = ChineseName
    __enname_class__ = EnglishName
    __jpname_class__ = JapaneseName
    __indexer__ = INDEXER

    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data

    def _index(self) -> str:
        return str(self.enname)

    def _gender(self):
        return self.__raw_data['gender']

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

    def _skins(self) -> List[Tuple[str, str]]:
        return [(item['name'], item['url']) for item in self.__raw_data['skins']]

    def _release_time(self):
        release_info = self.__raw_data['release']
        return release_info['time']

    def _order(self):
        return self._release_time()

    def __repr__(self):
        return f'<{type(self).__name__} {"/".join(map(str, self._names()))}, ' \
               f'{self.gender.name.lower()}, {self.rarity}{"*" * self.rarity}, ' \
               f'weapon: {self.weapon}, element: {self.element}>'
