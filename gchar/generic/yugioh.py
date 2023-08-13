from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'yugioh'
    __official_name__ = 'Yu-Gi-Oh!'
    __game_keywords__ = ['Yu-Gi-Oh!', 'Yu Gi', 'Yuu Gi Ou', '遊☆戯☆王', '遊戯王', 'You Xi Wang']
    __pixiv_keyword__ = '遊戯王'
    __pixiv_suffix__ = '遊戯王'


register_game(Character)

