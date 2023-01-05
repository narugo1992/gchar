from typing import List, Union, Type, Iterator

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

    @classmethod
    def all(cls, timeout: int = 5, **kwargs):
        raise NotImplementedError


def _yield_all_characters(ch: Union[Character, list, tuple, Type[Character]], **kwargs) -> Iterator[Character]:
    if isinstance(ch, Character):
        yield ch
    elif isinstance(ch, type) and issubclass(ch, Character):
        yield from ch.all(**kwargs)
    elif isinstance(ch, (list, tuple)):
        for item in ch:
            yield from _yield_all_characters(item, **kwargs)


def list_all_characters(*chs: Union[Character, list, tuple, Type[Character]], **kwargs) -> List[Character]:
    return list(_yield_all_characters(chs, **kwargs))
