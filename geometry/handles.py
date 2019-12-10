from typing import Any, Generator, Union, List, cast, NamedTuple

from .point import Number, Point


class EdgeHandle(NamedTuple):
    name: str
    factor: int = 1
    offset: Number = 0

    def __add__(self, offset: Number) -> 'EdgeHandle':  # type: ignore
        """
        Create a handle that offsets the edge by a given number
        away from the center of the shape

        >>> top
        stretch handle top+0

        >>> top + 10
        stretch handle top+10

        >>> bottom + 10
        stretch handle bottom-10
        """
        return EdgeHandle(self.name, self.factor, self.offset + self.factor * offset)

    def __sub__(self, offset: Number) -> 'EdgeHandle':
        """
        Create a handle that offsets the edge by a given number
        towards the center of the shape

        >>> top - 10
        stretch handle top-10

        >>> bottom - 10
        stretch handle bottom+10
        """
        return EdgeHandle(self.name, self.factor, self.offset - self.factor * offset)

    def __str__(self) -> str:
        offset = f"{self.offset:+}" if self.factor else ""
        return f"stretch handle {self.name}{offset}"

    def __repr__(self) -> str:
        return self.__str__()

    def position(self, shape: Any) -> Number:
        return cast(Number, getattr(shape, self.name) + self.offset)

    def __iter__(self) -> Generator['EdgeHandle', None, None]:
        yield self


def _to_vector(arg: Union[Number, Point]) -> Point:
    if isinstance(arg, Point):
        return arg
    return Point(arg, arg)


class PointHandle(NamedTuple):
    y: EdgeHandle
    x: EdgeHandle

    def __add__(self, offset: Union[Number, Point]) -> 'PointHandle':  # type: ignore
        """
        Create a handle that offsets the corner by a given vector away from the
        center of the shape

        >>> top_right
        stretch handle top_right+(0, 0)

        >>> top_right + 1
        stretch handle top_right+(1, 1)

        >>> top_right + Point(1, 2)
        stretch handle top_right+(1, 2)

        >>> bottom_right + Point(1, 2)
        stretch handle bottom_right+(1, -2)
        """
        vec = _to_vector(offset)
        return PointHandle(self.y + vec.y, self.x + vec.x)

    def __sub__(self, offset: Union[Number, Point]) -> 'PointHandle':
        """
        Create a handle that offsets the corner by a given vector towards the center of
        the shape

        >>> bottom_right - Point(1, 2)
        stretch handle bottom_right+(-1, 2)
        """
        vec = _to_vector(offset)
        return PointHandle(self.y - vec.y, self.x - vec.x)

    def position(self, shape: Any) -> Point:
        """
        Conventience method to access the position of the corner this handle refers to.

        >>> from geometry import Rect
        >>> top_right.position(Rect[0:2, 0:4])
        (2.0, 4.0)
        """
        return Point(self.x.position(shape), self.y.position(shape))

    def __iter__(self) -> Generator[EdgeHandle, None, None]:
        yield self.x
        yield self.y

    def __str__(self) -> str:
        vector = Point(self.x.offset, self.y.offset)
        return f'stretch handle {self.y.name}_{self.x.name}+{vector}'

    def __repr__(self) -> str:
        return self.__str__()


class MultiHandle(NamedTuple):
    name: str
    edges: List[EdgeHandle]

    def __add__(self, offset: Number) -> 'MultiHandle':  # type: ignore
        """
        Create a handle that offsets all edges by a given number away from the
        center of the shape

        >>> out + 1
        stretch handles left-1, right+1, top+1, bottom-1
        """
        return MultiHandle(self.name, [edge + offset for edge in self.edges])

    def __sub__(self, offset: Number) -> 'MultiHandle':
        """
        Create a handle that offsets all edges by a given number towards the
        center of the shape

        >>> width - 1
        stretch handles left+1, right-1
        """
        return MultiHandle(self.name, [edge - offset for edge in self.edges])

    def __iter__(self) -> Generator[EdgeHandle, None, None]:
        yield from self.edges

    def __str__(self) -> str:
        handles = ', '.join(f'{edge.name}{edge.offset:+}' for edge in self.edges)
        return f'stretch handles {handles}'

    def __repr__(self) -> str:
        return self.__str__()


left = EdgeHandle('left', -1)
right = EdgeHandle('right', 1)
bottom = EdgeHandle('bottom', -1)
top = EdgeHandle('top', 1)

top_left = PointHandle(top, left)
top_right = PointHandle(top, right)
bottom_left = PointHandle(bottom, left)
bottom_right = PointHandle(bottom, right)

width = MultiHandle('width', [left, right])
height = MultiHandle('height', [top, bottom])
out = MultiHandle('out', [left, right, top, bottom])
in_ = MultiHandle(
    'in',
    [
        EdgeHandle('left', 1),
        EdgeHandle('right', -1),
        EdgeHandle('bottom', 1),
        EdgeHandle('top', -1),
    ],
)

StretchHandle = Union[EdgeHandle, PointHandle, MultiHandle]
TranslateHandle = Union[EdgeHandle, PointHandle]
