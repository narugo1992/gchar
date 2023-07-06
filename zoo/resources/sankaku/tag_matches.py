from typing import Tuple

from waifuc.source import BaseDataSource, SankakuSource

from ..base.character import TagFeatureExtract
from ..base.tag_matches import TagMatcher


class SankakuTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return SankakuSource([self.tag])


class SankakuTagMatcher(TagMatcher):
    __site_name__ = 'chan.sankakucomplex.com'
    __tag_column__ = 'name'
    __count_column__ = 'post_count'
    __extra_filters__ = {'type': 4}
    __tag_fe__ = None

    def _alias_replace(self, tag, count) -> Tuple[str, int]:
        return tag, count
