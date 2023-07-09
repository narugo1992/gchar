from functools import partial
from typing import List, Mapping, Any

import click
from waifuc.source import BaseDataSource, LolibooruSource

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.base.character import TagFeatureExtract
from zoo.resources.konachan.tag_matches import KonachanTagMatcher
from .konachan.tags import KonachanTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.lolibooru')


class LolibooruTagCrawler(KonachanTagCrawler):
    __max_workers__ = 4
    __sqlite_indices__ = ['id', 'name', 'post_count', 'tag_type', 'is_ambiguous']
    __site_url__ = 'https://lolibooru.moe'

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        return [
            {**item, 'id': int(item['id']), 'post_count': int(item['post_count'])}
            for item in KonachanTagCrawler.get_tags_json(self)
        ]


class LolibooruTagFeatureExtract(TagFeatureExtract):
    def get_datasource(self) -> BaseDataSource:
        return LolibooruSource([self.tag, 'solo'])


class LolibooruTagMatcher(KonachanTagMatcher):
    __tag_column__ = 'name'
    __count_column__ = 'post_count'
    __extra_filters__ = {'tag_type': 4}
    __site_name__ = 'lolibooru.moe'
    __tag_fe__ = LolibooruTagFeatureExtract


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of lolibooru')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


LolibooruTagCrawler.add_commands(cli)
LolibooruTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
