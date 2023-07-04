import json
from typing import Optional, List, Mapping, Any

import xmltodict

from gchar.utils import srequest
from ..base.tags import ParallelTagCrawler


class Rule34TagCrawler(ParallelTagCrawler):
    __init_page__ = 0
    __max_workers__ = 12
    __id_key__ = 'id'

    def __init__(self, site_url: str = 'https://rule34.xxx'):
        ParallelTagCrawler.__init__(self, site_url)
        self.session.headers.update({
            'Content-Type': 'application/json; charset=utf-8',
        })

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        resp = srequest(self.session, 'GET', f'{self.site_url}/index.php', params={
            'page': 'dapi',
            's': 'tag',
            'q': 'index',
            'json': '1',
            'limit': '100',
            'pid': str(p),
        })
        resp.raise_for_status()

        json_data = xmltodict.parse(resp.text)
        if 'tags' not in json_data or 'tag' not in json_data['tags']:
            return None

        data = []
        for item in json_data['tags']['tag']:
            item = {key.lstrip('@'): value for key, value in item.items()}
            item['id'] = int(item['id'])
            item['type'] = int(item['type'])
            item['count'] = int(item['count'])
            item['ambiguous'] = json.loads(item['ambiguous'])
            data.append(item)

        return data

    __sqlite_indices__ = ['id', 'name', 'type', 'count', 'ambiguous']
