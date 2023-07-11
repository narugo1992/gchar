from typing import List

import pytest

from gchar.games.arknights import Character as ArknightsCharacter
from gchar.resources.sites import get_site_tag, list_available_sites


@pytest.fixture(scope='module')
def ark_surtr():
    return ArknightsCharacter.get('surtr')


@pytest.fixture()
def supported_sites() -> List[str]:
    return [
        'anime_pictures',
        'atfbooru',
        'sankaku',
        'danbooru',
        'hypnohub',
        'konachan',
        'konachan_net',
        'lolibooru',
        'rule34',
        'safebooru',
        'xbooru',
        'yande',
        'zerochan',
    ]


@pytest.mark.unittest
class TestResourcesSitesTags:
    @pytest.mark.parametrize(['ch', 'site', 'tag'], [
        ('surtr', 'danbooru', 'surtr_(arknights)'),
        (ArknightsCharacter.get('surtr'), 'danbooru', 'surtr_(arknights)'),
        ('surtr', 'danbooruxxx', ValueError),
    ])
    def test_get_site_tag(self, ch, site, tag):
        if isinstance(tag, type) and issubclass(tag, Exception):
            with pytest.raises(tag):
                _ = get_site_tag(ch, sure_only=True, site=site)
        else:
            assert get_site_tag(ch, sure_only=True, site=site) == tag

    @pytest.mark.parametrize(['ch', 'site', 'tag', 'min_count'], [
        ('surtr', 'danbooru', 'surtr_(arknights)', 2500),
        (ArknightsCharacter.get('surtr'), 'danbooru', 'surtr_(arknights)', 2500),
    ])
    def test_get_site_tag_with_count(self, ch, site, tag, min_count):
        actual_tag, posts = get_site_tag(ch, sure_only=True, site=site, with_posts=True)
        assert actual_tag == tag
        assert posts >= min_count

    def test_list_available_sites(self, supported_sites):
        sp_sites = list_available_sites()
        for site in supported_sites:
            assert site in sp_sites, \
                f'Site {site!r} should be supported but not found in supported sites - {sp_sites!r}.'
