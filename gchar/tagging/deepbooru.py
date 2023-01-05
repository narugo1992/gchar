from functools import lru_cache
from typing import Union, List, Dict, Set

import numpy as np
import pandas as pd
from PIL import Image
from huggingface_hub import hf_hub_download

from ..utils import is_cuda_available


@lru_cache()
def _get_deepdanbooru_onnx():
    try:
        import deepdanbooru_onnx
    except ImportError:
        from hbutils.system import pip_install

        reqs = ['deepdanbooru-onnx>=0.0.8']
        if is_cuda_available():
            reqs.append(['onnxruntime-gpu>=1.13'])
        pip_install(reqs)
        import deepdanbooru_onnx

    return deepdanbooru_onnx


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
    return _get_tags_from_txt(hf_hub_download('narugo/gchar_models', 'deepdanbooru/tags-character.txt'))


@lru_cache()
def _get_character_tag_set() -> Set[str]:
    return set(_get_character_tags())


def is_character_tag(tag: str):
    return tag in _get_character_tag_set()


def get_all_tags() -> List[str]:
    model = _get_deepbooru_model()
    return model.tags


_SINGLE_IMAGE = Union[Image.Image, np.ndarray, str]
_DEEPBOORU_MODEL = None


def _get_deepbooru_model():
    global _DEEPBOORU_MODEL
    if _DEEPBOORU_MODEL is None:
        deepdanbooru_onnx = _get_deepdanbooru_onnx()
        _DEEPBOORU_MODEL = deepdanbooru_onnx.DeepDanbooru()

    return _DEEPBOORU_MODEL


def init_deepbooru():
    _ = _get_deepbooru_model()


def _item_process(item: _SINGLE_IMAGE) -> np.ndarray:
    deepdanbooru_onnx = _get_deepdanbooru_onnx()
    if isinstance(item, str):
        return deepdanbooru_onnx.process_image(Image.open(item))
    elif isinstance(item, Image.Image):
        return deepdanbooru_onnx.process_image(item)
    elif isinstance(item, np.ndarray):
        return item
    else:
        raise TypeError(f'Unknown image format - {item!r}.')


def get_deepbooru_features(image: _SINGLE_IMAGE) -> pd.DataFrame:
    model = _get_deepbooru_model()
    feat = model.inference(_item_process(image))
    return pd.DataFrame({
        'name': model.tags,
        'confidence': feat.reshape(-1),
    })


def get_deepbooru_tags(image: _SINGLE_IMAGE, threshold: float = 0.7, no_character: bool = False) -> Dict[str, float]:
    model = _get_deepbooru_model()
    feat = model.inference(_item_process(image))
    image_tag = {}
    for tag, score in zip(model.tags, feat[0]):
        if score >= threshold and (not no_character or not is_character_tag(tag)):
            image_tag[tag] = score

    return {key: float(value) for key, value in sorted(image_tag.items(), key=lambda x: (-x[1], x[0]))}
