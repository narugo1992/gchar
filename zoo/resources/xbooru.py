from functools import partial

import click
from waifuc.source import BaseDataSource, XbooruSource

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.base.character import TagFeatureExtract
from .rule34.tag_matches import Rule34TagMatcher
from .rule34.tags import Rule34TagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.xbooru')


class XbooruTagCrawler(Rule34TagCrawler):
    __site_url__ = 'https://xbooru.com'


class XbooruTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return XbooruSource([self.tag])


class XbooruTagMatcher(Rule34TagMatcher):
    __site_name__ = 'xbooru.com'
    __tag_fe__ = XbooruTagFeatureExtract


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of xbooru')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


XbooruTagCrawler.add_commands(cli)
XbooruTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
