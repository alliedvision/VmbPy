"""BSD 2-Clause License

Copyright (c) 2023, Allied Vision Technologies GmbH
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import functools
from typing import Any, Callable, TypeVar

__all__ = [
    'EnterContextOnCall',
    'LeaveContextOnCall',
    'RaiseIfInsideContext',
    'RaiseIfOutsideContext'
]

# TODO: To improve type checking further consider usage of `ParamSpec`. Introduced to standard
# library with Python 3.10 and available as backport in `typing_extensions` package for Python >=3.8
T = TypeVar('T')


class EnterContextOnCall:
    """Decorator setting/injecting flag used for checking the context."""

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            args[0]._context_entered = True
            try:
                return func(*args, **kwargs)
            except Exception:
                # If an error occurs during the function call, we do not consider the context to be
                # entered
                args[0]._context_entered = False
                raise

        return wrapper


class LeaveContextOnCall:
    """Decorator clearing/injecting flag used for checking the context."""

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result = func(*args, **kwargs)
            args[0]._context_entered = False
            return result
        return wrapper


class RaiseIfInsideContext:
    """Raising RuntimeError is decorated Method is called inside with-statement.

    Note:
        This Decorator shall work only on Object implementing a Context Manger. For this to work
        object must offer a boolean attribute called ``_context_entered``
    """

    def __init__(self, msg='Called \'{}()\' inside of \'with\' context.'):
        self.msg = msg

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if args[0]._context_entered:
                msg = self.msg.format('{}'.format(func.__qualname__))
                raise RuntimeError(msg)

            return func(*args, **kwargs)
        return wrapper


class RaiseIfOutsideContext:
    """Raising RuntimeError is decorated Method is called outside with-statement.

    Note:
        This Decorator shall work only on Object implementing a Context Manger. For this to work
        object must offer a boolean attribute called ``_context_entered``
    """

    def __init__(self, msg='Called \'{}()\' outside of \'with\' context.'):
        self.msg = msg

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if not args[0]._context_entered:
                msg = self.msg.format('{}'.format(func.__qualname__))
                raise RuntimeError(msg)

            return func(*args, **kwargs)
        return wrapper
