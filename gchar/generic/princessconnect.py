from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'princessconnect'
    __official_name__ = 'Princess Connect'
    __game_keywords__ = ['Princess Connect', 'Princess Connect Re: Dive', 'プリンセスコネクト', 'purinsesukonekuto']
    __pixiv_keyword__ = 'プリンセスコネクト!Re:Dive'
    __pixiv_suffix__ = 'プリンセスコネクト!Re:Dive'


register_game(Character)

