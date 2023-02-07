import os
from unittest.mock import patch

import pytest


@pytest.fixture(scope='module', autouse=True)
def no_cache():
    with patch.dict(os.environ, {'NO_CACHE': '1'}):
        yield
