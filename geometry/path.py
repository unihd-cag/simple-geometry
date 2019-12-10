from enum import Enum
from typing import Any, Optional, cast, TypeVar
from dataclasses import dataclass

from .rect import Rect, BaseRect
from .point import Point, Number
from .userdata import HasUserData


class Direction(Enum):
    """
    Represents a direction along one of the coordinate axes.

    Fields are:

    - ``vector``: the direction as a point object
    - ``is_horizontal``: True if the direction is horizontal
    - ``start_point``: handle name of the start of this direction
    - ``end_point``: handle name of the end of this direction

    >>> Direction.up.vector
    (0, 1)

    >>> Direction.up.is_horizontal
    False

    >>> Direction.left.is_horizontal
    True

    >>> Direction.up.start_point
    'bottom_center'

    >>> Direction.up.end_point
    'top_center'
    """

    up = Point(0, 1), False, 'bottom_center', 'top_center'
    down = Point(0, -1), False, 'top_center', 'bottom_center'
    left = Point(-1, 0), True, 'center_right', 'center_left'
    right = Point(1, 0), True, 'center_left', 'center_right'

    def __init__(self, vector: Optional[Point], is_horizontal: bool, start: str, end: str) -> None:
        self.vector = vector
        self.is_horizontal = is_horizontal
        self.start_point = start
        self.end_point = end

    def __mul__(self, other: Number) -> Point:
        """
        Multiply the actual vector that represents this direction by a factor

        >>> Direction.up * 3
        (0, 3)
        """
        return (self.vector or Point(0, 0)) * other


Self = TypeVar('Self', bound='BaseSegment')


@dataclass
class BaseSegment(BaseRect):
    direction: Direction

    # Properties

    @property
    def length(self) -> Number:
        """
        The side in the direction of the segment. I.e. the height for vertical
        Segments and the width for horizontal Segments.

        >>> p = Segment.from_rect(Rect[2, 10], Direction.up)
        >>> p.length == p.height
        True
        """
        return self.width if self.direction.is_horizontal else self.height

    @property
    def thickness(self) -> Number:
        """
        The side perpendicular to the direction of the segment. I.e. the width for
        vertical Segments and the height for horizontal Segments.

        >>> p = Segment.from_rect(Rect[2, 10], Direction.up)
        >>> p.thickness == p.width
        True
        """
        return self.height if self.direction.is_horizontal else self.width

    @property
    def start(self) -> Point:
        """
        The start point of the Segment. E.g. for Segments with direction "up" this
        is identical to the bottom center point of the corresponding Rect.

        >>> p = Segment.from_rect(Rect[2, 10], Direction.up)
        >>> p.start == p.bottom_center
        True

        Assigning to start is identical to assigning to the corresponding point of
        the underlying Rect.

        >>> p.start = Point(0, 0)
        >>> p
        [-1:1, 0:10] (up)
        """
        return cast(Point, getattr(self, self.direction.start_point))

    @start.setter
    def start(self, target: Point) -> None:
        setattr(self, self.direction.start_point, target)

    @property
    def end(self) -> Point:
        """
        The start point of the Segment. E.g. for Segments with direction "up" this
        is identical to the top center point of the corresponding Rect.

        >>> p = Segment.from_rect(Rect[2, 10], Direction.up)
        >>> p.end == p.top_center
        True

        Assigning to start is identical to assigning to the corresponding point of
        the underlying Rect.

        >>> p.end = Point(0, 0)
        >>> p
        [-1:1, -10:0] (up)
        """
        return cast(Point, getattr(self, self.direction.end_point))

    @end.setter
    def end(self, target: Point) -> None:
        setattr(self, self.direction.end_point, target)

    def __str__(self) -> str:
        """
        The string representation of a segment.

        >>> Rect[0:2, 0:4, 'user data']
        [0:2, 0:4] 'user data'

        The format is [left:right, bottom:top] + (direction) + optional user data
        """
        rect = super().__str__()
        return f'{rect} ({self.direction.name})'


@dataclass(repr=False)
class Segment(HasUserData, BaseSegment):
    """
    An oriented path segment. This is basically a rectangle plus a direction.

    >>> Segment(0, 0, 10, 20, Direction.up)
    [-5:5, -10:10] (up)
    """

    @classmethod
    def from_rect(cls, rect: Rect, direction: Direction) -> 'Segment':
        """
        Create a segment from a rect and a direction

        >>> Segment.from_rect(Rect[0:2, 0:4], Direction.up)
        [0:2, 0:4] (up)
        """
        return Segment(rect.x, rect.y, rect.width, rect.height, direction, rect.user_data)

    @classmethod
    def from_start_end(
        cls, start: Point, end: Point, thickness: Number, user_data: Any = None
    ) -> 'Segment':
        """
        Create a segment from start point, end point and thickness

        >>> Segment.from_start_end(Point(0, 0), Point(0, 10), 2)
        [-1:1, 0:10] (up)

        >>> Segment.from_start_end(Point(0, 0), Point(10, 0), 4)
        [0:10, -2:2] (right)

        >>> Segment.from_start_end(Point(0, 0), Point(10, 10), 2)
        Traceback (most recent call last):
         ...
        ValueError: Segment must be parallel to one of the coordinate axes
        """
        center = (end + start) / 2
        if start.x == end.x:
            direction = Direction.up if end.y > start.y else Direction.down
            width = thickness
            height = abs(end - start)
        elif start.y == end.y:
            direction = Direction.right if end.x > start.x else Direction.left
            width = abs(end - start)
            height = thickness
        else:
            raise ValueError("Segment must be parallel to one of the coordinate axes")

        return Segment(center.x, center.y, width, height, direction, user_data)

    @property
    def rect(self) -> Rect:
        """
        Create a new rectangle from a segment by removing the direction information

        >>> Segment.from_start_end(Point(0, 0), Point(0, 10), 2).rect
        [-1:1, 0:10]
        """
        return Rect(self.x, self.y, self.width, self.height, self.user_data)
