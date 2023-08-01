import json
import os
from functools import lru_cache
from json import JSONDecodeError
from typing import Optional, Dict, Union, List

import requests
from huggingface_hub import hf_hub_download

from gchar.utils import get_requests_session
from gchar.utils.session import DEFAULT_TIMEOUT

REMOTE_PIXIV_SESSION_REPO = 'REMOTE_PIXIV_SESSION_REPO'


@lru_cache()
def _get_remote_session_index_raw():
    with open(hf_hub_download(os.environ[REMOTE_PIXIV_SESSION_REPO], filename='index.json',
                              repo_type='dataset', token=os.environ.get('HF_TOKEN')), 'r', encoding='utf-8') as f:
        files = json.load(f)

    items = []
    for session_file in files:
        with open(hf_hub_download(os.environ[REMOTE_PIXIV_SESSION_REPO], filename=session_file,
                                  repo_type='dataset', token=os.environ.get('HF_TOKEN')), 'r', encoding='utf-8') as f:
            items.append(json.load(f))

    return items


def get_pixiv_sessions(max_retries: int = 5, timeout: int = DEFAULT_TIMEOUT,
                       headers: Optional[Dict[str, str]] = None, **kwargs) -> List[requests.Session]:
    _ = kwargs
    sessions = []
    for session_item in _get_remote_session_index_raw():
        session = get_requests_session(max_retries, timeout, headers)
        session.cookies.update(session_item['cookies'])
        sessions.append(session)

    return sessions


def get_pixiv_refresh_token() -> str:
    for session_item in _get_remote_session_index_raw():
        return session_item['refresh_token']


def _is_single_pixiv_session_okay(session: requests.Session) -> bool:
    resp = session.get(
        'https://www.pixiv.net/rpc/notify_count.php?'
        'op=count_unread&lang=zh&version=9c834eede9446d61102731a4be356cd0f1090e84',
        headers={
            'Referer': f'https://www.pixiv.net/dashboard/works',
        }
    )
    if resp.ok:
        try:
            _ = resp.json()['popboard']
        except (JSONDecodeError, KeyError):
            return False
        else:
            return True
    else:
        return False


def is_pixiv_session_okay(session: Union[requests.Session, List[requests.Session]]) -> bool:
    if not isinstance(session, (list, tuple)):
        sessions = [session]
    else:
        sessions = session

    for s in sessions:
        if not _is_single_pixiv_session_okay(s):
            return False

    return True
