import os.path
from dataclasses import dataclass

from .session import get_requests_session
from ...utils import download_file


@dataclass
class Skin:
    name: str
    url: str

    def download(self, filename, max_retries: int = 3, timeout: int = 5):
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        session = get_requests_session(max_retries=max_retries, timeout=timeout)
        download_file(self.url, filename, session=session)
