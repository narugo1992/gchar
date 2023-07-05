from waifuc.source import BaseDataSource, DanbooruSource

from ..base.character import TagFeatureExtract
from ..base.tag_matches import TagMatcher


class DanbooruTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return DanbooruSource([self.tag, 'solo'])


class DanbooruTagMatcher(TagMatcher):
    __site_name__ = 'danbooru.donmai.us'
    __tag_column__ = 'name'
    __count_column__ = 'post_count'
    __extra_filters__ = {'category': 4}
    __tag_fe__ = DanbooruTagFeatureExtract
