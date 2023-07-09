from functools import partial

import click

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.sankaku.tag_matches import SankakuTagMatcher
from .tags import SankakuTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.sankaku')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of sankaku')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


SankakuTagCrawler.add_commands(cli)
SankakuTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
