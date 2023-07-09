from typing import Tuple, List, Iterator

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
        _exist_tags = {tag}
        while True:
            query = self.db.table('tag_aliases').select('*').where('alias', '=', tag)
            lst = list(query.get())
            if not lst:
                break
            else:
                new_tag = lst[0][self.__tag_column__]
                if new_tag in _exist_tags:
                    break

                _exist_tags.add(new_tag)
                tag = new_tag

        tlst = list(self.db.table('tags').select('*').where(self.__tag_column__, '=', tag).get())
        if tlst:
            tag, count = tlst[0][self.__tag_column__], tlst[0][self.__count_column__]

        return tag, count

    def _query_alias_via_pattern(self, pattern, *patterns):
        query = self.db.table('tag_aliases').select('*')
        or_clause = self.db.query()
        for i, p in enumerate([pattern, *patterns]):
            or_clause = or_clause.or_where(
                self.db.raw(f'LOWER(alias)')
                if self.__case_insensitive__ else 'alias',
                'like', p.lower() if self.__case_insensitive__ else p,
            )

        query = query.where(or_clause)
        return query

    def _yield_name_count(self, names: List[str]) -> Iterator[Tuple[str, int]]:
        name_words_sets = [self._split_name_to_words(name) for name in names]
        exist_tags = set()
        for patterns in self._batch_iter_patterns(name_words_sets):
            for row in self._query_via_pattern(*patterns).get():
                tag = row[self.__tag_column__]
                count = row[self.__count_column__]
                if tag in exist_tags:
                    continue

                origin_tag = tag
                tag, count = self._alias_replace(tag, count)
                if tag in exist_tags:
                    continue

                tag_words = self._split_tag_to_words(origin_tag)
                tag_words_n = self._split_name_to_words(origin_tag)
                filter_sim = max([
                    *(self._words_filter(name_words, tag_words) for name_words in name_words_sets),
                    *(self._words_filter(name_words, tag_words_n) for name_words in name_words_sets),
                ])
                if filter_sim < self.__min_similarity__:
                    continue

                exist_tags.add(tag)
                exist_tags.add(origin_tag)
                yield tag, count

            # find in alias table
            for row in self._query_alias_via_pattern(*patterns).get():
                tag = row['alias']
                count = None
                if tag in exist_tags:
                    continue

                origin_tag = tag
                tag, count = self._alias_replace(tag, count)
                if tag in exist_tags or count is None:
                    continue

                tag_words = self._split_tag_to_words(origin_tag)
                tag_words_n = self._split_name_to_words(origin_tag)
                filter_sim = max([
                    *(self._words_filter(name_words, tag_words) for name_words in name_words_sets),
                    *(self._words_filter(name_words, tag_words_n) for name_words in name_words_sets),
                ])
                if filter_sim < self.__min_similarity__:
                    continue

                exist_tags.add(tag)
                exist_tags.add(origin_tag)
                yield tag, count
