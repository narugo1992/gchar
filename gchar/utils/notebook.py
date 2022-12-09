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
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def import_tqdm() -> Type[std_tqdm]:
    if is_notebook():
        return nb_tqdm
    else:
        return std_tqdm
