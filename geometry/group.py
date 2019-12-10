from typing import List, Generator, Iterable, Tuple, TypeVar, Any, Union, Optional, Callable
from dataclasses import dataclass, field
from warnings import warn, simplefilter

from geometry.mixins import AppendMany
from .point import Number, Point
from .rect import Rect
from .translate import CanTranslate
from .path import Segment
from .userdata import HasUserData


T = TypeVar('T')
Shape = Union[Rect, Segment, 'Group']


def _pairwise(it: Iterable[T]) -> Iterable[Tuple[T, T]]:
    left = iter(it)
    right = iter(it)
    next(right, None)

    return zip(left, right)


def _same_axis(left: Point, right: Point) -> bool:
    return left.x == right.x or left.y == right.y


def _cum_sum(initial: Point, items: Iterable[Point]) -> Generator[Point, None, None]:
    yield initial

    for item in items:
        initial += item
        yield initial


_Decorated = Callable[..., Any]
_Decorator = Callable[[_Decorated], Any]


def _deprecate(alternative: str) -> _Decorator:  # pragma: no cover
    def decorator(func: _Decorated) -> _Decorated:
        def inner(*args: Any, **kwargs: Any) -> Any:
            simplefilter('always', DeprecationWarning)
            warn(
                f"{func.__name__} is deprecated, use {alternative} instead.",
                category=DeprecationWarning,
                stacklevel=2,
            )
            simplefilter('default', DeprecationWarning)
            return func(*args, **kwargs)

        return inner

    return decorator


_DIRECTION = {'down': 'bottom', 'up': 'top'}

_OPPOSITES = {
    'left': 'right',
    'top': 'bottom',
    'top_left': 'bottom_right',
    'top_right': 'bottom_left',
}

for _start, _end in list(_OPPOSITES.items()):
    _OPPOSITES[_end] = _start


Self = TypeVar('Self', bound='BaseGroup')


