from functools import lru_cache
from typing import Union, List, Dict, Set

import numpy as np
from PIL import Image
from deepdanbooru_onnx import DeepDanbooru, process_image

from .resource import get_resource_file


def _get_tags_from_txt(txtfile: str) -> List[str]:
    with open(txtfile, 'r') as f:
        tags = []
        for line in f:
            line = line.strip()
            if line:
                tags.append(line)

        return tags


@lru_cache()
def _get_character_tags() -> List[str]:
    return _get_tags_from_txt(get_resource_file('./deepbooru/tags-character.txt'))


@lru_cache()
def _get_character_tag_set() -> Set[str]:
    return set(_get_character_tags())


def is_character_tag(tag: str):
    return tag in _get_character_tag_set()


def get_all_tags() -> List[str]:
    model = _get_danbooru_model()
    return model.tags


_SINGLE_IMAGE = Union[Image.Image, np.ndarray, str]
_DEEPBOORU_MODEL = None


def _get_danbooru_model() -> DeepDanbooru:
    global _DEEPBOORU_MODEL
    if _DEEPBOORU_MODEL is None:
        _DEEPBOORU_MODEL = DeepDanbooru()

    return _DEEPBOORU_MODEL


def init_deepbooru():
    _ = _get_danbooru_model()


def _item_process(item: _SINGLE_IMAGE) -> np.ndarray:
    if isinstance(item, str):
        return process_image(Image.open(item))
    elif isinstance(item, Image.Image):
        return process_image(item)
    elif isinstance(item, np.ndarray):
        return item
    else:
        raise TypeError(f'Unknown image format - {item!r}.')


def get_deepbooru_features(image: _SINGLE_IMAGE) -> np.ndarray:
    model = _get_danbooru_model()
    feat = model.inference(_item_process(image))
    return feat.reshape(-1)


def get_deepbooru_tags(image: _SINGLE_IMAGE, threshold: float = 0.7, no_character: bool = False) -> Dict[str, float]:
    model = _get_danbooru_model()
    feat = model.inference(_item_process(image))
    image_tag = {}
    for tag, score in zip(model.tags, feat[0]):
        if score >= threshold and (not no_character or not is_character_tag(tag)):
            image_tag[tag] = score

    return image_tag
