from enum import IntEnum, unique, Enum


@unique
class Gender(Enum):
    OTHER = 0x0
    MALE = 0x1
    FEMALE = 0x2

    def __eq__(self, other):
        if isinstance(other, Gender):
            return other.value == self.value
        else:
            try:
                other = Gender.loads(other)
            except (TypeError, ValueError):
                return False
            else:
                return other == self

    @classmethod
    def loads(cls, val) -> 'Gender':
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            nval = val.lower().strip()
            if nval in {'男', '男性', 'boy', 'man', 'male'}:
                return cls.MALE
            elif nval in {'女', '女性', 'girl', 'woman', 'female'}:
                return cls.FEMALE
            else:
                return cls.OTHER
        else:
            raise TypeError(f'Invalid gender type - {val!r}.')


@unique
class Rarity(IntEnum):
    ZERO = 0x0
    ONE = 0x1
    TWO = 0x2
    THREE = 0x3
    FOUR = 0x4
    FIVE = 0x5

    @classmethod
    def loads(cls, val) -> 'Rarity':
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
        if isinstance(other, Clazz):
            return self.value == other.value
        else:
            try:
                return self == self.loads(other)
            except (TypeError, ValueError):
                return False

    @classmethod
    def loads(cls, val) -> 'Clazz':
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            try:
                return cls.__members__[val.upper().strip()]
            except KeyError:
                raise ValueError(f'Invalid class value - {val!r}.')
        else:
            raise TypeError(f'Invalid class type - {val!r}.')
