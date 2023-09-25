from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'shoujokagekirevuestarlight'
    __official_name__ = 'Shoujo☆Kageki Revue Starlight'
    __game_keywords__ = ['Shoujo☆Kageki Revue Starlight', 'Shoujo Kageki Revue Starlight', '少女☆歌劇 レヴュー・スタァライト',
                         'ShoujoKageki Revue Starlight', 'Shao Nu Ge Ju  revuyusutaaraito']
    __pixiv_keyword__ = '少女☆歌劇レヴュースタァライト'
    __pixiv_suffix__ = '少女☆歌劇レヴュースタァライト'


register_game(Character)
