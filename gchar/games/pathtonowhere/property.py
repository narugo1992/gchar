from enum import Enum


class Rarity(Enum):
    R = ('普', 1)
    SR = ('危', 2)
    SSR = ('狂', 3)

    def __init__(self, text: str, number: int):
        self.number = number
        self.text = text

    @classmethod
    def loads(cls, obj) -> 'Rarity':
        if isinstance(obj, Rarity):
            return obj
        elif isinstance(obj, int):
            for name, item in cls.__members__.items():
                if item.number == obj:
                    return item
            raise ValueError(f'Unknown rarity number - {obj!r}.')
        elif isinstance(obj, str):
            for name, item in cls.__members__.items():
                if name.upper() == obj.upper() or item.text.upper() == obj.upper():
                    return item
            raise KeyError(f'Unknown rarity text - {obj!r}.')
        else:
            raise TypeError(f'Unknown rarity type - {obj!r}.')

    def __eq__(self, other):
        if isinstance(other, Rarity):
            return self.value == other.value
        else:
            try:
                return self == self.loads(other)
            except (TypeError, ValueError, KeyError):
                return False
