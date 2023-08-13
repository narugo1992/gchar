from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'swordartonline'
    __official_name__ = 'Sword Art Online'
    __game_keywords__ = ['Sword Art Online', 'Sao', 'ソードアート・オンライン', 'sodoatoonrain']
    __pixiv_keyword__ = 'SAO'
    __pixiv_suffix__ = 'SAO'


register_game(Character)

