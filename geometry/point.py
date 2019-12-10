from typing import Union, Tuple, NamedTuple

Number = Union[int, float]
TuplePoint = Tuple[Number, Number]


class Point(NamedTuple):
    """
    Represents a 2D point in space, consisting of an x- and a y-coordinate

    >>> Point(10, 20)
    (10, 20)

    Vector is an alias for the Point type

    >>> Vector(4, 5)
    (4, 5)

    This class is implemented as a NamedTuple. This means:

    You can use it like a tuple

    >>> Point(4, 5)[0]
    4

    Its fields are named

    >>> Point(4, 5).x
    4
    >>> Point(4, 5).y
    5

    It is immutable

    >>> p = Point(4, 5)
    >>> p[0] = 0
    Traceback (most recent call last):
    ...
    TypeError: 'Point' object does not support item assignment
    """

    x: Number
    y: Number

    def __add__(self, point: 'Point') -> 'Point':  # type: ignore
        """
        Add two points component wise

        >>> Point(10, 20) + Point(100, 200)
        (110, 220)
        """
        return Point(self.x + point.x, self.y + point.y)

    def __sub__(self, point: 'Point') -> 'Point':
        """
        Subtract two points component wise

        >>> Point(10, 20) - Point(1, 2)
        (9, 18)
        """
        return Point(self.x - point.x, self.y - point.y)

    def __mul__(self, factor: Number) -> 'Point':
        """
        Multiply a point with a factor

        >>> Point(2, 3) * 4
        (8, 12)
        """
        return Point(self.x * factor, self.y * factor)

    def __rmul__(self, factor: Number) -> 'Point':
        """
        Multiply a point with a factor from the left

        >>> 4 * Point(2, 3)
        (8, 12)
        """
        return Point(self.x * factor, self.y * factor)

    def __floordiv__(self, factor: Number) -> 'Point':
        """
        Divide the components of a point by a factor (floor division)

        >>> Point(2, 3) // 2
        (1, 1)
        """
        return Point(self.x // factor, self.y // factor)

    def __truediv__(self, factor: Number) -> 'Point':
        """
        Divide the components of a point by a factor

        >>> Point(2, 3) / 2
        (1.0, 1.5)
        """
        return Point(self.x / factor, self.y / factor)

    def __matmul__(self, other: 'Point') -> Number:
        """
        Multiply two points (dot product)

        >>> Point(1, 2) @ Point(2, 3)
        8
        """
        return self.x * other.x + self.y * other.y

    def __neg__(self) -> 'Point':
        """
        Negate the components of a point

        >>> -Point(1, 2)
        (-1, -2)
        """
        return Point(-self.x, -self.y)

    def __abs__(self) -> Number:
        """
        The absolute value of a point: the length of the point

        >>> abs(Point(3, 4))
        5.0
        """
        return (self.x ** 2 + self.y ** 2) ** 0.5

    @property
    def yx(self) -> 'Point':
        """
        Transpose a point, i.e. flip x and y

        >>> Point(1, 2).yx
        (2, 1)
        """
        return Point(self.y, self.x)

    @property
    def length(self) -> Number:
        """
        The length of the point

        >>> Point(3, 4).length
        5.0
        """
        return (self.x ** 2 + self.y ** 2) ** 0.5

    @property
    def normalized(self) -> 'Point':
        """
        Return a copy of the point with the same direction but length 1.0

        >>> Point(1, 1).normalized
        (0.707..., 0.707...)
        """
        return self / self.length

    def __repr__(self) -> str:
        return f"({self.x!r}, {self.y!r})"


origin = Point(0, 0)
left = Point(-1, 0)
right = Point(1, 0)
down = Point(0, -1)
up = Point(0, 1)

Vector = Point
