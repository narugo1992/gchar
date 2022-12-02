from operator import ge, gt, le, lt


class Comparable:
    def _check_same_type(self, other):
        if type(self) == type(other):
            return other
        else:
            raise TypeError(f'Invalid type for compare - {other!r}.')

    def _key(self):
        raise NotImplementedError

    def __eq__(self, other):
        try:
            other = self._check_same_type(other)
        except TypeError:
            return False
        else:
            return self._key() == other._key()

    def __ne__(self, other):
        try:
            other = self._check_same_type(other)
        except TypeError:
            return True
        else:
            return self._key() != other._key()

    def _cmp(self, cmp, other):
        try:
            other = self._check_same_type(other)
        except TypeError:
            return False
        else:
            return cmp(self._key(), other._key())

    def __ge__(self, other):
        return self._cmp(ge, other)

    def __gt__(self, other):
        return self._cmp(gt, other)

    def __le__(self, other):
        return self._cmp(le, other)

    def __lt__(self, other):
        return self._cmp(lt, other)
