import json
from functools import lru_cache
from typing import Union, Mapping, List, Tuple

from huggingface_hub import hf_hub_download
from huggingface_hub.utils import EntryNotFoundError

from gchar.games import get_character
from gchar.games.base import Character
from gchar.games.dispatch.access import GAME_CHARS
from .base import SITES

_AVAIL_SITE_NAMES = set(SITES.keys())


@lru_cache()
def _get_tags_for_game_site(game: str, site: str):
    """
    Get the tags for a specific game and site.

    :param game: The name of the game.
    :type game: str
    :param site: The name of the site.
    :type site: str
    :return: The tags for the game and site.
    :rtype: List[dict]
    """
    try:
        with open(hf_hub_download(
                GAME_CHARS[game].__repository__,
                filename=f'{game}/tags_{SITES[site]}.json',
                repo_type='dataset'
        ), 'r', encoding='utf-8') as f:
            return json.load(f)['data']
    except EntryNotFoundError:
        return []


@lru_cache()
def _get_tag_mapping(game: str, site: str) -> Mapping[Union[str, int], List[dict]]:
    """
    Get the mapping of tags for a specific game and site.

    :param game: The name of the game.
    :type game: str
    :param site: The name of the site.
    :type site: str
    :return: The mapping of tags.
    :rtype: Mapping[Union[str, int], List[dict]]
    """
    tags = _get_tags_for_game_site(game, site)
    return {tag['index']: tag['tags'] for tag in tags}


def _get_raw_site_tags(ch: Union[Character, str], site: str, sure_only: bool = False,
                       allow_fuzzy: bool = False, **kwargs) -> List[dict]:
    """
    Get the raw tags for a character and site.

    :param ch: The character instance or name.
    :type ch: Union[Character, str]
    :param site: The name of the site.
    :type site: str
    :param sure_only: Whether to include only sure tags.
    :type sure_only: bool
    :param allow_fuzzy: Whether to allow fuzzy matching of character names.
    :type allow_fuzzy: bool
    :param kwargs: Additional arguments for character retrieval.
    :return: The raw tags for the character and site.
    :rtype: List[dict]
    """
    if site not in _AVAIL_SITE_NAMES:
        raise ValueError(f'Unsupported site - {site!r}.\n'
                         f'{list(SITES.keys())!r} are supported.')
    if not isinstance(ch, Character):
        ch = get_character(ch, allow_fuzzy, **kwargs)

    _tag_mapping = _get_tag_mapping(ch.__game_name__, site)
    if ch.index in _tag_mapping:
        tags = _tag_mapping[ch.index]
        if sure_only:
            tags = [tag for tag in tags if tag['sure']]
        return tags
    else:
        return []


def list_site_tags(ch: Union[Character, str], site: str, sure_only: bool = False,
                   with_posts: bool = False, allow_fuzzy: bool = False, **kwargs) \
        -> Union[List[str], List[Tuple[str, int]]]:
    """
    List the tags for a character and site.

    :param ch: The character instance or name.
    :type ch: Union[Character, str]
    :param site: The name of the site.
    :type site: str
    :param sure_only: Whether to include only sure tags.
    :type sure_only: bool
    :param with_posts: Whether to include the number of posts for each tag.
    :type with_posts: bool
    :param allow_fuzzy: Whether to allow fuzzy matching of character names.
    :type allow_fuzzy: bool
    :param kwargs: Additional arguments for character retrieval.
    :return: The list of tags for the character and site.
    :rtype: Union[List[str], List[Tuple[str, int]]]

    Examples::
        >>> from gchar.resources.sites import list_site_tags
        >>>
        >>> list_site_tags('amiya', 'danbooru')
        ['amiya_(arknights)', 'amiya_(guard)_(arknights)', 'amiya_(newsgirl)_(arknights)', 'amiya_(fresh_fastener)_(arknights)', 'amiya_(planter)_(arknights)', 'amiya_(guard)_(touch_the_stars)_(arknights)']
        >>> list_site_tags('surtr', 'danbooru')
        ['surtr_(arknights)', 'surtr_(colorful_wonderland)_(arknights)', 'surtr_(liberte_echec)_(arknights)']
        >>> list_site_tags('surtr', 'danbooru', with_posts=True)
        [('surtr_(arknights)', 2666), ('surtr_(colorful_wonderland)_(arknights)', 483), ('surtr_(liberte_echec)_(arknights)', 306)]
        >>> list_site_tags('surtr', 'zerochan')
        ['Surtr (Arknights)']
        >>> list_site_tags('surtr', 'anime_pictures')
        ['surtr (arknights)', 'surtr (liberte echec) (arknights)', 'surtr (colorful wonderland) (arknights)']
        >>> list_site_tags('surtr', 'anime_pictures', with_posts=True)
        [('surtr (arknights)', 471), ('surtr (liberte echec) (arknights)', 75), ('surtr (colorful wonderland) (arknights)', 49)]
    """
    tags = _get_raw_site_tags(ch, site, sure_only, allow_fuzzy, **kwargs)
    if with_posts:
        return [(tag['name'], tag['count']) for tag in tags]
    else:
        return [tag['name'] for tag in tags]


def get_site_tag(ch: Union[Character, str], site: str, sure_only: bool = False,
                 with_posts: bool = False, allow_fuzzy: bool = False, **kwargs) \
        -> Union[str, Tuple[str, int], None]:
    """
    Get a single tag for a character and site.

    :param ch: The character instance or name.
    :type ch: Union[Character, str]
    :param site: The name of the site.
    :type site: str
    :param sure_only: Whether to include only sure tags.
    :type sure_only: bool
    :param with_posts: Whether to include the number of posts for the tag.
    :type with_posts: bool
    :param allow_fuzzy: Whether to allow fuzzy matching of character names.
    :type allow_fuzzy: bool
    :param kwargs: Additional arguments for character retrieval.
    :return: The tag for the character and site.
    :rtype: Union[str, Tuple[str, int], None]

    Examples:
        >>> from gchar.resources.sites import get_site_tag
        >>>
        >>> get_site_tag('amiya', 'danbooru')
        'amiya_(arknights)'
        >>> get_site_tag('surtr', 'danbooru')
        'surtr_(arknights)'
        >>> get_site_tag('surtr', 'danbooru', with_posts=True)
        ('surtr_(arknights)', 2666)
        >>> get_site_tag('surtr', 'zerochan')
        'Surtr (Arknights)'
        >>> get_site_tag('surtr', 'anime_pictures')
        'surtr (arknights)'
        >>> get_site_tag('surtr', 'anime_pictures', with_posts=True)
        ('surtr (arknights)', 471)
    """
    tags = list_site_tags(ch, site, sure_only, with_posts, allow_fuzzy, **kwargs)
    if tags:
        return tags[0]
    else:
        return None
