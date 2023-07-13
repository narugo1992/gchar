import re
from typing import List, Union

from ...utils import Comparable


class _BaseName(Comparable):
    """
    Base class for modeling character names.

    The class provides common functionality for character name modeling.
    It inherits from the `Comparable` class and defines methods for equality comparison and string representation.

    Usage:
    - Use the `_BaseName` class as a base class for specific character name modeling classes.

    :param name: The name of the character.
    :type name: str
    """

    def __init__(self, name):
        """
        Initialize the _BaseName object.

        :param name: The name of the character.
        :type name: str
        """
        _ = name

    def _repr(self) -> str:
        """
        Get the string representation of the character name.

        This method should be implemented by the subclasses.

        :returns: The string representation of the character name.
        :rtype: str
        """
        raise NotImplementedError  # pragma: no cover

    def _check_same_type(self, other):
        """
        Check if the other object is of the same type as the current object.

        If the other object is of the same type, it is returned as is.
        Otherwise, a new instance of the current class is created with the value of the other object.

        :param other: The other object to check.
        :type other: object
        :returns: The other object if it is of the same type, or a new instance of the current class with the value of the other object.
        :rtype: _BaseName
        """
        if isinstance(other, _BaseName):
            return other
        else:
            return self.__class__(other)

    def _key(self):
        """
        Get the key used for comparison.

        This method should be implemented by the subclasses.

        :returns: The key used for comparison.
        :rtype: object
        """
        return self._repr()

    def __str__(self):
        """
        Get the string representation of the character name.

        :returns: The string representation of the character name.
        :rtype: str
        """
        return self._repr()

    def __repr__(self):
        """
        Get the string representation of the _BaseName object.

        :returns: The string representation of the _BaseName object.
        :rtype: str
        """
        return f'<{type(self).__name__} {self._repr()!r}>'

    def __bool__(self):
        """
        Check if the character name is considered True.

        :returns: True if the character name is considered True, False otherwise.
        :rtype: bool
        """
        return bool(self._repr())


class TextName(_BaseName):
    """
    Class for modeling character names based on text.

    The class inherits from _BaseName and provides methods for string representation and comparison.
    It supports containment check, length calculation, and item retrieval.

    Usage:
        * Use the TextName class to model character names based on text.

    :param name: The name of the character.
    :type name: str
    """

    def __init__(self, name: str):
        """
        Initialize the TextName object.

        :param name: The name of the character.
        :type name: str
        """
        if not isinstance(name, str):
            raise TypeError(f'Invalid name type - {name!r}.')
        _BaseName.__init__(self, name)
        self.__name = self._preprocess(name)

    def _repr(self) -> str:
        """
        Get the string representation of the character name.

        :returns: The string representation of the character name.
        :rtype: str
        """
        return self.__name

    def __contains__(self, item: str) -> bool:
        """
        Check if the character name contains a specific string.

        :param item: The string to check.
        :type item: str
        :returns: True if the character name contains the specified string, False otherwise.
        :rtype: bool
        """
        return item in self.__name

    def __len__(self):
        """
        Calculate the length of the character name.

        :returns: The length of the character name.
        :rtype: int
        """
        return len(self.__name)

    def __getitem__(self, item):
        """
        Get the item at the specified index or slice.

        :param item: The index or slice to retrieve.
        :type item: Union[int, slice]
        :returns: The item at the specified index or slice.
        :rtype: Any
        """
        return self.__name[item]

    @classmethod
    def _preprocess(cls, name: str) -> str:
        """
        Preprocess the character name.

        This method should be implemented by the subclasses to provide custom preprocessing logic.

        :param name: The name of the character.
        :type name: str
        :returns: The preprocessed name.
        :rtype: str
        """
        return name.strip()

    @classmethod
    def _eqprocess(cls, name: str) -> str:
        """
        Preprocess the character name for equality comparison.

        This method should be implemented by the subclasses to provide custom preprocessing logic.

        :param name: The name of the character.
        :type name: str
        :returns: The preprocessed name for equality comparison.
        :rtype: str
        """
        return re.sub(r'[\W_]+', '', name.lower())

    def _key(self):
        """
        Get the key used for comparison.

        :returns: The key used for comparison.
        :rtype: object
        """
        return self._eqprocess(_BaseName._key(self))


