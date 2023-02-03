from enum import unique, Enum, IntEnum


@unique
class Rarity(IntEnum):
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
class Weapon(Enum):
    CATALYST = 0x1
    CLAYMORE = 0x2
    SWORD = 0x3
    BOW = 0x4
    POLEARM = 0x5

    def __eq__(self, other):
        if isinstance(other, Weapon):
            return other.value == self.value
        else:
            try:
                other = Weapon.loads(other)
            except (TypeError, ValueError):
                return False
            else:
                return other == self

    @classmethod
    def loads(cls, val) -> 'Weapon':
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            pval = val.upper().strip()
            if pval in cls.__members__:
                return cls.__members__[pval]

            if pval in {'单手剑'}:
                return cls.SWORD
            elif pval in {'双手剑'}:
                return cls.CLAYMORE
            elif pval in {'长柄武器'}:
                return cls.POLEARM
            elif pval in {'法器'}:
                return cls.CATALYST
            elif pval in {'弓'}:
                return cls.BOW

            raise ValueError(f'Invalid weapon value - {val!r}.')
        else:
            raise TypeError(f'Invalid weapon type - {val!r}.')


@unique
class Element(Enum):
    PYRO = 0x1
    ANEMO = 0x2
    CRYO = 0x3
    ELECTRO = 0x4
    DENDRO = 0x5
    GEO = 0x6
    HYDRO = 0x7

    def __eq__(self, other):
        if isinstance(other, Element):
            return other.value == self.value
        else:
            try:
                other = Element.loads(other)
            except (TypeError, ValueError):
                return False
            else:
                return other == self

    @classmethod
    def loads(cls, val) -> 'Element':
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            pval = val.upper().strip()
            if pval in cls.__members__:
                return cls.__members__[pval]

            if pval in {'火'}:
                return cls.PYRO
            elif pval in {'风'}:
                return cls.ANEMO
            elif pval in {'冰'}:
                return cls.CRYO
            elif pval in {'雷'}:
                return cls.ELECTRO
            elif pval in {'草'}:
                return cls.DENDRO
            elif pval in {'岩'}:
                return cls.GEO
            elif pval in {'水'}:
                return cls.HYDRO

            raise ValueError(f'Invalid element value - {val!r}.')
        else:
            raise TypeError(f'Invalid element type - {val!r}.')
