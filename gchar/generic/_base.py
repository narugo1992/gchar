import re
from typing import List, Tuple, Optional

from ..games.base import Character, TextName
from ..games.base import ChineseName as _GenericChineseName
from ..games.base import EnglishName as _GenericEnglishName
from ..games.base import JapaneseName as _GenericJapaneseName


class ChineseName(_GenericChineseName):
    pass


class JapaneseName(_GenericJapaneseName):
    pass


class KoreanName(TextName):
    pass


class EnglishName(_GenericEnglishName):
    pass


class AliasName(TextName):
    pass


class _BaseGenericCharacter(Character):
    __cnname_class__ = ChineseName
    __enname_class__ = EnglishName
    __jpname_class__ = JapaneseName
    __alias_name_class__ = AliasName
    __repository__ = 'deepghs/generic_characters'
    __skin_repository__ = 'deepghs/generic_character_skins'

    def __init__(self, data):
        self._data = data

    def _index(self):
        return re.sub(r'[\W_]+', '_', self._enname().lower()).strip('_')

    def _cnname(self):
        _cnnames = self._data['cnnames']
        return _cnnames[0] if _cnnames else None

    def _cnnames(self):
        return self._data['cnnames']

    def _jpname(self):
        _jpnames = self._data['jpnames']
        return _jpnames[0] if _jpnames else None

    def _jpnames(self):
        return self._data['jpnames']

    def _enname(self):
        _ennames = self._data['ennames']
        return _ennames[0] if _ennames else None

    def _ennames(self):
        return self._data['ennames']

    def _krname(self):
        _krnames = self._data['krnames']
        return _krnames[0] if _krnames else None

    @property
    def krname(self) -> Optional[KoreanName]:
        name = self._krname()
        return KoreanName(name) if name is not None else None

    def _krnames(self):
        return self._data['krnames']

    @property
    def krnames(self) -> List[KoreanName]:
        return [KoreanName(name) for name in self._krnames()]

    def _custom_alias_names(self):
        return self._data['alias']

    def _gender(self):
        return self._data['gender']

    def _skins(self) -> List[Tuple[str, str]]:
        return [
            (item['name'], item['url'])
            for item in list(self._data.get('skins', self._data.get('skin')))
        ]

    def _release_time(self):
        return None

    def _order(self):
        return -self._data['strict'], -self._data['total'], self._index()

    def __repr__(self):
        return f'<{type(self).__name__} {"/".join(map(str, self._names()))}, gender: {self.gender}>'
