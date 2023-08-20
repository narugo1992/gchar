from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'theidolmstermillionlive'
    __official_name__ = 'THE iDOLM@STER: Million Live!'
    __game_keywords__ = ['THE iDOLM@STER: Million Live!', 'The Idolm@ster Million Live!: Theater Days', 'THE iDOLM@STER: Million Live', 'アイドルマスターミリオンライブ!', '아이돌마스터 밀리언 라이브', 'aidorumasutamirionraibu!', 'aidolmaseuteo milrieon raibeu']
    __pixiv_keyword__ = 'アイドルマスターミリオンライブ!'
    __pixiv_suffix__ = 'アイドルマスターミリオンライブ!'


register_game(Character)

