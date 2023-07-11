import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Union

from huggingface_hub import HfFileSystem, hf_hub_url

hf_fs = HfFileSystem()


@lru_cache()
def _read_hf_skins_meta(game: str, ch_index: Union[int, str]):
    online_dir = f'datasets/deepghs/game_characters/{game}/{ch_index}'
    meta_file = f'{online_dir}/.meta.json'
    if hf_fs.exists(meta_file):
        raw = json.loads(hf_fs.read_text(meta_file))
        return {
            skin['metadata']['name']: hf_hub_url(
                'deepghs/game_characters',
                filename=f'{game}/{ch_index}/{skin["name"]}',
                repo_type='dataset'
            ) for skin in raw['files']
        }
    else:
        return {}


@dataclass
class Skin:
    game: str
    ch_index: Union[int, str]
    name: str
    url: str

    @property
    def selected_url(self) -> str:
        return _read_hf_skins_meta(self.game, self.ch_index).get(self.name, self.url)
