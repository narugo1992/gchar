import os.path
from typing import Iterator, Tuple, Optional, List

from PIL import Image

from ...utils import grab_objects_from_image, image_padding, import_tqdm, get_deepbooru_tags

tqdm = import_tqdm()


class CrawlerSession:
    def iter_images(self, keywords, count: int = 100, **kwargs) \
            -> Iterator[Tuple[int, Tuple[int, int], str, Image.Image]]:
        raise NotImplementedError

    def iter_elements(self, keywords, count: int = 100,
                      elements: Optional[List[str]] = None, max_elements_per_image: int = 4,
                      threshold: float = 0.1, zoom: float = 1.25, max_cov: float = 0.6,
                      padding_background: Optional[str] = None, padding_size: Tuple[int, int] = (512, 704),
                      dp_tags: Optional[List[str]] = None, dp_ratio: float = 0.7,
                      dn_tags: Optional[List[str]] = None, dn_ratio: float = 0.25,
                      **kwargs) -> Iterator[Tuple[int, Tuple[int, int], Tuple[str, float], str, Image.Image]]:
        dp_tags = list(dp_tags or [])
        dn_tags = list(dn_tags or [])

        total_count = 0
        result_tqdm = tqdm(total=count if count > 0 else None, leave=True)
        for id_, (views, marks), filename, img in self.iter_images(keywords, count=-1, **kwargs):
            fbody, fext = os.path.splitext(filename)
            ccnt = 0
            for i, (type_, score, img_) in enumerate(grab_objects_from_image(img, threshold, elements, zoom, max_cov)):
                fname = f'{fbody}_{i}_{type_}{int(score * 100):02d}{fext}'
                img_ = image_padding(img_, padding_size[0], padding_size[1], padding_background)

                detected_tags = get_deepbooru_tags(img_, threshold=min(dn_ratio, dp_ratio))
                _need_skip = False
                for tag in dp_tags:
                    if detected_tags.get(tag, 0.0) < dp_ratio:
                        _need_skip = True
                        break

                for tag in dn_tags:
                    if detected_tags.get(tag, 0.0) >= dn_ratio:
                        _need_skip = True
                        break
                if _need_skip:
                    continue

                total_count += 1
                result_tqdm.set_description(f'{total_count} element(s) detected')
                result_tqdm.update()
                yield id_, (views, marks), (type_, score), fname, img_

                ccnt += 1
                if 0 <= max_elements_per_image <= ccnt:
                    break

                if 0 <= count <= total_count:
                    return
