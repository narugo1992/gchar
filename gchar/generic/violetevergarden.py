from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'violetevergarden'
    __official_name__ = 'Violet Evergarden'
    __game_keywords__ = ['Violet Evergarden', 'ヴァイオレット・エヴァーガーデン', 'vuaioretsutoevuagaden']
    __pixiv_keyword__ = 'ヴァイオレット・エヴァーガーデン'
    __pixiv_suffix__ = 'ヴァイオレット・エヴァーガーデン'


register_game(Character)

