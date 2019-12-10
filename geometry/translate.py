from typing import Any, Union, NamedTuple

from .point import Point, Number
from .handles import TranslateHandle, EdgeHandle


def int_if_possible(number: Any) -> Any:
    if isinstance(number, float) and number.is_integer():
        return int(number)
    return number


_int = int_if_possible


class Corner(NamedTuple):
    y: str
    x: str

    def __get__(self, instance: Any, owner: type) -> Point:
        x = getattr(instance, self.x)
        y = getattr(instance, self.y)
        return Point(_int(x), _int(y))

    def __set__(self, instance: Any, value: Point) -> None:
        setattr(instance, self.x, value.x)
        setattr(instance, self.y, value.y)


class CanTranslate:
    x: Number
    y: Number
    width: Number
    height: Number

    top_left = Corner('top', 'left')
    center_left = Corner('y', 'left')
    bottom_left = Corner('bottom', 'left')
    top_center = Corner('top', 'x')
    center_center = Corner('y', 'x')
    center = center_center
    bottom_center = Corner('bottom', 'x')
    top_right = Corner('top', 'right')
    center_right = Corner('y', 'right')
    bottom_right = Corner('bottom', 'right')

    @property
    def left(self) -> Number:
        """
        The left edge of the rect.

        >>> from geometry import Rect
        >>> r = Rect[1:2, 3:4]
        >>> r.left
        1.0

        Assigning the edge translates the whole rect.

        >>> r.left = 10
        >>> r
        [10:11, 3:4]
        """
        return self.x - self.width / 2

    @left.setter
    def left(self, value: Number) -> None:
        self.x += value - self.left

    @property
    def right(self) -> Number:
        """
        The right edge of the rect.

        >>> from geometry import Rect
        >>> r = Rect[1:2, 3:4]
        >>> r.right
        2.0

        Assigning the edge translates the whole rect.

        >>> r.right = 10
        >>> r
        [9:10, 3:4]
        """
        return self.x + self.width / 2

    @right.setter
    def right(self, value: Number) -> None:
        self.x += value - self.right

    @property
    def bottom(self) -> Number:
        """
        The bottom edge of the rect.

        >>> from geometry import Rect
        >>> r = Rect[1:2, 3:4]
        >>> r.bottom
        3.0

        Assigning the edge translates the whole rect.

        >>> r.bottom = 10
        >>> r
        [1:2, 10:11]
        """
        return self.y - self.height / 2

    @bottom.setter
    def bottom(self, value: Number) -> None:
        self.y += value - self.bottom

    @property
    def top(self) -> Number:
        """
        The top edge of the rect.

        >>> from geometry import Rect
        >>> r = Rect[1:2, 3:4]
        >>> r.top
        4.0

        Assigning the edge translates the whole rect.

        >>> r.top = 10
        >>> r
        [1:2, 9:10]
        """
        return self.y + self.height / 2

    @top.setter
    def top(self, value: Number) -> None:
        self.y += value - self.top

    def translate(self, **absolute: Union[Number, Point, TranslateHandle]) -> 'CanTranslate':
        """
        Translates the whole shape.

        >>> from geometry import Rect, right
        >>> r = Rect[2, 4]
        >>> r.translate(bottom_left=Point(0, 0))  # move the bottom left to the origin
        [0:2, 0:4]

        >>> r.translate(center=Point(0, 0))  # move the center to the origin
        [-1:1, -2:2]

        >>> r.translate(left=right)  # move by 2 (width) to the right
        [1:3, -2:2]

        >>> r.translate(left=right + 1)  # move by 3 (width + 1) to the right
        [4:6, -2:2]
        """

        for key, target in absolute.items():
            if isinstance(target, EdgeHandle):
                target = target.position(self)
            setattr(self, key, target)

        return self
