from enum import unique, IntEnum, Enum


@unique
class Group(Enum):
    USS = 0x1
    HMS = 0x2
    IJN = 0x3
    KMS = 0x4
    ICN_ROC = 0x5
    RN = 0x6
    SN = 0x7
    FFNF = 0x8
    MNF = 0x9

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
                return cls.ICN_ROC
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
class BasicLevel(IntEnum):
    COMMON = 0x1
    RARE = 0x2
    ELITE = 0x3
    ULTRA = 0x4
    EPIC = 0x5

    @classmethod
    def loads(cls, val) -> 'BasicLevel':
        if isinstance(val, cls):
            return val
        elif isinstance(val, int):
            for name, item in cls.__members__.items():
                if item.value == val:
                    return item.value

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
class ResearchLevel(IntEnum):
    TOP = 0x4
    DECISIVE = 0x5

    @classmethod
    def loads(cls, val) -> 'ResearchLevel':
        if isinstance(val, cls):
            return val
        elif isinstance(val, int):
            for name, item in cls.__members__.items():
                if item.value == val:
                    return item.value

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
