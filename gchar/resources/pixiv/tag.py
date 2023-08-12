import re
import warnings
from itertools import chain
from typing import Iterable, Iterator, Union, List, Tuple, Type, Mapping, Optional

from .keyword import _load_pixiv_names_for_game, _load_pixiv_alias_for_game
from ...games import get_character
from ...games.base import Character
from ...utils import optional_lru_cache


def _yield_tags(tags: Union[Tuple[str], List[str], str]) -> Iterator[str]:
    """
    Yield individual tags from a string or a list of tags.

    :param tags: The tags to yield.
    :type tags: Union[Tuple[str], List[str], str]
    :returns: An iterator of individual tags.
    :rtype: Iterator[str]
    """
    if isinstance(tags, str):
        for item in re.split(r'\s+', tags):
            if item:
                yield item
    elif isinstance(tags, (list, tuple, set)):
        for item in tags:
            yield from _yield_tags(item)


def _format_tags(positive, negative, or_clause=None):
    """
    Format the positive and negative tags into a valid Pixiv search tag string.

    :param positive: The positive tags.
    :type positive: Union[Tuple[str], List[str], str]
    :param negative: The negative tags.
    :type negative: Union[Tuple[str], List[str], str]
    :param or_clause: The OR clause tags.
    :type or_clause: Optional[Union[Tuple[str], List[str], str]]
    :returns: The formatted Pixiv search tag string.
    :rtype: str
    """
    positive_tags = list(_yield_tags(positive))
    negative_tags = list(_yield_tags(negative))
    or_clause_tags = list(_yield_tags(or_clause or ''))
    if len(or_clause_tags) == 1:
        or_tag = or_clause_tags[0]
        if or_tag not in positive_tags:
            positive_tags.append(or_tag)
        or_clause_tags = []

    positive_tags = set(positive_tags)
    or_clause_tags = set(or_clause_tags)
    negative_tags = set(negative_tags) - positive_tags - or_clause_tags
    positive_tags = sorted(positive_tags)
    negative_tags = sorted(negative_tags)
    or_clause_tags = sorted(or_clause_tags)

    all_phrases = [*positive_tags]
    if or_clause_tags:
        all_phrases.append(f'({" OR ".join(or_clause_tags)})')
    if negative_tags:
        all_phrases.extend((f'-{x}' for x in negative_tags))

    return ' '.join(all_phrases)


PIXIV_TAG_MAX_LENGTH = 256


