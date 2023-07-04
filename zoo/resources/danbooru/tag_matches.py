from ..base.tag_matches import TagMatcher


class DanbooruTagMatcher(TagMatcher):
    __site_name__ = 'danbooru.donmai.us'
    __tag_column__ = 'name'
    __count_column__ = 'post_count'
    __extra_filters__ = {'category': 4}
