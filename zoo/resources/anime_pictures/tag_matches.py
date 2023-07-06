from typing import Tuple

import numpy as np
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
        _known_names = {tag}
        _known_tuples = [(tag, count)]
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

            new_tag, new_count = a_rows[0][self.__tag_column__], a_rows[0][self.__count_column__]
            if new_tag in _known_names:
                cnts = np.array([c for _, c in _known_tuples])
                tag, count = _known_tuples[np.argmax(cnts)]
                break
            else:
                tag, count = new_tag, new_count

        return tag, count
