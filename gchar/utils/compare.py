from operator import ge, gt, le, lt


class Comparable:
    """
    Base class that allows subclasses to perform arbitrary comparison operations by implementing the necessary interfaces.

    Subclasses need to implement the `_key` method, which returns the key used for comparison.

    Supported comparison operators: ==, !=, >=, >, <=, <

    Usage:
        * Subclass `Comparable` and implement the `_key` method.
        * Objects of the subclass can then be compared using the defined comparison operators.

    Example:
        >>> class MyComparable(Comparable):
        >>>     def __init__(self, value):
        >>>         self.value = value
        ...
        >>>     def _key(self):
        >>>         return self.value
        ...
        >>> obj1 = MyComparable(5)
        >>> obj2 = MyComparable(10)
        >>> print(obj1 == obj2)  # False
        >>> print(obj1 < obj2)   # True

    """

    def _check_same_type(self, other):
        """
        Helper method to check if the type of the other object is the same as the current object's type.

        :param other: The other object to compare.
        :type other: object
        :returns: The other object if the types are the same.
        :rtype: object
        :raises TypeError: If the types are different.
        """
        if type(self) == type(other):
            return other
        else:
            raise TypeError(f'Invalid type for compare - {other!r}.')

    def _key(self):
        """
        Abstract method that needs to be implemented by subclasses.
        Returns the key used for comparison.

        :returns: The key used for comparison.
        :rtype: object
        :raises NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError  # pragma: no cover

    def __eq__(self, other):
        """
        Implementation of the equality operator (==).

        :param other: The other object to compare.
        :type other: object
        :returns: True if the objects are equal, False otherwise.
        :rtype: bool
        """
        try:
            other = self._check_same_type(other)
        except TypeError:
            return False
        else:
            return self._key() == other._key()

    def __ne__(self, other):
        """
        Implementation of the inequality operator (!=).

        :param other: The other object to compare.
        :type other: object
        :returns: True if the objects are not equal, False otherwise.
        :rtype: bool
        """
        try:
            other = self._check_same_type(other)
        except TypeError:
            return True
        else:
            return self._key() != other._key()

    def _cmp(self, cmp, other):
        """
        Helper method to perform comparison operations using the provided comparison function.

        :param cmp: The comparison function to use.
        :type cmp: callable
        :param other: The other object to compare.
        :type other: object
        :returns: The result of the comparison operation.
        :rtype: bool
        """
        try:
            other = self._check_same_type(other)
        except TypeError:
            return False
        else:
            return cmp(self._key(), other._key())

    def __ge__(self, other):
        """
        Implementation of the greater than or equal to operator (>=).

        :param other: The other object to compare.
        :type other: object
        :returns: True if the current object is greater than or equal to the other object, False otherwise.
        :rtype: bool
        """
        return self._cmp(ge, other)

    def __gt__(self, other):
        """
        Implementation of the greater than operator (>).

        :param other: The other object to compare.
        :type other: object
        :returns: True if the current object is greater than the other object, False otherwise.
        :rtype: bool
        """
        return self._cmp(gt, other)

    def __le__(self, other):
        """
        Implementation of the less than or equal to operator (<=).

        :param other: The other object to compare.
        :type other: object
        :returns: True if the current object is less than or equal to the other object, False otherwise.
        :rtype: bool
        """
        return self._cmp(le, other)

    def __lt__(self, other):
        """
        Implementation of the less than operator (<).

        :param other: The other object to compare.
        :type other: object
        :returns: True if the current object is less than the other object, False otherwise.
        :rtype: bool
        """
        return self._cmp(lt, other)
