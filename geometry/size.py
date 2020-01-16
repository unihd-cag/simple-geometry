from typing import NamedTuple
from .point import Number


class Size(NamedTuple):
    """
    Size represents a 2d size

    >>> Size(10, 20)
    Size(width=10, height=20)

    This class implements a named Tuple:

    >>> Size(10, 20)[0]
    10

    >>> Size(10, 20)[1]
    20

    Its fields are width and height:

    >>> Size(10, 20).width
    10

    >>> Size(10, 20).height
    20
    """

    width: Number
    height: Number
