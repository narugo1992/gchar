import datetime
import os
import shutil
from contextlib import contextmanager
from typing import Optional, ContextManager, List

from ditk import logging
from huggingface_hub import HfApi, CommitOperationAdd


class HuggingfaceDeployable:

    @contextmanager
    def with_files(self, **kwargs) -> ContextManager[List[str]]:
        raise NotImplementedError

    def get_default_namespace(self, **kwargs) -> str:
        raise NotImplementedError

    def export_to_directory(self, directory: str, namespace: Optional[str] = None, **kwargs):
        namespace = namespace or self.get_default_namespace(**kwargs)
        with self.with_files(**kwargs) as files:
            for file in files:
                dst_file = os.path.join(directory, namespace, os.path.basename(file))
                dst_dir = os.path.dirname(dst_file)
                if dst_dir:
                    os.makedirs(dst_dir, exist_ok=True)
                shutil.copyfile(file, dst_file)

    def deploy_to_huggingface(self, repository: str,
                              namespace: Optional[str] = None, revision: str = 'main', **kwargs):
        namespace = namespace or self.get_default_namespace(**kwargs)
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
