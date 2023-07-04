from functools import partial

import click
from ditk import logging

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from zoo.resources.rule34.tag_matches import Rule34TagMatcher
from .rule34.tags import Rule34TagCrawler

print_version = partial(_origin_print_version, 'zoo.resources.hypnohub')


class HypnohubTagMatcher(Rule34TagMatcher):
    __site_name__ = 'hypnohub.net'


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of hypnohub')
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
    crawler = Rule34TagCrawler('https://hypnohub.net')
    crawler.deploy_to_huggingface(repository, namespace, revision)


HypnohubTagMatcher.add_commands(cli)

if __name__ == '__main__':
    cli()
