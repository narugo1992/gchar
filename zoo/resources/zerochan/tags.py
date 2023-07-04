from typing import Optional, List, Mapping, Any

from pyquery import PyQuery as pq

from gchar.utils import srequest
from ..base.tags import ParallelTagCrawler


class ZerochanTagCrawler(ParallelTagCrawler):
    __max_workers__ = 4
    __id_key__ = 'tag'
    __init_page__ = 1

    def __init__(self, site_url: str = 'https://zerochan.net'):
        ParallelTagCrawler.__init__(self, site_url)
        self.session.headers.update({'User-Agent': 'Tag Crawler - narugo1992'})

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        resp = srequest(self.session, 'GET', f'{self.site_url}/tags', params={
            's': 'count',
            'm': 'details',
            'q': '',
            't': '',
            'p': str(p)
        })
        resp.raise_for_status()
        page = pq(resp.text)

        data = []
        for row in page('table.tags tr').items():
            if len(row('td')) == 0:
                continue

            type_ = row('td:nth-child(1)').attr('class').strip()
            name = row('td:nth-child(1)').text().strip()
            parent = row('td:nth-child(2)').text().strip()
            total = int(row('td:nth-child(3)').text().replace(',', '').strip())
            strict = int(row('td:nth-child(4)').text().replace(',', '').strip())
            children_count = int(row('td:nth-child(5)').text().replace(',', '').strip())
            parent_count = int(row('td:nth-child(6)').text().replace(',', '').strip())

            data.append({
                'tag': name,
                'type': type_,
                'parent': parent,
                'total': total,
                'strict': strict,
                'children_count': children_count,
                'parent_count': parent_count,
            })

        return data

    __sqlite_indices__ = ['children_count', 'parent', 'parent_count', 'strict', 'tag', 'total', 'type']
