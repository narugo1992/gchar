from typing import List, Tuple, Optional

from .name import ChineseName, EnglishName, JapaneseName, KoreanName
from .property import Rarity
from ..base import Character as _BaseCharacter, Gender
from ..base.name import _BaseName


class Character(_BaseCharacter):
    __game_name__ = 'starrail'
    __official_name__ = 'Honkai Star Rail'
    __cnname_class__ = ChineseName
    __enname_class__ = EnglishName
    __jpname_class__ = JapaneseName

    def __init__(self, raw_data):
        self.__raw_data = raw_data

    def _index(self):
        return self.__raw_data['id']

    def _cnname(self):
        return self.__raw_data['cnname']

    def _jpname(self):
        return self.__raw_data['jpname']

    def _enname(self):
        return self.__raw_data['enname']

    def _krname(self):
        return self.__raw_data['krname']

    @property
    def krname(self) -> Optional[KoreanName]:
        name = self._krname()
        return KoreanName(name) if name is not None else None

    def _krnames(self):
        name = self._krname()
        return [name] if name else []

    @property
    def krnames(self) -> List[KoreanName]:
        return [KoreanName(name) for name in self._krnames()]

    def _names(self) -> List[_BaseName]:
        return [*_BaseCharacter._names(self), *self.krnames]

    def _gender(self):
        return Gender.loads(self.__raw_data['gender'])

    def _skins(self) -> List[Tuple[str, str]]:
        return [
            (skin['name'], skin['url'])
            for skin in self.__raw_data['skins']
        ]

    def _release_time(self):
        return self.__raw_data['release']['time']

    def _order(self):
        return self._release_time(),

    @property
    def rarity(self):
        return Rarity.loads(self.__raw_data['rarity'])

    def __repr__(self):
        return f'<{type(self).__name__} {"/".join(map(str, self._names()))}, ' \
               f'{self.rarity.name}({int(self.rarity)}{"*" * self.rarity})>'
