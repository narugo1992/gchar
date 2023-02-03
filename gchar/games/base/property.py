from enum import unique, Enum


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
