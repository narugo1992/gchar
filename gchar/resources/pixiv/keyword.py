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
    game_name = cls.__game_name__
    resource_url = hf_hub_url(
        'deepghs/game_characters',
        filename=f'{game_name}/pixiv_alias.yaml',
        repo_type='dataset'
    )
    session = get_requests_session()
    if srequest(session, 'HEAD', resource_url, raise_for_status=False).ok:
        with open(hf_hub_download(
                'deepghs/game_characters',
                filename=f'{game_name}/pixiv_alias.yaml',
                repo_type='dataset'
        ), 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader)

        alias = data['alias']
        return {item['id']: item['alias'] for item in alias}

    else:
        return {}


def _parse_pixiv_names_file(names) -> Dict[str, Tuple[int, float, List[Tuple[str, int]]]]:
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
    game_name = cls.__game_name__
    with open(hf_hub_download(
            'deepghs/game_characters',
            filename=f'{game_name}/pixiv_names.json',
            repo_type='dataset'
    ), 'r', encoding='utf-8') as f:
        data = json.load(f)
        names = data['names']

    return _parse_pixiv_names_file(names)


@lru_cache()
def _load_pixiv_characters_for_game(cls: Type[Character]) -> Dict[str, Tuple[int, int]]:
    game_name = cls.__game_name__
    with open(hf_hub_download(
            'deepghs/game_characters',
            filename=f'{game_name}/pixiv_characters.json',
            repo_type='dataset'
    ), 'r', encoding='utf-8') as f:
        chs = json.load(f)['characters']

    return {item['index']: (item["illustrations"]["all"], item["illustrations"]["r18"]) for item in chs}


def get_pixiv_posts(char, allow_fuzzy: bool = True, fuzzy_threshold: int = 70, **kwargs) -> Optional[Tuple[int, int]]:
    original_char = char
    if not isinstance(char, Character):
        char = get_character(char, allow_fuzzy, fuzzy_threshold, **kwargs)
    if not char:
        raise ValueError(f'Unknown character - {original_char!r}.')

    all_data = _load_pixiv_characters_for_game(type(char))
    return all_data.get(char.index, None)
