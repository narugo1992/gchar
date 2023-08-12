from functools import partial

import click

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from .tags import PixivEnTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.pixiv')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Utils with pixiv resources.")
def cli():
    pass  # pragma: no cover


PixivEnTagCrawler.add_commands(cli)

if __name__ == '__main__':
    cli()  # pragma: no cover
