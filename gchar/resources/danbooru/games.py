from functools import lru_cache
from typing import Type, List, Tuple

from ...games.arknights import Character as ArknightsCharacter
from ...games.azurlane import Character as AzurLaneCharacter
from ...games.base import Character
from ...games.fgo import Character as FateGrandOrderCharacter
from ...games.genshin import Character as GenshinImpactCharacter
from ...games.girlsfrontline import Character as GirlsFrontLineCharacter
from ...games.neuralcloud import Character as NeuralChoudCharacter

_GAMES = [
    (ArknightsCharacter, 'arknights', 'arknights'),
    (FateGrandOrderCharacter, ['fate/grand_order', 'fate'], 'fgo'),
    (AzurLaneCharacter, 'azur_lane', 'azurlane'),
    (GenshinImpactCharacter, 'genshin_impact', 'genshin'),
    (GirlsFrontLineCharacter, 'girls\'_frontline', 'girlsfrontline'),
    (NeuralChoudCharacter, ['girls\'_frontline_nc', 'girls\'_frontline'], 'neuralcloud')
]


@lru_cache()
def _get_info_by_cls(cls: Type[Character]) -> Tuple[str, List[str]]:
    for cls_, game_names, name in _GAMES:
        if cls_ == cls or cls == name:
            return name, game_names

    raise TypeError(f'Unknown character class - {cls!r}.')  # pragma: no cover
