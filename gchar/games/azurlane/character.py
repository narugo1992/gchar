from typing import List, Optional, Union, Tuple, Iterator

from .name import EnglishName, JapaneseName, ChineseName, ChineseAliasName
from .property import BasicRarity, ResearchRarity, Group
from ..base import Character as _BaseCharacter, Skin


class Character(_BaseCharacter):
    """
    A class representing characters in the Azur Lane game.
    Inherits from _BaseCharacter.
    """

    __game_name__ = 'azurlane'
    __official_name__ = 'Azur Lane'
    __game_keywords__ = ['azur_lane', 'アズールレーン', 'azurlane']

    __cnname_class__ = ChineseName
    __enname_class__ = EnglishName
    __jpname_class__ = JapaneseName
    __alias_name_class__ = ChineseAliasName

    def __init__(self, raw_data: dict):
        """
        Initialize a Character object.

        :param raw_data: The raw data dictionary representing the character.
        :type raw_data: dict
        """
        self.__raw_data = raw_data

    def _index(self) -> str:
        """
        Get the index of the character.

        :return: The index of the character.
        :rtype: str
        """
        return self.__raw_data['id']

    def _cnname(self):
        """
        Get the Chinese name of the character.

        :return: The Chinese name of the character.
        :rtype: str
        """
        return self.__raw_data['cnname']['short']

    def _enname(self):
        """
        Get the English name of the character.

        :return: The English name of the character.
        :rtype: str
        """
        return self.__raw_data['enname']['short']

    def _jpname(self):
        """
        Get the primary Japanese name of the character.

        :return: The primary Japanese name of the character.
        :rtype: str
        """
        if self.__raw_data['jpnames']:
            return self.__raw_data['jpnames'][0]
        else:
            return None

    def _jpnames(self):
        """
        Get the list of all Japanese names of the character.

        :return: The list of all Japanese names of the character.
        :rtype: List[str]
        """
        return self.__raw_data['jpnames']

    def _custom_alias_names(self):
        """
        Get the list of custom alias names of the character.

        :return: The list of custom alias names of the character.
        :rtype: List[str]
        """
        return self.__raw_data['alias']

    def _gender(self):
        """
        Get the gender of the character.

        :return: The gender of the character.
        :rtype: str
        """
        return 'female'

    @property
    def rarity(self) -> Optional[Union[BasicRarity, ResearchRarity]]:
        """
        Get the rarity of the character.

        :return: The rarity of the character.
        :rtype: Optional[Union[BasicRarity, ResearchRarity]]
        """
        val = self.__raw_data['rarity']
        try:
            return BasicRarity.loads(val)
        except (ValueError, TypeError):
            return ResearchRarity.loads(val)

    @property
    def group(self) -> Union[Group, str]:
        """
        Get the group of the character.

        :return: The group of the character.
        :rtype: Union[Group, str]
        """
        try:
            return Group.loads(self.__raw_data['group'])
        except (TypeError, ValueError):
            return self.__raw_data['group']

    @property
    def is_meta(self) -> bool:
        """
        Check if the character is a meta character.

        :return: True if the character is a meta character, False otherwise.
        :rtype: bool
        """
        return self.__raw_data['is_meta']

    @property
    def is_refit(self) -> bool:
        """
        Check if the character is a refit character.

        :return: True if the character is a refit character, False otherwise.
        :rtype: bool
        """
        return self.__raw_data['is_refit']

    @property
    def is_mu(self) -> bool:
        """
        Check if the character is a Mu character.

        :return: True if the character is a Mu character, False otherwise.
        :rtype: bool
        """
        return self.__raw_data['is_mu']

    @property
    def is_chibi(self) -> bool:
        """
        Check if the character has a chibi form.

        :return: True if the character has a chibi form, False otherwise.
        :rtype: bool
        """
        return self.__raw_data['is_chibi']

    def _is_extra(self) -> bool:
        """
        Check if the character is considered an "extra" character.

        :return: True if the character is considered an "extra" character, False otherwise.
        :rtype: bool
        """
        return self.is_meta or self.is_refit or self.is_mu or self.is_chibi

    def _skins(self) -> List[Tuple[str, str]]:
        """
        Get the list of skins of the character.

        :return: The list of skins of the character, each represented as a tuple of (name, url).
        :rtype: List[Tuple[str, str]]
        """
        return [(item['name'], item['url']) for item in self.__raw_data['skins']]

    def _iter_formal_skins(self) -> Iterator[Skin]:
        for skin in self.skins:
            if 'chibi' not in skin.name.lower():
                yield skin

    def _release_time(self):
        """
        Get the release time of the character.

        :return: The release time of the character.
        :rtype: Optional[float]
        """
        release_info = self.__raw_data['release']
        return release_info['time']

    def _order(self):
        """
        Get the ordering key of the character.

        :return: The ordering key of the character.
        :rtype: float
        """
        return self._release_time()

    def __repr__(self):
        """
        Get the string representation of the character.

        :return: The string representation of the character.
        :rtype: str
        """
        return f'<{type(self).__name__} {self.index} - {"/".join(map(str, self._names()))}, ' \
               f'{self.rarity.label}({int(self.rarity)}{"*" * self.rarity}), ' \
               f'group: {self.group if isinstance(self.group, Group) else self.group}>'
