from functools import partial

import click

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from .tag_matches import GelbooruTagMatcher
from .tags import GelbooruTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.danbooru')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of danbooru')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


GelbooruTagCrawler.add_commands(cli)
GelbooruTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
