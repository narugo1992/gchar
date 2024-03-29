from typing import List, Tuple, Iterator

import math

from .name import EnglishName, JapaneseName, ChineseName, ChineseAliasName
from .property import Rarity, Clazz
from ..base import Character as _BaseCharacter, Skin


class Character(_BaseCharacter):
    __game_name__ = 'girlsfrontline'
    __official_name__ = 'Girls\' Frontline'
    __game_keywords__ = ['girls\'_frontline', 'ドールズフロントライン', 'gfl', 'girlsfrontline']
    __pixiv_keyword__ = 'ドールズフロントライン'
    __pixiv_suffix__ = 'ドールズフロントライン'
    __enname_class__ = EnglishName
    __cnname_class__ = ChineseName
    __jpname_class__ = JapaneseName
    __alias_name_class__ = ChineseAliasName

    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data

    def _index(self) -> int:
        return self.__raw_data['id']

    def _cnname(self):
        return self.__raw_data['cnname']

    def _cnnames(self):
        return self.__raw_data['cnnames']

    def _enname(self):
        return self.__raw_data['enname']

    def _jpname(self):
        return self.__raw_data['jpname']

    def _custom_alias_names(self):
        return self.__raw_data['alias']

    def _gender(self):
        return 'female'

    @property
    def rarity(self) -> Rarity:
        return Rarity.loads(self.__raw_data['rarity'])

    @property
    def clazz(self) -> Clazz:
        return Clazz.loads(self.__raw_data['class'])

    def _skins(self) -> List[Tuple[str, str]]:
        return [(item['desc'], item['url']) for item in self.__raw_data['skins']]

    def _iter_formal_skins(self) -> Iterator[Skin]:
        for skin in self.skins:
            if 'profile' not in skin.name.lower():
                yield skin

    def _release_time(self):
        release_info = self.__raw_data['release']
        return release_info['time']

    def _order(self):
        _release_time = self._release_time()
        return _release_time if _release_time is not None else math.inf

    def __repr__(self):
        if isinstance(self.rarity.value, int):
            _rarity_repr = f'{self.rarity.value}{"*" * self.rarity.value}'
        else:
            _rarity_repr = f'{self.rarity.name}'

        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'{_rarity_repr}, clazz: {self.clazz}>'
