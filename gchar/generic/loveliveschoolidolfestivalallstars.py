from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'loveliveschoolidolfestivalallstars'
    __official_name__ = 'Love Live! School Idol Festival ALL STARS'
    __game_keywords__ = ['Love Live! School Idol Festival ALL STARS', 'ラブライブ！スクールアイドルフェスティバルall Stars', 'raburaibu!sukuruaidoruhuesuteibaruall Stars']
    __pixiv_keyword__ = None
    __pixiv_suffix__ = None


register_game(Character)

