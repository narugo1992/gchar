import os.path
import re
from typing import Iterator, Tuple, Union, List

import numpy as np
from PIL import Image
from hbutils.system import urlsplit
from imgutils.metrics import ccip_extract_feature
from tqdm.auto import tqdm
from waifuc.action import ModeConvertAction, FaceCountAction, PersonSplitAction, PaddingAlignAction, NoMonochromeAction
from waifuc.source import BaseDataSource
from waifuc.source.web import WebDataSource
from waifuc.utils import task_ctx

from gchar.games.azurlane import Character as AzurLaneCharacter
from gchar.games.base import Character
from gchar.games.base import Skin
from gchar.games.fgo import Character as FateGrandOrderCharacter
from gchar.games.girlsfrontline import Character as GirlsFrontLineCharacter
from gchar.games.neuralcloud import Character as NeuralCloudCharacter


def _yield_skin_default(ch: Character) -> Iterator[Skin]:
    yield from ch.skins


def _yield_skin_girlsfrontline(ch: GirlsFrontLineCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if 'profile' not in skin.name.lower():
            yield skin


def _yield_skin_fgo(ch: FateGrandOrderCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if '愚人节' not in skin.name and 'Grail'.lower() not in skin.name.lower():
            yield skin


def _yield_skin_neuralcloud(ch: NeuralCloudCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if '愚' not in skin.name and 'ZOO' not in skin.name:
            yield skin


def _yield_skin_azurlane(ch: AzurLaneCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if 'chibi' not in skin.name.lower():
            yield skin


_SKIN_YIELDERS = {
    'girlsfrontline': _yield_skin_girlsfrontline,
    'fgo': _yield_skin_fgo,
    'neuralcloud': _yield_skin_neuralcloud,
    'azurlane': _yield_skin_azurlane,
}


class CharacterSkinSource(WebDataSource):
    def __init__(self, ch: Character, download_silent: bool = True):
        WebDataSource.__init__(self, ch.__game_name__, download_silent=download_silent)
        self.ch = ch

    def _yield_skins(self):
        yielder = _SKIN_YIELDERS.get(self.ch.__game_name__, _yield_skin_default)
        yield from yielder(self.ch)

    def _iter_data(self) -> Iterator[Tuple[Union[str, int], str, dict]]:
        for skin in self._yield_skins():
            _, ext = os.path.splitext(urlsplit(skin.url).filename)
            name = re.sub(r'[\W_]+', '', skin.name).strip('_')
            meta = {
                'skin': {
                    'name': skin.name,
                    'url': skin.url,
                },
                'group_id': f'{self.group_name}_{name}',
                'filename': f'{self.group_name}_{name}{ext}',
            }
            yield skin.name, skin.url, meta


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
