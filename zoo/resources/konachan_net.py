from functools import partial

import click
from ditk import logging
from waifuc.source import BaseDataSource, KonachanNetSource

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.base.character import TagFeatureExtract
from zoo.resources.konachan.tag_matches import KonachanTagMatcher
from .konachan.tags import KonachanDirectTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.konachan_net')


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
    crawler = KonachanDirectTagCrawler('https://konachan.net')
    crawler.deploy_to_huggingface(repository, namespace, revision)


KonachanNetTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
