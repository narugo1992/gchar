from enum import IntEnum, unique


@unique
class Rarity(IntEnum):
    ONE = 0x1
    TWO = 0x2
    THREE = 0x3

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
class Clazz(IntEnum):
    GUARD = 1
    SHOOTER = 2
    WARRIOR = 3
    SPECIALIST = 4
    MEDIC = 5

    @classmethod
    def loads(cls, val) -> 'Clazz':
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            pval = val.upper()
            if pval in cls.__members__:
                return cls.__members__[pval]

            if pval in {'守卫'}:
                return cls.GUARD
            elif pval in {'射手'}:
                return cls.SHOOTER
            elif pval in {'战士'}:
                return cls.WARRIOR
            elif pval in {'特种'}:
                return cls.SPECIALIST
            elif pval in {'医师'}:
                return cls.MEDIC

            raise ValueError(f'Invalid class value - {val!r}.')
        elif isinstance(val, int):
            for _, item in cls.__members__.items():
                if item.value == val:
                    return item
            else:
                raise ValueError(f'Invalid class value - {val!r}.')
        else:
            raise TypeError(f'Invalid class type - {val!r}.')

    def __eq__(self, other):
        if isinstance(other, Clazz):
            return self.value == other.value
        else:
            try:
                return self == self.loads(other)
            except (TypeError, ValueError):
                return False
