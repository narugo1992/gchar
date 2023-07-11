import pytest

from gchar.utils import Comparable


class IntCmp(Comparable):
    def __init__(self, x):
        self.x = x

    def _key(self):
        return self.x


class SubIntCmp(IntCmp):
    pass


@pytest.fixture()
def v1():
    return IntCmp(1)


@pytest.fixture()
def v2():
    return IntCmp(2)


@pytest.mark.unittest
class TestUtilsCompare:
    def test_comparable(self, v1, v2):
        assert v1 < v2
        assert v2 > v1
        assert v1 == IntCmp(1)
        assert v2 == IntCmp(2)
        assert v1 != v2
        assert v1 <= v2
        assert v1 <= v1
        assert v2 >= v1
        assert v2 >= v2

        assert v1 != SubIntCmp(1)
        assert not (v1 == SubIntCmp(1))
        assert not (v1 <= SubIntCmp(2))

        assert SubIntCmp(1) < SubIntCmp(2)
        assert SubIntCmp(2) > SubIntCmp(1)
        assert SubIntCmp(1) != SubIntCmp(2)
        assert SubIntCmp(1) <= SubIntCmp(2)
        assert SubIntCmp(1) <= SubIntCmp(1)
        assert SubIntCmp(2) >= SubIntCmp(1)
        assert SubIntCmp(2) >= SubIntCmp(2)
