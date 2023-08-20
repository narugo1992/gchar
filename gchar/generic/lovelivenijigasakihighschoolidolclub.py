from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'lovelivenijigasakihighschoolidolclub'
    __official_name__ = 'Love Live! Nijigasaki Gakuen School Idol Doukoukai'
    __game_keywords__ = ['Love Live! Nijigasaki Gakuen School Idol Doukoukai', 'Love Live! Nijigasaki High School Idol Club', 'ラブライブ！虹ヶ咲学園スクールアイドル同好会', 'raburaibu!Hong keXiao Xue Yuan sukuruaidoruTong Hao Hui']
    __pixiv_keyword__ = 'ラブライブ!虹ヶ咲学園スクールアイドル同好会'
    __pixiv_suffix__ = 'ラブライブ!虹ヶ咲学園スクールアイドル同好会'


register_game(Character)

