from typing import Tuple

from ..pixiv.tags import PixivTagCrawler


class PixivEnTagCrawler(PixivTagCrawler):
    __site_url__ = 'https://dic.pixiv.net/en'
    __site_name__ = 'en.pixiv.net'

    CATEGORY_NAME_MAP = {
        'Anime': 'anime', 'Manga': 'manga', 'Novel': 'novel', 'Game': 'game', 'Figure': 'figure',
        'Music': 'music', 'Art': 'art', 'Design': 'design', 'General': 'general', 'Person': 'person',
        'Character': 'character', 'Quote': 'quote', 'Event': 'event', 'Doujin': 'doujin'
    }

    __mark_tags__: Tuple[str, str, str, str] = ('Updated', 'View count', 'Submitted works', 'Checklist')
