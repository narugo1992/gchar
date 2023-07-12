import os
from functools import lru_cache, wraps


def optional_lru_cache(*pargs, **pkwargs):
    """
    Decorator that optionally applies LRU caching to a function's return value based on the presence of the 'NO_CACHE'
    environment variable.

    The function is decorated with the `lru_cache` decorator with the provided arguments `pargs` and `pkwargs` to enable
    caching. However, if the 'NO_CACHE' environment variable is present, the original function is called directly
    without caching.

    :param pargs: Positional arguments to be passed to the `lru_cache` decorator.
    :type pargs: tuple
    :param pkwargs: Keyword arguments to be passed to the `lru_cache` decorator.
    :type pkwargs: dict
    :returns: Decorated function.
    :rtype: callable
    """

    def _decorator(func):
        _cached_func = lru_cache(*pargs, **pkwargs)(func)

        @wraps(func)
        def _new_func(*args, **kwargs):
            if os.environ.get('NO_CACHE', None):
                return func(*args, **kwargs)
            else:
                return _cached_func(*args, **kwargs)

        return _new_func

    return _decorator
