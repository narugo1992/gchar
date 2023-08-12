import re
from typing import List, Tuple, Optional, Iterator

from .name import ChineseName, JapaneseName, KoreanName, EnglishName
from .property import Rarity, Clazz, Burst
from ..base import Character as _BaseCharacter, Gender, Skin
from ..base.name import _BaseName


class Character(_BaseCharacter):
    __game_name__ = 'nikke'
    __official_name__ = 'Nikke: Goddess of Victory'
    __cnname_class__ = ChineseName
    __jpname_class__ = JapaneseName
    __enname_class__ = EnglishName

    def __init__(self, raw_data):
        self.__raw_data = raw_data

    def _index(self):
        return re.sub(r'[\W_]+', '_', self.__raw_data['enname'][0].lower()).strip('_')

    def _cnname(self):
        return self.__raw_data['cnname']

    def _jpname(self):
        return self.__raw_data['jpname'][0] if self.__raw_data['jpname'] else None

    def _jpnames(self):
        return self.__raw_data['jpname']

    def _enname(self):
        return self.__raw_data['enname'][0] if self.__raw_data['enname'] else None

    def _ennames(self):
        return self.__raw_data['enname']

    def _krname(self):
        return self.__raw_data['krname'][0] if self.__raw_data['krname'] else None

    @property
    def krname(self) -> Optional[KoreanName]:
        name = self._krname()
        return KoreanName(name) if name is not None else None

    def _krnames(self):
        return self.__raw_data['krname']

    @property
    def krnames(self) -> List[KoreanName]:
        return [KoreanName(name) for name in self._krnames()]

    def _names(self) -> List[_BaseName]:
        return [*_BaseCharacter._names(self), *self.krnames]

    def _gender(self):
        return Gender.FEMALE

    @property
    def rarity(self) -> Rarity:
        return Rarity.loads(self.__raw_data['rarity'])

    @property
    def clazz(self) -> str:
        return Clazz.loads(self.__raw_data['class'])

    @property
    def weapon_type(self) -> str:
        return self.__raw_data['weapontype']

    @property
    def manufacturer(self) -> str:
        return self.__raw_data['manufacturer']

    @property
    def burst(self) -> str:
        return Burst.loads(self.__raw_data['burst'])

    @property
    def code(self) -> str:
        return self.__raw_data['code']

    def _skins(self) -> List[Tuple[str, str]]:
        return [
            (skin['name'], skin['url'])
            for skin in self.__raw_data['skins']
        ]

    def _iter_formal_skins(self) -> Iterator[Skin]:
        for skin in self.skins:
            if 'anim' not in skin.name.lower():
                yield skin

    def _release_time(self):
        return self.__raw_data['release']['time']

    def _order(self):
        return self._release_time() or 0.0, 1 if self._is_extra() else 0

    def _is_extra(self) -> bool:
        return self._enname() and ':' in self._enname()

    def __repr__(self):
        return f'<{type(self).__name__} {"/".join(map(str, self._names()))}, ' \
               f'{self.rarity.name}({int(self.rarity)}{"*" * self.rarity}), ' \
               f'class: {self.clazz}, burst: {self.burst}, weapon_type: {self.weapon_type}>'
