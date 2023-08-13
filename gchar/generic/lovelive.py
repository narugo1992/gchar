from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'lovelive'
    __official_name__ = 'Love Live!'
    __game_keywords__ = ['Love Live!', 'ラブライブ！ School Idol Project', 'raburaibu! School Idol Project']
    __pixiv_keyword__ = 'ラブライブ!'
    __pixiv_suffix__ = 'ラブライブ!'


register_game(Character)

