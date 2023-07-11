from typing import List, Tuple

from .name import ChineseName, EnglishName
from .property import Rarity
from ..base.character import Character as _BaseCharacter


class Character(_BaseCharacter):
    __game_name__ = 'pathtonowhere'
    __official_name__ = 'Path To Nowhere'
    __cnname_class__ = ChineseName
    __enname_class__ = EnglishName

    def __init__(self, raw_data):
        self.__raw_data = raw_data

    def _index(self):
        return self.__raw_data['id']

    def _cnname(self):
        return self.__raw_data['cnname']

    def _jpname(self):
        return []

    def _enname(self):
        return self.__raw_data['enname']

    def _gender(self):
        return self.__raw_data['gender']

    def _skins(self) -> List[Tuple[str, str]]:
        return [(skin['name'], skin['url']) for skin in self.__raw_data['skins']]

    def _release_time(self):
        return None

    @property
    def rarity(self) -> Rarity:
        return Rarity.loads(self.__raw_data['rarity'])

    @property
    def job(self):
        return self.__raw_data['job']

    @property
    def group(self):
        return self.__raw_data['group']

    def __repr__(self):
        return f'<{type(self).__name__} {self._index()} - {"/".join(map(str, self._names()))}, ' \
               f'{self.rarity.name}({self.rarity.number}{"*" * self.rarity.number}), ' \
               f'job: {self.job}, group: {self.group}>'
