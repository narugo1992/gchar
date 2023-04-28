import re
from typing import List, Tuple

from .index import INDEXER
from .name import EnglishName, JapaneseName, ChineseName, ChineseAliasName
from .property import Rarity, WeaponType, Role, AttackType
from ..base import Character as _BaseCharacter, Gender


class Character(_BaseCharacter):
    __cnname_class__ = ChineseName
    __enname_class__ = EnglishName
    __jpname_class__ = JapaneseName
    __alias_name_class__ = ChineseAliasName
    __indexer__ = INDEXER

    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data

    def _index(self) -> str:
        return re.sub(r'\W+', '_', self._enname().lower())

    def _cnname(self):
        return self.__raw_data['cnnames'][0]

    def _jpname(self):
        return self.__raw_data['jpnames'][0]

    def _enname(self):
        return self.__raw_data['ennames'][0]

    def _cnnames(self):
        return self.__raw_data['cnnames']

    def _jpnames(self):
        return self.__raw_data['jpnames']

    def _ennames(self):
        return self.__raw_data['ennames']

    def _gender(self):
        return Gender.FEMALE

    @property
    def rarity(self) -> Rarity:
        return Rarity.loads(self.__raw_data['data']['rarity'])

    @property
    def role(self) -> Role:
        return Role.loads(self.__raw_data['data']['role'])

    @property
    def weapon_type(self) -> WeaponType:
        return WeaponType.loads(self.__raw_data['data']['weapon_type'])

    @property
    def attack_type(self) -> AttackType:
        return AttackType.loads(self.__raw_data['data']['attack_type'])

    def _skins(self) -> List[Tuple[str, str]]:
        return [(item['name'], item['url']) for item in self.__raw_data['skins']]

    def _release_time(self):
        release_info = self.__raw_data['release']
        return release_info['time']

    def _order(self):
        return self._release_time()

    def __repr__(self):
        return f'<{type(self).__name__} {"/".join(map(str, self._names()))}, ' \
               f'{self.rarity.name}({int(self.rarity)}{"*" * self.rarity}), ' \
               f'role: {self.role}, attack: {self.attack_type}, weapon: {self.weapon_type}>'
