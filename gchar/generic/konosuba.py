from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'konosuba'
    __official_name__ = 'Kono Subarashii Sekai ni Shukufuku wo!'
    __game_keywords__ = ['Kono Subarashii Sekai ni Shukufuku wo!', 'Kono Subarashii Sekai ni Shukufuku wo', 'Konosuba', "Konosuba - God's Blessing on This Wonderful World!", 'konosuba!', 'この素晴らしい世界に祝福を!', 'KonoSuba', 'konoSu Qing rashiiShi Jie niZhu Fu wo!']
    __pixiv_keyword__ = 'この素晴らしい世界に祝福を!'
    __pixiv_suffix__ = 'この素晴らしい世界に祝福を!'


register_game(Character)

