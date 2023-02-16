import re
from typing import Optional
from urllib.parse import quote

import requests
from pyquery import PyQuery as pq

from ...utils import get_requests_session, sget

_MOEGIRL_WEBSITE = 'https://zh.moegirl.org.cn'


def get_alias_from_moegirl_wiki(keyword: str, session: Optional[requests.Session] = None):
    session = session or get_requests_session()
    resp = sget(session, f'{_MOEGIRL_WEBSITE}/zh-hans/{quote(keyword)}', raise_for_status=False)
    if resp.ok:
        full_page = pq(resp.text)
        info_table = full_page('.infotemplatebox table')
        for row in info_table('tr').items():
            row_heads = list(row('th').items())
            row_cells = list(row('td').items())
            if len(row_heads) != 1 or len(row_cells) != 1:
                continue

            head_text = row_heads[0].text().strip()
            if head_text in {'别名', '别号', '别称', '又名'}:
                words = []
                sentences = []
                row_cell = row_cells[0]
                row_cell = row_cell.remove('sup')
                for ruby in row_cell('ruby').items():
                    ruby = ruby.remove('.template-ruby-hidden')
                    ruby.replace_with(ruby('rb').text())

                sentences.extend([item.text().strip() for item in row_cell('span.heimu').items()])
                row_cell = row_cell.remove('span.heimu')

                cell_text = re.sub(r'\[\d+]', '', row_cell.text().strip())
                sentences.append(cell_text)

                for sentence in sentences:
                    sentence = re.sub(r'[(（][\s\S]*?[)）]', '', sentence)
                    words.extend([word.strip() for word in re.findall(r'\b[\w \t\-・·`_]+\b', sentence)])

                return words

        return []
    else:
        if resp.status_code == 404:
            return []
        else:
            resp.raise_for_status()
