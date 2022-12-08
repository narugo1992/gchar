from typing import Dict

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


def get_main_colors(image: Image.Image, n: int = 7) -> Dict[str, float]:
    image = image.copy().convert('RGB')
    rt = (image.size[0] * image.size[1] / 90000) ** 0.5
    if rt > 1.0:
        image = image.resize((int(image.size[0] / rt), int(image.size[1] / rt)))

    raw = np.asarray(image).reshape(-1, 3)
    kmeans = KMeans(n_clusters=n)
    kmeans.fit(raw)

    labels = kmeans.labels_
    analysis = [0 for _ in range(n)]
    for label in list(labels):
        analysis[label] += 1
    percents = [v / (image.size[0] * image.size[1]) for v in analysis]
    centroids = kmeans.cluster_centers_

    retval = []
    for (r, g, b), percent in zip(centroids.tolist(), percents):
        r, g, b = map(int, map(round, (r, g, b)))
        color = f'#{r:02x}{g:02x}{b:02x}'
        retval.append((percent, color))

    return {c: p for p, c in sorted(retval, key=lambda x: (-x[0], *x[1:]))}


def image_padding(image: Image.Image, width: int, height: int, background: str = None) -> Image.Image:
    ratio = max(image.width / width, image.height / height)
    w, h = map(int, (image.width / ratio, image.height / ratio))
    image = image.resize((w, h), Image.ANTIALIAS)

    if not background:
        background, *_ = get_main_colors(image).keys()
    result = Image.new('RGB', (width, height), background)
    result.paste(image, (int((width - w) / 2), int((height - h) / 2)))
    return result
