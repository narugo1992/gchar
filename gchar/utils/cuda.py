import shutil
import subprocess
from functools import lru_cache


@lru_cache()
def is_cuda_available() -> bool:
    nvidia_smi = shutil.which('nvidia-smi')
    try:
        return bool(nvidia_smi and subprocess.check_output([nvidia_smi, '-x', '-q']))
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False
