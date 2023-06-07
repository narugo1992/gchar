import math
from typing import List, Tuple

from .index import _KNOWN_DATA_FIELDS, INDEXER
from .name import EnglishName, JapaneseName, ChineseName, ChineseAliasName
from .property import Level, Clazz
from ..base import Character as _BaseCharacter


class Character(_BaseCharacter):
    """
    Here is an example of operator data from prts.wiki

    .. code-block::
        :linenos:
        :language: text

        {
            "data-adapt": "普通",
            "data-atk": "102",
            "data-birth_place": "未公开",
            "data-block": "1",
            "data-cost": "3",
            "data-def": "28",
            "data-en": "U-Official",
            "data-flex": "缺陷",
            "data-group": "",
            "data-hp": "385",
            "data-id": "U007",
            "data-interval": "1.3s",
            "data-ja": "",
            "data-logo": "罗德岛",
            "data-nation": "罗德岛",
            "data-obtain_method": "活动获得",
            "data-phy": "普通",
            "data-plan": "缺陷",
            "data-position": "远程位",
            "data-potential": "`",
            "data-profession": "辅助",
            "data-race": "札拉克",
            "data-rarity": "0",
            "data-re_deploy": "200s",
            "data-res": "0",
            "data-sex": "女",
            "data-skill": "缺陷",
            "data-sortid": "274",
            "data-subprofession": "吟游者",
            "data-tag": "控场",
            "data-team": "",
            "data-tolerance": "普通",
            "data-trust": "120,20,0",
            "data-zh": "U-Official"
        }
    """
    __cnname_class__ = ChineseName
    __enname_class__ = EnglishName
    __jpname_class__ = JapaneseName
    __alias_name_class__ = ChineseAliasName
    __indexer__ = INDEXER

    def __init__(self, raw_data: dict):
        self.__origin_raw_data = raw_data
        self.__raw_data = raw_data['data']
        self.__skins = raw_data['skins']
        self.__is_extra = None

    def _index(self):
        return self.__raw_data.get('data-index') or self.__raw_data.get('data-id')

    def _gender(self):
        return self.__raw_data['data-sex']

    @property
    def rarity(self) -> Level:
        return Level.loads(int(self.__raw_data['data-rarity']) + 1)

    @property
    def clazz(self) -> Clazz:
        return Clazz.loads(self.__raw_data.get('data-class') or self.__raw_data.get('data-profession'))

    def _cnname(self):
        return self.__raw_data.get('data-cn') or self.__raw_data.get('data-zh') or None

    def _enname(self):
        return self.__raw_data.get('data-en') or None

    def _jpname(self):
        return self.__raw_data.get('data-jp') or self.__raw_data.get('data-ja') or None

    def _alias_names(self):
        return list(self.__origin_raw_data.get('alias', []) or [])

    def _skins(self) -> List[Tuple[str, str]]:
        return [(item['name'], item['url']) for item in self.__skins]

    def __getattr__(self, item: str):
        key = 'data-' + item.replace('_', '-')
        if key in _KNOWN_DATA_FIELDS:
            return self.__raw_data.get(key, None)
        else:
            return object.__getattribute__(self, item)

    def _is_extra(self) -> bool:
        return (self.enname and 'the' in self.enname) or \
            (self.enname == 'amiya' and self.cnname != '阿米娅')

    def _order(self):
        release_info = self.__origin_raw_data['release']
        _release_time = release_info['time'] if release_info['time'] is not None else math.inf
        _release_index = release_info['index'] if release_info['index'] is not None else math.inf
        return _release_time, _release_index

    def _release_time(self):
        _release_time, _ = self._order()
        return _release_time

    def __repr__(self):
        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'{self.gender.name.lower()}, {self.rarity}{"*" * self.rarity}>'
