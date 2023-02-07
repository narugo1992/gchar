import os
from functools import lru_cache, wraps


def optional_lru_cache(*pargs, **pkwargs):
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
