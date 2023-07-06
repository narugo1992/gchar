import re
from itertools import chain
from typing import Optional, List, Mapping, Any

from pyquery import PyQuery as pq

from gchar.utils import srequest
from ..rule34.tags import ParallelTagCrawler


class GelbooruTagCrawler(ParallelTagCrawler):
    __init_page__ = 1
    __max_workers__ = 4
    __id_key__ = 'name'

    def __init__(self):
        ParallelTagCrawler.__init__(self, 'https://gelbooru.com')

    # def get_tag_aliases_from_page(self, p, **kwargs) -> List[Tuple[str, str]]:
    #     pass
    #
    # def get_tag_aliases_json(self) -> List[Tuple[str, str]]:
    #     pass

    def get_tags_from_page(self, p, **kwargs) -> Optional[List[Mapping[str, Any]]]:
        resp = srequest(self.session, 'GET', f'{self.site_url}/index.php', params={
            'page': 'tags',
            's': 'list',
            'pid': str((p - 1) * 50),
        })
        resp.raise_for_status()

        page = pq(resp.text)

        page_pg = page('#paginator .pagination')
        paginator_words = set([
            item.text().strip()
            for item in chain(page_pg('a').items(), page_pg('b').items())
        ])
        if str(p) not in paginator_words:
            return None

        table = page('table.highlightable')

        data = []
        for row in table('tr').items():
            if len(list(row('td').items())) == 0:
                continue

            td_1 = row('td:nth-child(1)')
            tag = td_1('span:nth-child(1)').text().strip()
            count = int(td_1('span:nth-child(2)').text().strip())
            td_2 = row('td:nth-child(2)')
            type_ = re.sub(r'\(\s*edit\s*\)', '', td_2.text(), re.IGNORECASE).strip()
            data.append({
                'name': tag,
                'count': count,
                'type': type_,
            })

        return data

    __sqlite_indices__ = ['name', 'count', 'type']
