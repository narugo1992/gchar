from functools import partial

import click
from ditk import logging

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.zerochan.parents import deploy_generic_character_ds_parent
from .characters import deploy_generic_character_ds
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


@cli.command('chars', context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawl offline character information.')
@click.option('-r', '--repository', 'repository', type=str, default='deepghs/generic_character_ds',
              help='Repository to deploy offline aliases.', show_default=True)
@click.option('-f', '--file_in_repo', 'file_in_repo', type=str, default='zerochan.net.json',
              help='File in repository.', show_default=True)
@click.option('-n', '--max_workers', 'max_workers', type=int, default=4,
              help='Workers to crawl the information.', show_default=True)
@click.option('--min_strict', 'min_strict', type=int, default=3,
              help='Min strict images of the characters.', show_default=True)
def chars(repository: str, file_in_repo: str, max_workers: int, min_strict: int):
    logging.try_init_root(logging.INFO)
    deploy_generic_character_ds(repository, file_in_repo, min_strict, max_workers)


@cli.command('parents', context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawl offline parent information.')
@click.option('-r', '--repository', 'repository', type=str, default='deepghs/generic_character_ds',
              help='Repository to deploy offline aliases.', show_default=True)
@click.option('-f', '--file_in_repo', 'file_in_repo', type=str, default='zerochan.net_parents.json',
              help='File in repository.', show_default=True)
@click.option('-n', '--max_workers', 'max_workers', type=int, default=4,
              help='Workers to crawl the information.', show_default=True)
@click.option('--min_strict', 'min_strict', type=int, default=3,
              help='Min strict images of the characters.', show_default=True)
@click.option('--min_character_count', 'min_character_count', type=int, default=5,
              help='Min character count of each parent tag.', show_default=True)
def parents(repository: str, file_in_repo: str, max_workers: int, min_strict: int, min_character_count: int):
    logging.try_init_root(logging.INFO)
    deploy_generic_character_ds_parent(repository, file_in_repo, min_strict, min_character_count, max_workers)


ZerochanTagCrawler.add_commands(cli)
ZerochanTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
