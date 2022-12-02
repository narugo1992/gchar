import io
from itertools import islice
from typing import Iterable, Iterator

from gchar.games.base import Character


class PixivCharPool:
    __seperator__ = '|'
    __max_reject__ = 20
    __ai_tags__ = ['NovelAI', 'AINovel', 'Diffusion', 'ai绘画']

    def __init__(self, chars: Iterable[Character]):
        self.__chars = list(chars)

    def _find_char(self, item):
        for ch in self.__chars:
            if ch == item:
                return ch
        return None

    def __contains__(self, item):
        return bool(self._find_char(item))

    def _iter_dup_names(self, name: str) -> Iterator[str]:
        for ch in self.__chars:
            for sname in map(str, ch.names):
                if len(name) < len(sname) and name in sname:
                    yield sname

    def get_tag(self, item, base_tag: str, inverse: bool = False, no_ai: bool = True):
        char = self._find_char(item)
        if not char:
            raise ValueError(f'Unknown character - {item!r}.')

        included = []
        rejected = []
        for name in char._names():
            sname = str(name)
            if not inverse:
                items = list(islice(self._iter_dup_names(sname), self.__max_reject__ + 1))
                if len(items) <= self.__max_reject__:
                    included.append(sname)
                    for xname in items:
                        rejected.append(xname)
            else:
                rejected.append(sname)

        if no_ai:
            for ai_tag in self.__ai_tags__:
                rejected.append(ai_tag)

        included = sorted(set(included))
        rejected = sorted([w for w in set(rejected) if w not in included])

        with io.StringIO() as sf:
            if base_tag:
                print(base_tag, file=sf, end=' ')

            if included:
                if len(included) > 1:
                    print(f'({" OR ".join(included)})', file=sf, end=' ')
                else:
                    print(included[0], file=sf, end=' ')

            if rejected:
                print(*map(lambda x: f'-{x}', rejected), file=sf, end=' ', sep=' ')

            return sf.getvalue().strip()
