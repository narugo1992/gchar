from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'idolmastercinderellagirls'
    __official_name__ = 'THE iDOLM@STER: Cinderella Girls'
    __game_keywords__ = ['THE iDOLM@STER: Cinderella Girls', 'Idolmaster: Cinderella Girls', 'アイドルマスターシンデレラガールズ', 'aidorumasutashindereragaruzu']
    __pixiv_keyword__ = 'アイドルマスターシンデレラガールズ'
    __pixiv_suffix__ = 'アイドルマスターシンデレラガールズ'


register_game(Character)

