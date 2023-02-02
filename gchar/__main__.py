from functools import partial

import click
from tqdm.auto import tqdm

from .games.arknights.index import _download_from_huggingface as _arknights_download
from .games.azurlane.index import _download_from_huggingface as _azurlane_download
from .games.fgo.index import _download_from_huggingface as _fgo_download
from .games.genshin.index import _download_from_huggingface as _genshin_download
from .games.girlsfrontline.index import _download_from_huggingface as _girlsfrontline_download
from .resources.danbooru.index import _download_from_huggingface as _download_danbooru_tags
from .utils import GLOBAL_CONTEXT_SETTINGS
from .utils import print_version as _origin_print_version

print_version = partial(_origin_print_version, 'gchar')

GAMES = ['fgo', 'arknights', 'azurlane', 'genshin', 'girlsfrontline']
DOWNLOAD_FUNCS = {
    'fgo': _fgo_download,
    'arknights': _arknights_download,
    'genshin': _genshin_download,
    'azurlane': _azurlane_download,
    'girlsfrontline': _girlsfrontline_download,
}


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Utils with gchar.")
def cli():
    pass  # pragma: no cover


@cli.command('update', help='Download the newest data from huggingface.')
@click.option('--game', '-g', 'game', type=click.Choice(GAMES), default=None,
              help='Update data of given game from huggingface. '
                   'All games will be updated when not given.', show_default=True)
def update(game):
    if not game:
        games = GAMES
    else:
        games = [game]

    games_tqdm = tqdm(games)
    for _gitem in games_tqdm:
        games_tqdm.set_description(_gitem)

        click.echo(click.style(f'Downloading characters of {_gitem} ...', fg='yellow'))
        DOWNLOAD_FUNCS[_gitem]()
        click.echo(click.style(f'Downloading danbooru tags of {_gitem} ...', fg='yellow'))
        _download_danbooru_tags(_gitem)

    click.echo(click.style('Completed!', fg='green'))


if __name__ == '__main__':
    cli()  # pragma: no cover
