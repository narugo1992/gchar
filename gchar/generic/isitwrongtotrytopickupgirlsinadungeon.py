from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'isitwrongtotrytopickupgirlsinadungeon'
    __official_name__ = 'Dungeon ni Deai wo Motomeru no wa Machigatteiru no Darou ka'
    __game_keywords__ = ['Dungeon ni Deai wo Motomeru no wa Machigatteiru no Darou ka', 'Danmachi', 'Is It Wrong To Try To Pick Up Girls In A Dungeon', 'ダンまち', 'ダンジョンに出会いを求めるのは間違っているのだろうか', 'danmachi', 'danziyonniChu Hui iwoQiu merunohaJian Wei tsuteirunodarouka']
    __pixiv_keyword__ = 'ダンジョンに出会いを求めるのは間違っているだろうか'
    __pixiv_suffix__ = 'ダンジョンに出会いを求めるのは間違っているだろうか'


register_game(Character)

