from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'eiyuudensetsusennokiseki'
    __official_name__ = 'Eiyuu Densetsu: Sen no Kiseki'
    __game_keywords__ = ['Eiyuu Densetsu: Sen no Kiseki', 'Eyiyuu Densetsu: Sen No Kiseki', 'Sen No Kiseki',
                         'The Legend Of Heroes: Trails Of Cold Steel', '英雄伝説 閃の軌跡',
                         'Ying Xiong Chuan Shuo  Shan noGui Ji']
    __pixiv_keyword__ = '閃の軌跡'
    __pixiv_suffix__ = None


register_game(Character)
