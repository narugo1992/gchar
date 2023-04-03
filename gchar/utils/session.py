import random
import time
from typing import Optional, Dict

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import RequestException

DEFAULT_TIMEOUT = 10  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def get_requests_session(max_retries: int = 5, timeout: int = DEFAULT_TIMEOUT,
                         headers: Optional[Dict[str, str]] = None) -> requests.Session:
    session = requests.session()
    retries = Retry(
        total=max_retries, backoff_factor=1,
        # status_forcelist=[500, 501, 502, 503, 504, 505, 506, 507, 509, 510, 511],
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    adapter = TimeoutHTTPAdapter(max_retries=retries, timeout=timeout)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        **dict(headers or {}),
    })

    return session


def srequest(session: requests.Session, method, url, *, max_retries: int = 5,
             sleep_time: float = 5.0, raise_for_status: bool = True, **kwargs) -> requests.Response:
    if isinstance(session, (list, tuple)):
        session = random.choice(session)

    resp = None
    for _ in range(max_retries):
        try:
            resp = session.request(method, url, **kwargs)
        except RequestException:
            time.sleep(sleep_time)
        else:
            break
    assert resp is not None
    if raise_for_status:
        resp.raise_for_status()

    return resp


def sget(session: requests.Session, url, *, max_retries: int = 5,
         sleep_time: float = 5.0, raise_for_status: bool = True, **kwargs) -> requests.Response:
    return srequest(
        session, 'GET', url,
        max_retries=max_retries,
        sleep_time=sleep_time,
        raise_for_status=raise_for_status,
        **kwargs,
    )
