from functools import partial

import click
from ditk import logging

from gchar.games import list_available_game_names
from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from .konachan.tag_matches import KonachanTagMatcher
from .konachan.tags import KonachanTagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.yande')


class YandeTagMatcher(KonachanTagMatcher):
    __site_name__ = 'yande.re'


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of yande')
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
    crawler = KonachanTagCrawler('https://yande.re')
    crawler.deploy_to_huggingface(repository, namespace, revision)


@cli.command('chtags', help='Match tags of characters from database.',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--repository', '-r', 'repository', type=str, default='deepghs/game_characters',
              help='Repository to publish to.', show_default=True)
@click.option('--namespace', '-n', 'namespace', type=str, default=None,
              help='Namespace to publish to, default to game name.', show_default=True)
@click.option('--revision', '-R', 'revision', type=str, default='main',
              help='Revision for pushing the model.', show_default=True)
@click.option('--game', '-g', 'game_name', type=click.Choice(list_available_game_names()), required=True,
              help='Game to deploy.', show_default=True)
def chtags(repository: str, namespace: str, revision: str, game_name: str):
    logging.try_init_root(logging.INFO)
    matcher = YandeTagMatcher(game_name)
    matcher.deploy_to_huggingface(repository, namespace, revision)


if __name__ == '__main__':
    cli()
