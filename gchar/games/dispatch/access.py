from functools import lru_cache
from itertools import islice
from typing import Iterator, Tuple, Optional, List, Type, Dict

from huggingface_hub.utils import EntryNotFoundError
from thefuzz import fuzz

from ..arknights import Character as ArknightsCharacter
from ..azurlane import Character as AzurLaneCharacter
from ..base import Character
from ..bluearchive import Character as BlueArchiveCharacter
from ..fgo import Character as FateGrandOrderCharacter
from ..genshin import Character as GenshinImpactCharacter
from ..girlsfrontline import Character as GirlsFrontLineCharacter
from ..neuralcloud import Character as NeuralCloudCharacter
from ..nikke import Character as NikkeCharacter
from ..pathtonowhere import Character as PathToNowhereCharacter
from ..starrail import Character as StarRailCharacter
from ...utils import optional_lru_cache

GAME_CHARS: Dict[str, Type[Character]] = {}


def register_game(cls: Type[Character]):
    """
    Register a game and its corresponding character class.

    :param cls: The character class.
    :type cls: Type[Character]
    :raises KeyError: If the game is already registered.
    """
    if cls.__game_name__ in GAME_CHARS:
        raise KeyError(f'Game {cls.__game_name__!r} already exist.')
    else:
        GAME_CHARS[cls.__game_name__] = cls


def list_available_game_names() -> List[str]:
    """
    Get a list of available game names.

    :return: The list of game names.
    :rtype: List[str]

    Examples::
        >>> from gchar.games import list_available_game_names
        >>>
        >>> list_available_game_names()
        ['arknights', 'azurlane', 'bluearchive', 'fgo', 'genshin', 'girlsfrontline', 'neuralcloud', 'nikke', 'pathtonowhere', 'starrail']
    """
    return sorted(GAME_CHARS.keys())


def get_character_class(game_name: str) -> Type[Character]:
    """
    Get the character class for a given game name.

    :param game_name: The name of the game.
    :type game_name: str
    :return: The character class.
    :rtype: Type[Character]
    :raises KeyError: If the game is not found.
    """
    if game_name in GAME_CHARS:
        return GAME_CHARS[game_name]
    else:
        raise KeyError(f'Game {game_name!r} not found.')


register_game(ArknightsCharacter)
register_game(FateGrandOrderCharacter)
register_game(AzurLaneCharacter)
register_game(GenshinImpactCharacter)
register_game(GirlsFrontLineCharacter)
register_game(NeuralCloudCharacter)
register_game(BlueArchiveCharacter)
register_game(PathToNowhereCharacter)
register_game(NikkeCharacter)
register_game(StarRailCharacter)


def load_generic():
    from ...generic import import_generic
    import_generic()


@optional_lru_cache()
def _all_characters(**kwargs) -> List[Character]:
    """
    Get a list of all characters from all registered games.

    :param kwargs: Additional arguments for character retrieval.
    :return: The list of characters.
    :rtype: List[Character]
    """
    from ...resources.pixiv import get_pixiv_posts

    chs: List[Tuple[Character, int, bool, int]] = []
    cnt = 0
    for _, _ch_set in GAME_CHARS.items():
        for ch in _ch_set.all(**kwargs, sorted=False):
            try:
                counts = get_pixiv_posts(ch)
                if counts:
                    all_count, _ = counts
                else:
                    all_count = 0
            except EntryNotFoundError:
                all_count = 0
            chs.append((ch, all_count, ch.is_extra, cnt))
            cnt += 1

    chs = sorted(chs, key=lambda x: (0 if not x[2] else 1, -x[1], x[3]))
    return [ch for ch, _, _, _ in chs]


# NAME SIMILAR: 101-200
# ALIAS SIMILAR: 1-100
_ALIAS_MATCH = 300
_NAME_MATCH = 400


def _name_trim(name: str) -> str:
    """
    Trim a character name by removing spaces, dashes, underscores, and special characters.

    :param name: The character name.
    :type name: str
    :return: The trimmed character name.
    :rtype: str
    """
    return name.replace(' ', '').replace('-', '').replace('_', '').replace(chr(160), '').replace('\t', '')


