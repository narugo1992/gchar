from functools import partial
from typing import Optional

import click

from .games import _GAMES
from .index import _local_file, _save_tags_to_local, _online_tags_url
from ...utils import GLOBAL_CONTEXT_SETTINGS
from ...utils import print_version as _origin_print_version

print_version = partial(_origin_print_version, 'gchar.resources.danbooru')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Utils with Girls' Front-line.")
def cli():
    pass  # pragma: no cover


@cli.command('update', help='Update the local index of characters.',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--game', '-g', 'game', type=click.Choice([item for _, _, item in _GAMES]), required=True,
              help='Game to crawl danbooru tags.')
@click.option('--output', '-o', 'output', type=click.Path(dir_okay=False), default=None,
              help='Output path of index file.', show_default=None)
def update(game, output: Optional[str]):
    output = output or _local_file(game)
    click.secho('Updating from danbooru.donmai.us ...', fg='yellow')
    _save_tags_to_local(game, output)
    click.secho('Completed!', fg='green')


@cli.command('download', help='Download the index of characters from huggingface.')
@click.option('--game', '-g', 'game', type=click.Choice([item for _, _, item in _GAMES]), required=True,
              help='Game to crawl danbooru tags.')
def download(game):
    click.echo(click.style(f'Downloading from {_online_tags_url(game)} ...', fg='yellow'))
    print('The data should be downloaded here. TODO: implement this feature.')
    click.echo(click.style('Completed!', fg='green'))


if __name__ == '__main__':
    cli()  # pragma: no cover
