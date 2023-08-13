from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'touhou'
    __official_name__ = 'Touhou'
    __game_keywords__ = ['Touhou', 'Touhou Project', 'Project Shrine Maiden', 'Tōhō Project', '東方project', '동방', '東方', '東方プロジェクト', 'Toho Project', 'Dong Fang project', 'dongbang', 'Dong Fang', 'Dong Fang puroziekuto']
    __pixiv_keyword__ = '東方'
    __pixiv_suffix__ = '東方'


register_game(Character)

