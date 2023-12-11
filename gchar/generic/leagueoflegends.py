from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'leagueoflegends'
    __official_name__ = 'League of Legends'
    __game_keywords__ = ['League of Legends', '伝説のリーグ', 'Chuan Shuo nori-gu']
    __pixiv_keyword__ = 'League_of_Legends'
    __pixiv_suffix__ = 'League_of_Legends'


register_game(Character)

