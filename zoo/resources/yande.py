from functools import partial

import click
from waifuc.source import YandeSource, BaseDataSource

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.base.character import TagFeatureExtract
from .konachan.tag_matches import KonachanTagMatcher
from .konachan.tags import KonachanTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.yande')


class YandeTagCrawler(KonachanTagCrawler):
    __site_url__ = 'https://yande.re'


class YandeTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return YandeSource([self.tag])


class YandeTagMatcher(KonachanTagMatcher):
    __site_name__ = 'yande.re'
    __tag_fe__ = YandeTagFeatureExtract


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of yande')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


YandeTagCrawler.add_commands(cli)
YandeTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
