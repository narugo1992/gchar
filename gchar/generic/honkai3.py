from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'honkai3'
    __official_name__ = 'Houkai 3rd'
    __game_keywords__ = ['Houkai 3rd', 'Honkai Impact', '崩坏3rd', 'Honkai Impact 3rd', '崩壊3rd', 'Beng Pi 3rd', 'Beng Huai 3rd']
    __pixiv_keyword__ = '崩坏3rd'
    __pixiv_suffix__ = '崩坏3rd'


register_game(Character)

