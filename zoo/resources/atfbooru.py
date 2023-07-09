from functools import partial

import click
from waifuc.source import ATFBooruSource, BaseDataSource

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.base.character import TagFeatureExtract
from .danbooru.tag_matches import DanbooruTagMatcher
from .danbooru.tags import DanbooruTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.atfbooru')


class ATFBooruTagCrawler(DanbooruTagCrawler):
    __site_url__ = 'https://booru.allthefallen.moe'


class ATFBooruTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return ATFBooruSource([self.tag])


class ATFBooruTagMatcher(DanbooruTagMatcher):
    __site_name__ = 'booru.allthefallen.moe'
    __tag_fe__ = ATFBooruTagFeatureExtract


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of atfbooru')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


ATFBooruTagCrawler.add_commands(cli)
ATFBooruTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
