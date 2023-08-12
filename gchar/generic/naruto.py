from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'naruto'
    __official_name__ = 'NARUTO'
    __game_keywords__ = ['NARUTO']


register_game(Character)
