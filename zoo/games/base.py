import datetime
import json
import os.path
import time
from contextlib import contextmanager
from functools import partial
from typing import Optional, Iterator, Any, ContextManager, List

import click
import requests
from ditk import logging
from hbutils.system import TemporaryDirectory
from huggingface_hub import HfApi, CommitOperationAdd

from gchar.utils import get_requests_session, GLOBAL_CONTEXT_SETTINGS
from gchar.utils import print_version as _origin_print_version


class GameIndexer:
    __game_name__ = 'default'
    __root_website__ = 'https://root.website.com'

    def _create_session(self, timeout: int = 5, retries: int = 3, headers=None, **kwargs):
        _ = kwargs
        return get_requests_session(max_retries=retries, timeout=timeout, headers=headers)

    def _crawl_index_from_online(self, session: requests.Session, maxcnt: Optional[int] = None,
                                 **kwargs) -> Iterator[Any]:
        raise NotImplementedError

    @contextmanager
    def crawl_index_to_local(self, maxcnt: Optional[int] = None, timeout: int = 5, retries: int = 3, **kwargs) \
            -> ContextManager[List[str]]:
        session = self._create_session(timeout, retries, **kwargs)
        data = list(self._crawl_index_from_online(session, maxcnt, **kwargs))
        with TemporaryDirectory() as td:
            index_file = os.path.join(td, 'index.json')
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'data': data,
                    'last_updated': time.time(),
                }, f, indent=4, ensure_ascii=False)

            yield [index_file]

    def deploy_to_huggingface(self, repository: str = 'deepghs/game_characters', revision: str = 'main',
                              maxcnt: Optional[int] = None, timeout: int = 5, retries: int = 3, **kwargs):
        logging.info(f'Initializing repository {repository!r} ...')
        hf_client = HfApi(token=os.environ['HF_TOKEN'])
        hf_client.create_repo(repo_id=repository, repo_type='dataset', exist_ok=True)

        with self.crawl_index_to_local(maxcnt, timeout, retries, **kwargs) as files:
            current_time = datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
            commit_message = f"Publish {self.__game_name__}\'s character data, on {current_time}"
            logging.info(f'Publishing {self.__game_name__}\'s character data to repository {repository!r} ...')
            hf_client.create_commit(
                repository,
                [
                    CommitOperationAdd(
                        path_in_repo=f'{self.__game_name__}/{os.path.basename(file)}',
                        path_or_fileobj=file,
                    ) for file in files
                ],
                commit_message=commit_message,
                repo_type='dataset',
                revision=revision,
            )

    def get_cli(self):
        print_version = partial(_origin_print_version, self.__class__.__module__)

        @click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS},
                     help=f"Game character data indexer of {self.__game_name__}.")
        @click.option('-v', '--version', is_flag=True,
                      callback=print_version, expose_value=False, is_eager=True)
        def cli():
            pass  # pragma: no cover

        @cli.command('index', help='Index the game characters onto huggingface.',
                     context_settings={**GLOBAL_CONTEXT_SETTINGS})
        @click.option('--timeout', '-t', 'timeout', type=int, default=5,
                      help='Timeout of this update.', show_default=True)
        @click.option('--maxcnt', '-n', 'maxcnt', type=int, default=None,
                      help='Max count to crawler (only used for debugging and testing).', show_default=True)
        @click.option('--repository', '-r', 'repository', type=str, default='deepghs/game_characters',
                      help='Repository to publish to.', show_default=True)
        @click.option('--revision', '-R', 'revision', type=str, default='main',
                      help='Revision for pushing the model.', show_default=True)
        def index(timeout: int, maxcnt: Optional[int], repository: str, revision: str):
            logging.try_init_root(logging.INFO)
            self.deploy_to_huggingface(repository, revision, maxcnt, timeout)

        return cli
