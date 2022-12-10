import os.path
import tempfile
import time
from typing import Iterator, Tuple

from PIL import Image
from pixivpy3 import AppPixivAPI, PixivError
from requests import RequestException

from ..base import CrawlerSession
from ...utils import func_retry, import_tqdm

tqdm = import_tqdm()


class PixivOr:
    def __init__(self, *items):
        self.__items = items

    def __bool__(self):
        return bool(self.__items)

    def __str__(self):
        if not self.__items:
            return '<none>'
        elif len(self.__items) == 1:
            return str(self.__items[0])
        else:
            return '(' + ' OR '.join(self.__items) + ')'

    def __repr__(self):
        return f'<{type(self).__name__} {self.__items!r}>'


class PixivNot:
    def __iter__(self, item):
        self.__item = item

    def __str__(self):
        return f'-{self.__item}'

    def __repr__(self):
        return f'<{type(self).__name__} {self.__item!r}>'


def _to_pixiv_keywords(obj):
    if isinstance(obj, (str, PixivNot, PixivOr)):
        return str(obj)
    elif isinstance(obj, (list, tuple)):
        return ' '.join(map(str, obj))
    else:
        raise TypeError(f'Unknown pixiv keywords - {obj!r}.')


class _PixivReAuth(Exception):
    pass


class PixivSession(CrawlerSession):
    REAUTH_TIMESPAN = 20 * 60

    def __init__(self, refresh_token: str, proxies=None):
        _kwargs = {}
        if proxies:
            _kwargs['proxies'] = proxies
        self.__api = AppPixivAPI(**_kwargs)
        self.__refresh_token = refresh_token
        self.__last_auth = None

    def __auth(self):
        self.__api.auth(refresh_token=self.__refresh_token)

    def __try_auth(self):
        if self.__last_auth is None or self.__last_auth + self.REAUTH_TIMESPAN > time.time():
            self.__auth()
            self.__last_auth = time.time()

    @func_retry((PixivError, _PixivReAuth), retries=3, delay=1.0)
    def search(self, keywords, offset: int = 0):
        self.__try_auth()
        keywords = _to_pixiv_keywords(keywords)
        data = self.__api.search_illust(keywords, sort='popular_desc', offset=offset)
        if 'illusts' not in data:
            self.__last_auth = None
            raise _PixivReAuth
        else:
            return data

    @func_retry((PixivError, _PixivReAuth, ConnectionError, RequestException), retries=3, delay=1.0)
    def download(self, url, path, fname):
        self.__api.download(url, path=path, fname=fname)

    def iter_images(self, keywords, count: int = 100, use_original: bool = False, min_diff: float = 0.15,
                    allow_ai: bool = False, max_page_in_illust: int = -1, max_page_when_grab: int = 1,
                    min_bookmarks: int = 100) \
            -> Iterator[Tuple[int, Tuple[int, int], str, Image.Image]]:
        keywords = _to_pixiv_keywords(keywords)

        page_cnt, current_cnt, current_offset = 0, 0, 0
        page_progress = tqdm(leave=True)
        cnt_progress = tqdm(total=count if count > 0 else None, leave=True)
        while current_cnt < count or count < 0:
            try:
                all_data = self.search(keywords, current_offset)
            except PixivError:
                continue

            page_cnt += 1
            page_progress.set_description(f'Scanning {keywords!r} page {page_cnt} ...')
            page_progress.update()

            illusts = all_data['illusts']
            for illust in illusts:
                if illust["type"] != "illust":
                    continue
                if not allow_ai and illust["illust_ai_type"]:
                    continue

                pages = illust['page_count']
                if illust['page_count'] > max_page_in_illust > 0:
                    continue
                marks = illust["total_bookmarks"]
                if marks < min_bookmarks:
                    continue

                if pages == 1:
                    if use_original:
                        urls = [illust["meta_single_page"]["original_image_url"]]
                    else:
                        urls = [illust["image_urls"]["large"]]
                else:
                    if use_original:
                        urls = [img["image_urls"]["original"] for img in illust["meta_pages"]]
                    else:
                        urls = [img["image_urls"]["large"] for img in illust["meta_pages"]]

                with tempfile.TemporaryDirectory() as td:
                    _last_image = None
                    for url in urls[:max_page_when_grab]:
                        filename = os.path.basename(url)
                        try:
                            self.download(url, path=td, fname=filename)
                        except (PixivError, ConnectionError, RequestException):
                            continue

                        current_cnt += 1
                        cnt_progress.set_description(f'{current_cnt} image(s) downloaded')
                        cnt_progress.update()

                        current_image = Image.open(os.path.join(td, filename))
                        # if _last_image and image_diff_percent(_last_image, current_image) < min_diff:
                        #     continue

                        yield illust["id"], (illust["total_view"], marks), filename, current_image
                        _last_image = current_image

                if 0 <= count <= current_cnt:
                    break

            current_offset += len(illusts)
