from sys import version_info
from typing import Tuple, Any, Union, Sequence, TypeVar, Optional
from dataclasses import dataclass

from .point import Point, Number
from .userdata import HasUserData
from .translate import CanTranslate, int_if_possible as _int
from .handles import StretchHandle

Range = Union[slice, Number]
InitTuple = Union[Tuple[Range, Range, Any], Tuple[Range, Range]]


def _to_start_stop(value: Range) -> Tuple[Number, Number]:
    if isinstance(value, slice):
        assert value.step is None, "step may not be given"
        assert value.stop is not None, "stop must be given"
        return value.start or 0, value.stop
    half = value / 2
    return -half, half


Self = TypeVar('Self', bound='BaseRect')


@dataclass
class BaseRect(CanTranslate):
    x: Number
    y: Number
    width: Number
    height: Number

    def __post_init__(self) -> None:
        assert self.width >= 0, "width must be positive"
        assert self.height >= 0, "height must be positive"

    @property
    def long_side(self) -> Number:
        """
        Return the longer side of the rectangle

        >>> Rect[0:3, 0:2].long_side
        3

        >>> Rect[0:2, 0:3].long_side
        3
        """
        return self.width if self.width > self.height else self.height

    @property
    def short_side(self) -> Number:
        """
        Return the shorter side of the rectangle

        >>> Rect[0:3, 0:2].short_side
        2

        >>> Rect[0:2, 0:3].short_side
        2
        """
        return self.width if self.width < self.height else self.height

    # Stretching

    def _stretch_left(self, offset: Number) -> None:
        self.width -= offset
        self.x += offset / 2

    def _stretch_right(self, offset: Number) -> None:
        self.width += offset
        self.x += offset / 2

    def _stretch_bottom(self, offset: Number) -> None:
        self.height -= offset
        self.y += offset / 2

    def _stretch_top(self, offset: Number) -> None:
        self.height += offset
        self.y += offset / 2

    def stretch(self: Self, *relative: StretchHandle, **absolute: Union[Number, Point]) -> Self:
        """
        Stretch the given edges or corners of the rectangle. I.e. move the given edge
        or corner while leaving the opposite edge or corner intact.

        You can stretch the edges to an absolute coordinate.

        >>> Rect[2:4, 4:6].stretch(left=0)
        [0:4, ...]

        >>> Rect[2:4, 4:6].stretch(right=6)
        [2:6, ...]

        >>> r = Rect[2:4, 4:6]; r2 = r.copy()
        >>> r.stretch(left=0, right=6) == r2.stretch(left=0).stretch(right=6)
        True

        >>> Rect[2:4, 4:6].stretch(bottom=0)
        [2:4, 0:6]

        >>> Rect[2:4, 4:6].stretch(top=8)
        [2:4, 4:8]

        You can stretch the edges relatively. Here, positive numbers will always stretch
        away from the center.

        >>> from geometry import left
        >>> Rect[2:4, 4:6].stretch(left + 1)
        [1:4, 4:6]

        >>> from geometry import right, bottom, top
        >>> Rect[2:5, 4:7].stretch(left - 1, right - 1, bottom - 1, top - 1)
        [3:4, 5:6]

        It is also possible to stretch the corners like this:

        >>> Rect[2:4, 4:6].stretch(bottom_left=Point(0, 0))
        [0:4, 0:6]

        >>> from geometry import bottom_left
        >>> Rect[2:4, 4:6].stretch(bottom_left + Point(1, 2))
        [1:4, 2:6]

        As a shortcut you can also pass a scalar instead of a vector in the relative case.

        >>> Rect[2:4, 4:6].stretch(bottom_left + 2)
        [0:4, 2:6]

        Here is another shortcut for stretching every edge out

        >>> from geometry import out
        >>> Rect[2:4, 4:6].stretch(out + 1)
        [1:5, 3:7]

        And inwards:

        >>> from geometry import in_
        >>> Rect[2:5, 4:7].stretch(in_ + 1)
        [3:4, 5:6]
        """

        for handles in relative:
            for handle in handles:
                getattr(self, f'_stretch_{handle.name}')(handle.offset)

        for key, target in absolute.items():
            if isinstance(target, Point):
                keys: Sequence[str] = key.split('_')
                targets: Sequence[Number] = (target.x, target.y)
            else:
                keys = (key,)
                targets = (target,)

            for k, t in zip(keys, targets):
                offset = t - getattr(self, k)
                getattr(self, f'_stretch_{k}')(offset)

        return self

    def __str__(self) -> str:
        """
        The string representation of a rect.

        >>> Rect[0:2, 0:4, 'user data']
        [0:2, 0:4] 'user data'

        The format is [left:right, bottom:top] + optional user data
        """
        left_ = _int(self.left)
        right_ = _int(self.right)
        bottom_ = _int(self.bottom)
        top_ = _int(self.top)
        return f"[{left_}:{right_}, {bottom_}:{top_}]"

    # Topology

    def is_inside_of(self, rect: 'BaseRect') -> bool:
        """
        Check if this rectangle is inside the other rectangle.

        >>> Rect[1, 1].is_inside_of(Rect[2, 2])
        True

        >>> Rect[2, 2].is_inside_of(Rect[2, 2])
        True

        >>> Rect[1, 2].is_inside_of(Rect[2, 1])
        False

        You can also use the `in` operator

        >>> Rect[1, 1] in Rect[2, 2]
        True

        >>> Rect[1, 1] not in Rect[2, 2]
        False
        """
        return (
            self.left >= rect.left
            and self.right <= rect.right
            and self.bottom >= rect.bottom
            and self.top <= rect.top
        )

    def __contains__(self, rect: 'BaseRect') -> bool:
        return rect.is_inside_of(self)

    def intersection(self, rect: 'Rect') -> Optional['Rect']:
        """
        Calculate the intersecting rectangle between this and the given rectangle.

        If the rectangles don't intersect, ``None`` is returned

        ::

            +---------+
            |         |
            |    +----+----+
            |    |    |    |
            +----+----+    |
                 |         |
                 +---------+

        >>> Rect[0:2, 0:4].intersection(Rect[1:3, 2:6])
        [1:2, 2:4]

        >>> Rect[0:1, 0:1].intersection(Rect[1:2, 1:2]) is None
        True

        >>> Rect[0:1, 0:1].intersection(Rect[2:3, 2:3]) is None
        True
        """
        left = max(self.left, rect.left)
        right = min(self.right, rect.right)
        bottom = max(self.bottom, rect.bottom)
        top = min(self.top, rect.top)

        if left >= right or bottom >= top:
            return None

        return Rect.from_edges(left, right, bottom, top)

    def union(self, rect: 'Rect') -> Optional['Rect']:
        """
        Calculate the union rectangle of this and the given rectangle.

        ::

            +----+-------+
            |    |       |
            +----+       |
            |       +----+
            |       |    |
            +-------+----+

        >>> Rect[0:1, 0:1].union(Rect[2:3, 2:3])
        [0:3, 0:3]
        """
        left = min(self.left, rect.left)
        right = max(self.right, rect.right)
        bottom = min(self.bottom, rect.bottom)
        top = max(self.top, rect.top)
        return Rect.from_edges(left, right, bottom, top)


