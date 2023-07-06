import re
from itertools import chain
from typing import Optional, List, Mapping, Any, Tuple

from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from gchar.utils import srequest
from ..rule34.tags import ParallelTagCrawler


class GelbooruTagCrawler(ParallelTagCrawler):
    __init_page__ = 1
    __max_workers__ = 4
    __id_key__ = 'name'

    def __init__(self):
        ParallelTagCrawler.__init__(self, 'https://gelbooru.com')

    def _get_tag_aliases_from_page(self, p, **kwargs) -> List[Tuple[str, str]]:
        resp = srequest(self.session, 'GET', f'{self.site_url}/index.php', params={
            'page': 'alias',
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
            return []

        table = page('#aliases table')

        data = []
        for row in table('tr').items():
            if len(list(row('td').items())) == 0:
                continue

            first_a, second_a = row('a').items()
            alias_tag = first_a.text().strip()
            tag = second_a.text().strip()
            data.append((alias_tag, tag))

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
            type_text = re.sub(r'\(\s*edit\s*\)', '', td_2.text(), re.IGNORECASE).strip()
            type_, *others = re.split('\s*,\s*', type_text)
            is_ambiguous = bool(others and 'ambiguous' in others)

            data.append({
                'name': tag,
                'count': count,
                'type': type_,
                'is_ambiguous': is_ambiguous,
            })

        return data

    __sqlite_indices__ = ['name', 'count', 'type', 'is_ambiguous']