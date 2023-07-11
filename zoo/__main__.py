import itertools
import re
import warnings
from datetime import date
from functools import partial

import click

from gchar.games.dispatch import list_available_game_names
from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version

print_version = partial(_origin_print_version, 'zoo')

_KNOWN_GAMES = list_available_game_names()


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Utils with gchar.")
def cli():
    pass  # pragma: no cover


SCHEDULE_TABLE = [
    ('fgo',),
    ('girlsfrontline',),
    ('arknights',),
    ('azurlane',),
    ('genshin', 'neuralcloud', 'bluearchive', 'pathtonowhere'),
]
GAMES = list(itertools.chain(*SCHEDULE_TABLE))
if set(GAMES) - set(_KNOWN_GAMES):
    raise ValueError(f'Unknown game names - {sorted(set(GAMES) - set(_KNOWN_GAMES))}.')
if set(_KNOWN_GAMES) - set(GAMES):
    warnings.warn(f'Unscheduled game names - {sorted(set(_KNOWN_GAMES) - set(GAMES))}')


@cli.command('schedule', help='Check the scheduling of this date')
@click.option('--game', '-g', 'game', type=click.Choice(GAMES), required=True,
              help='Game to query.', show_default=True)
def schedule(game: str):
    index = (date.today() - date(2020, 1, 1)).days % len(SCHEDULE_TABLE)
    if index < 0:
        index += len(SCHEDULE_TABLE)

    if game in SCHEDULE_TABLE[index]:
        click.echo('yes')
    else:
        click.echo('no')


@cli.command('scheck', help='String scheduled check')
@click.option('--game', '-g', 'game', type=click.Choice(GAMES), required=True,
              help='Game to query.', show_default=True)
@click.option('--string', '-s', 'string', type=str, required=True)
def scheck(game: str, string: str):
    selected = set(map(str.lower, re.findall(r'\b\w+\b', string)))
    if game.lower().strip() in selected:
        click.echo('yes')
    else:
        click.echo('no')


if __name__ == '__main__':
    cli()
