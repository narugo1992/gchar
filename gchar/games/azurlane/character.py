from functools import lru_cache
from typing import List, Optional, Union

from .index import _refresh_index, get_index
from .name import EnglishName, JapaneseName, ChineseName, ChineseAliasName
from .property import BasicRarity, ResearchRarity, Group
from ..base import Character as _BaseCharacter
from ..base import Skin


class Character(_BaseCharacter):
    __cnname_class__ = ChineseName
    __enname_class__ = EnglishName
    __jpname_class__ = JapaneseName
    __alias_name_class__ = ChineseAliasName
    __index_func__ = lru_cache()(get_index)

    def __init__(self, raw_data: dict):
        self.__raw_data = raw_data

    def _index(self) -> str:
        return self.__raw_data['id']

    def _cnname(self):
        return self.__raw_data['cnname']['short']

    def _enname(self):
        return self.__raw_data['enname']['short']

    def _jpname(self):
        if self.__raw_data['jpnames']:
            return self.__raw_data['jpnames'][0]
        else:
            return None

    def _jpnames(self):
        return self.__raw_data['jpnames']

    def _alias_names(self):
        return self.__raw_data['alias']

    @property
    def rarity(self) -> Optional[Union[BasicRarity, ResearchRarity]]:
        val = self.__raw_data['rarity']
        try:
            return BasicRarity.loads(val)
        except (ValueError, TypeError):
            return ResearchRarity.loads(val)

    @property
    def group(self) -> Union[Group, str]:
        try:
            return Group.loads(self.__raw_data['group'])
        except (TypeError, ValueError):
            return self.__raw_data['group']

    @property
    def is_meta(self) -> bool:
        return self.__raw_data['is_meta']

    @property
    def is_refit(self) -> bool:
        return self.__raw_data['is_refit']

    @property
    def is_mu(self) -> bool:
        return self.__raw_data['is_mu']

    @property
    def is_chibi(self) -> bool:
        return self.__raw_data['is_chibi']

    def _is_extra(self) -> bool:
        return self.is_meta or self.is_refit or self.is_mu or self.is_chibi

    @property
    def skins(self) -> List[Skin]:
        return [Skin(item['name'], item['url']) for item in self.__raw_data['skins']]

    def __repr__(self):
        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'{self.rarity.label}({int(self.rarity)}{"*" * self.rarity}), ' \
               f'group: {self.group if isinstance(self.group, Group) else self.group}>'

    @classmethod
    def refresh_index(cls, timeout: int = 5):
        _refresh_index(timeout)
