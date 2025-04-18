import logging
import random
import time
from functools import lru_cache
from typing import Optional, Dict

import requests
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import RequestException

DEFAULT_TIMEOUT = 60  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    """
    Custom HTTP adapter that sets a default timeout for requests.

    Inherits from `HTTPAdapter`.

    Usage:
    - Create an instance of `TimeoutHTTPAdapter` and pass it to a `requests.Session` object's `mount` method.

    Example:
    ```python
    session = requests.Session()
    adapter = TimeoutHTTPAdapter(timeout=10)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    ```

    :param timeout: The default timeout value in seconds. (default: 10)
    :type timeout: int
    """

    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        """
        Sends a request with the provided timeout value.

        :param request: The request to send.
        :type request: PreparedRequest
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :returns: The response from the request.
        :rtype: Response
        """
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def get_requests_session(max_retries: int = 5, timeout: int = DEFAULT_TIMEOUT,
                         headers: Optional[Dict[str, str]] = None, session: Optional[requests.Session] = None) \
        -> requests.Session:
    """
    Returns a requests Session object configured with retry and timeout settings.

    :param max_retries: The maximum number of retries. (default: 5)
    :type max_retries: int
    :param timeout: The default timeout value in seconds. (default: 10)
    :type timeout: int
    :param headers: Additional headers to be added to the session. (default: None)
    :type headers: Optional[Dict[str, str]]
    :param session: An existing requests Session object to use. If not provided, a new Session object is created. (default: None)
    :type session: Optional[requests.Session]
    :returns: The requests Session object.
    :rtype: requests.Session
    """
    session = session or requests.session()
    retries = Retry(
        total=max_retries, backoff_factor=1,
        status_forcelist=[413, 429, 500, 501, 502, 503, 504, 505, 506, 507, 509, 510, 511],
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
    )
    adapter = TimeoutHTTPAdapter(max_retries=retries, timeout=timeout, pool_connections=32, pool_maxsize=32)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        "User-Agent": get_random_ua(),
        **dict(headers or {}),
    })

    return session


def srequest(session: requests.Session, method, url, *, max_retries: int = 5,
             sleep_time: float = 5.0, raise_for_status: bool = True, **kwargs) -> requests.Response:
    """
    Send a request using the provided session object with retry and timeout settings.

    :param session: The requests Session object to use for the request.
    :type session: requests.Session
    :param method: The HTTP method for the request.
    :type method: str
    :param url: The URL for the request.
    :type url: str
    :param max_retries: The maximum number of retries. (default: 5)
    :type max_retries: int
    :param sleep_time: The sleep time between retries in seconds. (default: 5.0)
    :type sleep_time: float
    :param raise_for_status: Whether to raise an exception for non-successful response status codes. (default: True)
    :type raise_for_status: bool
    :param kwargs: Additional keyword arguments for the request.
    :type kwargs: dict
    :returns: The response from the request.
    :rtype: requests.Response
    """
    if isinstance(session, (list, tuple)):
        session = random.choice(session)

    resp = None
    for _ in range(max_retries):
        try:
            resp = session.request(method, url, **kwargs)
            if resp.status_code in {429}:
                resp.raise_for_status()
        except RequestException as err:
            logging.error(f'Request error - {err!r}')
            time.sleep(sleep_time)
        else:
            break
    assert resp is not None, f'Request failed for {max_retries} time(s).'
    if raise_for_status:
        resp.raise_for_status()

    return resp


def sget(session: requests.Session, url, *, max_retries: int = 5,
         sleep_time: float = 5.0, raise_for_status: bool = True, **kwargs) -> requests.Response:
    """
    Send a GET request using the provided session object with retry and timeout settings.

    :param session: The requests Session object to use for the request.
    :type session: requests.Session
    :param url: The URL for the request.
    :type url: str
    :param max_retries: The maximum number of retries. (default: 5)
    :type max_retries: int
    :param sleep_time: The sleep time between retries in seconds. (default: 5.0)
    :type sleep_time: float
    :param raise_for_status: Whether to raise an exception for non-successful response status codes. (default: True)
    :type raise_for_status: bool
    :param kwargs: Additional keyword arguments for the request.
    :type kwargs: dict
    :returns: The response from the request.
    :rtype: requests.Response
    """
    return srequest(
        session, 'GET', url,
        max_retries=max_retries,
        sleep_time=sleep_time,
        raise_for_status=raise_for_status,
        **kwargs,
    )


@lru_cache()
def _ua_pool():
    software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.EDGE.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.MACOS.value]

    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1000)
    return user_agent_rotator


def get_random_ua():
    return _ua_pool().get_random_user_agent()


@lru_cache()
def _ua_mobile_pool():
    software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.SAFARI.value]
    operating_systems = [OperatingSystem.ANDROID.value, OperatingSystem.IOS.value]

    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1000)
    return user_agent_rotator


def get_random_mobile_ua():
    return _ua_mobile_pool().get_random_user_agent()
