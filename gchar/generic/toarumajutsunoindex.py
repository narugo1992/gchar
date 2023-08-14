from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'toarumajutsunoindex'
    __official_name__ = 'To Aru Majutsu no Index'
    __game_keywords__ = ['To Aru Majutsu no Index', 'A Certain Magical Index', 'To Aru Majutsu No Index 2', 'とある魔術の禁書目録', '어마금', 'toaruMo Shu noJin Shu Mu Lu', 'eomageum']
    __pixiv_keyword__ = 'とある魔術の禁書目録'
    __pixiv_suffix__ = 'とある魔術の禁書目録'


register_game(Character)

