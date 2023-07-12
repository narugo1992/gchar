from enum import IntEnum


class Rarity(IntEnum):
    SR = 4
    SSR = 5

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
