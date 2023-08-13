from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'pokemon'
    __official_name__ = 'Pokémon'
    __game_keywords__ = ['Pokémon', 'Evolution Chain', 'Evolution Line', 'Guardians Ultra', '포켓몬', 'Pocket Monsters', 'ポケモン', 'ミクリカップ', 'Pokemon', 'pokesmon', 'pokemon', 'mikurikatsupu']
    __pixiv_keyword__ = 'ポケモン'
    __pixiv_suffix__ = 'ポケモン'


register_game(Character)

