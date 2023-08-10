from functools import partial

import click
from ditk import logging

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from .tag_aliases import deploy_alias_offline
from .tag_matches import ZerochanTagMatcher
from .tags import ZerochanTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.zerochan')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of zerochan')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


@cli.command('alias', context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawl offline alias information.')
@click.option('-r', '--repository', 'repository', type=str, default='deepghs/site_tags',
              help='Repository to deploy offline aliases.', show_default=True)
@click.option('-f', '--file_in_repo', 'file_in_repo', type=str, default='zerochan.net/alias_offline.csv',
              help='File in repository.', show_default=True)
@click.option('-n', '--max_workers', 'max_workers', type=int, default=4,
              help='Workers to crawl the information.', show_default=True)
def alias(repository: str, file_in_repo: str, max_workers: int):
    logging.try_init_root(logging.INFO)
    deploy_alias_offline(repository, file_in_repo, max_workers)


ZerochanTagCrawler.add_commands(cli)
ZerochanTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
