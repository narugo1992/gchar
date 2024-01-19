from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'granbluefantasy'
    __official_name__ = 'Granblue Fantasy'
    __game_keywords__ = ['Granblue Fantasy', 'Gbf', 'グラブル', 'グランブルーファンタジー', 'guraburu', 'guranburu-huantazi-']
    __pixiv_keyword__ = 'グランブルーファンタジー'
    __pixiv_suffix__ = 'グランブルーファンタジー'


register_game(Character)

