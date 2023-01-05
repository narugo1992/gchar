from functools import lru_cache
from pathlib import Path
from typing import Tuple, Dict, Mapping

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from huggingface_hub import hf_hub_download

from ..utils import is_cuda_available


@lru_cache()
def _try_init_onnxruntime():
    from hbutils.system import check_reqs, pip_install
    if not check_reqs(['onnxruntime']):
        reqs = ['onnxruntime>=1.13']
        if is_cuda_available():
            reqs.append(['onnxruntime-gpu>=1.13'])
        pip_install(reqs)


def make_square(img, target_size):
    old_size = img.shape[:2]
    desired_size = max(old_size)
    desired_size = max(desired_size, target_size)

    delta_w = desired_size - old_size[1]
    delta_h = desired_size - old_size[0]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    color = [255, 255, 255]
    return cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)


def smart_resize(img, size):
    # Assumes the image has already gone through make_square
    if img.shape[0] > size:
        img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
    elif img.shape[0] < size:
        img = cv2.resize(img, (size, size), interpolation=cv2.INTER_CUBIC)
    else:  # just do nothing
        pass

    return img


class WaifuDiffusionInterrogator:
    def __init__(
            self,
            repo='SmilingWolf/wd-v1-4-vit-tagger',
            model_path='model.onnx',
            tags_path='selected_tags.csv',
            mode: str = "auto"
    ) -> None:
        self.__repo = repo
        self.__model_path = model_path
        self.__tags_path = tags_path
        self._provider_mode = mode

        self.__initialized = False
        self._model, self._tags = None, None

    def _init(self) -> None:
        if self.__initialized:
            return

        model_path = Path(hf_hub_download(self.__repo, filename=self.__model_path))
        tags_path = Path(hf_hub_download(self.__repo, filename=self.__tags_path))

        _try_init_onnxruntime()
        from onnxruntime import InferenceSession, get_available_providers
        providers = {
            "cpu": "CPUExecutionProvider",
            "gpu": "CUDAExecutionProvider",
            "tensorrt": "TensorrtExecutionProvider",
            "auto": "CUDAExecutionProvider" if "CUDAExecutionProvider" in get_available_providers()
            else "CPUExecutionProvider",
        }
        self._model = InferenceSession(str(model_path), providers=[providers[self._provider_mode]])
        self._tags = pd.read_csv(tags_path)

        self.__initialized = True

    def _calculation(self, image: Image.Image) -> pd.DataFrame:
        self._init()

        # code for converting the image and running the model is taken from the link below
        # thanks, SmilingWolf!
        # https://huggingface.co/spaces/SmilingWolf/wd-v1-4-tags/blob/main/app.py

        # convert an image to fit the model
        _, height, _, _ = self._model.get_inputs()[0].shape

        # alpha to white
        image = image.convert('RGBA')
        new_image = Image.new('RGBA', image.size, 'WHITE')
        new_image.paste(image, mask=image)
        image = new_image.convert('RGB')
        image = np.asarray(image)

        # PIL RGB to OpenCV BGR
        image = image[:, :, ::-1]

        image = make_square(image, height)
        image = smart_resize(image, height)
        image = image.astype(np.float32)
        image = np.expand_dims(image, 0)

        # evaluate model
        input_name = self._model.get_inputs()[0].name
        label_name = self._model.get_outputs()[0].name
        confidence = self._model.run([label_name], {input_name: image})[0]

        full_tags = self._tags[['name', 'category']].copy()
        full_tags['confidence'] = confidence[0]

        return full_tags

    def feature_frame(self, image: Image) -> pd.DataFrame:
        full_tags = self._calculation(image)
        return full_tags[full_tags['category'] != 9][['name', 'confidence']]

    def interrogate(self, image: Image) -> Tuple[Dict[str, float], Dict[str, float]]:
        full_tags = self._calculation(image)

        # first 4 items are for rating (general, sensitive, questionable, explicit)
        ratings = dict(full_tags[full_tags['category'] == 9][['name', 'confidence']].values)

        # rest are regular tags
        tags = dict(full_tags[full_tags['category'] != 9][['name', 'confidence']].values)

        return ratings, tags


WAIFU_MODELS: Mapping[str, WaifuDiffusionInterrogator] = {
    'wd14-vit': WaifuDiffusionInterrogator(),
    'wd14-convnext': WaifuDiffusionInterrogator(
        repo='SmilingWolf/wd-v1-4-convnext-tagger'
    ),
}


def _get_wd14_tags_result(image: Image.Image, model: str = 'wd14-vit'):
    return WAIFU_MODELS[model].interrogate(image)


def get_wd14_safety(image: Image.Image, model: str = 'wd14-vit') -> Dict[str, float]:
    ratings, _ = _get_wd14_tags_result(image, model)
    return ratings


def get_wd14_tags(image: Image.Image, model: str = 'wd14-vit', threshold: float = 0.7):
    _, tags = _get_wd14_tags_result(image, model)
    return {
        key: value
        for key, value in sorted(tags.items(), key=lambda x: (-x[1], x[0]))
        if value >= threshold
    }


def get_wd14_features(image: Image.Image, model: str = 'wd14-vit') -> pd.DataFrame:
    return WAIFU_MODELS[model].feature_frame(image)
