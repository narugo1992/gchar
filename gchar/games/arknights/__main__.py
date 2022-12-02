from functools import partial

import click

from .index import _refresh_index
from ...utils import GLOBAL_CONTEXT_SETTINGS
from ...utils import print_version as _origin_print_version

print_version = partial(_origin_print_version, 'gchar.games.arknights')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Utils with Arknights.")
def cli():
    pass  # pragma: no cover


@cli.command('update', help='Update the local index of characters.',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--timeout', '-t', 'timeout', type=int, default=5,
              help='Timeout of this update.', show_default=True)
def update(timeout: int):
    click.secho('Updating from prts.wiki ...', fg='yellow')
    _refresh_index(timeout=timeout)
    click.secho('Completed!', fg='green')


if __name__ == '__main__':
    cli()
