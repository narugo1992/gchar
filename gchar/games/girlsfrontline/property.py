from enum import Enum, unique


@unique
class Rarity(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    EXTRA = 'EXTRA'

    @classmethod
    def loads(cls, val) -> 'Rarity':
        if isinstance(val, Rarity):
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
        if isinstance(other, Rarity):
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
            pval = val.upper()
            if pval in cls.__members__:
                return cls.__members__[pval]

            if pval in {'手枪', '手'}:
                return cls.HG
            elif pval in {'突击步枪', '突'}:
                return cls.AR
            elif pval in {'步枪', '步'}:
                return cls.RF
            elif pval in {'冲锋枪', '冲'}:
                return cls.SMG
            elif pval in {'机枪', '机'}:
                return cls.MG
            elif pval in {'霰弹枪', '霰'}:
                return cls.SG

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