@dataclass(repr=False)
class Rect(HasUserData, BaseRect):
    """
    An axis-aligned rectangle defined by a center point, width and height. An optional
    user data object may also be given.

    >>> Rect(0, 1, 10, 20).x
    0

    >>> Rect(0, 1, 10, 20).y
    1

    >>> Rect(0, 1, 10, 20).width
    10

    >>> Rect(0, 1, 10, 20).height
    20

    The string representation has the following meaning:
    ``[<left edge>:<right edge>, <bottom edge>:<top edge>]``

    >>> Rect(0, 0, 10, 20)
    [-5:5, -10:10]

    >>> Rect(0, 0, 2, 4, 'user data')
    [-1:1, -2:2] 'user data'

    >>> Rect(0, 0, 10, 20).top_left
    (-5, 10)

    >>> Rect(0, 0, 10, 20).bottom_center
    (0, -10)
    """

    @staticmethod
    def from_size(width: Number, height: Number, user: Any = None) -> 'Rect':
        """
        Construct a rect with a given width and height.
        The center point will be (0, 0).

        >>> Rect.from_size(4, 6)
        [-2:2, -3:3]
        """
        return Rect(0, 0, width, height, user)

    @staticmethod
    def from_edges(
        left: Number, right: Number, bottom: Number, top: Number, user_data: Any = None
    ) -> 'Rect':
        """
        Construct a rect from the given edge coordinates

        >>> Rect.from_edges(1, 3, 2, 4)
        [1:3, 2:4]
        """
        x = (left + right) / 2
        y = (bottom + top) / 2
        width = right - left
        height = top - bottom
        return Rect(x, y, width, height, user_data)

    def __class_getitem__(cls, init_tuple: InitTuple) -> 'Rect':
        """
        Construct a rect using slice notation.

        >>> Rect[0:2, 0:4]
        [0:2, 0:4]

        >>> Rect[2, 4]
        [-1:1, -2:2]

        >>> Rect[0:2, 0:4, 'red']
        [0:2, 0:4] 'red'
        """
        x_range, y_range, *optional_user_data = init_tuple
        user_data = optional_user_data[0] if optional_user_data else None

        horizontal = _to_start_stop(x_range)
        vertical = _to_start_stop(y_range)

        return Rect.from_edges(*horizontal, *vertical, user_data)


# In python 3.7 the implicit class method __class_getitem__ was added
# This allows the following syntax: Rect[0:3, 0:4]
# We need a meta class in python 3.6 to backport that behaviour
if version_info < (3, 7):  # pragma: no cover

    _old_rect_class = Rect

    class RectMeta(type):
        def __getitem__(self, init_tuple: InitTuple) -> Rect:
            # noinspection PyArgumentList
            return _old_rect_class.__class_getitem__(self, init_tuple)  # type: ignore

    class Rect(_old_rect_class, metaclass=RectMeta):  # type: ignore
        pass
