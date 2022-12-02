from enum import unique, Enum, IntEnum


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
class Level(IntEnum):
    FOUR = 0x4
    FIVE = 0x5

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
