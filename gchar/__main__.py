import re
from datetime import date
from functools import partial
from itertools import chain

import click
from tqdm.auto import tqdm

from .games.arknights.index import INDEXER as ARKNIGHTS_INDEXER
from .games.azurlane.index import INDEXER as AZURLANE_INDEXER
from .games.fgo.index import INDEXER as FGO_INDEX
from .games.genshin.index import INDEXER as GENSHIN_INDEXER
from .games.girlsfrontline.index import INDEXER as GIRLSFRONTLINE_INDEXER
from .games.neuralcloud.index import INDEXER as NEURALCLOUD_INDEXER
from .resources.danbooru.index import _download_from_huggingface as _download_danbooru_tags
from .resources.pixiv.keyword import _download_pixiv_names_for_game, _download_pixiv_characters_for_game, \
    _download_pixiv_alias_for_game
from .utils import GLOBAL_CONTEXT_SETTINGS
from .utils import print_version as _origin_print_version

print_version = partial(_origin_print_version, 'gchar')

GAMES = ['fgo', 'arknights', 'azurlane', 'genshin', 'girlsfrontline', 'neuralcloud']
DOWNLOAD_FUNCS = {
    'fgo': partial(FGO_INDEX.download_index_from_online, force=True),
    'arknights': partial(ARKNIGHTS_INDEXER.download_index_from_online, force=True),
    'genshin': partial(GENSHIN_INDEXER.download_index_from_online, force=True),
    'azurlane': partial(AZURLANE_INDEXER.download_index_from_online, force=True),
    'girlsfrontline': partial(GIRLSFRONTLINE_INDEXER.download_index_from_online, force=True),
    'neuralcloud': partial(NEURALCLOUD_INDEXER.download_index_from_online, force=True),
}


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Utils with gchar.")
def cli():
    pass  # pragma: no cover


SCHEDULE_TABLE = [
    ('fgo', 'girlsfrontline', 'arknights'),
    ('azurlane', 'genshin', 'neuralcloud'),
]
for name in chain(*SCHEDULE_TABLE):
    assert name in GAMES, f'Name {name!r} not in games.'


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
        click.echo(click.style(f'Downloading pixiv alias of {_gitem} ...', fg='yellow'))
        _download_pixiv_alias_for_game(_gitem)
        click.echo(click.style(f'Downloading pixiv names of {_gitem} ...', fg='yellow'))
        _download_pixiv_names_for_game(_gitem)
        click.echo(click.style(f'Downloading pixiv characters of {_gitem} ...', fg='yellow'))
        _download_pixiv_characters_for_game(_gitem)

    click.echo(click.style('Completed!', fg='green'))


if __name__ == '__main__':
    cli()  # pragma: no cover
