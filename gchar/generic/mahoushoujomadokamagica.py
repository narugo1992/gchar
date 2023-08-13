from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'mahoushoujomadokamagica'
    __official_name__ = 'Mahou Shoujo Madoka☆Magica'
    __game_keywords__ = ['Mahou Shoujo Madoka☆Magica', 'Puella Magi Madoka Magica', 'Mahou Shoujo Madoka Magica', 'Magical Girl Madoka Magica', '마법소녀 마도카 마기카', '魔法少女まどか★マギカ', '魔法少女まどか☆マギカ', '魔法少女小圓', 'Mahou Shoujo MadokaMagica', 'mabeobsonyeo madoka magika', 'Mo Fa Shao Nu madokamagika', 'Mo Fa Shao Nu Xiao Yuan']
    __pixiv_keyword__ = '魔法少女まどか☆マギカ'
    __pixiv_suffix__ = '魔法少女まどか☆マギカ'


register_game(Character)

