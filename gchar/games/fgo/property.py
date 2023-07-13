from enum import IntEnum, unique, Enum


@unique
class Rarity(IntEnum):
    """
    Enum representing the rarity of FGO characters.

    :cvar ZERO: Rarity 0
    :cvar ONE: Rarity 1
    :cvar TWO: Rarity 2
    :cvar THREE: Rarity 3
    :cvar FOUR: Rarity 4
    :cvar FIVE: Rarity 5
    """

    ZERO = 0x0
    ONE = 0x1
    TWO = 0x2
    THREE = 0x3
    FOUR = 0x4
    FIVE = 0x5

    @classmethod
    def loads(cls, val) -> 'Rarity':
        """
        Load a rarity from a value.

        :param val: The value to load the rarity from.
        :type val: Union[int, :class:`Rarity`]
        :returns: The loaded rarity.
        :rtype: :class:`Rarity`
        :raises ValueError: If the value is invalid.
        """
        if isinstance(val, cls):
            return val
        elif isinstance(val, int):
            for name, item in cls.__members__.items():
                if item.value == val:
                    return item.value

            raise ValueError(f'Invalid level value - {val!r}.')
        else:
            raise TypeError(f'Invalid level type - {val!r}.')


@unique
class Clazz(Enum):
    """
    Enum representing the class of FGO characters.

    :cvar SABER: Saber class
    :cvar LANCER: Lancer class
    :cvar ARCHER: Archer class
    :cvar RIDER: Rider class
    :cvar CASTER: Caster class
    :cvar ASSASSIN: Assassin class
    :cvar BERSERKER: Berserker class
    :cvar AVENGER: Avenger class
    :cvar RULER: Ruler class
    :cvar MOONCANCER: MoonCancer class
    :cvar SHIELDER: Shielder class
    :cvar ALTEREGO: AlterEgo class
    :cvar PRETENDER: Pretender class
    :cvar FOREIGNER: Foreigner class
    """

    SABER = 0x1
    LANCER = 0x2
    ARCHER = 0x3
    RIDER = 0x4
    CASTER = 0x5
    ASSASSIN = 0x6
    BERSERKER = 0x7
    AVENGER = 0x8
    RULER = 0x9
    MOONCANCER = 0xa
    SHIELDER = 0xb
    ALTEREGO = 0xc
    PRETENDER = 0xd
    FOREIGNER = 0xe

    def __eq__(self, other):
        """
        Compare the class with another class.

        :param other: The other class to compare.
        :type other: Union[:class:`Clazz`, str]
        :returns: True if the classes are equal, False otherwise.
        :rtype: bool
        """
        if isinstance(other, Clazz):
            return self.value == other.value
        else:
            try:
                return self == self.loads(other)
            except (TypeError, ValueError):
                return False

    @classmethod
    def loads(cls, val) -> 'Clazz':
        """
        Load a class from a value.

        :param val: The value to load the class from.
        :type val: Union[str, :class:`Clazz`]
        :returns: The loaded class.
        :rtype: :class:`Clazz`
        :raises ValueError: If the value is invalid.
        """
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            try:
                return cls.__members__[val.upper().strip()]
            except KeyError:
                raise ValueError(f'Invalid class value - {val!r}.')
        else:
            raise TypeError(f'Invalid class type - {val!r}.')
