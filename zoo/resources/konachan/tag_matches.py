from waifuc.source import BaseDataSource, KonachanSource

from ..base.character import TagFeatureExtract
from ..base.tag_matches import TagMatcher


class KonachanTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return KonachanSource([self.tag])


class KonachanTagMatcher(TagMatcher):
    __site_name__ = 'konachan.com'
    __tag_fe__ = KonachanTagFeatureExtract