def _yield_characters(name: str, allow_fuzzy: bool = False, fuzzy_threshold: int = 80, **kwargs) \
        -> Iterator[Tuple[Character, int]]:
    """
    Yield characters that match the given name.

    :param name: The character name.
    :type name: str
    :param allow_fuzzy: Whether to allow fuzzy matching of character names.
    :type allow_fuzzy: bool
    :param fuzzy_threshold: The threshold for fuzzy matching.
    :type fuzzy_threshold: int
    :param kwargs: Additional arguments for character retrieval.
    :return: The iterator of matching characters and their match scores.
    :rtype: Iterator[Tuple[Character, int]]
    """
    all_chs = _all_characters(**kwargs)
    for ch in all_chs:
        if any([_name == name for _name in ch._names()]):
            yield ch, _NAME_MATCH
    for ch in all_chs:
        if any([_name == name for _name in ch.alias_names]):
            yield ch, _ALIAS_MATCH

    if allow_fuzzy:
        @lru_cache()
        def _get_formatted_name(cls) -> str:
            return str(cls(name))

        items: List[Tuple[Character, int, int]] = []
        for i, ch in enumerate(all_chs):
            name_fuzzs = [
                fuzz.WRatio(
                    _name_trim(_get_formatted_name(type(_name))),
                    _name_trim(str(_name)),
                    force_ascii=False
                )
                for _name in ch._names()
            ]
            if name_fuzzs and max(name_fuzzs) >= fuzzy_threshold:
                items.append((ch, max(name_fuzzs) + 100, i))
        items = sorted(items, key=lambda x: (-x[1], x[2]))
        for ch, fuzzy, _ in items:
            yield ch, fuzzy

        items: List[Tuple[Character, int, int]] = []
        for i, ch in enumerate(all_chs):
            alias_fuzzs = [
                fuzz.WRatio(
                    _name_trim(_get_formatted_name(type(_name))),
                    _name_trim(str(_name)),
                    force_ascii=False
                )
                for _name in ch.alias_names
            ]
            if alias_fuzzs and max(alias_fuzzs) >= fuzzy_threshold:
                items.append((ch, max(alias_fuzzs), i))
        items = sorted(items, key=lambda x: (-x[1], x[2]))
        for ch, fuzzy, _ in items:
            yield ch, fuzzy


def list_character(name: str, limit: Optional[int] = None, allow_fuzzy: bool = False,
                   fuzzy_threshold: int = 80, **kwargs) -> List[Character]:
    """
    List characters that match the given name.

    :param name: The character name.
    :type name: str
    :param limit: The maximum number of characters to return.
    :type limit: Optional[int]
    :param allow_fuzzy: Whether to allow fuzzy matching of character names.
    :type allow_fuzzy: bool
    :param fuzzy_threshold: The threshold for fuzzy matching.
    :type fuzzy_threshold: int
    :param kwargs: Additional arguments for character retrieval.
    :return: The list of matching characters.
    :rtype: List[Character]
    """
    iterator = _yield_characters(name, allow_fuzzy, fuzzy_threshold, **kwargs)
    if limit is not None:
        iterator = islice(iterator, limit)

    ordered = [ch for ch, _ in iterator]
    assert limit is None or len(ordered) <= limit
    return ordered


def get_character(name: str, allow_fuzzy: bool = False, fuzzy_threshold: int = 80,
                  contains_extra: bool = True, **kwargs) -> Optional[Character]:
    """
    Get a character that matches the given name.

    :param name: The character name.
    :type name: str
    :param allow_fuzzy: Whether to allow fuzzy matching of character names.
    :type allow_fuzzy: bool
    :param fuzzy_threshold: The threshold for fuzzy matching.
    :type fuzzy_threshold: int
    :param contains_extra: Whether to include extra characters.
    :type contains_extra: bool
    :param kwargs: Additional arguments for character retrieval.
    :return: The matching character, or None if not found.
    :rtype: Optional[Character]

    Examples::
        >>> from gchar.games import get_character
        >>>
        >>> get_character('amiya')
        <Character R001 - 阿米娅/amiya/アーミヤ, female, 5*****>
        >>> get_character('surtr')
        <Character R111 - 史尔特尔/surtr/スルト, female, 6******>
        >>> get_character('dusk')
        <Character NM02 - 夕/dusk/シー, female, 6******>
        >>> get_character('yae_miko')
        <Character 八重神子/yae_miko/八重神子/やえみこ, female, 5*****, weapon: Weapon.CATALYST, element: Element.ELECTRO>
    """
    _items = list_character(name, limit=1, allow_fuzzy=allow_fuzzy, fuzzy_threshold=fuzzy_threshold,
                            contains_extra=contains_extra, **kwargs)
    if _items:
        return _items[0]
    else:
        return None
