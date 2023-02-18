import json
import os.path
import re
import time
from typing import List, Tuple, Iterator, Dict, Union, Type, Optional

import requests
from requests.auth import HTTPBasicAuth, AuthBase
from tqdm.auto import tqdm

from .games import _get_info_by_cls
from ...config.meta import __VERSION__
from ...games import __file__ as __games_file__
from ...games.base import Character
from ...utils import sget, get_requests_session, download_file, optional_lru_cache


def _get_danbooru_auth() -> Optional[AuthBase]:
    username = os.environ.get('DANBOORU_USERNAME', '')
    api_token = os.environ.get('DANBOORU_APITOKEN', '')
    if username or api_token:
        return HTTPBasicAuth(username, api_token)
    else:
        return None


def _get_danbooru_tags(session: requests.Session, game: str) -> Iterator[Tuple[int, str, int]]:
    page = 1
    page_tqdm = tqdm()
    while True:
        page_tqdm.set_description(f'Tag *_({game}) page {page}')
        resp = sget(
            session, 'https://danbooru.donmai.us/tags.json',
            params={
                'search[name_matches]': f'*_({game})',
                'search[name]': None,
                'search[category]': "4",  # characters only
                'search[hide_empty]': "no",
                'search[has_wiki]': None,
                'search[has_artist]': None,
                'search[order]': None,
                "limit": str(1000),
                "page": str(page),
            },
            auth=_get_danbooru_auth(),
        )
        page_tqdm.update()

        tags = resp.json()
        for item in tags:
            yield item['id'], item['name'], item['post_count']
        page += 1

        if not tags:
            break


PATTERN = re.compile(r'^(?P<title>[^(]+)(_\((?P<subtitle>\S+?)\))?_\((?P<game>[^)]+)\)$')


def _split_name(tag: str) -> Tuple[str, List[str], str]:
    matching = PATTERN.fullmatch(tag)
    if not matching:
        raise ValueError(f'Invalid tag - {tag!r}.')  # pragma: no cover

    title, subtitle, game = matching.group('title'), matching.group('subtitle'), matching.group('game')
    if subtitle:
        subtitles = subtitle.split(')_(')
    else:
        subtitles = []
    subtitles = [t for t in subtitles if t != game]

    return title, subtitles, game


def _trim_name_to_ascii(name: str) -> str:
    return ''.join(re.findall('[a-zA-Z0-9]+', name.lower()))


def _makeup_tags(session: requests.Session, games: Union[List[str], str]) -> List[Dict]:
    if not isinstance(games, (list, tuple, set)):
        games = [games]
    games_tqdm = tqdm(games)
    tags: List[Dict] = []
    for game in games_tqdm:
        games_tqdm.set_description(game)
        for tid, tag, posts in _get_danbooru_tags(session, game):
            title, subtitles, game = _split_name(tag)
            tags.append({
                'id': tid,
                'tag': tag,
                'posts': posts,
                'split': {
                    'title': title,
                    'subtitles': subtitles,
                    'game': game,
                },
            })

    return tags


def _make_lookup_by_tags(tags: List[Dict]) -> Dict[str, List[int]]:
    lookup: Dict[str, List[int]] = {}
    for i, item in enumerate(tags):
        _trimed = _trim_name_to_ascii(item['split']['title'])
        if _trimed not in lookup:
            lookup[_trimed] = []
        lookup[_trimed].append(i)

    return lookup


_GAMES_DIRECTORY = os.path.dirname(__games_file__)


def _local_file(name: str) -> str:
    return os.path.join(_GAMES_DIRECTORY, name, 'danbooru_tags.json')


def _is_lookup_local_ready(cls: Type[Character]):
    name, _ = _get_info_by_cls(cls)
    return os.path.exists(_local_file(name))


def _save_tags_to_local(cls: Type[Character], file: Optional[str] = None,
                        session: Optional[requests.Session] = None):
    session = session or get_requests_session(headers={
        "User-Agent": f"gchar/{__VERSION__}",
        'Content-Type': 'application/json; charset=utf-8',
    })
    name, game_names = _get_info_by_cls(cls)
    tags = _makeup_tags(session, game_names)
    file = file or _local_file(name)
    _file_dir = os.path.dirname(file)
    if _file_dir:
        os.makedirs(_file_dir, exist_ok=True)
    with open(file, 'w', encoding='utf-8') as f:
        json.dump({
            'tags': tags,
            'last_updated': time.time(),
        }, f, indent=4, ensure_ascii=False)


def _load_lookup_from_local(cls: Type[Character]) -> Tuple[List[Dict], Dict[str, List[int]]]:
    name, _ = _get_info_by_cls(cls)
    with open(_local_file(name), 'r', encoding='utf-8') as f:
        data = json.load(f)
        tags = data['tags']
        return tags, _make_lookup_by_tags(tags)


def _online_tags_url(name: str) -> str:
    return f'https://huggingface.co/datasets/deepghs/game_characters/resolve/main/{name}/danbooru_tags.json'


def _download_from_huggingface(name: str):
    download_file(_online_tags_url(name), _local_file(name))


@optional_lru_cache()
def get_lookup(cls: Type[Character], crawl: bool = False) -> Tuple[List[Dict], Dict[str, List[int]]]:
    if not _is_lookup_local_ready(cls):
        if crawl:
            _save_tags_to_local(cls)
        else:
            name, _ = _get_info_by_cls(cls)
            _download_from_huggingface(name)

    return _load_lookup_from_local(cls)
