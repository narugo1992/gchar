from typing import List, Mapping, Any, Optional, Tuple

from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from gchar.utils import srequest, get_requests_session
from ..base.tags import TagCrawler, ParallelTagCrawler


class _BaseKonachanTagCrawler(ParallelTagCrawler):
    __init_page__ = 1
    __id_key__ = 'id'
    __max_workers__ = 8

    def __init__(self, site_url: str):
        TagCrawler.__init__(self, site_url, get_requests_session(timeout=60))

    def _get_tag_aliases_from_page(self, p):
        resp = srequest(self.session, 'GET', f'{self.site_url}/tag_alias', params={'page': str(p)})
        resp.raise_for_status()

        page = pq(resp.text)
        table = page('#aliases table')
        headers = [item.text().strip().lower() for item in table('thead th').items()]

        data = []
        for row in table('tbody tr').items():
            texts = [item.text().strip() for item in row('td').items()]
            v = dict(zip(headers, texts))
            data.append((v['alias'], v['to']))

        return data

    def get_tag_aliases_json(self) -> List[Tuple[str, str]]:
        data, exist_ids = [], set()
        pg_tags = tqdm(desc=f'Tag Aliases')
        pg_pages = tqdm(desc=f'Pages')
        return self._load_data_with_pages(
            self._get_tag_aliases_from_page,
            lambda x: x[0],
            data, exist_ids, pg_pages, pg_tags,
        )

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        resp = srequest(self.session, 'GET', f'{self.site_url}/tag.json', params={
            'limit': '100',
            'page': str(p),
        })
        resp.raise_for_status()
        return resp.json()

    __sqlite_indices__ = ['id', 'name', 'type', 'count', 'ambiguous']


class KonachanDirectTagCrawler(_BaseKonachanTagCrawler):

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        resp = srequest(self.session, 'GET', f'{self.site_url}/tag.json', params={
            'limit': '0',
        })
        resp.raise_for_status()
        return sorted(resp.json(), key=lambda x: x['id'])


class KonachanTagCrawler(_BaseKonachanTagCrawler):
    pass
