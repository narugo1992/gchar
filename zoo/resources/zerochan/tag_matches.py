from typing import Tuple

from waifuc.source import BaseDataSource, ZerochanSource

from ..base.character import TagFeatureExtract
from ..base.tag_matches import TagMatcher


class ZerochanTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return ZerochanSource(self.tag, strict=True)


class ZerochanTagMatcher(TagMatcher):
    __site_name__ = 'zerochan.net'
    __tag_column__ = 'tag'
    __count_column__ = 'total'
    __case_insensitive__ = True
    __extra_filters__ = {'type': 'character'}
    __tag_fe__ = ZerochanTagFeatureExtract

    def _alias_replace(self, tag, count) -> Tuple[str, int]:
        return tag, count
