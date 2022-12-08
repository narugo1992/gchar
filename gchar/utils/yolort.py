import os
import tempfile
from contextlib import contextmanager
from functools import lru_cache
from typing import List, Union, ContextManager, Optional, Dict

import cv2
import numpy as np
from PIL import Image
from yolort.models import YOLOv5
from yolort.utils import Visualizer

from .resource import get_resource_file

_YOLO_MODEL = None
_SCORE_THRESHOLD = 0.01


def _get_yolo_model() -> YOLOv5:
    global _YOLO_MODEL
    if _YOLO_MODEL is None:
        _YOLO_MODEL = YOLOv5.load_from_yolov5(
            get_resource_file('./yolort/yolov5s.pt'),
            score_thresh=_SCORE_THRESHOLD,
        )
        _YOLO_MODEL.eval()

    return _YOLO_MODEL


_LABEL_PATH = get_resource_file('./yolort/coco.names')


@lru_cache()
def _get_names() -> List[str]:
    with open(_LABEL_PATH, 'r') as f:
        names = []
        for line in f:
            line = line.strip()
            if line:
                names.append(line)

        return names


@lru_cache()
def _get_name_to_id_map() -> Dict[str, int]:
    return {name: i for i, name in enumerate(_get_names())}


def _name_to_id(name: Union[int, str]) -> int:
    if isinstance(name, int):
        return name
    else:
        _map = _get_name_to_id_map()
        if name in _map:
            return _map[name]
        else:
            raise ValueError(f'Unknown name for yolort - {name!r}.')


@contextmanager
def _ensure_png_image(image: Union[Image.Image, str]) -> ContextManager[str]:
    if isinstance(image, str):
        image = Image.open(image)
    elif isinstance(image, Image.Image):
        image = image
    else:
        raise TypeError(f'Unknown image type - {image!r}.')

    with tempfile.TemporaryDirectory() as td:
        image = image.convert('RGB')
        image_filename = os.path.join(td, 'img.png')
        image.save(image_filename, format='png')

        yield image_filename


def detect_object_in_image(image: Union[Image.Image, str], threshold: float = 0.1,
                           concerned_names: Optional[List[str]] = None):
    concerned_names = list(concerned_names or _get_names())
    concerned_ids = {_name_to_id(name) for name in concerned_names}

    model = _get_yolo_model()
    with _ensure_png_image(image) as image_filename:
        predictions = model.predict(image_filename)
        pred = predictions[0]

        linenos = []
        for i, (score, label, box) in enumerate(zip(pred['scores'], pred['labels'], pred['boxes'])):
            label = label.tolist()
            if label in concerned_ids and score >= threshold:
                linenos.append(i)

        linenos = tuple(linenos)
        return {key: value[linenos,] for key, value in pred.items()}


def visual_detection_result(image: Union[Image.Image, str], pred: Dict, scale: float = 1.0):
    with _ensure_png_image(image) as image_filename:
        with open(image_filename, 'rb') as rf:
            flags = 1
            bytes_as_np_array = np.frombuffer(rf.read(), dtype=np.uint8)
            image = cv2.imdecode(bytes_as_np_array, flags)

        v = Visualizer(image, metalabels=_LABEL_PATH)
        v.draw_instance_predictions(pred)
        v.imshow(scale=scale)
