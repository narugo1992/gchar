from functools import partial

import click

from .index import _refresh_index, ROOT_SITE, _INDEX_FILE, _download_from_huggingface, ONLINE_INDEX_URL
from ...utils import GLOBAL_CONTEXT_SETTINGS
from ...utils import print_version as _origin_print_version

print_version = partial(_origin_print_version, 'gchar.games.azurlane')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Utils with Azur Lane.")
def cli():
    pass  # pragma: no cover


@cli.command('update', help='Update the local index of characters.',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--timeout', '-t', 'timeout', type=int, default=5,
              help='Timeout of this update.', show_default=True)
@click.option('--maxcnt', '-n', 'maxcnt', type=int, default=None,
              help='Max count to crawler (only used for debugging and testing).', show_default=True)
@click.option('--output', '-o', 'output', type=click.Path(dir_okay=False), default=None,
              help='Output path of index file.', show_default=_INDEX_FILE)
def update(timeout: int, maxcnt: int, output: str):
    click.secho(f'Updating from {ROOT_SITE} ...', fg='yellow')
    _refresh_index(timeout=timeout, maxcnt=maxcnt, index_file=output)
    click.secho('Completed!', fg='green')


@cli.command('download', help='Download the index of characters from huggingface.')
def download():
    click.echo(click.style(f'Downloading from {ONLINE_INDEX_URL} ...', fg='yellow'))
    _download_from_huggingface()
    click.echo(click.style('Completed!', fg='green'))


if __name__ == '__main__':
    cli()
