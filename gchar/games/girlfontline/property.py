from enum import Enum, unique


@unique
class Level(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    EXTRA = 'EXTRA'

    @classmethod
    def loads(cls, val) -> 'Level':
        if isinstance(val, Level):
            return val
        elif isinstance(val, (int, str)):
            if isinstance(val, str):
                val = val.upper()

            for key, item in cls.__members__.items():
                if key == val:
                    return item
                elif item.value == val:
                    return item

            raise ValueError(f'Invalid level value - {val!r}.')
        else:
            raise TypeError(f'Invalid level type - {val!r}.')

    def __eq__(self, other):
        if isinstance(other, Level):
            return self.value == other.value
        else:
            try:
                return self == self.loads(other)
            except (TypeError, ValueError):
                return False


@unique
class Clazz(Enum):
    MG = 'MG'
    SMG = 'SMG'
    RF = 'RF'
    AR = 'AR'
    SG = 'SG'
    HG = 'HG'

    @classmethod
    def loads(cls, val) -> 'Clazz':
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            try:
                return cls.__members__[val.upper()]
            except KeyError:
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
