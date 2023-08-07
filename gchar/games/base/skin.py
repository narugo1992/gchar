import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Union

from huggingface_hub import HfFileSystem, hf_hub_url

hf_fs = HfFileSystem()


@lru_cache()
def _read_hf_skins_meta(game: str, ch_index: Union[int, str]):
    """
    Read the metadata for the skins of a game character from the Hugging Face Hub.

    The function reads the metadata file for the specified game character from the Hugging Face Hub dataset repository.
    It retrieves the names and URLs of the skins that have been synchronized to the Hugging Face Hub.

    :param game: The game name.
    :type game: str
    :param ch_index: The index or ID of the game character.
    :type ch_index: Union[int, str]
    :returns: A dictionary mapping skin names to their Hugging Face Hub URLs.
    :rtype: dict
    """
    from gchar.games.dispatch.access import GAME_CHARS
    repository = GAME_CHARS[game].__skin_repository__

    online_dir = f'datasets/{repository}/{game}/{ch_index}'
    meta_file = f'{online_dir}/.meta.json'
    if hf_fs.exists(meta_file):
        raw = json.loads(hf_fs.read_text(meta_file))
        return {
            skin['metadata']['name']: hf_hub_url(
                repository,
                filename=f'{game}/{ch_index}/{skin["name"]}',
                repo_type='dataset'
            ) for skin in raw['files']
        }
    else:
        return {}


@dataclass
class Skin:
    """
    Represents a skin of a game character.

    The class stores information about the game, character index, skin name, and original URL of the skin.
    It provides a property `selected_url` that returns the URL of the skin, which is either the Hugging Face Hub URL
    if the skin has been synchronized or the original URL.

    :param game: The game name.
    :type game: str
    :param ch_index: The index or ID of the game character.
    :type ch_index: Union[int, str]
    :param name: The name of the skin.
    :type name: str
    :param url: The original URL of the skin.
    :type url: str
    """

    game: str
    ch_index: Union[int, str]
    name: str
    url: str

    @property
    def selected_url(self) -> str:
        """
        Get the URL of the skin.

        If the skin has been synchronized to the Hugging Face Hub, the Hugging Face Hub URL is returned.
        Otherwise, the original URL is returned.

        :returns: The URL of the skin.
        :rtype: str
        """
        return _read_hf_skins_meta(self.game, self.ch_index).get(self.name, self.url)
