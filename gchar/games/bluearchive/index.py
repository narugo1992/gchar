import os.path
import re
import unicodedata
import warnings
from datetime import datetime
from typing import Optional, Iterator, Any
from urllib.parse import urljoin

import requests
from hbutils.system import TemporaryDirectory
from pyquery import PyQuery as pq
from tqdm.auto import tqdm

from ..base import BaseIndexer
from ...utils import sget, download_file

SERVANT_ALT_PATTERN = re.compile(r'Servant (?P<id>\d+)\.[a-zA-Z\d]+')
PAGE_REL_PATTERN = re.compile(r'var data_list\s*=\"(?P<ids>[\d,\s]*)\"')


def _merge_list(*lst):
    retval = []
    _exists = set()
    for lt in lst:
        for item in lt:
            if item not in _exists:
                retval.append(item)
                _exists.add(item)

    return retval


class Indexer(BaseIndexer):
    __game_name__ = 'bluearchive'
    __official_name__ = 'blue archive'
    __root_website__ = 'https://bluearchive.wiki/'
    __cn_root_website__ = 'https://ba.gamekee.com'  # do not add '/' at the tail, or the api will crash

    _CN_TITLE_PATTERN = re.compile(r'^(?P<title>\w+?)\s*(\((?P<comment>\w+?)\))?$')
    _CN_NAME_PATTERN = re.compile(r'^(?P<jpname>[^(]+)\s*(\((?P<cnname>[^)]+)\))?\s*(?P<extra>\w+)?$')

    def _get_ch_info_from_cn(self, session: requests.Session, content_id, title):
        resp = sget(session, f'{self.__cn_root_website__}/v1/content/detail/{content_id}', headers={
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "referrer": f"https://ba.gamekee.com/{content_id}.html",
            "game-alias": "ba",
            "game-id": "0",
        })
        data = resp.json()['data']
        assert data['content_id'] == content_id, \
            f'Content ID not match, {content_id!r} expected but {data["content_id"]!r} actually found!'
        page_full = pq(data['content'])

        jpnames, cnnames = [], []
        _title_matching = self._CN_TITLE_PATTERN.fullmatch(unicodedata.normalize('NFKC', title))
        cn_title, comment = _title_matching.group('title'), _title_matching.group('comment')

        first_table, *_ = page_full('table').items()
        fr, *_ = first_table('tr:nth-child(1)').items()
        ch_title = fr.text().strip()
        _title_matching = self._CN_TITLE_PATTERN.fullmatch(unicodedata.normalize('NFKC', ch_title))
        assert comment == _title_matching.group('comment'), \
            f'Comment not match, {comment!r} in title, ' \
            f'but {_title_matching.group("comment")!r} in page header.'
        if _title_matching.group('title') != cn_title:
            cnnames.append(_title_matching.group('title'))

        info_table = None
        for table in page_full('table.mould-table').items():
            if table('tbody tr:nth-child(1)').text().strip() == '学生信息':
                info_table = table
                break

        assert info_table is not None, f'Info table not found for character {content_id!r}.'

        row2 = info_table('tbody tr:nth-child(2)')
        assert row2('td:nth-child(1)').text().strip() == '全名'

        full_name_raw = unicodedata.normalize('NFKC', row2('td:nth-child(2)').text())
        _full_name_matching = self._CN_NAME_PATTERN.fullmatch(full_name_raw)
        if _full_name_matching.group('extra'):
            jpnames.append(re.sub(r'\s+', '', _full_name_matching.group('jpname') +
                                  _full_name_matching.group('extra')))

            jpnames.append(re.sub(r'\s+', '', _full_name_matching.group('cnname') +
                                  _full_name_matching.group('extra')))
        else:
            jpnames.append(re.sub(r'\s+', '', _full_name_matching.group('jpname')))
            if _full_name_matching.group('cnname'):
                cnnames.append(re.sub(r'\s+', '', _full_name_matching.group('cnname')))

        row3 = info_table('tbody tr:nth-child(3)')
        if row3('td:nth-child(1)').text().strip() == '繁中译名':
            tw_name_raw = unicodedata.normalize('NFKC', row3('td:nth-child(2)').text())
            tw_matching = self._CN_TITLE_PATTERN.fullmatch(tw_name_raw)
            cnnames.append(unicodedata.normalize('NFKC', tw_matching.group('title')))

        image_url = urljoin(resp.url, page_full('table tr:nth-child(2) img').attr('src'))
        return (cn_title, comment), (cnnames, jpnames, image_url)

    def _crawl_index_from_cn(self, session: requests.Session):
        resp = sget(session, f"{self.__cn_root_website__}/v1/wiki/entry", headers={
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "referrer": "https://ba.gamekee.com/",
            "game-alias": "ba",
            "game-id": "0",
        })
        data = resp.json()
        ch_list = data['data']['entry_list'][4]
        assert ch_list['name'] == "学生图鉴"

        ch_all = ch_list['child'][2]
        assert ch_all['name'] == "所有学生"

        items = []
        for ch_info in tqdm(ch_all['child']):
            content_id = ch_info['content_id']

            items.append(self._get_ch_info_from_cn(session, content_id, ch_info['name']))

        items = sorted(items, key=lambda x: (x[0][0], x[0][1] or ''))
        ch_ret = {}
        for (cn_title, comment), (cnnames, jpnames, skin_url) in items:
            if cn_title not in ch_ret:
                ch_ret[cn_title] = {
                    'title': cn_title,
                    'cnnames': [cn_title],
                    'jpnames': [],
                    'skins': [],
                    'is_extra': comment != '联动',
                }
            old_item = ch_ret[cn_title]
            old_item['cnnames'] = _merge_list(old_item['cnnames'], cnnames)
            old_item['jpnames'] = _merge_list(old_item['jpnames'], jpnames)
            # noinspection PyTypeChecker
            old_item['skins'].append({'name': comment or '默认', 'url': skin_url})

        return ch_ret

    def _get_names_by_ch_url(self, session: requests.Session, ch_url: str):
        resp = sget(session, ch_url)
        full_page = pq(resp.text)
        ch_table = full_page('table.wikitable.character')

        image_file_page_url = urljoin(
            resp.url,
            full_page("article.tabber__panel[data-title=Artwork] a.image").attr("href")
        )
        src_resp = sget(session, image_file_page_url)
        full_image_url = urljoin(src_resp.url, pq(src_resp.text)(".fullMedia a").attr('href'))

        for row in ch_table('tr').items():
            if row('th:nth-child(1)').text().lower().strip() == 'full name':
                en_line, jp_line = row('td:nth-child(2)').text().splitlines(keepends=True)
                enname = en_line.strip()
                jpname = re.sub(r'\s+', '', jp_line).lstrip('(').rstrip(')')

                return enname, jpname, full_image_url
        else:
            assert False, f'Enname and jpname not found on {ch_url!r}.'

    def _crawl_index_from_en(self, session: requests.Session):
        resp = sget(session, f'{self.__root_website__}/wiki/Characters')
        full_page = pq(resp.text)

        columns = []
        for head in full_page('table.wikitable th').items():
            title = head('img').attr('alt') if head('img') else head.text().strip()
            title = re.sub(r'\W+', '_', title.lower()).strip('_')
            columns.append(title)

        retval = []
        for row in tqdm(list(full_page('table.wikitable tbody tr').items())):
            if row('th'):
                continue
            if '(' in row('td:nth-child(2)').text():
                continue

            values = []
            for item in row('td').items():
                if item('img'):
                    if 'rarity' in (item.attr('class') or ''):
                        values.append(len(list(item('img').items())))
                    else:
                        values.append(item('img').attr('alt'))
                else:
                    values.append(item.text().strip())

            assert len(columns) == len(values)
            data = dict(zip(columns[1:], values[1:]))
            assert 1 <= data['rarity'] <= 3

            date_match = re.fullmatch(r'^\s*(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)\s*$', data['release_date'])
            release_time = datetime.strptime(
                f'{date_match.group("year")}/{date_match.group("month")}/{date_match.group("day")} 17:00:00 +0800',
                '%Y/%m/%d %H:%M:%S %z'
            )

            info_url = urljoin(resp.url, row('td:nth-child(2) a').attr('href'))
            full_enname, jpname, en_image_url = self._get_names_by_ch_url(session, info_url)
            retval.append({
                'data': data,
                'enname': row('td:nth-child(2)').text().strip(),
                'full_enname': full_enname,
                'jpname': jpname,
                'en_image_url': en_image_url,
                'release_time': release_time.timestamp(),
            })

        return retval

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None, **kwargs) \
            -> Iterator[Any]:
        from PIL import Image
        from imgutils.data import load_image
        from imgutils.metrics import lpips_extract_feature, lpips_difference

        cn_ret = self._crawl_index_from_cn(session)
        en_ret = self._crawl_index_from_en(session)

        def cut_for_content(image, threshold: int = 10):
            import numpy as np
            data = np.array(image)
            tp_data = data[:, :, 3]  # HxW

            width_valids = np.array(range(image.width))[tp_data.mean(axis=0) > threshold]
            height_valids = np.array(range(image.height))[tp_data.mean(axis=1) > threshold]

            width_range = width_valids.min(), width_valids.max()
            height_range = height_valids.min(), height_valids.max()

            return image.crop((width_range[0], height_range[0], width_range[1], height_range[1]))

        with TemporaryDirectory() as td:
            cn_images = {}
            for cn_name, cn_item in tqdm(cn_ret.items()):
                file = os.path.join(td, f'cn_{cn_name}.png')
                download_file(cn_item['skins'][0]['url'], file, session=session)
                image = load_image(cut_for_content(Image.open(file).convert('RGBA')))
                cn_images[cn_name] = (image, lpips_extract_feature(image))

            en_images = {}
            for i, en_item in enumerate(tqdm(en_ret)):
                file = os.path.join(td, f'en_{i}.png')
                download_file(en_item['en_image_url'], file, session=session)
                image = load_image(cut_for_content(Image.open(file).convert('RGBA')))
                en_images[i] = (image, lpips_extract_feature(image))

            matches = []
            for cn_key, (cn_image, cn_feat) in tqdm(cn_images.items()):
                for en_key, (en_image, en_feat) in en_images.items():
                    matches.append((cn_key, en_key, lpips_difference(cn_feat, en_feat)))

            matches = sorted(matches, key=lambda x: (x[2], x[0], x[1]))
            recorded = []
            _remain_cn_keys, _remain_en_keys = set(cn_images.keys()), set(en_images.keys())
            for cn_key, en_key, diff in matches:
                if cn_key in _remain_cn_keys and en_key in _remain_en_keys and diff < 0.55:
                    _remain_cn_keys.remove(cn_key)
                    _remain_en_keys.remove(en_key)
                    recorded.append((cn_key, en_key, diff))

            if _remain_cn_keys:
                warnings.warn(f'Unmatched chinese names: {list(_remain_cn_keys)!r}.')
            if _remain_en_keys:
                warnings.warn(f'Unmatched english names: '
                              f'{[en_ret[en_key]["enname"] for en_key in _remain_en_keys]!r}.')

            recorded = sorted(recorded, key=lambda x: x[1])
            for cn_key, en_key, diff in recorded:
                cn_info = cn_ret[cn_key]
                en_info = en_ret[en_key]
                yield {
                    'cnnames': cn_info['cnnames'],
                    'ennames': _merge_list([en_info['enname'], en_info['full_enname']]),
                    'jpnames': _merge_list([en_info['jpname']], cn_info['jpnames']),
                    'is_extra': cn_info['is_extra'],
                    'skins': cn_info['skins'],
                    'data': en_info['data'],
                    'release': {
                        'time': en_info['release_time'],
                    },
                    'match_diff': diff,
                }


INDEXER = Indexer()
