from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'theidolmster'
    __official_name__ = 'THE iDOLM@STER'
    __game_keywords__ = ['THE iDOLM@STER', 'Puchimas!!: Petit Petit Idolm@ster', 'Puchimas!: Petit Idolm@ster', 'The Idolm@ster Movie: Kagayaki No Mukougawa E!', 'The Idolm@ster Shiny Festa', 'The Idolm@ster: Platinum Stars', 'The Idolmaster', 'アイドルマスター', 'aidorumasuta']
    __pixiv_keyword__ = 'アイドルマスター'
    __pixiv_suffix__ = 'アイドルマスター'


register_game(Character)

