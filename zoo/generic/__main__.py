import os.path
import pathlib
import re
import textwrap
from functools import partial
from typing import Optional

import click
from ditk import logging
from unidecode import unidecode

from gchar.generic import __file__ as _GCHAR_GENERIC
from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from ._meta import get_full_info_for_datasource

_GCHAR_GENERIC_DIR = os.path.dirname(_GCHAR_GENERIC)
_ZOO_GENERIC_DIR = os.path.dirname(__file__)
_GCHAR_GENERIC_INIT_FILE = os.path.join(_GCHAR_GENERIC_DIR, '__init__.py')

print_version = partial(_origin_print_version, 'zoo.resources.anime_pictures')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of anime_pictures')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


@cli.command('create', context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Create new generic data source.')
@click.option('-n', '--name', 'name', type=str, required=True,
              help='Name of the generic source.', show_default=True)
@click.option('--game_name', 'game_name', type=str, default=None,
              help='Name of the new game, used for file\'s name,', show_default=True)
@click.option('-T', '--official_name', 'official_name', type=str, default=None,
              help='Official name of new game.', show_default=True)
def create(name, game_name: Optional[str] = None, official_name: Optional[str] = None):
    logging.try_init_root(logging.INFO)
    logging.info(f'Getting meta information of game {name!r} ...')
    _game_name, _official_name, root_ws, all_names, pixiv_keyword = get_full_info_for_datasource(name)
    game_name = game_name or _game_name
    official_name = official_name or _official_name
    logging.info(f'Game name: {game_name!r}, official name: {official_name!r}')
    logging.info(f'All names and aliases: {all_names!r}')
    logging.info(f'Pixiv keyword: {pixiv_keyword!r}')

    _indexer_file = os.path.join(_ZOO_GENERIC_DIR, f'{game_name}.py')
    _indexer_code = textwrap.dedent(f"""
from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = {game_name!r}
    __official_name__ = {official_name!r}
    __root_website__ = {root_ws!r}


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

    """.lstrip())

    _cls_file = os.path.join(_GCHAR_GENERIC_DIR, f'{game_name}.py')
    _cls_code = textwrap.dedent(f"""
from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = {game_name!r}
    __official_name__ = {official_name!r}
    __game_keywords__ = {all_names!r}
    __pixiv_keyword__ = {pixiv_keyword!r}
    __pixiv_suffix__ = {pixiv_keyword!r}


register_game(Character)

    """.lstrip())

    if os.path.exists(_indexer_file):
        raise FileExistsError(f'Indexer file {_indexer_file!r} exists.')
    if os.path.exists(_cls_file):
        raise FileExistsError(f'Data class file {_cls_file!r} exists.')

    logging.info(f'Writing indexer file {_indexer_file!r} ...')
    with open(_indexer_file, 'w', encoding='utf-8') as f:
        print(_indexer_code, file=f, end='')
    logging.info(f'Writing class model file {_cls_file!r} ...')
    with open(_cls_file, 'w', encoding='utf-8') as f:
        print(_cls_code, file=f, end='')

    logging.info(f'Appending import statement to {_GCHAR_GENERIC_INIT_FILE!r} ...')
    _init_origin_code = pathlib.Path(_GCHAR_GENERIC_INIT_FILE).read_text(encoding='utf-8')
    wds = [unidecode(wd).capitalize() for wd in re.split(r'[\W_]+', official_name) if wd]
    new_cls_name = ''.join(wds) + 'Character'
    with open(_GCHAR_GENERIC_INIT_FILE, 'w', encoding='utf-8') as f:
        print(f'from .{game_name} import Character as {new_cls_name}', file=f)
        print(_init_origin_code, file=f, end='')


if __name__ == '__main__':
    cli()
