from functools import partial

import click

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from .tag_matches import WallHavenTagMatcher
from .tags import WallHeavenTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.sankaku')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of wallhaven')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


WallHeavenTagCrawler.add_commands(cli)
WallHavenTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
