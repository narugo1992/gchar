from enum import IntEnum, unique, Enum


@unique
class Level(IntEnum):
    ONE = 0x1
    TWO = 0x2
    THREE = 0x3
    FOUR = 0x4
    FIVE = 0x5
    SIX = 0x6

    @classmethod
    def loads(cls, val) -> 'Level':
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
    GUARD = 0x1
    DEFENDER = 0x2
    CASTER = 0x3
    SNIPER = 0x4
    SPECIALIST = 0x5
    SUPPORTER = 0x6
    MEDIC = 0x7
    VANGUARD = 0x8

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
            val = val.lower().strip()
            if val in {'近卫', 'guard'}:
                return cls.GUARD
            elif val in {'重装', 'defender'}:
                return cls.DEFENDER
            elif val in {'术师', 'caster'}:
                return cls.CASTER
            elif val in {'狙击', 'sniper'}:
                return cls.SNIPER
            elif val in {'特种', 'specialist'}:
                return cls.SPECIALIST
            elif val in {'辅助', 'supporter'}:
                return cls.SUPPORTER
            elif val in {'医疗', 'medic'}:
                return cls.MEDIC
            elif val in {'先锋', 'vanguard'}:
                return cls.VANGUARD
            else:
                raise ValueError(f'Invalid class value - {val!r}.')

        else:
            raise TypeError(f'Invalid class type - {val!r}.')
