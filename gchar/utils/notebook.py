from typing import Type

from tqdm import tqdm as std_tqdm
from tqdm.notebook import tqdm as nb_tqdm

try:
    from IPython import get_ipython
except ImportError:
    get_ipython = None


def is_notebook() -> bool:
    if not get_ipython:  # ipython not installed
        return False

    try:
        ipy = get_ipython()
        if 'google.colab' in str(ipy):
            return True  # google colab

        shell = ipy.__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


_tqdm = None


def import_tqdm() -> Type[std_tqdm]:
    global _tqdm
    if _tqdm is None:
        if is_notebook():
            _tqdm = nb_tqdm
        else:
            _tqdm = std_tqdm

    return _tqdm


def set_tqdm(tqdm: Type[std_tqdm]):
    global _tqdm
    _tqdm = tqdm
