from typing import Optional, List, Mapping, Any

from hbutils.system import urlsplit
from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from gchar.utils import srequest
from ..base.tags import ParallelTagCrawler


class WallHeavenTagCrawler(ParallelTagCrawler):
    __max_workers__ = 12
    __id_key__ = 'id'
    __init_page__ = 1

    __site_url__ = 'https://wallhaven.cc'

    def __init__(self):
        ParallelTagCrawler.__init__(self)

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        resp = srequest(self.session, 'GET', f'{self.__site_url__}/tags', params={'page': str(p)})
        taglist = pq(resp.text)('#taglist')
        tagmains = list(taglist('.taglist-tagmain').items())
        stats = list(taglist('.taglist-stats').items())
        assert len(tagmains) == len(
            stats), f'Tag mains ({len(tagmains)}) not match with stats ({len(stats)}) on page {p}.'

        data = []
        for tagmain, stat in zip(tagmains, stats):
            tag_name = tagmain('.taglist-name a').text().strip()
            tag_id = int(urlsplit(tagmain('.taglist-name a').attr('href')).path_segments[-1])

            *_, category_atag = tagmain('.taglist-category a').items()
            category_name = category_atag.text().strip()
            category_id = int(urlsplit(category_atag.attr('href')).path_segments[-1])

            posts = int(stat('.taglist-wallcount').text().strip().replace(',', ''))
            views = int(stat('.taglist-viewcount').text().strip().replace(',', ''))
            subscriptions = int(stat('.taglist-subcount').text().strip().replace(',', ''))

            data.append({
                'name': tag_name,
                'id': tag_id,
                'category_name': category_name,
                'category_id': category_id,
                'posts': posts,
                'views': views,
                'subscriptions': subscriptions,
            })

        return data

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        data, exist_ids = [], set()
        pg_pages = tqdm(desc='Total pages')
        pg_tags = tqdm(desc='Total tags')
        return self._load_data_with_pages(
            self.get_tags_from_page,
            lambda x: x[self.__id_key__],
            data, exist_ids, pg_pages, pg_tags,
        )

    __sqlite_indices__ = ['name', 'id', 'category_name', 'category_id', 'posts', 'views', 'subscriptions']
