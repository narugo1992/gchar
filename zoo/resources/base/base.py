import datetime
import os
from contextlib import contextmanager
from typing import Optional, ContextManager, List

from ditk import logging
from huggingface_hub import HfApi, CommitOperationAdd


class HuggingfaceDeployable:
    __default_repository__: str

    @contextmanager
    def with_files(self, **kwargs) -> ContextManager[List[str]]:
        raise NotImplementedError

    def _get_default_namespace(self, **kwargs) -> str:
        raise NotImplementedError

    def deploy_to_huggingface(self, repository: Optional[str] = None,
                              namespace: Optional[str] = None, revision: str = 'main', **kwargs):
        repository = repository or self.__default_repository__
        namespace = namespace or self._get_default_namespace(**kwargs)
        logging.info(f'Initializing repository {repository!r} ...')
        hf_client = HfApi(token=os.environ['HF_TOKEN'])
        hf_client.create_repo(repo_id=repository, repo_type='dataset', exist_ok=True)

        with self.with_files(**kwargs) as files:
            current_time = datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
            commit_message = f"Publish {namespace}\'s data, on {current_time}"
            logging.info(f'Publishing {namespace}\'s data to repository {repository!r} ...')
            hf_client.create_commit(
                repository,
                [
                    CommitOperationAdd(
                        path_in_repo=f'{namespace}/{os.path.basename(file)}',
                        path_or_fileobj=file,
                    ) for file in files
                ],
                commit_message=commit_message,
                repo_type='dataset',
                revision=revision,
            )
