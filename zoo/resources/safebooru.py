from functools import partial

import click
from ditk import logging
from waifuc.source import BaseDataSource, SafebooruSource

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.base.character import TagFeatureExtract
from zoo.resources.danbooru.tag_matches import DanbooruTagMatcher
from .danbooru.tags import DanbooruTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.safebooru')


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
    crawler = DanbooruTagCrawler('https://safebooru.donmai.us')
    crawler.deploy_to_huggingface(repository, namespace, revision)


SafebooruTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
