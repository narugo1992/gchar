import json
import os.path
import time
from functools import partial
from typing import Optional

import click
from ditk import logging

from gchar.games.dispatch.access import GAME_CHARS
from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from .keyword import _get_pixiv_search_count_by_name, _get_pixiv_character_search_counts_by_game
from .session import is_pixiv_session_okay, get_pixiv_sessions
from .tag_matches import PixivTagMatcher
from .tags import PixivTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.pixiv')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Utils with pixiv resources.")
def cli():
    pass  # pragma: no cover


@cli.command('names', help='Update the information of names.',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--game', '-g', 'game', type=click.Choice(sorted(GAME_CHARS.keys())), required=True,
              help='Game to crawl pixiv names.')
@click.option('--interval', 'interval', type=float, default=0.2,
              help='Sleep time after every name.', show_default=True)
@click.option('--min_interval', 'min_interval', type=float, default=0.2,
              help='Min sleep time after every name.', show_default=True)
@click.option('--sleep_every', 'sleep_every', type=int, default=70,
              help='Sleep after some number of names.', show_default=True)
@click.option('--sleep_time', 'sleep_time', type=float, default=30.0,
              help='Sleep time after some number of names.', show_default=True)
@click.option('--ensure_times', '-E', 'ensure_times', type=int, default=2,
              help='Ensure times at the end of crawler.', show_default=True)
@click.option('--output', '-o', 'output', type=click.Path(dir_okay=False), required=True,
              help='Output path of names\' data file.', show_default=None)
@click.option('--maxcnt', '-n', 'maxcnt', type=int, default=None,
              help='Max count to crawler (only used for debugging and testing).', show_default=True)
def names(game, output: str, interval: float, min_interval: float,
          sleep_every: int, sleep_time: float, ensure_times: int, maxcnt: Optional[int]):
    logging.try_init_root(logging.INFO)

    session = get_pixiv_sessions()
    if not is_pixiv_session_okay(session):
        raise ValueError('Pixiv session is down! Please use new cookies.')
    click.secho('Updating from pixiv.net web ajax ...', fg='yellow')

    game_cls = GAME_CHARS[game]
    data = _get_pixiv_search_count_by_name(
        game_cls, session,
        interval=interval, min_interval=min_interval,
        sleep_every=sleep_every, sleep_time=sleep_time,
        ensure_times=ensure_times, maxcnt=maxcnt,
    )
    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            'names': data,
            'last_updated': time.time(),
        }, f, indent=4, ensure_ascii=False)

    click.secho('Completed!', fg='green')


@cli.command('characters', help='Update the information of characters.',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--game', '-g', 'game', type=click.Choice(sorted(GAME_CHARS.keys())), required=True,
              help='Game to crawl pixiv names.')
@click.option('--interval', 'interval', type=float, default=0.2,
              help='Sleep time after every name.', show_default=True)
@click.option('--min_interval', 'min_interval', type=float, default=0.2,
              help='Min sleep time after every name.', show_default=True)
@click.option('--sleep_every', 'sleep_every', type=int, default=70,
              help='Sleep after some number of names.', show_default=True)
@click.option('--sleep_time', 'sleep_time', type=float, default=30.0,
              help='Sleep time after some number of names.', show_default=True)
@click.option('--ensure_times', '-E', 'ensure_times', type=int, default=2,
              help='Ensure times at the end of crawler.', show_default=True)
@click.option('--input', '-i', 'input_file', type=click.Path(dir_okay=False, exists=True), default=None,
              help='Character name json file to use. Use the online version when not given.', show_default=True)
@click.option('--output', '-o', 'output', type=click.Path(dir_okay=False), required=True,
              help='Output path of names\' data file.', show_default=None)
@click.option('--maxcnt', '-n', 'maxcnt', type=int, default=None,
              help='Max count to crawler (only used for debugging and testing).', show_default=True)
def characters(game, input_file: Optional[str], output: str, interval: float, min_interval: float,
               sleep_every: int, sleep_time: float, ensure_times: int, maxcnt: Optional[int]):
    logging.try_init_root(logging.INFO)

    session = get_pixiv_sessions()
    if not is_pixiv_session_okay(session):
        raise ValueError('Pixiv session is down! Please use new cookies.')
    click.secho('Updating from pixiv.net web ajax ...', fg='yellow')

    game_cls = GAME_CHARS[game]
    data = _get_pixiv_character_search_counts_by_game(
        game_cls, session,
        interval=interval, min_interval=min_interval,
        sleep_every=sleep_every, sleep_time=sleep_time,
        ensure_times=ensure_times, maxcnt=maxcnt,
        input_file=input_file,
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


PixivTagCrawler.add_commands(cli)
PixivTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()  # pragma: no cover
