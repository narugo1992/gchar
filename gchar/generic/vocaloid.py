from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'vocaloid'
    __official_name__ = 'VOCALOID'
    __game_keywords__ = ['VOCALOID', 'V1', 'V2', 'ボーカロイド', 'bokaroido']
    __pixiv_keyword__ = 'VOCALOID'
    __pixiv_suffix__ = 'VOCALOID'


register_game(Character)

