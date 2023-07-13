import json
from functools import lru_cache
from typing import Type, Dict, Tuple, Optional, List, Union

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import yaml
from huggingface_hub import hf_hub_download, hf_hub_url

from ...games import get_character
from ...games.base import Character
from ...utils import get_requests_session, srequest


@lru_cache()
def _load_pixiv_alias_for_game(cls: Type[Character]) -> Dict[Union[int, str], List[str]]:
    """
    Load the Pixiv aliases for a specific game's character class.

    :param cls: The character class.
    :type cls: Type[Character]
    :returns: A dictionary mapping character IDs or names to a list of Pixiv aliases.
    :rtype: Dict[Union[int, str], List[str]]
    """
    game_name = cls.__game_name__
    resource_url = hf_hub_url(
        cls.__repository__,
        filename=f'{game_name}/pixiv_alias.yaml',
        repo_type='dataset'
    )
    session = get_requests_session()
    if srequest(session, 'HEAD', resource_url, raise_for_status=False).ok:
        with open(hf_hub_download(
                cls.__repository__,
                filename=f'{game_name}/pixiv_alias.yaml',
                repo_type='dataset'
        ), 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader)

        alias = data['alias']
        return {item['id']: item['alias'] for item in alias}

    else:
        return {}


def _parse_pixiv_names_file(names) -> Dict[str, Tuple[int, float, List[Tuple[str, int]]]]:
    """
    Parse the Pixiv names file and return a dictionary with character information.

    :param names: The names data from the Pixiv names file.
    :type names: Any
    :returns: A dictionary containing character names, counts, pollution ratio, and pollution words.
    :rtype: Dict[str, Tuple[int, float, List[Tuple[str, int]]]]
    """
    all_dict = {item['name']: item for item in names}
    all_counts = {}

    def _get_count(name):
        if name in all_counts:
            return all_counts[name]
        elif name not in all_dict:
            return 0
        else:
            item = all_dict[name]
            cnt = item['count']
            for ex in item['keyword']['excluded']:
                cnt += _get_count(ex)

            all_counts[name] = cnt
            return cnt

    retval = {}
    for item in names:
        name = item['name']
        count = _get_count(name)
        kwinfo = item['keyword']

        p_total = kwinfo['items']
        p_polluted = kwinfo['polluted']
        pollution_ratio = (p_polluted / p_total) if p_polluted else 0.0
        pollition_words = [(word, int(pcnt / p_total * count))
                           for word, pcnt in kwinfo['pollution'].items() if pcnt > 0]

        retval[name] = (count, pollution_ratio, pollition_words)

    return retval


def _load_pixiv_names_for_game(cls: Type[Character]) -> Dict[str, Tuple[int, float, List[Tuple[str, int]]]]:
    """
    Load the Pixiv names for a specific game's character class.

    :param cls: The character class.
    :type cls: Type[Character]
    :returns: A dictionary containing character names, counts, pollution ratio, and pollution words.
    :rtype: Dict[str, Tuple[int, float, List[Tuple[str, int]]]]
    """
    game_name = cls.__game_name__
    with open(hf_hub_download(
            cls.__repository__,
            filename=f'{game_name}/pixiv_names.json',
            repo_type='dataset'
    ), 'r', encoding='utf-8') as f:
        data = json.load(f)
        names = data['names']

    return _parse_pixiv_names_file(names)


@lru_cache()
def _load_pixiv_characters_for_game(cls: Type[Character]) -> Dict[str, Tuple[int, int]]:
    """
    Load the Pixiv character data for a specific game's character class.

    :param cls: The character class.
    :type cls: Type[Character]
    :returns: A dictionary mapping character indices to the number of all illustrations and R18 illustrations.
    :rtype: Dict[str, Tuple[int, int]]
    """
    game_name = cls.__game_name__
    with open(hf_hub_download(
            cls.__repository__,
            filename=f'{game_name}/pixiv_characters.json',
            repo_type='dataset'
    ), 'r', encoding='utf-8') as f:
        chs = json.load(f)['characters']

    return {item['index']: (item["illustrations"]["all"], item["illustrations"]["r18"]) for item in chs}


def get_pixiv_posts(char: Union[str, Character], allow_fuzzy: bool = True, fuzzy_threshold: int = 70, **kwargs) \
        -> Optional[Tuple[int, int]]:
    """
    Get the number of Pixiv posts for a given character.

    :param char: The character name or instance of Character class.
    :type char: Union[str, Character]
    :param allow_fuzzy: Whether to allow fuzzy matching of character names.
    :type allow_fuzzy: bool
    :param fuzzy_threshold: The threshold for fuzzy matching.
    :type fuzzy_threshold: int
    :returns: A tuple containing the number of all illustrations and R18 illustrations, or None if the character is unknown.
    :rtype: Optional[Tuple[int, int]]
    :raises ValueError: If the character is unknown.

    Examples::
        >>> from gchar.resources.pixiv import get_pixiv_posts
        >>>
        >>> get_pixiv_posts('amiya')
        (14130, 1113)
        >>> get_pixiv_posts('surtr')
        (5579, 787)
    """
    original_char = char
    if not isinstance(char, Character):
        char = get_character(char, allow_fuzzy, fuzzy_threshold, **kwargs)
    if not char:
        raise ValueError(f'Unknown character - {original_char!r}.')

    all_data = _load_pixiv_characters_for_game(type(char))
    return all_data.get(char.index, None)
