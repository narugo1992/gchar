from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'lovelivesunshine'
    __official_name__ = 'Love Live! Sunshine!!'
    __game_keywords__ = ['Love Live! Sunshine!!', 'Love Live! Sunshine', 'ラブライブ！サンシャイン!!', 'raburaibu!sanshiyain!!']
    __pixiv_keyword__ = 'ラブライブ!サンシャイン!!'
    __pixiv_suffix__ = 'ラブライブ!サンシャイン!!'


register_game(Character)

