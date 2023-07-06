import json
from functools import lru_cache
from typing import Union, Mapping, List, Tuple

from huggingface_hub import hf_hub_download

from gchar.games import get_character
from gchar.games.base import Character
from .base import SITES

_AVAIL_SITE_NAMES = set(SITES.keys())


@lru_cache()
def _get_tags_for_game_site(game: str, site: str):
    with open(hf_hub_download(
            'deepghs/game_characters',
            filename=f'{game}/tags_{SITES[site]}.json',
            repo_type='dataset'
    ), 'r', encoding='utf-8') as f:
        return json.load(f)['data']


@lru_cache()
def _get_tag_mapping(game: str, site: str) -> Mapping[Union[str, int], List[dict]]:
    tags = _get_tags_for_game_site(game, site)
    return {tag['index']: tag['tags'] for tag in tags}


def _get_raw_site_tags(ch: Union[Character, str], site: str, sure_only: bool = False,
                       allow_fuzzy: bool = False, **kwargs) -> List[dict]:
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
    tags = _get_raw_site_tags(ch, site, sure_only, allow_fuzzy, **kwargs)
    if with_posts:
        return [(tag['name'], tag['count']) for tag in tags]
    else:
        return [tag['name'] for tag in tags]


def get_site_tag(ch: Union[Character, str], site: str, sure_only: bool = False,
                 with_posts: bool = False, allow_fuzzy: bool = False, **kwargs) \
        -> Union[str, Tuple[str, int], None]:
    tags = list_site_tags(ch, site, sure_only, with_posts, allow_fuzzy, **kwargs)
    if tags:
        return tags[0]
    else:
        return None
