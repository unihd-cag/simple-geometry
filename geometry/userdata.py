from typing import Any, TypeVar
from copy import deepcopy, copy
from dataclasses import dataclass


Self = TypeVar('Self', bound='HasUserData')


@dataclass
class HasUserData:
    user_data: Any = None

    keep = object()
    shallow_copy = object()
    deep_copy = object()

    def copy(self: Self, user_data: Any = keep) -> Self:
        """
        Copy the rect or any other shape.
        You can specify the copy behaviour for the user data object.

        The default is a shallow copy

        >>> from geometry import Rect
        >>> r = Rect[0:1, 0:1, ['my', 'user', 'data']]
        >>> r.copy(Rect.shallow_copy)
        [0:1, 0:1] ['my', 'user', 'data']

        You can force a deep copy

        >>> r = Rect[0:1, 0:1, [...]]
        >>> r.copy(Rect.deep_copy)
        [0:1, 0:1] [...]

        You can pass the user data without copying

        >>> r = Rect[0:1, 0:1, [...]]
        >>> r.copy(Rect.keep)
        [0:1, 0:1] [...]

        And you can supply a completely new user data object

        >>> r = Rect[0:1, 0:1, [...]]
        >>> r.copy('completely new')
        [0:1, 0:1] 'completely new'
        """
        copied = copy(self)

        if user_data is self.keep:
            copied.user_data = self.user_data
        elif user_data is self.shallow_copy:
            copied.user_data = copy(self.user_data)
        elif user_data is self.deep_copy:
            copied.user_data = deepcopy(self.user_data)
        else:
            copied.user_data = user_data

        return copied

    def __str__(self) -> str:
        base = super().__str__()
        user_data = "" if self.user_data is None else f" {self.user_data!r}"
        return f"{base}{user_data}"

    def __repr__(self) -> str:
        return self.__str__()
