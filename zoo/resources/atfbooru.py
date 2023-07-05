from functools import partial

import click
from ditk import logging
from waifuc.source import ATFBooruSource, BaseDataSource

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.base.character import TagFeatureExtract
from .danbooru.tag_matches import DanbooruTagMatcher
from .danbooru.tags import DanbooruTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.atfbooru')


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
    crawler = DanbooruTagCrawler('https://booru.allthefallen.moe')
    crawler.deploy_to_huggingface(repository, namespace, revision)


ATFBooruTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
