from functools import partial

import click
from waifuc.source import BaseDataSource, KonachanNetSource

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.base.character import TagFeatureExtract
from zoo.resources.konachan.tag_matches import KonachanTagMatcher
from .konachan.tags import KonachanDirectTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.konachan_net')


class KonachanNetDirectTagCrawler(KonachanDirectTagCrawler):
    __site_url__ = 'https://konachan.net'


class KonachanNetTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return KonachanNetSource([self.tag])


class KonachanNetTagMatcher(KonachanTagMatcher):
    __site_name__ = 'konachan.net'
    __tag_fe__ = KonachanNetTagFeatureExtract


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of konachan_net')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


KonachanNetDirectTagCrawler.add_commands(cli)
KonachanNetTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
