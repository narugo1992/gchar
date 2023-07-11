import os
import os.path
import subprocess
import sys
from contextlib import contextmanager
from typing import ContextManager, Optional
from urllib.error import URLError

import requests
from hbutils.system import get_free_port
from hbutils.testing import isolated_directory
from requests.exceptions import RequestException

TESTFILE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'testfile'))


@contextmanager
def isolated_to_testfile():
    items = os.listdir(TESTFILE_DIR)
    with isolated_directory({item: os.path.join(TESTFILE_DIR, item) for item in items}):
        yield


@contextmanager
def start_http_server(directory, port, silent: bool = True) -> ContextManager[str]:
    with open(os.devnull, 'w') as nullfile:
        process = None
        try:
            process = subprocess.Popen(
                [sys.executable, '-m', 'http.server', '--directory', directory, str(port)],
                stdin=sys.stdin if not silent else None,
                stdout=sys.stdout if not silent else nullfile,
                stderr=sys.stderr if not silent else nullfile,
            )

            url = f'http://127.0.0.1:{port}'
            while True:
                try:
                    resp = requests.head(url, timeout=0.2)
                    resp.raise_for_status()
                except (URLError, RequestException, ConnectionError):
                    continue
                else:
                    break

            yield url

        finally:
            if process is not None:
                process.kill()
                process.wait()


@contextmanager
def start_http_server_to_testfile(port: Optional[int] = None, silent: bool = True) -> ContextManager[str]:
    port = port or get_free_port(strict=False)
    with start_http_server(TESTFILE_DIR, port, silent) as url:
        yield url
