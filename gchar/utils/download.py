import requests


def download_file(url, filename, session: requests.Session = None, chunk_size: int = 8192):
    session = session or requests
    with session.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size):
                f.write(chunk)
