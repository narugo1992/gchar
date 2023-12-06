import re
from enum import IntEnum, Enum
from functools import total_ordering


class Rarity(IntEnum):
    R = 1
    SR = 2
    SSR = 3

    @classmethod
    def loads(cls, obj):
        if isinstance(obj, Rarity):
            return obj
        elif isinstance(obj, str):
            return cls.__members__[obj.upper().strip()]
        elif isinstance(obj, int):
            for name, item in cls.__members__.items():
                if item.value == obj:
                    return item

            raise ValueError(f'Unknown rarity value - {obj!r}.')
        else:
            raise TypeError(f'Unknown rarity type - {obj!r}.')


@total_ordering
class Clazz(Enum):
    ATTACKER = (('attackers', 'attacker', '火力型'), 1)
    DEFENDER = (('defenders', 'defender', '防御型'), 2)
    SUPPORTER = (('supporters', 'supporter', '辅助型'), 3)

    def __init__(self, aliases, number):
        self.aliases = aliases
        self.number = number

    @classmethod
    def loads(cls, obj):
        if isinstance(obj, Clazz):
            return obj
        elif isinstance(obj, str):
            for key, item in cls.__members__.items():
                names = set(map(str.lower, [key, *item.aliases]))
                if obj.lower().strip() in names:
                    return item
            raise ValueError(f'Unknown class - {obj!r}')
        elif isinstance(obj, int):
            for key, item in cls.__members__.items():
                if item.number == obj:
                    return item
            raise ValueError(f'Unknown class number - {obj!r}.')
        else:
            raise TypeError(f'Unknown class type - {obj!r}.')

    def __eq__(self, other):
        if isinstance(other, Clazz):
            return self.name == other.name
        else:
            try:
                return self == self.loads(other)
            except (KeyError, ValueError, TypeError):
                return False

    def __hash__(self):
        return hash(self.aliases)

    def __lt__(self, other):
        return self.number < other.number

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}: {self.number}>'


@total_ordering
class Burst(Enum):
    I = (('burst skill i', 'i'), 1)
    II = (('burst skill ii', 'ii'), 2)
    III = (('burst skill iii', 'iii'), 3)
    ALL = (('burst skill all', 'all'), 0xf)

    def __init__(self, aliases, number):
        self.aliases = aliases
        self.number = number

    @classmethod
    def _name_preprocess(cls, name):
        return re.sub(r'[\W_]+', '', name.lower().strip())

    @classmethod
    def loads(cls, obj):
        if isinstance(obj, Burst):
            return obj
        elif isinstance(obj, str):
            for key, item in cls.__members__.items():
                names = set(map(cls._name_preprocess, [key, *item.aliases]))
                if cls._name_preprocess(obj) in names:
                    return item
            raise ValueError(f'Unknown class - {obj!r}')
        elif isinstance(obj, int):
            for key, item in cls.__members__.items():
                if item.number == obj:
                    return item
            raise ValueError(f'Unknown class number - {obj!r}.')
        else:
            raise TypeError(f'Unknown class type - {obj!r}.')

    def __eq__(self, other):
        if isinstance(other, Burst):
            return self.name == other.name
        else:
            try:
                return self == self.loads(other)
            except (KeyError, ValueError, TypeError):
                return False

    def __hash__(self):
        return hash(self.aliases)

    def __lt__(self, other):
        return self.number < other.number

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}: {self.number}>'
