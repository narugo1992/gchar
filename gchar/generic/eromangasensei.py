from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'eromangasensei'
    __official_name__ = 'Eromanga Sensei'
    __game_keywords__ = ['Eromanga Sensei', 'Ero Manga Sensei', 'Ero Manga Sensei - Imouto To Akazu No Ma', 'Ero Manga Sensei - My Little Sister And The Locked Room', 'Eromanga Sensei - Imouto To Akazu No Ma', 'Eromanga-sensei', 'エロマンガ先生', 'eromangaXian Sheng']
    __pixiv_keyword__ = 'エロマンガ先生'
    __pixiv_suffix__ = 'エロマンガ先生'


register_game(Character)