class SegmentName(_BaseName):
    """
    Class for modeling character names based on segments.

    The class inherits from _BaseName and provides methods for string representation and comparison.
    It supports containment check, length calculation, and item retrieval.

    Usage:
        * Use the SegmentName class to model character names based on segments.

    :param name: The name of the character.
    :type name: Union[str, List[str]]
    """
    __seperator__ = '_'

    def __init__(self, name: Union[str, List[str]]):
        """
        Initialize the SegmentName object.

        :param name: The name of the character.
        :type name: Union[str, List[str]]
        """
        if not isinstance(name, (str, list, tuple)):
            raise TypeError(f'Invalid name type - {name!r}.')
        _BaseName.__init__(self, name)
        self.__words = self._preprocess(name)

    def _repr(self):
        """
        Get the string representation of the character name.

        :returns: The string representation of the character name.
        :rtype: str
        """
        return self.__seperator__.join(self.__words)

    def __contains__(self, item: Union[str, List[str]]) -> bool:
        """
        Check if the character name contains a specific string or list of strings.

        :param item: The string or list of strings to check.
        :type item: Union[str, List[str]]
        :returns: True if the character name contains the specified string or list of strings, False otherwise.
        :rtype: bool
        """
        target = self._preprocess(item)
        n = len(target)
        for i in range(0, len(self.__words) - n + 1):
            if self.__words[i:i + n] == target:
                return True

        return False

    def __len__(self):
        """
        Calculate the length of the character name.

        :returns: The length of the character name.
        :rtype: int
        """
        return len(self.__words)

    def __getitem__(self, item) -> List[str]:
        """
        Get the item at the specified index or slice.

        :param item: The index or slice to retrieve.
        :type item: Union[int, slice]
        :returns: The item at the specified index or slice.
        :rtype: List[str]
        """
        return self.__words[item]

    _SPLITTERS = re.compile(r'[\s_,]+')

    @classmethod
    def _preprocess(cls, name: Union[str, List[str]]) -> List[str]:
        """
        Preprocess the character name.

        This method should be implemented by the subclasses to provide custom preprocessing logic.

        :param name: The name of the character.
        :type name: Union[str, List[str]]
        :returns: The preprocessed name.
        :rtype: List[str]
        """
        if isinstance(name, str):
            words = cls._SPLITTERS.split(name.strip().lower())
        else:
            words = name

        words = [wd.lower().strip() for wd in words]
        words = [wd for wd in words if wd]
        return words


class ChineseName(TextName):
    """
    Class for modeling Chinese character names.

    The class inherits from TextName and represents character names written in Chinese.

    Usage:
    - Use the ChineseName class to model Chinese character names.

    :param name: The name of the character.
    :type name: str
    """
    pass


class JapaneseName(TextName):
    """
    Class for modeling Japanese character names.

    The class inherits from TextName and represents character names written in Japanese.

    Usage:
    - Use the JapaneseName class to model Japanese character names.

    :param name: The name of the character.
    :type name: str
    """
    pass


class EnglishName(SegmentName):
    """
    Class for modeling English character names.

    The class inherits from SegmentName and represents character names written in English.

    Usage:
    - Use the EnglishName class to model English character names.

    :param name: The name of the character.
    :type name: Union[SegmentName, TextName, str, List[str]]
    """

    @classmethod
    def _word_trans(cls, name: str) -> str:
        """
        Translate individual words in the character name.

        This method should be implemented by the subclasses to provide custom word translation logic.

        :param name: The name of the character.
        :type name: str
        :returns: The translated name.
        :rtype: str
        """
        return name

    @classmethod
    def _preprocess(cls, name: Union[SegmentName, TextName, str, List[str]]) -> List[str]:
        """
        Preprocess the character name.

        This method should be implemented by the subclasses to provide custom preprocessing logic.

        :param name: The name of the character.
        :type name: Union[SegmentName, TextName, str, List[str]]
        :returns: The preprocessed name.
        :rtype: List[str]
        """
        if isinstance(name, SegmentName):
            return name[:]
        elif isinstance(name, TextName):
            return cls._preprocess(str(name))
        elif isinstance(name, str):
            name = cls._word_trans(name).replace(chr(160), ' ')
        elif isinstance(name, list):
            name = [cls._word_trans(wd) for wd in name]
        else:
            raise TypeError(f'Invalid name type - {name!r}.')

        return SegmentName._preprocess(name)


class GenericAliasName(TextName):
    """
    Class for modeling generic character names with aliases.

    The class inherits from TextName and represents generic character names that may have aliases.

    Usage:
    - Use the GenericAliasName class to model generic character names with aliases.

    :param name: The name of the character.
    :type name: str
    """

    @classmethod
    def _eqprocess(cls, name: str) -> str:
        """
        Preprocess the character name for equality comparison.

        This method should be implemented by the subclasses to provide custom preprocessing logic.

        :param name: The name of the character.
        :type name: str
        :returns: The preprocessed name for equality comparison.
        :rtype: str
        """
        return ' '.join(filter(bool, re.split(r'[\W_]+', TextName._eqprocess(name))))
