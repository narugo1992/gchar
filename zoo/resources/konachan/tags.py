from typing import List, Mapping, Any, Optional

from gchar.utils import srequest, get_requests_session
from ..base.tags import TagCrawler, ParallelTagCrawler


class KonachanDirectTagCrawler(TagCrawler):
    def __init__(self, site_url: str):
        TagCrawler.__init__(self, site_url, get_requests_session(timeout=60))

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        resp = srequest(self.session, 'GET', f'{self.site_url}/tag.json', params={
            'limit': '0',
        })
        resp.raise_for_status()
        return sorted(resp.json(), key=lambda x: x['id'])

    __sqlite_indices__ = ['id', 'name', 'type', 'count', 'ambiguous']


class KonachanTagCrawler(ParallelTagCrawler):
    __init_page__ = 1
    __id_key__ = 'id'
    __max_workers__ = 8

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        resp = srequest(self.session, 'GET', f'{self.site_url}/tag.json', params={
            'limit': '100',
            'page': str(p),
        })
        resp.raise_for_status()
        return resp.json()

    __sqlite_indices__ = ['id', 'name', 'type', 'count', 'ambiguous']
