from typing import List, Union, Tuple

import numpy as np
from PIL import Image
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from ...utils import get_deepbooru_features, import_tqdm

tqdm = import_tqdm()


def recommend_pca_dims(df, n_features: int, thresholds: Tuple[float, ...]) -> Tuple[int, ...]:
    standardize = StandardScaler()
    standardize.fit(df)
    std_data = standardize.transform(df)

    pca_all = PCA(n_features)
    pca_all.fit(std_data)
    evr = np.cumsum(pca_all.explained_variance_ratio_)
    return tuple(np.searchsorted(evr, t) + 1 for t in thresholds)


def cluster_images(images: List[Union[str, Image.Image]], pca_min_ratio: float = 0.9,
                   dbscan_divs: float = 4, dbscan_min_samples: int = 6,
                   min_conf: float = 0.3, max_conf: float = 1.0):
    images_progress = tqdm(images)
    feats = []
    for i, image in enumerate(images_progress):
        images_progress.set_description(f'Featuring image {i}/{len(images)} ...')
        feats.append(get_deepbooru_features(image))

    batch = np.stack(feats)
    pbatch = batch.copy()
    pbatch = np.clip(pbatch, min_conf, max_conf)

    std1 = StandardScaler()
    std1.fit(pbatch)
    std_data = std1.transform(pbatch)

    best_dims, = recommend_pca_dims(std_data, np.min(std_data.shape), (pca_min_ratio,))
    pca = PCA(n_components=best_dims)
    pca.fit(std_data)
    pca_data = pca.transform(std_data)

    std2 = StandardScaler()
    std2.fit(pca_data)
    processed_data = std2.transform(pca_data)

    algo = DBSCAN(eps=best_dims / dbscan_divs, min_samples=dbscan_min_samples)
    algo.fit(std_data)
    pred = algo.fit_predict(processed_data)

    n_clusters = np.max(pred) + 1
    clusters: List[List[Union[str, Image.Image]]] = [[] for _ in range(n_clusters)]
    noises = []
    for i, cid in enumerate(pred):
        if cid >= 0:
            clusters[cid].append(images[i])
        else:
            noises.append(images[i])

    return clusters, noises
