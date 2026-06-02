from __future__ import annotations

import functools
from collections.abc import Callable

import global_switch

class _GlobalSwitch:
    def __init__(self, *, default: bool = False) -> None:
        self.__enabled = default

    def get(self) -> bool:
        return self.__enabled

    def set(self, enabled_or_disabled: bool) -> None:
        self.__enabled = enabled_or_disabled

IS_ENABLED = global_switch.GlobalSwitch()

def set(enabled_or_disabled: bool) -> None:
    IS_ENABLED.set(enabled_or_disabled)

def make_dryable[**P, R = None](
    *,
    default_return_value: R = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Return a new version of the function that skisp execution if dry mode
    is globally enabled.

    If the function's return type is non-None, a default value must be
    provided.
    """

    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(function)
        def dryable_function(*args: P.args, **kwargs: P.kwargs) -> R:
            if IS_ENABLED:
                return default_return_value
            return function(*args, **kwargs)
        return dryable_function
    return decorator
