from typing import List, Union

import numpy as np
from PIL import Image
from ...utils import get_deepbooru_features

def get_features(images: List[Union[str, Image.Image]]) -> List[np.ndarray]:
    get_deepbooru_features()
    pass


def cluster_images(images: List[Union[str, Image.Image]]):
    pass
