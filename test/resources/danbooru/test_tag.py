import pytest
from hbutils.testing import disable_output

from gchar.resources.danbooru.tags import get_danbooru_tag


@pytest.mark.unittest
class TestResourcesDanbooruTag:
    @pytest.mark.parametrize(['ch', 'tag'], [
        ('CEO', 'penthesilea_(fate)'),
        ('CBA', 'scathach_skadi_(fate)'),
        ('amiya', 'amiya_(arknights)'),
        ('林雨霞', 'lin_(arknights)'),
        ('战车', None),
        ('saber', 'artoria_pendragon_(fate)'),
        ('character_not_exist_wtf', ValueError),
    ])
    def test_get_danbooru_tag(self, ch, tag):
        if isinstance(tag, type) and issubclass(tag, Exception):
            with pytest.raises(tag):
                _ = get_danbooru_tag(ch)
        else:
            assert get_danbooru_tag(ch) == tag

    @pytest.mark.parametrize(['ch', 'tag'], [
        ('CEO', 'penthesilea_(fate)'),
        ('CBA', 'scathach_skadi_(fate)'),
        ('战车', None),
        ('saber', 'artoria_pendragon_(fate)'),
        ('character_not_exist_wtf', ValueError),
    ])
    def test_get_danbooru_tag_without_local(self, ch, tag, no_tags_json):
        with disable_output():
            if isinstance(tag, type) and issubclass(tag, Exception):
                with pytest.raises(tag):
                    _ = get_danbooru_tag(ch)
            else:
                assert get_danbooru_tag(ch) == tag
