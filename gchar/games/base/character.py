import builtins
import json
from functools import lru_cache
from itertools import chain
from typing import List, Union, Type, Iterator, Optional, Tuple, Dict

from huggingface_hub import hf_hub_download, HfFileSystem

from .name import _BaseName, ChineseName, EnglishName, JapaneseName, GenericAliasName
from .property import Gender
from .skin import Skin
from ...utils import Comparable

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import yaml

hf_fs = HfFileSystem()


class Character(Comparable):
    """
    Base class for modeling characters in different games.

    The class provides methods for accessing and managing character attributes, such as name, gender, skins, etc.
    It also provides class methods for retrieving and listing characters.

    Usage:
    - Inherit from the gchar.games.base.Character class and implement the required methods to customize the character model.

    :var __repository__: The repository name for the character data.
    :var __game_name__: The name of the game.
    :var __official_name__: The official name of the character.
    :var __cnname_class__: The class for modeling Chinese character names.
    :var __enname_class__: The class for modeling English character names.
    :var __jpname_class__: The class for modeling Japanese character names.
    :var __alias_name_class__: The optional class for modeling alias names.
    """

    __repository__: str = 'deepghs/game_characters'
    __skin_repository__: str = 'deepghs/game_character_skins'
    __game_name__: str
    __official_name__: str
    __cnname_class__: Type[ChineseName] = ChineseName
    __enname_class__: Type[EnglishName] = EnglishName
    __jpname_class__: Type[JapaneseName] = JapaneseName
    __alias_name_class__: Optional[Type[ChineseName]] = None

    def _index(self):
        """
        Get the index of the character.

        This method should be implemented by the subclasses.

        :returns: The index of the character.
        :rtype: Any
        """
        raise NotImplementedError  # pragma: no cover

    @property
    def index(self):
        """
        Get the index of the character.

        :returns: The index of the character.
        :rtype: Any
        """
        return self._index()

    def _cnname(self):
        """
        Get the Chinese name of the character.

        This method should be implemented by the subclasses.

        :returns: The Chinese name of the character.
        :rtype: str
        """
        raise NotImplementedError  # pragma: no cover

    def _cnnames(self):
        """
        Get additional Chinese names of the character.

        This method should be implemented by the subclasses.

        :returns: The additional Chinese names of the character.
        :rtype: List[str]
        """
        cnname = self._cnname()
        return [cnname] if cnname else []

    @property
    def cnname(self):
        """
        Get the Chinese name of the character.

        :returns: The Chinese name of the character.
        :rtype: gchar.games.base.ChineseName
        """
        cnname = self._cnname()
        return self.__cnname_class__(cnname) if cnname else None

    @property
    def cnnames(self):
        """
        Get additional Chinese names of the character.

        :returns: The additional Chinese names of the character.
        :rtype: List[gchar.games.base.ChineseName]
        """
        names = [self.__cnname_class__(name) for name in self._cnnames() if name]
        return [name for name in names if name]

    def _jpname(self):
        """
        Get the Japanese name of the character.

        This method should be implemented by the subclasses.

        :returns: The Japanese name of the character.
        :rtype: str
        """
        raise NotImplementedError  # pragma: no cover

    def _jpnames(self):
        """
        Get additional Japanese names of the character.

        This method should be implemented by the subclasses.

        :returns: The additional Japanese names of the character.
        :rtype: List[str]
        """
        jpname = self._jpname()
        return [jpname] if jpname else []

    @property
    def jpname(self):
        """
        Get the Japanese name of the character.

        :returns: The Japanese name of the character.
        :rtype: gchar.games.base.JapaneseName
        """
        jpname = self._jpname()
        return self.__jpname_class__(jpname) if jpname else None

    @property
    def jpnames(self):
        """
        Get additional Japanese names of the character.

        :returns: The additional Japanese names of the character.
        :rtype: List[gchar.games.base.JapaneseName]
        """
        names = [self.__jpname_class__(name) for name in self._jpnames() if name]
        return [name for name in names if name]

    def _enname(self):
        """
        Get the English name of the character.

        This method should be implemented by the subclasses.

        :returns: The English name of the character.
        :rtype: str
        """
        raise NotImplementedError  # pragma: no cover

    def _ennames(self):
        """
        Get additional English names of the character.

        This method should be implemented by the subclasses.

        :returns: The additional English names of the character.
        :rtype: List[str]
        """
        enname = self._enname()
        return [enname] if enname else []

    @property
    def enname(self):
        """
        Get the English name of the character.

        :returns: The English name of the character.
        :rtype: gchar.games.base.EnglishName
        """
        enname = self._enname()
        return self.__enname_class__(enname) if enname else None

    @property
    def ennames(self):
        """
        Get additional English names of the character.

        :returns: The additional English names of the character.
        :rtype: List[gchar.games.base.EnglishName]
        """
        names = [self.__enname_class__(name) for name in self._ennames() if name]
        return [name for name in names if name]

    def _custom_alias_names(self):
        """
        Get custom alias names of the character.

        This method should be implemented by the subclasses.

        :returns: The custom alias names of the character.
        :rtype: List[str]
        """
        return []

    def _generic_alias_names(self):
        """
        Get generic alias names of the character.

        This method should be implemented by the subclasses.

        :returns: The generic alias names of the character.
        :rtype: List[str]
        """
        return sorted(self._get_alias_index().get(self.index, None) or [])

    @property
    def alias_names(self):
        """
        Get all alias names of the character.

        :returns: The alias names of the character.
        :rtype: List[Union[gchar.games.base.ChineseName, gchar.games.base.GenericAliasName]]
        """
        return [
            *(self.__alias_name_class__(name) for name in self._custom_alias_names()),
            *(GenericAliasName(name) for name in self._generic_alias_names()),
        ]

    def _names(self) -> List[_BaseName]:
        """
        Get all names of the character.

        This method should be implemented by the subclasses.

        :returns: The names of the character.
        :rtype: List[_gchar.games.base.BaseName]
        """
        return [*self.cnnames, *self.ennames, *self.jpnames]

    @property
    def names(self) -> List[str]:
        """
        Get all names of the character as strings.

        :returns: The names of the character.
        :rtype: List[str]
        """
        return sorted(set(map(str, self._names())))

    def _gender(self):
        """
        Get the gender of the character.

        This method should be implemented by the subclasses.

        :returns: The gender of the character.
        :rtype: Union[str, Gender]
        """
        raise NotImplementedError  # pragma: no cover

    @property
    def gender(self) -> Gender:
        """
        Get the gender of the character.

        :returns: The gender of the character.
        :rtype: Gender
        """
        return Gender.loads(self._gender())

    def _is_extra(self) -> bool:
        """
        Check if the character is an extra character.

        This method should be implemented by the subclasses.

        :returns: True if the character is an extra character, False otherwise.
        :rtype: bool
        """
        return False

    @property
    def is_extra(self) -> bool:
        """
        Check if the character is an extra character.

        :returns: True if the character is an extra character, False otherwise.
        :rtype: bool
        """
        return bool(self._is_extra())

    def _skins(self) -> List[Tuple[str, str]]:
        """
        Get the skins of the character.

        This method should be implemented by the subclasses.

        :returns: The skins of the character as a list of tuples containing the skin name and URL.
        :rtype: List[Tuple[str, str]]
        """
        raise NotImplementedError  # pragma: no cover

    @property
    def skins(self) -> List[Skin]:
        """
        Get the skins of the character.

        :returns: The skins of the character as a list of Skin objects.
        :rtype: List[Skin]
        """
        return [Skin(self.__game_name__, self._index(), name, url) for name, url in self._skins()]

    def _iter_formal_skins(self) -> Iterator[Skin]:
        yield from self.skins

    @property
    def formal_skins(self) -> List[Skin]:
        """
        Get the formal skin of the character.
        """
        return list(self._iter_formal_skins())

    def _release_time(self):
        """
        Get the release time of the character.

        This method should be implemented by the subclasses.

        :returns: The release time of the character as a UNIX timestamp, or None if unknown.
        :rtype: Optional[float]
        """
        raise NotImplementedError  # pragma: no cover

    @property
    def release_time(self) -> Optional[float]:
        """
        Get the release time of the character.

        :returns: The release time of the character as a UNIX timestamp, or None if unknown.
        :rtype: Optional[float]
        """
        return self._release_time()

    def _order(self):
        """
        Get the order value for sorting characters.

        This method should be implemented by the subclasses.

        :returns: The order value for sorting characters.
        :rtype: Any
        """
        return ()

    def _key(self):
        """
        Get the key value for comparing characters.

        :returns: The key value for comparing characters.
        :rtype: Tuple[Any, Any, Any]
        """
        return self._order(), self._index(), (1 if self._is_extra() else 0)

    def __eq__(self, other) -> bool:
        """
        Compare the character with another character or a name.

        :param other: The character or name to compare.
        :type other: Union[gchar.games.base.Character, str]
        :returns: True if the character is equal to the other character or name, False otherwise.
        :rtype: bool
        """
        if type(other) == type(self):
            return self.index == other.index
        else:
            if self.index is not None and self.index == other:
                return True
            for name in chain(self._names(), self.alias_names):
                if name == other:
                    return True

            return False

    def __ne__(self, other):
        """
        Compare the character with another character or a name for inequality.

        :param other: The character or name to compare.
        :type other: Union[gchar.games.base.Character, str]
        :returns: True if the character is not equal to the other character or name, False otherwise.
        :rtype: bool
        """
        return not self.__eq__(other)

    @classmethod
    @lru_cache()
    def _get_index(cls) -> List[Dict]:
        """
        Get the index of all characters.

        :returns: The index of all characters.
        :rtype: List[Dict]
        """
        with open(hf_hub_download(
                repo_id=cls.__repository__,
                filename=f'{cls.__game_name__}/index.json',
                repo_type='dataset',
        ), 'r', encoding='utf-8') as f:
            return json.load(f)['data']

    @classmethod
    @lru_cache()
    def _get_alias_index(cls):
        """
        Get the index of alias names for all characters.

        :returns: The index of alias names for all characters.
        :rtype: Dict
        """
        if hf_fs.exists(f'datasets/{cls.__repository__}/{cls.__game_name__}/index_alias.yaml'):
            with open(hf_hub_download(
                    repo_id=cls.__repository__,
                    filename=f'{cls.__game_name__}/index_alias.yaml',
                    repo_type='dataset',
            ), 'r', encoding='utf-8') as f:
                data = yaml.load(f, Loader)

            return {
                item['id']: item['alias']
                for item in data['alias']
            }

        else:
            return {}

    @classmethod
    @lru_cache()
    def _simple_all(cls, contains_extra: bool = True) -> List:
        """
        Get all characters.

        :param contains_extra: Whether to include extra characters in the result.
        :type contains_extra: bool
        :returns: All characters.
        :rtype: List[gchar.games.base.Character]
        """
        all_chs = [cls(data) for data in cls._get_index()]
        chs = [ch for ch in all_chs if contains_extra or not ch.is_extra]
        return chs

    @classmethod
    def all(cls, contains_extra: bool = True, sorted: bool = True) -> List:
        """
        Get all characters.

        :param contains_extra: Whether to include extra characters in the result.
        :type contains_extra: bool
        :param sorted: Whether to sort the characters by order.
        :type sorted: bool
        :returns: All characters.
        :rtype: List[gchar.games.base.Character]
        """
        chs = cls._simple_all(contains_extra)
        if sorted:
            return builtins.sorted(chs)
        else:
            return chs

    @classmethod
    def get(cls, name, **kwargs):
        """
        Get a character by name.

        :param name: The name of the character.
        :type name: str
        :returns: The character with the given name, or None if not found.
        :rtype: Optional[gchar.games.base.Character]
        """
        for item in cls._simple_all(**kwargs):
            if item == name:
                return item

        return None


def _yield_all_characters(ch: Union[Character, list, tuple, Type[Character]], **kwargs) -> Iterator[Character]:
    """
    Helper function to recursively yield all characters.

    :param ch: The character or list of characters.
    :type ch: Union[gchar.games.base.Character, list, tuple, Type[gchar.games.base.Character]]
    :returns: An iterator over all characters.
    :rtype: Iterator[gchar.games.base.Character]
    """
    if isinstance(ch, Character):
        yield ch
    elif isinstance(ch, type) and issubclass(ch, Character):
        yield from ch.all(**kwargs)
    elif isinstance(ch, (list, tuple)):
        for item in ch:
            yield from _yield_all_characters(item, **kwargs)


def list_all_characters(*chs: Union[Character, list, tuple, Type[Character]], **kwargs) -> List[Character]:
    """
    List all characters.

    :param chs: The characters or lists of characters.
    :type chs: Union[gchar.games.base.Character, list, tuple, Type[gchar.games.base.Character]]
    :param contains_extra: Whether to include extra characters in the result.
    :type contains_extra: bool
    :returns: All characters.
    :rtype: List[gchar.games.base.Character]
    """
    return list(_yield_all_characters(chs, **kwargs))