@dataclass
class BaseGroup(CanTranslate):
    shapes: List[Shape] = field(default_factory=list)
    bbox: Optional[Rect] = field(default=None)

    def __post_init__(self) -> None:
        self.update()

    @property  # type: ignore
    def x(self) -> Number:  # type: ignore
        """
        The x coordinate of the center of the bounding box

        >>> Group([Rect[0:1, 0:2], Rect[9:10, 19:20]]).x
        5.0

        Setting the x coordinate moves every shape in the group

        >>> g = Group([Rect[2, 2]])
        >>> g.x += 10
        >>> g.shapes[0]
        [9:11, -1:1]
        """
        assert self.bbox is not None, "group has no shapes"
        return self.bbox.x

    @x.setter
    def x(self, value: Number) -> None:
        assert self.bbox is not None, "group has no shapes"
        offset = value - self.bbox.x
        for shape in self.shapes:
            shape.x += offset
        self.bbox.x = value

    @property  # type: ignore
    def y(self) -> Number:  # type: ignore
        """
        The y coordinate of the center of the bounding box

        >>> Group([Rect[0:1, 0:2], Rect[9:10, 19:20]]).y
        10.0

        Setting the y coordinate moves every shape in the group

        >>> g = Group([Rect[2, 2]])
        >>> g.y += 10
        >>> g.shapes[0]
        [-1:1, 9:11]
        """
        assert self.bbox is not None, "group has no shapes"
        return self.bbox.y

    @y.setter
    def y(self, value: Number) -> None:
        assert self.bbox is not None, "group has no shapes"
        offset = value - self.bbox.y
        for shape in self.shapes:
            shape.y += offset
        self.bbox.y = value

    @property
    def width(self) -> Number:  # type: ignore
        """
        The width of the bounding box

        >>> Group([Rect[0:1, 0:2], Rect[9:10, 19:20]]).width
        10.0
        """
        assert self.bbox is not None, "group has no shapes"
        return self.bbox.width

    @property
    def height(self) -> Number:  # type: ignore
        """
        The width of the bounding box

        >>> Group([Rect[0:1, 0:2], Rect[9:10, 19:20]]).height
        20.0
        """
        assert self.bbox is not None, "group has no shapes"
        return self.bbox.height

    def _update_bbox(self, shape: Shape) -> None:
        if self.bbox is None:
            self.bbox = Rect(shape.x, shape.y, shape.width, shape.height)

        if shape.left < self.bbox.left:
            self.bbox.stretch(left=shape.left)
        if shape.right > self.bbox.right:
            self.bbox.stretch(right=shape.right)
        if shape.bottom < self.bbox.bottom:
            self.bbox.stretch(bottom=shape.bottom)
        if shape.top > self.bbox.top:
            self.bbox.stretch(top=shape.top)

    def update(self) -> None:
        """
        Recalculate the bounding box for all contained shapes.

        This is necessary when you manually change a shape after you
        added it to the group.

        >>> r = Rect[2, 4]
        >>> g = Group([r])
        >>> r.bottom_left = Point(0, 0)
        >>> r in g.bbox
        False

        >>> g.update()
        >>> r in g.bbox
        True
        """
        for shape in self.shapes:
            self._update_bbox(shape)

    @_deprecate('Group.append')
    def add(self: Self, shape: Shape) -> Self:  # pragma: no cover
        self.append(shape)
        return self

    def append(self, shape: Shape) -> None:
        """
        Add one shape to the group. The bounding box will be updated.

        >>> g = Group([Rect[0:2, 0:3]])
        >>> g.bbox
        [0:2, 0:3]
        >>> g.append(Rect[10:12, 0:1])
        >>> g.bbox
        [0:12, 0:3]
        """
        self.shapes.append(shape)
        self._update_bbox(shape)

    def __copy__(self: Self) -> Self:
        """
        Copy a group and all contained shapes.

        >>> r = Rect[0:2, 0:4]
        >>> g = Group([r])
        >>> g
        {[0:2, 0:4]} ...

        >>> from geometry import right
        >>> copied = g.copy()
        >>> r.stretch(right+2)
        [0:4, 0:4]
        >>> g
        {[0:4, 0:4]} ...
        >>> copied
        {[0:2, 0:4]} ...
        """
        shapes = [shape.copy() for shape in self.shapes]
        return type(self)(shapes)

    def __str__(self) -> str:
        inner = ", ".join(str(shape) for shape in self.shapes)
        bbox = "" if self.bbox is None else f" {self.bbox}"
        return f"{{{inner}}}{bbox}"


