from waifuc.source import BaseDataSource, GelbooruSource

from ..base.character import TagFeatureExtract
from ..base.tag_matches import TagMatcher


class GelbooruTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return GelbooruSource([self.tag])


class GelbooruTagMatcher(TagMatcher):
    __site_name__ = 'gelbooru.com'
    __tag_fe__ = GelbooruSource
