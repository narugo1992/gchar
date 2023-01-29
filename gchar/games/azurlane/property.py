from enum import unique, IntEnum, Enum


@unique
class Group(Enum):
    USS = 0x1
    HMS = 0x2
    IJN = 0x3
    KMS = 0x4
    DE = 0x5
    RN = 0x6
    SN = 0x7
    FFNF = 0x8
    MNF = 0x9

    def __eq__(self, other):
        if isinstance(other, Group):
            return self.value == other.value
        else:
            try:
                return self == Group.loads(other)
            except (TypeError, ValueError):
                return False

    @classmethod
    def loads(cls, val) -> 'Group':
        if isinstance(val, cls):
            return val
        elif isinstance(val, str):
            if val == '白鹰':
                return cls.USS
            elif val == '皇家':
                return cls.HMS
            elif val == '重樱':
                return cls.IJN
            elif val == '铁血':
                return cls.KMS
            elif val == '东煌':
                return cls.DE
            elif val == '撒丁帝国':
                return cls.RN
            elif val == '北方联合':
                return cls.SN
            elif val == '自由鸢尾':
                return cls.FFNF
            elif val == '维希教廷':
                return cls.MNF
            else:
                raise ValueError(f'Invalid group value - {val!r}.')
        else:
            raise TypeError(f'Invalid group type - {val!r}.')


@unique
class BasicRarity(IntEnum):
    COMMON = 0x1
    RARE = 0x2
    ELITE = 0x3
    ULTRA = 0x4
    EPIC = 0x5

    @property
    def label(self) -> str:
        if self == self.COMMON:
            return '普通'
        elif self == self.RARE:
            return '稀有'
        elif self == self.ELITE:
            return '精锐'
        elif self == self.ULTRA:
            return '超稀有'
        elif self == self.EPIC:
            return '海上传奇'
        else:
            raise ValueError(f'Unknown basic level - {self!r}.')  # pragma: no cover

    def __eq__(self, other):
        if isinstance(other, BasicRarity):
            return self.value == other.value
        else:
            try:
                return self == self.loads(other)
            except (TypeError, ValueError):
                return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def loads(cls, val) -> 'BasicRarity':
        if isinstance(val, cls):
            return val
        elif isinstance(val, int):
            for name, item in cls.__members__.items():
                if item.value == val:
                    return item

            raise ValueError(f'Invalid level value - {val!r}.')
        elif isinstance(val, str):
            if val == '普通':
                return cls.COMMON
            elif val == '稀有':
                return cls.RARE
            elif val == '精锐':
                return cls.ELITE
            elif val == '超稀有':
                return cls.ULTRA
            elif val == '海上传奇':
                return cls.EPIC
            else:
                raise ValueError(f'Invalid level string - {val!r}.')
        else:
            raise TypeError(f'Invalid level type - {val!r}.')


@unique
class ResearchRarity(IntEnum):
    TOP = 0x4
    DECISIVE = 0x5

    @property
    def label(self) -> str:
        if self == self.TOP:
            return '最高方案'
        elif self == self.DECISIVE:
            return '决战方案'
        else:
            raise ValueError(f'Unknown research level - {self!r}.')  # pragma: no cover

    def __eq__(self, other):
        if isinstance(other, ResearchRarity):
            return self.value == other.value
        else:
            try:
                return self == self.loads(other)
            except (TypeError, ValueError):
                return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def loads(cls, val) -> 'ResearchRarity':
        if isinstance(val, cls):
            return val
        elif isinstance(val, int):
            for name, item in cls.__members__.items():
                if item.value == val:
                    return item

            raise ValueError(f'Invalid level value - {val!r}.')
        elif isinstance(val, str):
            if val == '最高方案':
                return cls.TOP
            elif val == '决战方案':
                return cls.DECISIVE
            else:
                raise ValueError(f'Invalid level string - {val!r}.')
        else:
            raise TypeError(f'Invalid level type - {val!r}.')
