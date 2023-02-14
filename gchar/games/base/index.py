import json
import os.path
import re
import time
from functools import partial
from typing import Optional, Iterator, Any
from urllib.parse import urlsplit

import click
import requests
from hbutils.string import env_template

from ...utils import GLOBAL_CONTEXT_SETTINGS
from ...utils import download_file, get_requests_session, optional_lru_cache
from ...utils import print_version as _origin_print_version

__GAMES_DIRECTORY__ = os.path.normpath(os.path.join(__file__, '..', '..'))


class IndexerMeta(type):
    __DOWNLOAD_URL__ = 'https://huggingface.co/datasets/deepghs/game_characters/resolve/main/${game_name}/index.json'
    __DIRECTORY__ = os.path.join(__GAMES_DIRECTORY__, '${game_name}')
    __INDEX_FILE__ = os.path.join(__DIRECTORY__, 'index.json')
    __PACKAGE_NAME__ = 'gchar.games.${game_name}'

    def __init__(cls, name, bases, dict_):
        type.__init__(cls, name, bases, dict_)
        cls.__original_names = set([name for name in dir(type) if name.startswith('__') and name.endswith('__')])

    @property
    def _env_names(cls):
        return {
            '_'.join(re.findall(r'[0-9a-zA-Z]+', name)).lower(): getattr(cls, name)
            for name in dir(cls)
            if name.startswith('__') and name.endswith('__') and name not in cls.__original_names
        }

    def _render_template(cls, template, safe=False, default=''):
        return env_template(template, cls._env_names, safe, default)

    @property
    def download_url(cls):
        return cls._render_template(cls.__DOWNLOAD_URL__)

    @property
    def directory(cls):
        return cls._render_template(cls.__DIRECTORY__)

    @property
    def index_file(cls):
        return cls._render_template(cls.__INDEX_FILE__)

    @property
    def package_name(cls):
        return cls._render_template(cls.__PACKAGE_NAME__)


class BaseIndexer(metaclass=IndexerMeta):
    __game_name__ = 'default'
    __official_name__ = 'official name'
    __root_website__ = 'https://root.website.com'

    @property
    def official_name(self):
        return re.sub(r'\s+', ' ', self.__official_name__).strip().lower()

    @property
    def capitalized_name(self):
        return re.sub(r'[a-zA-Z0-9]+', lambda x: x.group(0).capitalize(), self.official_name)

    def _create_session(self, timeout: int = 5, retries: int = 3, headers=None, **kwargs):
        _ = kwargs
        return get_requests_session(max_retries=retries, timeout=timeout, headers=headers)

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None,
                                 **kwargs) -> Iterator[Any]:
        raise NotImplementedError

    def crawl_index_to_local(self, output_filename: Optional[str] = None,
                             maxcnt: Optional[int] = None, timeout: int = 5, retries: int = 3, **kwargs):
        session = self._create_session(timeout, retries, **kwargs)
        data = list(self._crawl_index_from_online(session, maxcnt, **kwargs))
        with open(output_filename or self.__class__.index_file, 'w', encoding='utf-8') as f:
            json.dump({
                'data': data,
                'last_updated': time.time(),
            }, f, indent=4, ensure_ascii=False)

    def download_index_from_online(self, force: bool = False, **kwargs):
        _ = kwargs
        if force or not os.path.exists(self.__class__.index_file):
            download_file(self.__class__.download_url, self.__class__.index_file)

    @optional_lru_cache()
    def get_index(self, force: bool = False, crawl: bool = False, **kwargs):
        if force or not os.path.exists(self.__class__.index_file):
            if crawl:
                self.crawl_index_to_local(output_filename=self.__class__.index_file, **kwargs)
            else:
                self.download_index_from_online(force=True, **kwargs)

        with open(self.__class__.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)['data']

    def get_cli(self):
        print_version = partial(_origin_print_version, self.__class__.package_name)

        @click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS},
                     help=f"Utils with {self.capitalized_name}.")
        @click.option('-v', '--version', is_flag=True,
                      callback=print_version, expose_value=False, is_eager=True)
        def cli():
            pass  # pragma: no cover

        split_website_url = urlsplit(self.__root_website__)

        @cli.command('update', help=f'Update the local index of characters from {split_website_url.hostname}.',
                     context_settings={**GLOBAL_CONTEXT_SETTINGS})
        @click.option('--timeout', '-t', 'timeout', type=int, default=5,
                      help='Timeout of this update.', show_default=True)
        @click.option('--maxcnt', '-n', 'maxcnt', type=int, default=None,
                      help='Max count to crawler (only used for debugging and testing).', show_default=True)
        @click.option('--output', '-o', 'output', type=click.Path(dir_okay=False), default=None,
                      help='Output path of index file.', show_default=self.__class__.index_file)
        def update(timeout: int, maxcnt: Optional[int], output: Optional[str]):
            short_url = f'{split_website_url.scheme}://{split_website_url.hostname}'
            click.secho(f'Updating from {short_url} ...', fg='yellow')
            self.crawl_index_to_local(output, maxcnt, timeout)
            click.secho('Completed!', fg='green')

        split_download_url = urlsplit(self.__class__.download_url)

        @cli.command('download', help=f'Download the index of characters from {split_download_url.hostname}.')
        def download():
            short_url = f'{split_download_url.scheme}://{split_download_url.hostname}'
            click.echo(click.style(f'Downloading from {short_url} ...', fg='yellow'))
            self.download_index_from_online(force=True)
            click.echo(click.style('Completed!', fg='green'))

        return cli
