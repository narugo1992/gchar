from ..base.tag_matches import TagMatcher


class SankakuTagMatcher(TagMatcher):
    __site_name__ = 'chan.sankakucomplex.com'
    __tag_column__ = 'name'
    __count_column__ = 'post_count'
    __extra_filters__ = {'type': 4}
