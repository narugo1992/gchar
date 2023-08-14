from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'spyxfamily'
    __official_name__ = 'Spy × Family'
    __game_keywords__ = ['Spy × Family', '스파이패밀리', 'Spy x Family', 'スパイファミリー', 'seupaipaemilri', 'supaihuamiri']
    __pixiv_keyword__ = 'SPY×FAMILY'
    __pixiv_suffix__ = 'SPY×FAMILY'


register_game(Character)

