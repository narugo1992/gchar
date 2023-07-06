from functools import partial

import click
from ditk import logging

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from .tag_matches import GelbooruTagMatcher
from .tags import GelbooruTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.danbooru')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of danbooru')
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
    crawler = GelbooruTagCrawler()
    crawler.deploy_to_huggingface(repository, namespace, revision)


@cli.command('tags_export', help='Crawl tags database to local',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--output_directory', '-o', 'output_directory', type=str, default='.',
              help='Output directory', show_default=True)
@click.option('--namespace', '-n', 'namespace', type=str, default=None,
              help='Namespace to publish to, default to site\' host.', show_default=True)
def tags_export(output_directory: str, namespace: str):
    logging.try_init_root(logging.INFO)
    crawler = GelbooruTagCrawler()
    crawler.export_to_directory(output_directory, namespace)


GelbooruTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
