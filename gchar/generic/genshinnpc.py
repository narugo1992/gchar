from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'genshinnpc'
    __official_name__ = 'Genshin Impact'
    __game_keywords__ = ['Genshin Impact', 'Wonsin', '原神', 'Yuan Shen']
    __pixiv_keyword__ = '原神'
    __pixiv_suffix__ = '原神'


register_game(Character)

