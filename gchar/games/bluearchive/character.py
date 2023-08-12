import re
from typing import List, Tuple

from .name import EnglishName, JapaneseName, ChineseName, ChineseAliasName
from .property import Rarity, WeaponType, Role, AttackType
from ..base import Character as _BaseCharacter, Gender


class Character(_BaseCharacter):
    """
    Represents a character in Blue Archive.
    Inherits from the base class _BaseCharacter.
    """
    __game_name__ = 'bluearchive'
    __official_name__ = 'Blue Archive'
    __game_keywords__ = ['blue_archive', 'ブルーアーカイブ', 'BlueArchive']
    __cnname_class__ = ChineseName
    __enname_class__ = EnglishName
    __jpname_class__ = JapaneseName
    __alias_name_class__ = ChineseAliasName

    def __init__(self, raw_data: dict):
        """
        Initializes a Character object with raw data.

        :param raw_data: The raw data of the character.
        :type raw_data: dict
        """
        self.__raw_data = raw_data

    def _index(self) -> str:
        """
        Generates the index of the character.

        :return: The generated index.
        :rtype: str
        """
        return re.sub(r'\W+', '_', self._enname().lower())

    def _cnname(self):
        """
        Returns the Chinese name of the character.

        :return: The Chinese name.
        :rtype: str
        """
        return self.__raw_data['cnnames'][0]

    def _jpname(self):
        """
        Returns the Japanese name of the character.

        :return: The Japanese name.
        :rtype: str
        """
        return self.__raw_data['jpnames'][0]

    def _enname(self):
        """
        Returns the English name of the character.

        :return: The English name.
        :rtype: str
        """
        return self.__raw_data['ennames'][0]

    def _cnnames(self):
        """
        Returns a list of Chinese names of the character.

        :return: The list of Chinese names.
        :rtype: List[str]
        """
        return self.__raw_data['cnnames']

    def _jpnames(self):
        """
        Returns a list of Japanese names of the character.

        :return: The list of Japanese names.
        :rtype: List[str]
        """
        return self.__raw_data['jpnames']

    def _ennames(self):
        """
        Returns a list of English names of the character.

        :return: The list of English names.
        :rtype: List[str]
        """
        return self.__raw_data['ennames']

    def _gender(self):
        """
        Returns the gender of the character.

        :return: The gender.
        :rtype: Gender
        """
        return Gender.FEMALE

    @property
    def rarity(self) -> Rarity:
        """
        Returns the rarity of the character.

        :return: The rarity.
        :rtype: :class:`Rarity`
        """
        return Rarity.loads(self.__raw_data['data']['rarity'])

    @property
    def role(self) -> Role:
        """
        Returns the role of the character.

        :return: The role.
        :rtype: Role
        """
        return Role.loads(self.__raw_data['data']['role'])

    @property
    def weapon_type(self) -> WeaponType:
        """
        Returns the weapon type of the character.

        :return: The weapon type.
        :rtype: WeaponType
        """
        return WeaponType.loads(self.__raw_data['data']['weapon_type'])

    @property
    def attack_type(self) -> AttackType:
        """
        Returns the attack type of the character.

        :return: The attack type.
        :rtype: AttackType
        """
        return AttackType.loads(self.__raw_data['data']['attack_type'])

    def _skins(self) -> List[Tuple[str, str]]:
        """
        Returns the list of skins for the character.

        :return: The list of skins.
        :rtype: List[Tuple[str, str]]
        """
        return [(item['name'], item['url']) for item in self.__raw_data['skins']]

    def _release_time(self):
        """
        Returns the release time of the character.

        :return: The release time.
        :rtype: int
        """
        release_info = self.__raw_data['release']
        return release_info['time']

    def _order(self):
        """
        Returns the order of the character for sorting.

        :return: The order.
        :rtype: int
        """
        return self._release_time()

    def __repr__(self):
        """
        Returns a string representation of the character.

        :return: The string representation.
        :rtype: str
        """
        return f'<{type(self).__name__} {"/".join(map(str, self._names()))}, ' \
               f'{self.rarity.name}({int(self.rarity)}{"*" * self.rarity}), ' \
               f'role: {self.role}, attack: {self.attack_type}, weapon: {self.weapon_type}>'
