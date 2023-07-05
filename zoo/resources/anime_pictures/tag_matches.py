from ..base.tag_matches import TagMatcher


class AnimePicturesTagMatcher(TagMatcher):
    __site_name__ = 'anime-pictures.net'
    __tag_column__ = 'tag'
    __count_column__ = 'num_pub'
    __extra_filters__ = {'type': 1}
