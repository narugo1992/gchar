from waifuc.source import BaseDataSource, AnimePicturesSource

from ..base.character import TagFeatureExtract
from ..base.tag_matches import TagMatcher


class AnimePicturesTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return AnimePicturesSource([self.tag, 'solo'])


class AnimePicturesTagMatcher(TagMatcher):
    __site_name__ = 'anime-pictures.net'
    __tag_column__ = 'tag'
    __count_column__ = 'num_pub'
    __extra_filters__ = {'type': 1}
    __tag_fe__ = AnimePicturesTagFeatureExtract
