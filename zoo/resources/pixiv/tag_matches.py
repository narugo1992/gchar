from typing import Tuple

from waifuc.source import BaseDataSource, PixivSearchSource

from ..base.character import TagFeatureExtract
from ..base.tag_matches import TagMatcher


class PixivFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        from .session import get_pixiv_refresh_token
        return PixivSearchSource(self.tag, refresh_token=get_pixiv_refresh_token())


class PixivTagMatcher(TagMatcher):
    __site_name__ = 'pixiv.net'
    __tag_column__ = 'name'
    __count_column__ = 'posts'
    __extra_filters__ = {'is_character': 1}
    __tag_fe__ = PixivFeatureExtract

    def _alias_replace(self, tag, count) -> Tuple[str, int]:
        return tag, count
