from ...games.arknights import Character as ArknightsCharacter
from ...games.azurlane import Character as AzurLaneCharacter
from ...games.fgo import Character as FateGrandOrderCharacter
from ...games.genshin import Character as GenshinImpactCharacter
from ...games.girlsfrontline import Character as GirlsFrontLineCharacter

_GAMES = [
    (ArknightsCharacter, 'アークナイツ'),
    (FateGrandOrderCharacter, 'Fate/GrandOrder', 'Fate'),
    (AzurLaneCharacter, 'アズールレーン'),
    (GenshinImpactCharacter, '原神'),
    (GirlsFrontLineCharacter, 'ドールズフロントライン'),
]
