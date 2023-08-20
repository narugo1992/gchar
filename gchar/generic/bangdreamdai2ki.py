from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'bangdreamdai2ki'
    __official_name__ = 'BanG Dream! Dai 2-ki'
    __game_keywords__ = ['BanG Dream! Dai 2-ki', 'Bang Dream! 2nd Phase', 'Bang Dream! 2nd Season']
    __pixiv_keyword__ = None
    __pixiv_suffix__ = None


register_game(Character)

