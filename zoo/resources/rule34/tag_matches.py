from waifuc.source import BaseDataSource, Rule34Source

from ..base.character import TagFeatureExtract
from ..base.tag_matches import TagMatcher


class Rule34TagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return Rule34Source([self.tag])


class Rule34TagMatcher(TagMatcher):
    __site_name__ = 'rule34.xxx'
    __tag_fe__ = Rule34TagFeatureExtract
