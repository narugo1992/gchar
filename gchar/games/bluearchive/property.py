import re
from enum import IntEnum, unique, Enum


@unique
class Rarity(IntEnum):
    R = 0x1
    SR = 0x2
    SSR = 0x3

    @classmethod
    def loads(cls, val) -> 'Rarity':
        if isinstance(val, cls):
            return val
        elif isinstance(val, int):
            for name, item in cls.__members__.items():
                if item.value == val:
                    return item

            raise ValueError(f'Invalid level value - {val!r}.')
        else:
            raise TypeError(f'Invalid level type - {val!r}.')


@unique
class WeaponType(Enum):
    SMG = 'SMG'
    RL = 'RL'
    HG = 'HG'
    FT = 'FT'
    SG = 'SG'
    MT = 'MT'
    AR = 'AR'
    MG = 'MG'
    GL = 'GL'
    SR = 'SR'
    RG = 'RG'

    @classmethod
    def loads(cls, val) -> 'WeaponType':
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            pval = val.upper()
            if pval in cls.__members__:
                return cls.__members__[pval]

            raise ValueError(f'Invalid class value - {val!r}.')
        else:
            raise TypeError(f'Invalid class type - {val!r}.')

    def __eq__(self, other):
        if isinstance(other, WeaponType):
            return self.value == other.value
        else:
            try:
                return self == self.loads(other)
            except (TypeError, ValueError):
                return False


@unique
class Role(Enum):
    ATTACKER = 'ATTACKER'
    TACTICAL_SUPPORT = 'TACTICAL SUPPORT'
    HEALER = 'HEALER'
    SUPPORT = 'SUPPORT'
    TANK = 'TANK'

    @classmethod
    def loads(cls, val) -> 'Role':
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            pval = re.sub(r'\W+', '_', val.upper()).strip('_')
            if pval in cls.__members__:
                return cls.__members__[pval]

            raise ValueError(f'Invalid class value - {val!r}.')
        else:
            raise TypeError(f'Invalid class type - {val!r}.')

    def __eq__(self, other):
        if isinstance(other, Role):
            return self.value == other.value
        else:
            try:
                return self == self.loads(other)
            except (TypeError, ValueError):
                return False


@unique
class AttackType(Enum):
    PENETRATION = 'PENETRATION'
    EXPLOSIVE = 'EXPLOSIVE'
    MYSTIC = 'MYSTIC'

    @classmethod
    def loads(cls, val) -> 'AttackType':
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            pval = re.sub(r'\W+', '_', val.upper()).strip('_')
            if pval in cls.__members__:
                return cls.__members__[pval]

            raise ValueError(f'Invalid class value - {val!r}.')
        else:
            raise TypeError(f'Invalid class type - {val!r}.')

    def __eq__(self, other):
        if isinstance(other, AttackType):
            return self.value == other.value
        else:
            try:
                return self == self.loads(other)
            except (TypeError, ValueError):
                return False
