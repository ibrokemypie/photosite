"""
I must confess to the reader, this was a magic spell cast by an LLM to resolve
functools' cache decorators breaking the type of the decorated function, losing
the ability to read/check the wrapped function's signature.

I spent a lot of time reading a lot of different threads and PR's trying to
resolve this in different ways, so far it seems like an unsolved problem for
reasons beyond me.

Here are some issues to track:
    https://github.com/python/typeshed/issues/6347
    https://github.com/python/typeshed/pull/11662
    https://github.com/facebook/pyrefly/issues/43
"""

from functools import _CacheInfo
from functools import cache as _original_cache
from functools import lru_cache as _original_lru_cache
from typing import Any, Callable, ParamSpec, Protocol, TypeVar, cast, overload

P = ParamSpec("P")
R = TypeVar("R")


class _lru_cache_wrapper(Protocol[P, R]):
    __wrapped__: Callable[P, R]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def cache_info(self) -> _CacheInfo: ...
    def cache_clear(self) -> None: ...
    # def cache_parameters(self) -> _CacheParameters: ...
    def __copy__(self) -> "_lru_cache_wrapper[P, R]": ...
    def __deepcopy__(self, memo: Any, /) -> "_lru_cache_wrapper[P, R]": ...


@overload
def lru_cache(func: Callable[P, R]) -> _lru_cache_wrapper[P, R]: ...
@overload
def lru_cache(
    *, maxsize: int | None = ..., typed: bool = False
) -> Callable[[Callable[P, R]], _lru_cache_wrapper[P, R]]: ...


def lru_cache(
    func: Callable[P, R] | None = None,
    *,
    maxsize: int | None = 128,
    typed: bool = False,
) -> _lru_cache_wrapper[P, R] | Callable[[Callable[P, R]], _lru_cache_wrapper[P, R]]:
    if func is not None:
        return cast(
            _lru_cache_wrapper[P, R],
            _original_lru_cache(maxsize=maxsize, typed=typed)(func),
        )
    else:

        def decorator(inner_func: Callable[P, R]) -> _lru_cache_wrapper[P, R]:
            return cast(
                _lru_cache_wrapper[P, R],
                _original_lru_cache(maxsize=maxsize, typed=typed)(inner_func),
            )

        return decorator


def cache(func: Callable[P, R]) -> _lru_cache_wrapper[P, R]:
    return cast(_lru_cache_wrapper[P, R], _original_cache(func))  # type: ignore
