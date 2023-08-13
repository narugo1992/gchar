from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'bangdream'
    __official_name__ = 'BanG Dream!'
    __game_keywords__ = ['BanG Dream!']
    __pixiv_keyword__ = 'BanG_Dream!'
    __pixiv_suffix__ = 'BanG_Dream!'


register_game(Character)

