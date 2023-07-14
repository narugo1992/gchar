from typing import Tuple, Iterator

from waifuc.source import BaseDataSource, WallHavenSource

from ..base.character import TagFeatureExtract
from ..base.tag_matches import TagMatcher


class WallHavenFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return WallHavenSource(self.tag, no_ai=False, select='thumbnail')


class WallHavenTagMatcher(TagMatcher):
    __site_name__ = 'wallhaven.cc'
    __tag_column__ = 'name'
    __count_column__ = 'posts'
    __extra_filters__ = {'category_id': [20, 49]}
    __tag_fe__ = WallHavenFeatureExtract

    def _alias_replace(self, tag, count) -> Tuple[str, int]:
        return tag, count

    def _yield_mapped_tags(self, tag) -> Iterator[Tuple[str, dict]]:
        lst = list(self.db.table('tags').where(self.__tag_column__, '=', tag).get())
        yield f"id:{lst[0]['id']}", {'name': tag}
