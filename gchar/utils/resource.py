import os.path

_RESOURCE_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'resource'))


def get_resource_file(relpath: str) -> str:
    return os.path.join(_RESOURCE_PATH, relpath)
