import re
from enum import IntEnum, unique, Enum


@unique
class Rarity(IntEnum):
    """
    Enum representing the rarity of a character in Blue Archive.
    """

    R = 0x1
    SR = 0x2
    SSR = 0x3

    @classmethod
    def loads(cls, val) -> 'Rarity':
        """
        Load a rarity value.

        :param val: The rarity value to load.
        :type val: Union[int, :class:`Rarity`]
        :return: The loaded rarity.
        :rtype: :class:`Rarity`
        :raises ValueError: If the value is invalid.
        :raises TypeError: If the type is invalid.
        """
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
    """
    Enum representing the weapon type of a character in Blue Archive.
    """

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
        """
        Load a weapon type value.

        :param val: The weapon type value to load.
        :type val: Union[str, WeaponType]
        :return: The loaded weapon type.
        :rtype: WeaponType
        :raises ValueError: If the value is invalid.
        :raises TypeError: If the type is invalid.
        """
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
    """
    Enum representing the role of a character in Blue Archive.
    """

    ATTACKER = 'ATTACKER'
    TACTICAL_SUPPORT = 'TACTICAL SUPPORT'
    HEALER = 'HEALER'
    SUPPORT = 'SUPPORT'
    TANK = 'TANK'

    @classmethod
    def loads(cls, val) -> 'Role':
        """
        Load a role value.

        :param val: The role value to load.
        :type val: Union[str, Role]
        :return: The loaded role.
        :rtype: Role
        :raises ValueError: If the value is invalid.
        :raises TypeError: If the type is invalid.
        """
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
    """
    Enum representing the attack type of a character in Blue Archive.
    """

    PENETRATION = 'PENETRATION'
    EXPLOSIVE = 'EXPLOSIVE'
    MYSTIC = 'MYSTIC'
    SONIC = 'SONIC'

    @classmethod
    def loads(cls, val) -> 'AttackType':
        """
        Load an attack type value.

        :param val: The attack type value to load.
        :type val: Union[str, AttackType]
        :return: The loaded attack type.
        :rtype: AttackType
        :raises ValueError: If the value is invalid.
        :raises TypeError: If the type is invalid.
        """
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
