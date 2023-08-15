from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'kantaicollection'
    __official_name__ = 'Kantai Collection'
    __game_keywords__ = ['Kantai Collection', '칸코레', '캉코레', '艦隊これくしょん -艦これ', '艦隊これくしょん', 'kankore', 'kangkore', 'Jian Dui korekushiyon -Jian kore', 'Jian Dui korekushiyon']
    __pixiv_keyword__ = '艦隊これくしょん'
    __pixiv_suffix__ = '艦隊これくしょん'


register_game(Character)

