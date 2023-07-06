from typing import Tuple

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

    def _alias_replace(self, tag, count) -> Tuple[str, int]:
        while True:
            c_rows = list(self.db.table('tags').select('*').where(self.__tag_column__, '=', tag).get())
            if not c_rows:
                break

            alias_id = c_rows[0]['alias']
            if alias_id is None:
                break
            a_rows = list(self.db.table('tags').select('*').where('id', '=', alias_id).get())
            if not a_rows:
                break

            tag, count = a_rows[0][self.__tag_column__], a_rows[0][self.__count_column__]

        return tag, count
