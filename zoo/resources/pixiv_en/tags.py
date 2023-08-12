from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, List, Mapping, Any
from urllib.parse import urljoin

from pyquery import PyQuery as pq

from gchar.utils import srequest
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

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        json_data = PixivTagCrawler.get_tags_json(self)
        retval = []

        def _get_info(idx, item):
            wiki_url = item['wiki_url']
            resp = srequest(self.session, 'GET', wiki_url)
            page = pq(resp.text)
            for trans_item in page('#article-relation .interlang li'):
                lang = trans_item('a').attr('lang')
                item[f'trans_{lang}'] = trans_item('a').attr('gtm-id')
                item[f'trans_{lang}_wiki_url'] = urljoin(wiki_url, trans_item('a').attr('href'))

            retval.append((idx, item))

        tp = ThreadPoolExecutor(max_workers=self.__max_workers__)
        for i, item in enumerate(json_data):
            tp.submit(_get_info, i, item)
        tp.shutdown()

        retval = sorted(retval)
        retval = [item for _, item in retval]
        return retval
