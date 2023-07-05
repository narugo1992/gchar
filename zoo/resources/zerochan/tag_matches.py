from ..base.tag_matches import TagMatcher


class ZerochanTagMatcher(TagMatcher):
    __site_name__ = 'zerochan.net'
    __tag_column__ = 'tag'
    __count_column__ = 'total'
    __extra_filters__ = {'type': 'character'}
