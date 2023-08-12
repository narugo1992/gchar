from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'naruto'
    __official_name__ = 'NARUTO'
    __game_keywords__ = ['NARUTO']
    __pixiv_keyword__ = 'NARUTO'
    __pixiv_suffix__ = None


register_game(Character)
