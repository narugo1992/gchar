from enum import unique, Enum


@unique
class Gender(Enum):
    """
    Enumeration class representing the gender of a character.

    The class provides three gender options: OTHER, MALE, and FEMALE.
    It supports equality comparison with other Gender objects and string values.
    The class also provides a method `loads` for parsing and converting string values into Gender objects.

    Usage:
        * Use the Gender enum to represent the gender of a character.

    Supported string values for each gender:
        * OTHER: "OTHER"
        * MALE: "MALE", "男", "男性", "boy", "man", "male"
        * FEMALE: "FEMALE", "女", "女性", "girl", "woman", "female"
    """
    OTHER = 0x0
    MALE = 0x1
    FEMALE = 0x2

    def __eq__(self, other):
        """
        Equality comparison with other Gender objects or string values.

        :param other: The other object to compare.
        :type other: object
        :returns: True if the objects are equal, False otherwise.
        :rtype: bool
        """
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
        """
        Parse and convert a string value into a Gender object.

        The method accepts string values representing genders and converts them into the corresponding Gender enum object.
        If the input value is already a Gender object, it is returned as is.

        :param val: The value to parse and convert.
        :type val: Union[str, Gender]
        :returns: The Gender object corresponding to the input value.
        :rtype: Gender
        :raises TypeError: If the input value is of an invalid type.
        """
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
