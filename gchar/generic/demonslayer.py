from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'demonslayer'
    __official_name__ = 'Kimetsu no Yaiba'
    __game_keywords__ = ['Kimetsu no Yaiba', 'Blade Of Demon Destruction', 'Demon Slayer: Kimetsu No Yaiba', 'Kny', 'Demon Slayer', '鬼滅の刃', 'Gui Mie noRen']
    __pixiv_keyword__ = '鬼滅の刃'
    __pixiv_suffix__ = '鬼滅の刃'


register_game(Character)

