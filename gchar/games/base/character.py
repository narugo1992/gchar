from typing import List

from .name import _BaseName


class Character:
    def _index(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def index(self):
        return self._index()

    def _names(self) -> List[_BaseName]:
        raise NotImplementedError  # pragma: no cover

    @property
    def names(self) -> List[str]:
        return sorted(set(map(str, self._names())))
