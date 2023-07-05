from functools import partial
from typing import List, Mapping, Any

import click
from ditk import logging

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.konachan.tag_matches import KonachanTagMatcher
from .konachan.tags import KonachanTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.lolibooru')


class LolibooruTagCrawler(KonachanTagCrawler):
    __max_workers__ = 4
    __sqlite_indices__ = ['id', 'name', 'post_count', 'tag_type', 'is_ambiguous']

    def get_tags_json(self) -> List[Mapping[str, Any]]:
        return [
            {**item, 'id': int(item['id']), 'post_count': int(item['post_count'])}
            for item in KonachanTagCrawler.get_tags_json(self)
        ]


class LolibooruTagMatcher(KonachanTagMatcher):
    __tag_column__ = 'name'
    __count_column__ = 'post_count'
    __extra_filters__ = {'tag_type': 4}
    __site_name__ = 'lolibooru.moe'


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of lolibooru')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


@cli.command('tags', help='Crawl tags database',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--repository', '-r', 'repository', type=str, default='deepghs/site_tags',
              help='Repository to publish to.', show_default=True)
@click.option('--namespace', '-n', 'namespace', type=str, default=None,
              help='Namespace to publish to, default to site\' host.', show_default=True)
@click.option('--revision', '-R', 'revision', type=str, default='main',
              help='Revision for pushing the model.', show_default=True)
def tags(repository: str, namespace: str, revision: str):
    logging.try_init_root(logging.INFO)
    crawler = LolibooruTagCrawler('https://lolibooru.moe')
    crawler.deploy_to_huggingface(repository, namespace, revision)


LolibooruTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
