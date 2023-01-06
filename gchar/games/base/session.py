from typing import Optional, Dict

import requests
from requests.adapters import HTTPAdapter


def get_requests_session(max_retries: int = 3, headers: Optional[Dict[str, str]] = None) -> requests.Session:
    session = requests.session()
    session.mount('http://', HTTPAdapter(max_retries=max_retries))
    session.mount('https://', HTTPAdapter(max_retries=max_retries))
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
        **dict(headers),
    })

    return session
