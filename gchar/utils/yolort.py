import os
import tempfile
from contextlib import contextmanager
from functools import lru_cache
from typing import List, Union, ContextManager, Optional, Dict, Iterator, Tuple

import cv2
import matplotlib
import numpy as np
import torch
from PIL import Image

from .resource import get_resource_file

_YOLO_MODEL = None
_SCORE_THRESHOLD = 0.01


@contextmanager
def _keep_matplotlib_backend():
    backend = matplotlib.get_backend()
    try:
        yield
    finally:
        matplotlib.use(backend, force=True)


def _get_yolo_model():
    global _YOLO_MODEL
    if _YOLO_MODEL is None:
        with _keep_matplotlib_backend():
            from yolort.models import YOLOv5
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

        with _keep_matplotlib_backend():
            from yolort.utils import Visualizer
            v = Visualizer(image, metalabels=_LABEL_PATH)
            v.draw_instance_predictions(pred)
            v.imshow(scale=scale)


def _rect_area(a: Tuple[float, float, float, float]) -> float:
    ax0, ay0, ax1, ay1 = a
    return abs(ax1 - ax0) * abs(ay1 - ay0)


def _rect_overlap(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float]) -> float:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b

    x0, y0 = max(ax0, bx0), max(ay0, by0)
    x1, y1 = min(ax1, bx1), min(ay1, by1)
    width, height = x1 - x0, y1 - y0
    if width >= 0.0 and height >= 0.0:
        return width * height
    else:
        return 0.0


def grab_objects_from_image(image: Union[Image.Image, str], threshold: float = 0.1,
                            concerned_names: Optional[List[str]] = None, zoom: float = 1.1,
                            max_cov: bool = 0.6) \
        -> Iterator[Tuple[str, float, Image.Image]]:
    pred = detect_object_in_image(image, threshold, concerned_names)
    with _ensure_png_image(image) as image_filename:
        img = Image.open(image_filename)
        width, height = img.size

        for i, (score, label, (x0, y0, x1, y1)) in enumerate(zip(pred['scores'], pred['labels'], pred['boxes'])):
            score, label = map(torch.Tensor.tolist, (score, label))
            x0, y0, x1, y1 = map(torch.Tensor.tolist, (x0, y0, x1, y1))

            _area = _rect_area((x0, y0, x1, y1))
            _covered = False
            for j in range(i):
                xx0, yy0, xx1, yy1 = map(torch.Tensor.tolist, pred['boxes'][j])
                if _rect_overlap((xx0, yy0, xx1, yy1), (x0, y0, x1, y1)) > max_cov * _area:
                    _covered = True
                    break

            if _covered:
                continue

            xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
            hx, hy = xm - x0, ym - y0
            xx0, xx1 = max(xm - hx * zoom, 0.0), min(xm + hx * zoom, width)
            yy0, yy1 = max(ym - hy * zoom, 0.0), min(ym + hy * zoom, height)
            yield _get_names()[label], score, img.crop((xx0, yy0, xx1, yy1))
