import json
import os.path
import re
from typing import Iterator, Tuple, Union, List

import numpy as np
from PIL import Image
from hbutils.system import urlsplit
from huggingface_hub import HfFileSystem, hf_hub_url
from imgutils.metrics import ccip_extract_feature
from tqdm.auto import tqdm
from waifuc.action import ModeConvertAction, FaceCountAction, PersonSplitAction, PaddingAlignAction, NoMonochromeAction
from waifuc.source import BaseDataSource
from waifuc.source.web import WebDataSource
from waifuc.utils import task_ctx

from gchar.games.base import Character
from gchar.generic import import_generic

import_generic()


class CharacterSkinSource(WebDataSource):
    def __init__(self, ch: Character, download_silent: bool = True):
        WebDataSource.__init__(self, ch.__game_name__, download_silent=download_silent)
        self.ch = ch
        self.hf_fs = HfFileSystem()

    def _yield_skins(self):
        yield from self.ch.formal_skins

    def _iter_data(self) -> Iterator[Tuple[Union[str, int], str, dict]]:
        skin_dir = f'datasets/{self.ch.__skin_repository__}/{self.ch.__game_name__}/{self.ch.index}'
        meta_json = f'{skin_dir}/.meta.json'
        if self.hf_fs.exists(meta_json):
            meta = json.loads(self.hf_fs.read_text(meta_json))
            skin_files = {item['metadata']['name']: item['name'] for item in meta['files']}

            for skin in self._yield_skins():
                if skin.name in skin_files:
                    url = hf_hub_url(
                        self.ch.__skin_repository__,
                        filename=f'{self.ch.__game_name__}/{self.ch.index}/{skin_files[skin.name]}',
                        repo_type='dataset',
                    )

                    _, ext = os.path.splitext(urlsplit(url).filename)
                    name = re.sub(r'[\W_]+', '', skin.name).strip('_')
                    meta = {
                        'skin': {
                            'name': skin.name,
                            'url': skin.url,
                        },
                        'group_id': f'{self.group_name}_{name}',
                        'filename': f'{self.group_name}_{name}{ext}',
                    }
                    yield skin.name, url, meta


def get_ccip_features_of_character(ch: Character, maxcnt: int = 10) -> List[np.ndarray]:
    s = CharacterSkinSource(ch)
    images = []
    title = f'{ch.__game_name__}.{str(ch.enname)}'
    with task_ctx(title):
        for item in s.attach(
                ModeConvertAction('RGB', 'white'),
                PersonSplitAction(),
                PaddingAlignAction((512, 704)),
        )[:maxcnt]:
            images.append(item.image)

    feats = []
    for image in tqdm(images, desc=f'Feature Extract - {title}'):
        feats.append(ccip_extract_feature(image))
    return feats


class TagFeatureExtract:
    def __init__(self, tag):
        self.tag = tag

    def get_datasource(self) -> BaseDataSource:
        raise NotImplementedError

    def get_images(self, maxcnt: int = 10) -> List[Image.Image]:
        images = []
        with task_ctx(self.tag):
            for item in self.get_datasource().attach(
                    ModeConvertAction('RGB', 'white'),
                    NoMonochromeAction(),
                    FaceCountAction(1),
                    PersonSplitAction(),
                    FaceCountAction(1),
                    PaddingAlignAction((512, 704)),
            )[:maxcnt]:
                images.append(item.image)

        return images

    def get_features(self, maxcnt: int = 10) -> List[np.ndarray]:
        feats = []
        for image in tqdm(self.get_images(maxcnt), desc=f'Feature Extract - {self.tag}'):
            feats.append(ccip_extract_feature(image))

        return feats
