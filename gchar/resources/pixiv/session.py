import json
import os
from functools import lru_cache
from json import JSONDecodeError
from typing import Optional, Dict

import requests

from ...utils import get_requests_session
from ...utils.session import DEFAULT_TIMEOUT

REMOTE_PIXIV_SESSION_URL = 'REMOTE_PIXIV_SESSION_URL'


@lru_cache()
def _get_remote_session_raw():
    remote_url = os.environ.get(REMOTE_PIXIV_SESSION_URL, None)
    resp = requests.get(remote_url)
    resp.raise_for_status()
    return json.loads(resp.text)


@lru_cache()
def _get_remote_session_cookies() -> Dict[str, str]:
    return _get_remote_session_raw()['cookies']


@lru_cache()
def _get_remote_refresh_token():
    return _get_remote_session_raw()['refresh_token']


def get_pixiv_session(max_retries: int = 5, timeout: int = DEFAULT_TIMEOUT,
                      headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Session:
    _ = kwargs
    session = get_requests_session(max_retries, timeout, headers)
    session.cookies.update(_get_remote_session_cookies())

    return session


def is_pixiv_session_okay(session: requests.Session) -> bool:
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
