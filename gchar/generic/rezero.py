from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'rezero'
    __official_name__ = 'Re:Zero Kara Hajimeru Isekai Seikatsu'
    __game_keywords__ = ['Re:Zero Kara Hajimeru Isekai Seikatsu', 'Re:zero', 'Re:zero − Starting Life In Another World', 'Re：ゼロから始める異世界生活', 'Re:ゼロから始める異世界生活', 'Re:Zero', 'Re:zero - Starting Life In Another World', 'Re:zerokaraShi meruYi Shi Jie Sheng Huo']
    __pixiv_keyword__ = 'Re:ゼロから始める異世界生活'
    __pixiv_suffix__ = 'Re:ゼロから始める異世界生活'


register_game(Character)

