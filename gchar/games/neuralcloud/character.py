from typing import List, Tuple, Mapping, Optional

from .index import INDEXER
from .name import EnglishName, ChineseName, ChineseAliasName, JapaneseName
from .property import Clazz, Rarity
from ..base import Character as _BaseCharacter
from ..girlsfrontline import Character as GFCharacter
from ...utils import optional_lru_cache


class Character(_BaseCharacter):
    __enname_class__ = EnglishName
    __cnname_class__ = ChineseName
    __jpname_class__ = JapaneseName
    __alias_name_class__ = ChineseAliasName
    __indexer__ = INDEXER

    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data

    def _index(self) -> int:
        return self.__raw_data['id']

    def _cnname(self):
        return self.__raw_data['cnname']

    @property
    def cnnames(self):
        names = [self.__cnname_class__(name) for name in self._cnnames() if name]
        if self.gf_char:
            names.extend(self.gf_char.cnnames)

        return [name for name in names if name]

    def _jpname(self):
        return self.__raw_data['jpname']

    @property
    def jpnames(self):
        names = [self.__jpname_class__(name) for name in self._jpnames() if name]
        if self.gf_char:
            names.extend(self.gf_char.jpnames)
        return [name for name in names if name]

    def _enname(self):
        return self.__raw_data['enname']

    @property
    def ennames(self):
        names = [self.__enname_class__(name) for name in self._ennames() if name]
        if self.gf_char:
            names.extend(self.gf_char.ennames)
        return [name for name in names if name]

    def _alias_names(self):
        return self.__raw_data['alias']

    def _gender(self):
        return self.__raw_data['gender']

    @property
    def clazz(self) -> Clazz:
        return Clazz.loads(self.__raw_data['class'])

    @property
    def rarity(self) -> Rarity:
        return Rarity.loads(self.__raw_data['rarity'])

    @property
    def company(self) -> str:
        return self.__raw_data.get('company', None)

    @property
    def gf_char(self) -> Optional[GFCharacter]:
        if self.__raw_data["gf"]:
            return self._list_index_of_gf()[self.__raw_data["gf"]["id"]]
        else:
            return None

    def _skins(self) -> List[Tuple[str, str]]:
        return [(item['name'], item['url']) for item in self.__raw_data['skins']]

    def __repr__(self):
        # return f'233 {type(self).__name__} {self.index} {self._names()} {self.rarity} {self.clazz}'
        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'rarity: {self.rarity}{"*" * self.rarity}, clazz: {self.clazz.name}>'

    def _release_time(self):
        release_info = self.__raw_data['release']
        return release_info['time']

    def _order(self):
        return self._release_time()

    @classmethod
    @optional_lru_cache()
    def _list_index_of_gf(cls) -> Mapping[int, GFCharacter]:
        return {ch.index: ch for ch in GFCharacter.all(contains_extra=False)}
