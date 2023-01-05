import shutil
from unittest import skipUnless

import pytest

from gchar.utils import is_cuda_available


@pytest.mark.unittest
class TestUtilsCuda:
    @skipUnless(not shutil.which('nvidia-smi'), 'no cuda required')
    def test_is_cuda_available_no_cuda(self):
        assert not is_cuda_available()

    @skipUnless(shutil.which('nvidia-smi'), 'cuda required')
    def test_is_cuda_available_with_cuda(self):
        assert is_cuda_available()
