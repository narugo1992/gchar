import os
import time
from hashlib import sha256, sha1

import requests
from huggingface_hub import hf_hub_url, HfApi
from huggingface_hub.utils import HfHubHTTPError


def hf_resource_check(local_filename, repo_id: str, file_in_repo: str, repo_type='model', revision='main',
                      chunk_for_hash: int = 1 << 20):
    response = requests.post(
        f"https://huggingface.co/api/{repo_type}s/{repo_id}/paths-info/{revision}",
        json={"paths": [file_in_repo]},
    )
    metadata = response.json()[0]
    if 'lfs' in metadata:
        is_lfs, oid, filesize = True, metadata['lfs']['oid'], metadata['lfs']['size']
    else:
        is_lfs, oid, filesize = False, metadata['oid'], metadata['size']

    if filesize != os.path.getsize(local_filename):
        return False

    if is_lfs:
        sha = sha256()
    else:
        sha = sha1()
        sha.update(f'blob {filesize}\0'.encode('utf-8'))
    with open(local_filename, 'rb') as f:
        # make sure the big files will not cause OOM
        while True:
            data = f.read(chunk_for_hash)
            if not data:
                break
            sha.update(data)

    return sha.hexdigest() == oid


def hf_need_upload(local_filename, repo_id: str, file_in_repo: str, repo_type='model', revision='main',
                   chunk_for_hash: int = 1 << 20, **kwargs):
    _ = kwargs
    if requests.head(hf_hub_url(repo_id, file_in_repo, repo_type=repo_type, revision=revision)).ok:
        return not hf_resource_check(local_filename, repo_id, file_in_repo, repo_type, revision, chunk_for_hash)
    else:
        return True


def hf_upload_file_if_need(api: HfApi, local_filename, path_in_repo: str, repo_id: str,
                           max_attempts: int = 10, wait_before_retry: int = 1, **kwargs):
    attempt = 0
    while True:
        attempt += 1
        try:
            if hf_need_upload(local_filename, repo_id, path_in_repo, **kwargs):
                api.upload_file(
                    path_or_fileobj=local_filename,
                    path_in_repo=path_in_repo,
                    repo_id=repo_id,
                    **kwargs
                )
        except HfHubHTTPError as error:
            if error.response.status_code != 412 or attempt > max_attempts:
                raise
            time.sleep(wait_before_retry)
        else:
            break
