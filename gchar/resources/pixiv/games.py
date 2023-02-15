import os
from functools import lru_cache
from typing import Type, Tuple, Union

from ...games import __file__ as __games_file__
from ...games.arknights import Character as ArknightsCharacter
from ...games.azurlane import Character as AzurLaneCharacter
from ...games.base import Character
from ...games.fgo import Character as FateGrandOrderCharacter
from ...games.genshin import Character as GenshinImpactCharacter
from ...games.girlsfrontline import Character as GirlsFrontLineCharacter
from ...games.neuralcloud import Character as NeuralCloudCharacter

_GAMES = [
    (ArknightsCharacter, 'arknights', 'アークナイツ'),
    (FateGrandOrderCharacter, 'fgo', 'Fate/GrandOrder', 'Fate'),
    (AzurLaneCharacter, 'azurlane', 'アズールレーン'),
    (GenshinImpactCharacter, 'genshin', '原神'),
    (GirlsFrontLineCharacter, 'girlsfrontline', 'ドールズフロントライン'),
    (NeuralCloudCharacter, 'neuralcloud', '云图计划')
]


@lru_cache()
def _get_items_from_ch_type(cls: Union[Type[Character], str]) -> Tuple[Tuple[Type[Character], str], str, str]:
    for item in _GAMES:
        if len(item) == 3:
            _cls, game_name, game_tag = item
            base_tag = game_tag
        elif len(item) == 4:
            _cls, game_name, game_tag, base_tag = item
        else:
            assert False, f'Invalid games item - {item!r}.'  # pragma: no cover

        if cls == _cls or cls == game_name:
            return (_cls, game_name), game_tag, base_tag

    raise TypeError(f'Unknown character type - {cls}.')  # pragma: no cover


_GAMES_DIRECTORY = os.path.dirname(__games_file__)


def _local_names_file(name: str) -> str:
    return os.path.join(_GAMES_DIRECTORY, name, 'pixiv_names.json')


def _local_characters_file(name: str) -> str:
    return os.path.join(_GAMES_DIRECTORY, name, 'pixiv_characters.json')


def _local_alias_file(name: str) -> str:
    return os.path.join(_GAMES_DIRECTORY, name, 'pixiv_alias.yaml')
