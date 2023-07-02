import datetime
import json
import os
import time
from functools import partial

import click
from ditk import logging
from hbutils.system import TemporaryDirectory
from huggingface_hub import HfApi, CommitOperationAdd

from gchar.utils import GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version
from .tags import crawl_tags_to_json

print_version = partial(_origin_print_version, 'gchar.resources.danbooru')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Crawler of anime-pictures.net')
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass  # pragma: no cover


@cli.command('tags', help='Crawl tags database',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--repository', '-r', 'repository', type=str, default='deepghs/site_tags',
              help='Repository to publish to.', show_default=True)
@click.option('--namespace', '-n', 'namespace', type=str, default='anime-pictures.net',
              help='Namespace to publish to.', show_default=True)
@click.option('--revision', '-R', 'revision', type=str, default='main',
              help='Revision for pushing the model.', show_default=True)
def tags(repository: str, namespace: str, revision: str):
    hf_client = HfApi(token=os.environ['HF_TOKEN'])
    hf_client.create_repo(repo_id=repository, repo_type='dataset', exist_ok=True)

    data = crawl_tags_to_json()
    with TemporaryDirectory() as td:
        json_file = os.path.join(td, 'tags.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'data': data,
                'last_updated': time.time(),
            }, f, indent=4, ensure_ascii=False, sort_keys=True)

        current_time = datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
        commit_message = f"Publish {namespace}\' tags, on {current_time}"
        logging.info(f'Publishing {namespace!r}\'s tags to repository {repository!r} ...')
        hf_client.create_commit(
            repository,
            [CommitOperationAdd(
                path_in_repo=f'{namespace}/tags.json',
                path_or_fileobj=json_file,
            )],
            commit_message=commit_message,
            repo_type='dataset',
            revision=revision,
        )


if __name__ == '__main__':
    cli()
