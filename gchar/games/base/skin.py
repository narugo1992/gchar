import os.path
import tempfile
from dataclasses import dataclass

from PIL import Image

from .session import get_requests_session
from ...utils import download_file


@dataclass
class Skin:
    name: str
    url: str

    def download(self, filename, max_retries: int = 3):
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        session = get_requests_session(max_retries=max_retries)
        download_file(self.url, filename, session=session)

    def to_pil(self, max_retries: int = 3) -> Image.Image:
        with tempfile.TemporaryDirectory() as td:
            image_filename = os.path.join(td, os.path.basename(self.url))
            self.download(image_filename, max_retries)
            return Image.open(image_filename)
