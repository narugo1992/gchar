from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'theidolmstershinycolors'
    __official_name__ = 'THE iDOLM@STER: SHINY COLORS'
    __game_keywords__ = ['THE iDOLM@STER: SHINY COLORS', 'The Idolm@ster Shiny Colors', 'The Idolmaster Shiny Colors', 'アイドルマスター シャイニーカラーズ', 'aidorumasuta shiyainikarazu']
    __pixiv_keyword__ = 'アイドルマスターシャイニーカラーズ'
    __pixiv_suffix__ = 'アイドルマスターシャイニーカラーズ'


register_game(Character)

