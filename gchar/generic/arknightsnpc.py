from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'arknightsnpc'
    __official_name__ = 'Arknights'
    __game_keywords__ = ['Arknights', 'アークナイツ', 'akunaitsu']
    __pixiv_keyword__ = 'アークナイツ'
    __pixiv_suffix__ = 'アークナイツ'


register_game(Character)