class PixivCharPool:
    def __init__(self, chars: Iterable[Character],
                 names_dict: Mapping[str, Tuple[int, float, List[Tuple[str, int]]]],
                 names_alias: Mapping[Union[str, int], List[str]]):
        """
        Initialize the Pixiv character pool.

        :param chars: The iterable of Character instances.
        :type chars: Iterable[Character]
        :param names_dict: The mapping of character names to their Pixiv data.
        :type names_dict: Mapping[str, Tuple[int, float, List[Tuple[str, int]]]]
        :param names_alias: The mapping of character IDs or names to their Pixiv aliases.
        :type names_alias: Mapping[Union[str, int], List[str]]
        """
        self.__chars = list(chars)
        self.__names_dict = names_dict
        self.__names_alias = names_alias
        self.__all_names = sorted(
            set(self.__names_dict.keys()) |
            set(chain(*self.__names_alias.values()))
        )

    def __get_name_item(self, name) -> Optional[Tuple[int, float, List[Tuple[str, int]]]]:
        """
        Get the Pixiv data for a specific character name.

        :param name: The character name.
        :type name: str
        :returns: The Pixiv data tuple.
        :rtype: Optional[Tuple[int, float, List[Tuple[str, int]]]]
        """
        return self.__names_dict.get(name, None)

    def __get_name_count(self, name) -> int:
        """
        Get the count of illustrations for a specific character name.

        :param name: The character name.
        :type name: str
        :returns: The count of illustrations.
        :rtype: int
        """
        tpl = self.__get_name_item(name)
        if tpl:
            count, _, _ = tpl
            return count
        else:
            return 0

    def __get_name_pollution_ratio(self, name) -> float:
        """
        Get the pollution ratio for a specific character name.

        :param name: The character name.
        :type name: str
        :returns: The pollution ratio.
        :rtype: float
        """
        tpl = self.__get_name_item(name)
        if tpl:
            _, ratio, _ = tpl
            return ratio
        else:
            return 0.0

    def __get_name_pollution_words(self, name) -> List[Tuple[str, int]]:
        """
        Get the pollution words and their counts for a specific character name.

        :param name: The character name.
        :type name: str
        :returns: A list of pollution word-count tuples.
        :rtype: List[Tuple[str, int]]
        """
        tpl = self.__get_name_item(name)
        if tpl:
            _, _, pollution = tpl
            return pollution
        else:
            return []

    def _iter_dup_names(self, name: str) -> Iterator[str]:
        """
        Iterate over duplicate names that contain the given name.

        :param name: The name to search for.
        :type name: str
        :returns: An iterator of duplicate names.
        :rtype: Iterator[str]
        """
        for sname in self.__all_names:
            if name != sname and name in sname:
                yield sname

    def get_tag(self, char: Character, use_english: bool = False,
                positive: Optional[List[str]] = None, negative: Optional[List[str]] = None,
                max_exclude_per_word: int = 20, max_exclude: int = 20, max_pollution_ratio: float = 0.8,
                max_length: int = PIXIV_TAG_MAX_LENGTH):
        """
        Generate a Pixiv search tag for a specific character.

        :param char: The character instance or name.
        :type char: Union[Character, str]
        :param use_english: Whether to use English names in the tag.
        :type use_english: bool
        :param positive: The positive tags to include.
        :type positive: Optional[List[str]]
        :param negative: The negative tags to exclude.
        :type negative: Optional[List[str]
        :param max_exclude_per_word: The maximum number of excluded tags per word.
        :type max_exclude_per_word: int
        :param max_exclude: The maximum number of excluded tags.
        :type max_exclude: int
        :param max_pollution_ratio: The maximum pollution ratio for including tags.
        :type max_pollution_ratio: float
        :param max_length: The maximum length of the generated tag.
        :type max_length: int
        :returns: The generated Pixiv search tag.
        :rtype: str
        """
        if not isinstance(char, Character):
            raise TypeError(f'Invalid character type - {char!r}.')

        char_names = [*char.cnnames, *char.jpnames]
        if use_english:
            char_names.extend(char.ennames)
        if char.index in self.__names_alias:
            char_names.extend(self.__names_alias[char.index])

        char_names = sorted(set(map(lambda x: str(x).lower(), char_names)))

        origin_positive = positive
        origin_negative = negative
        positive = set(_yield_tags(positive or []))
        negative = set(_yield_tags(negative or [])) - positive
        or_clause = set()

        exclude_names = set()
        exclude_name_pairs = []
        min_pollution = 1.0
        for chname in char_names:
            s_chname = str(chname)
            name_pollution_ratio = self.__get_name_pollution_ratio(s_chname)
            min_pollution = min(name_pollution_ratio, min_pollution)
            all_exnames = list(self._iter_dup_names(s_chname))
            if name_pollution_ratio <= max_pollution_ratio and len(all_exnames) <= max_exclude_per_word:
                or_clause.add(s_chname)

                for pword, pcnt in self.__get_name_pollution_words(s_chname):
                    if pword not in positive and pword not in or_clause and \
                            pword != char and pword not in exclude_names:
                        exclude_names.add(pword)
                        exclude_name_pairs.append((pword, pcnt, 1))

                for exname in all_exnames:
                    if exname not in positive and exname not in or_clause and \
                            exname != char and exname not in exclude_names:
                        exclude_names.add(exname)
                        exclude_name_pairs.append((exname, self.__get_name_count(exname), 0))

        if or_clause:
            exclude_name_pairs = sorted(exclude_name_pairs, key=lambda x: (x[2], -x[1], len(x[0]), x[0]))[:max_exclude]

            while True:
                current_negative = set(negative)
                for exname, _, _ in exclude_name_pairs:
                    current_negative.add(exname)

                ret_keyword = _format_tags(positive, current_negative, or_clause)
                if len(ret_keyword) > max_length:
                    exclude_name_pairs = exclude_name_pairs[:-1]
                else:
                    return ret_keyword
        else:
            return self.get_tag(char, use_english, origin_positive, origin_negative,
                                max_exclude_per_word, max_exclude, max_pollution_ratio=min_pollution + 0.015)

    def _iter_end_dup_names(self, name: str) -> Iterator[str]:
        """
        Iterate over names that end with the given name.

        :param name: The name to search for.
        :type name: str
        :returns: An iterator of names.
        :rtype: Iterator[str]
        """
        for sname in self.__all_names:
            if name != sname and sname.endswith(name):
                yield sname

    def get_simple_tag(self, char: Character, base_tag: str, max_exclude: int = 20):
        """
        Generate a simplified Pixiv search tag for a specific character.

        :param char: The character instance.
        :type char: Character
        :param base_tag: The base tag to append to the character name.
        :type base_tag: str
        :param max_exclude: The maximum number of excluded tags.
        :type max_exclude: int
        :returns: The generated simplified Pixiv search tag.
        :rtype: str
        """
        if not isinstance(char, Character):
            raise TypeError(f'Invalid character type - {char!r}.')

        positive = set()
        negative = set()
        or_clause = set()
        if char.jpnames:
            exclude_names = set()
            for jpname in char.jpnames:
                if base_tag:
                    positive.add(f'{jpname}({base_tag})')
                else:
                    positive.add(jpname)
                for exname in self._iter_end_dup_names(str(jpname)):
                    exclude_names.add(exname)

            for exname in sorted(exclude_names, key=lambda x: self.__get_name_count(x), reverse=True)[:max_exclude]:
                negative.add(exname)

        else:
            raise ValueError(f'Japanese name not found for character - {char!r}.')

        return _format_tags(positive, negative, or_clause)