@dataclass(repr=False)
class Group(HasUserData, AppendMany[Shape], BaseGroup):
    """
    Represents a collection of shapes or nested groups.

    >>> Group()
    {}

    >>> Group([Rect[2, 4]])
    {[-1:1, -2:2]} [-1:1, -2:2]

    >>> Group([Rect[0:1, 0:1], Rect[9:10, 19:20]])
    {[0:1, 0:1], [9:10, 19:20]} [0:10, 0:20]

    >>> Group([Rect[0:3, 0:3], Rect[2, 2]])
    {[0:3, 0:3], [-1:1, -1:1]} [-1:3, -1:3]

    .. warning ::

        The group does not keep track of changes to the contained shapes.
        If you manually change shapes that are inside a group, you must :meth:`update`
        the group.
    """

    @classmethod
    def path_from_points(cls, thickness: Number, *points: Point, user_data: Any = None) -> 'Group':
        """
        Create a Path (Group of Segments) from a list of absolute points.


        ::

                             end
                         +----O----+
                         |    |    |
                     +---+----|----|    ---
                     |   |    |    |     |
            start -> O--------O----+   thickness
                     |   |    |    |     |
                     +--------+----+    ---



        `O` are the given points

        >>> p = Group.path_from_points(2, Point(0, 0), Point(10, 0), Point(10, 10))
        >>> p.shapes[0]
        [0:11, -1:1] (right)
        >>> p.shapes[1]
        [9:11, -1:10] (up)

        Duplicating consecutive points are skipped
        >>> Group.path_from_points(2, Point(0, 0), Point(5, 0), Point(5, 0), Point(5, 5))
        {[0:6, -1:1] (right), [4:6, -1:5] (up)} ...
        """
        assert len(points) > 1, "must give at least two points"

        segments: List[Shape] = []
        last_iteration = len(points) - 2
        for i, (left, right) in enumerate(_pairwise(points)):
            assert _same_axis(left, right), "consecutive points must share an axis"
            try:
                pad = (right - left).normalized * thickness / 2
            except ZeroDivisionError:
                continue
            left = left if i == 0 else left - pad
            right = right if i == last_iteration else right + pad
            segments.append(Segment.from_start_end(left, right, thickness, user_data))
        return Group(segments)

    @classmethod
    def path_from_vectors(
        cls, thickness: Number, start: Point, *edges: Point, user_data: Any = None
    ) -> 'Group':
        """

        Create a Path (Group of Segments) from a starting point and cumulative
        directions.

        >>> from geometry import Direction
        >>> right = Direction.right
        >>> g = Group.path_from_vectors(2, Point(0, 0), right * 10, right * 20)
        >>> g.shapes[0]
        [0:11, -1:1] (right)
        >>> g.shapes[1]
        [9:30, -1:1] (right)
        """
        return cls.path_from_points(thickness, *_cum_sum(start, edges), user_data=user_data)

    def grid(
        self, x_steps: int, x_direction: str, y_steps: int, y_direction: str
    ) -> Generator[Tuple[int, int, 'Group'], None, None]:
        """
        Span a grid of copies of this group.

        group.grid(5, 'right', 3, 'down') will create a grid of 5 times 3 copies


        ::

            XOOOO
            OOOOO
            OOOOO

        X is the initial group.

        The generator yield a tuple of the column number, row number and the group copy.

        >>> g = Group([Rect[2, 5]])
        >>> [cell.center for x, y, cell in g.grid(3, 'right', 2, 'up')]
        [(0, 0), (2, 0), (4, 0), (0, 5), (2, 5), (4, 5)]
        """
        x_end = _DIRECTION.get(x_direction, x_direction)
        y_end = _DIRECTION.get(y_direction, y_direction)
        x_start = _OPPOSITES[x_end]
        y_start = _OPPOSITES[y_end]
        for y, rows in self._grid_1d(y_start, y_end, y_steps):
            for x, cell in rows._grid_1d(x_start, x_end, x_steps):
                yield x, y, cell

    def _grid_1d(
        self, target: str, source: str, times: int
    ) -> Generator[Tuple[int, 'Group'], None, None]:
        copy = self.copy()
        yield 0, copy.copy()

        for i in range(1, times):
            setattr(copy, target, getattr(copy, source))
            yield i, copy.copy()

    def _flip_horizontally(self) -> None:
        x = self.x

        for shape in self.shapes:
            distance = shape.x - x
            shape.x = x - distance

            if isinstance(shape, Group):
                shape._flip_horizontally()

    def _flip_vertically(self) -> None:
        y = self.y

        for shape in self.shapes:
            distance = shape.y - y
            shape.y = y - distance

            if isinstance(shape, Group):
                shape._flip_vertically()

    def flip(self, *, horizontally: bool = False, vertically: bool = False) -> None:
        """
        Mirror the shapes in this group at the center lines of this group.

        Either horizontally or vertically or both.

        Note: this actually modified the contained shapes. If you don't want
        that behaviour, copy the group first: ``group.copy().flip(...)``

        ::

            E.g. a horizontal flip

            +----+----+     +----+----+
            |    |    |     |    |    |
            +----+    |  => |    +----+
            |    +----+     |----+    |
            |    |    |     |    |    |
            +----+----+     +----+----+

        >>> top_left = Rect[0:1, 2:3]
        >>> bottom_right = Rect[1:2, 0:1]
        >>> g = Group([top_left, bottom_right])
        >>> g.flip(horizontally=True)

        >>> top_left  # is now top right
        [1:2, 2:3]
        >>> bottom_right  # is now bottom left
        [0:1, 0:1]

        >>> g.flip(vertically=True)
        >>> top_left  # is now bottom right
        [1:2, 0:1]
        >>> bottom_right  # is now top left
        [0:1, 2:3]
        """

        if horizontally:
            self._flip_horizontally()
        if vertically:
            self._flip_vertically()
