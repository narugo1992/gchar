from functools import partial

import click
from waifuc.source import BaseDataSource, SafebooruSource

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.base.character import TagFeatureExtract
from zoo.resources.danbooru.tag_matches import DanbooruTagMatcher
from .danbooru.tags import DanbooruTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.safebooru')


class SafebooruTagCrawler(DanbooruTagCrawler):
    __site_url__ = 'https://safebooru.donmai.us'


class SafebooruTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return SafebooruSource([self.tag, 'solo'])


class SafebooruTagMatcher(DanbooruTagMatcher):
    __site_name__ = 'safebooru.donmai.us'
    __tag_fe__ = SafebooruTagFeatureExtract


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of safebooru')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


SafebooruTagCrawler.add_commands(cli)
SafebooruTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
