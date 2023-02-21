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
            "data-cn": "龙舌兰",
            "data-position": "近战位",
            "data-en": "Tequila",
            "data-sex": "男",
            "data-tag": "爆发",
            "data-race": "佩洛",
            "data-rarity": "4",
            "data-class": "近卫",
            "data-approach": "活动获得",
            "data-camp": "玻利瓦尔",
            "data-team": "",
            "data-des": "近卫干员龙舌兰，在战场上也面带笑容。",
            "data-feature": "通常不攻击且阻挡数为0，技能未开启时<span style=\"color:#00B0FF;\">40</span>
                             秒内攻击力逐渐提升至最高<span style=\"color:#00B0FF;\">+200%</span>且技能结束时重置攻击力",
            "data-str": "标准",
            "data-flex": "标准",
            "data-tolerance": "普通",
            "data-plan": "优良",
            "data-skill": "标准",
            "data-adapt": "普通",
            "data-moredes": "别担心，他会把一切都安排妥帖。",
            "data-icon": "//prts.wiki/images/4/42/%E5%A4%B4%E5%83%8F_%E9%BE%99%E8%88%8C%E5%85%B0.png",
            "data-half": "//prts.wiki/images/thumb/3/34/%E5%8D%8A%E8%BA%AB%E5%83%8F_%E9%BE%99%E8%88%8C%E5%85
                          %B0_1.png/110px-%E5%8D%8A%E8%BA%AB%E5%83%8F_%E9%BE%99%E8%88%8C%E5%85%B0_1.png",
            "data-ori-hp": "1,871",
            "data-ori-atk": "137",
            "data-ori-def": "238",
            "data-ori-res": "15",
            "data-ori-dt": "80s",
            "data-ori-dc": "11→13",
            "data-ori-block": "2→2→3",
            "data-ori-cd": "1.2s",
            "data-index": "BV12",
            "data-jp": "テキーラ",
            "data-birthplace": "玻利瓦尔",
            "data-nation": "玻利瓦尔",
            "data-group": ""
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
        return self.__raw_data['data-index']

    def _gender(self):
        return self.__raw_data['data-sex']

    @property
    def rarity(self) -> Level:
        return Level.loads(int(self.__raw_data['data-rarity']) + 1)

    @property
    def clazz(self) -> Clazz:
        return Clazz.loads(self.__raw_data['data-class'])

    def _cnname(self):
        return self.__raw_data['data-cn']

    def _enname(self):
        return self.__raw_data.get('data-en', None)

    def _jpname(self):
        return self.__raw_data.get('data-jp', None)

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
        return release_info['time'], release_info['index']

    def _release_time(self):
        _release_time, _ = self._order()
        return _release_time

    def __repr__(self):
        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'{self.gender.name.lower()}, {self.rarity}{"*" * self.rarity}>'
