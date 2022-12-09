import io
import time
from functools import wraps
from typing import Union, Type, Tuple

from ditk import logging


def func_call_repr(func, *args, **kwargs):
    with io.StringIO() as sio:
        if hasattr(func, '__module__'):
            print(func.__module__, end='', file=sio)
        print(func.__name__, end='', file=sio)
        print('(', end='', file=sio)

        _first = True
        for ag in args:
            if _first:
                _first = False
            else:
                print(', ', end='', file=sio)
            print(f'{ag!r}', end='', file=sio)
        for k, v in kwargs.items():
            if _first:
                _first = False
            else:
                print(', ', end='', file=sio)
            print(f'{k!r}: {v!r}', end='', file=sio)
        print(')', end='', file=sio)

        return sio.getvalue()


def func_retry(errors: Union[Type[Exception], Tuple[Type[Exception], ...]], retries: int = 3, delay: float = 3.0):
    def _decorator(func):
        @wraps(func)
        def _new_func(*args, **kwargs):
            _retry = 0
            while True:
                try:
                    return func(*args, *kwargs)
                except errors as err:
                    if _retry > retries:
                        logging.error(f'Unable to call {func_call_repr(func, *args, **kwargs)}!')
                        raise
                    else:
                        logging.warn(f'Call {func_call_repr(func, *args, **kwargs)} failed, '
                                     f'try again ({_retry}/{retries}) - {err!r} ...')
                        if delay:
                            time.sleep(delay)

        return _new_func

    return _decorator
