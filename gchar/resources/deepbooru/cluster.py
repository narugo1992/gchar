from functools import lru_cache
from typing import List, Union, Tuple

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from ...utils import get_deepbooru_features, import_tqdm
from ...utils.deepbooru import get_all_tags
from ...utils.resource import get_resource_file

tqdm = import_tqdm()

_KEY_ROOTS = [
    'bangs',
    'beard',
    'braid',
    'braids',
    'cheeks',
    'ear',
    'ears',
    'eye',
    'eyebrows',
    'eyelashes',
    'eyes',
    'forehead',
    'hair',
    'hairband',
    'hairclip',
    'hairstyle',
    'headband',
    'horn',
    'horns',
    'lace',
    'lips',
    'necktie',
    'nose',
    'ponytail',
    'ribbon',
    'skin',
    'tassel',
    'updo',
    'wig',
]


@lru_cache()
def _get_general_analysis() -> pd.DataFrame:
    return pd.read_csv(get_resource_file('./deepbooru/tags-general-analysis.csv'))


@lru_cache()
def _get_key_character_tags():
    df = _get_general_analysis()
    _keys = set(_KEY_ROOTS)
    filtered_rows = df[(df['root'].isin(_keys)) & (df['pos'].isin({'NOUN', 'PROPN'}))]
    return list(filtered_rows['tag'])


def recommend_pca_dims(df, n_features: int, thresholds: Tuple[float, ...]) -> Tuple[int, ...]:
    standardize = StandardScaler()
    standardize.fit(df)
    std_data = standardize.transform(df)

    pca_all = PCA(n_features)
    pca_all.fit(std_data)
    evr = np.cumsum(pca_all.explained_variance_ratio_)
    return tuple(np.searchsorted(evr, t) + 1 for t in thresholds)


def _get_tags_ids(tags: List[str]) -> Tuple[int, ...]:
    tag_set = set(tags)
    retval = []
    for i, tag in enumerate(get_all_tags()):
        if tag in tag_set:
            retval.append(i)

    return tuple(retval)


@lru_cache()
def _get_key_character_ids() -> Tuple[int, ...]:
    return _get_tags_ids(_get_key_character_tags())


_FEATURE_NAME = '__feature__'


def cluster_images(images: List[Union[str, Image.Image]], pca_min_ratio: float = 0.9,
                   dbscan_divs: float = 4, dbscan_min_samples: int = 6,
                   min_conf: float = 0.3, max_conf: float = 1.0, ch_tags_only: bool = True):
    images_progress = tqdm(images)
    feats = []
    for i, image in enumerate(images_progress):
        images_progress.set_description(f'Featuring image {i}/{len(images)} ...')
        if hasattr(image, _FEATURE_NAME):
            f = getattr(image, _FEATURE_NAME)
        else:
            f = get_deepbooru_features(image)
            setattr(image, _FEATURE_NAME, f)
        feats.append(f)

    batch = np.stack(feats)
    if ch_tags_only:
        batch = batch[:, _get_key_character_ids()]

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
