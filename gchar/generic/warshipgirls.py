from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'warshipgirls'
    __official_name__ = 'Zhan Jian Shao Nyu'
    __game_keywords__ = ['Zhan Jian Shao Nyu', 'Senkan Shoujo', 'Warship Girls', 'Warship Girls R', 'Warship Girls: Project R', 'Zhan Jian Shao Nyu R', '战舰少女', '战舰少女r', '戦艦少女', '戰艦少女', 'Zhan Jian Shao Nu', 'Zhan Jian Shao Nu r']
    __pixiv_keyword__ = '战舰少女'
    __pixiv_suffix__ = '战舰少女'


register_game(Character)

