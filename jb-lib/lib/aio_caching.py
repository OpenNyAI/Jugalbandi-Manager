import functools
from cachetools.keys import methodkey


class NullContext(object):
    """A class for noop context managers."""

    def __enter__(self):
        """Return ``self`` upon entering the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Raise any exception triggered within the runtime context."""

    async def __aenter__(self):
        """Return ``self`` upon entering the runtime context."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Raise any exception triggered within the runtime context."""


def aiocachedmethod(cache, key=methodkey, lock=None):
    """Decorator to wrap a class or instance method with a memoizing
    callable that saves results in a cache.

    adapted for asyncio from "cachedmethod" of cachetools

    Example:
    >>> import asyncio
    >>> import operator
    >>> from service_base.api import aiocachedmethod
    >>> class MyCacher:
    ...     def __init__(self):
    ...         self._cache = {}
    ...         self.i = 1
    ...     @aiocachedmethod(operator.attrgetter("_cache"))
    ...     async def get_camera(self, camera_id: int):
    ...         self.i += 1
    ...         return camera_id + self.i
    >>> async def print_camera():
    ...     cacher = MyCacher()
    ...     print(await cacher.get_camera(20))
    ...     print(await cacher.get_camera(20))
    ...     print(await cacher.get_camera(30))
    >>> asyncio.run(print_camera())
    22
    22
    33
    """

    def null(s):
        return NullContext()

    lock = lock or null

    def decorator(method):
        async def wrapper(self, *args, **kwargs):
            c = cache(self)
            if c is None:
                return method(self, *args, **kwargs)
            k = key(self, *args, **kwargs)
            try:
                with lock(self):
                    return c[k]
            except KeyError:
                pass  # key not found
            v = await method(self, *args, **kwargs)
            # in case of a race, prefer the item already in the cache
            try:
                with lock(self):
                    return c.setdefault(k, v)
            except ValueError:
                return v  # value too large

        def clear(self):
            c = cache(self)

            if c is not None:
                with lock(self):
                    c.clear()

        wrapper.cache = cache
        wrapper.cache_key = key
        wrapper.cache_lock = lock
        wrapper.cache_clear = clear

        return functools.update_wrapper(wrapper, method)

    return decorator
