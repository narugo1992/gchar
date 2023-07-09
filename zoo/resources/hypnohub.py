from functools import partial

import click
from waifuc.source import HypnoHubSource, BaseDataSource

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.base.character import TagFeatureExtract
from zoo.resources.rule34.tag_matches import Rule34TagMatcher
from .rule34.tags import Rule34TagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.hypnohub')


class HypnoHubTagCrawler(Rule34TagCrawler):
    __site_url__ = 'https://hypnohub.net'


class HypnohubTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return HypnoHubSource([self.tag])


class HypnohubTagMatcher(Rule34TagMatcher):
    __site_name__ = 'hypnohub.net'
    __tag_fe__ = HypnohubTagFeatureExtract


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of hypnohub')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


HypnoHubTagCrawler.add_commands(cli)
HypnohubTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
