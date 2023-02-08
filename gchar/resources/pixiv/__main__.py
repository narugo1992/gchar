import json
import os.path
import time
from functools import partial
from typing import Optional

import click

from .games import _GAMES, _local_names_file, _local_characters_file
from .keyword import get_pixiv_name_search_count, get_pixiv_character_search_count
from .session import is_pixiv_session_okay, get_pixiv_session
from ...utils import GLOBAL_CONTEXT_SETTINGS
from ...utils import print_version as _origin_print_version

print_version = partial(_origin_print_version, 'gchar.resources.pixiv')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Utils with pixiv resources.")
def cli():
    pass  # pragma: no cover


@cli.command('names', help='Update the information of names.',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--game', '-g', 'game', type=click.Choice([item[1] for item in _GAMES]), required=True,
              help='Game to crawl pixiv names.')
@click.option('--interval', 'interval', type=float, default=0.2,
              help='Sleep time after every name.', show_default=True)
@click.option('--sleep_every', 'sleep_every', type=int, default=70,
              help='Sleep after some number of names.', show_default=True)
@click.option('--sleep_time', 'sleep_time', type=float, default=30.0,
              help='Sleep time after some number of names.', show_default=True)
@click.option('--ensure_times', '-E', 'ensure_times', type=int, default=3,
              help='Ensure times at the end of crawler.', show_default=True)
@click.option('--output', '-o', 'output', type=click.Path(dir_okay=False), default=None,
              help='Output path of names\' data file.', show_default=None)
def names(game, output: Optional[str], interval: float, sleep_every: int, sleep_time: float, ensure_times: int):
    output = output or _local_names_file(game)
    session = get_pixiv_session()
    if not is_pixiv_session_okay(session):
        raise ValueError('Pixiv session is down! Please use new cookies.')
    click.secho('Updating from pixiv.net web ajax ...', fg='yellow')

    data = get_pixiv_name_search_count(
        game, session,
        interval=interval, sleep_every=sleep_every,
        sleep_time=sleep_time, ensure_times=ensure_times,
    )
    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            'names': [
                {
                    'name': name,
                    'count': count,
                } for name, count in data
            ],
            'last_updated': time.time(),
        }, f, indent=4, ensure_ascii=False)

    click.secho('Completed!', fg='green')


@cli.command('characters', help='Update the information of characters.',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--game', '-g', 'game', type=click.Choice([item[1] for item in _GAMES]), required=True,
              help='Game to crawl pixiv names.')
@click.option('--interval', 'interval', type=float, default=0.2,
              help='Sleep time after every name.', show_default=True)
@click.option('--sleep_every', 'sleep_every', type=int, default=70,
              help='Sleep after some number of names.', show_default=True)
@click.option('--sleep_time', 'sleep_time', type=float, default=30.0,
              help='Sleep time after some number of names.', show_default=True)
@click.option('--ensure_times', '-E', 'ensure_times', type=int, default=3,
              help='Ensure times at the end of crawler.', show_default=True)
@click.option('--output', '-o', 'output', type=click.Path(dir_okay=False), default=None,
              help='Output path of names\' data file.', show_default=None)
def characters(game, output: Optional[str], interval: float, sleep_every: int, sleep_time: float, ensure_times: int):
    output = output or _local_characters_file(game)
    session = get_pixiv_session()
    if not is_pixiv_session_okay(session):
        raise ValueError('Pixiv session is down! Please use new cookies.')
    click.secho('Updating from pixiv.net web ajax ...', fg='yellow')

    data = get_pixiv_character_search_count(
        game, session,
        interval=interval, sleep_every=sleep_every,
        sleep_time=sleep_time, ensure_times=ensure_times,
    )
    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            'characters': data,
            'last_updated': time.time(),
        }, f, indent=4, ensure_ascii=False)

    click.secho('Completed!', fg='green')


if __name__ == '__main__':
    cli()  # pragma: no cover