@optional_lru_cache()
def _get_char_pool(cls: Type[Character], **kwargs):
    """
    Get the Pixiv character pool for a specific character class.

    :param cls: The character class.
    :type cls: Type[Character]
    :returns: The PixivCharPool instance.
    :rtype: PixivCharPool
    """
    names_dict = _load_pixiv_names_for_game(cls)
    names_alias = _load_pixiv_alias_for_game(cls)
    return PixivCharPool(cls.all(**kwargs), names_dict, names_alias)


def get_pixiv_keywords(char: Union[Character, str], simple: bool = False, use_english: bool = True,
                       includes: Optional[List[str]] = None, exclude: Optional[List[str]] = None,
                       allow_fuzzy: bool = True, fuzzy_threshold: int = 70, max_exclude: int = 20,
                       max_pollution_ratio: float = 0.8, max_length: int = PIXIV_TAG_MAX_LENGTH, **kwargs):
    """
    Get the Pixiv search keywords for a specific character.

    :param char: The character instance or name.
    :type char: Union[Character, str]
    :param simple: Whether to generate a simplified tag.
    :type simple: bool
    :param use_english: Whether to use English names in the tag.
    :type use_english: bool
    :param includes: The positive tags to include.
    :type includes: Optional[Union[Tuple[str], List[str], str]]
    :param exclude: The negative tags to exclude.
    :type exclude: Optional[Union[Tuple[str], List[str], str]]
    :param allow_fuzzy: Whether to allow fuzzy matching of character names.
    :type allow_fuzzy: bool
    :param fuzzy_threshold: The threshold for fuzzy matching.
    :type fuzzy_threshold: int
    :param max_exclude: The maximum number of excluded tags.
    :type max_exclude: int
    :param max_pollution_ratio: The maximum pollution ratio for including tags.
    :type max_pollution_ratio: float
    :param max_length: The maximum length of the generated tag.
    :type max_length: int
    :returns: The generated Pixiv search keywords.
    :rtype: str
    :raises ValueError: If the character is unknown.

    Examples::
        >>> from gchar.resources.pixiv import get_pixiv_keywords
        >>>
        >>> get_pixiv_keywords('amiya')
        'アークナイツ (amiya OR アーミヤ OR 阿米娅)'
        >>> get_pixiv_keywords('surtr')
        'アークナイツ (surtr OR スルト OR 史尔特尔) -明日方舟スルト'
        >>> get_pixiv_keywords('dusk')  # ケルシー and ドロシー way cause search noises
        'アークナイツ (dusk OR シー OR 夕) -ケルシー -シージ -シーン -ドロシー -ルーシー -夕張 -夕日 -夕焼け'
    """
    original_char = char
    if not isinstance(char, Character):
        char = get_character(char, allow_fuzzy, fuzzy_threshold, **kwargs)
    if not char:
        raise ValueError(f'Unknown character - {original_char!r}.')
    if max_length > PIXIV_TAG_MAX_LENGTH:
        warnings.warn(UserWarning(f'The maximum length pixiv supports is {PIXIV_TAG_MAX_LENGTH}, '
                                  f'but {max_length!r} is given. '
                                  f'This may result in no search results.'), stacklevel=2)

    pool = _get_char_pool(type(char), **kwargs)
    game_tag = char.__pixiv_keyword__
    base_tag = char.__pixiv_suffix__

    try:
        if simple:
            return pool.get_simple_tag(char, base_tag, max_exclude=max_exclude)
    except ValueError:
        warnings.warn(UserWarning(f'No japanese name for {char!r}, falling back to full tag.'), stacklevel=2)

    pos = [*(includes or [])]
    if game_tag:
        pos.append(game_tag)
    return pool.get_tag(char, use_english, positive=pos, negative=exclude,
                        max_exclude=max_exclude, max_pollution_ratio=max_pollution_ratio, max_length=max_length)
