from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'fireemblem'
    __official_name__ = 'Fire Emblem'
    __game_keywords__ = ['ファイアーエムブレム', 'Fire Emblem', 'huaia-emuburemu']
    __pixiv_keyword__ = 'ファイアーエムブレム'
    __pixiv_suffix__ = 'FE'


register_game(Character)
