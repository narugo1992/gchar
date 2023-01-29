from typing import Optional, Dict

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.status_codes import codes as _http_status_codes

_5xx = [val for val in _http_status_codes.keys() if val // 100 == 5]


def get_requests_session(max_retries: int = 3, headers: Optional[Dict[str, str]] = None) -> requests.Session:
    session = requests.session()
    retries = Retry(total=max_retries, backoff_factor=1,
                    status_forcelist=[500, 501, 502, 503, 504, 505, 506, 507, 509, 510, 511])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
        **dict(headers or {}),
    })

    return session
