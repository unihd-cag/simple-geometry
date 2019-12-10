from typing import Any, Generator, List, Union, Optional, Callable, Dict

from .point import Number
from .rect import Rect
from .group import Group
from .path import Segment
from .mixins import AppendMany

Shape = Union[Rect, Group, Segment]


class Html:
    """
    Helper class to represent and manipulate html elements.

    >>> Html('div', background='red')
    <div style="background: red"></div>

    Integers are converted to 'px'

    >>> Html('div', margin=10)
    <div style="margin: 10px"></div>
    """

    _attrs = {'element', 'style'}

    def __init__(self, element: str, **style: Any) -> None:
        self.element = element
        self.style = style

    def __getattr__(self, key: str) -> Any:
        """
        Read a style attribute

        >>> Html('div', background='red').background
        'red'

        >>> Html('div').background is None
        True
        """
        return self.style.get(key)

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Change the style properties or regular attributes of the class

        >>> html = Html.div()
        >>> html.element = 'p'
        >>> html
        <p style=""></p>

        >>> html.background = 'red'
        >>> html
        <p style="background: red"></p>
        """
        if key in Html._attrs:
            super().__setattr__(key, value)
        else:
            self.style[key] = value

    @classmethod
    def div(cls, **style: Any) -> 'Html':
        """
        Shortcut to create a div element

        >>> Html.div()
        <div style=""></div>
        """
        return Html('div', **style)

    def update(self, **kwargs: Any) -> None:
        """
        Dict like method to update the style properties

        >>> html = Html.div()
        >>> html.update(background='red')
        >>> html
        <div style="background: red"></div>
        """
        self.style.update(**kwargs)

    @staticmethod
    def _key(key: str) -> str:
        return key.replace('_', '-')

    @staticmethod
    def _value(value: Any) -> str:
        if isinstance(value, (int, float)):
            return f'{value}px'
        return str(value)

    def open(self) -> str:
        """
        The opening tag of the html element

        >>> Html.div().open()
        '<div style="">'
        """
        style = '; '.join(
            f'{Html._key(key)}: {Html._value(value)}' for key, value in self.style.items()
        )
        return f'<{self.element} style="{style}">'

    def close(self) -> str:
        """
        The closing tag of the html element

        >>> Html.div().close()
        '</div>'
        """
        return f'</{self.element}>'

    def open_close(self) -> str:
        return self._repr_html_()

    def _repr_html_(self) -> str:
        return self.open() + self.close()

    def __str__(self) -> str:
        return self.open_close()

    def __repr__(self) -> str:
        return self.__str__()


StyleGetterTarget = Union[str, Dict[str, Union[str, int]]]
StyleGetterCallable = Callable[[Any], StyleGetterTarget]
StyleGetterDict = Dict[Any, StyleGetterTarget]
StyleGetter = Union[StyleGetterCallable, StyleGetterDict]


class Canvas(AppendMany[Shape]):
    """
    A Canvas that can hold different shapes or groups of shapes and display them
    as html.

    >>> Canvas(100, 200).html()
    '<div style="position: relative; width: 100px; height: 200px">...

    You may pass a scale factor that will be applied to the canvas itself and all
    shapes that will be added

    >>> Canvas(10, 20, scale=2).html()
    '<div style="position: relative; width: 20px; height: 40px">...

    You can use the user_data field for style and color information

    >>> c = Canvas(100, 200)
    >>> c.append(Rect[20, 40, 'red'])
    >>> 'background: red' in c.html()
    True

    By default the shapes are displayed in black

    >>> c = Canvas(100, 200)
    >>> c.append(Rect[20, 40])
    >>> 'background: black' in c.html()
    True

    The user_data may also be a dictionary of css attributes

    >>> c = Canvas(100, 200)
    >>> c.append(Rect[20, 40, {'background': 'none', 'border': '1px solid yellow'}])
    >>> 'background: none' in c.html() and 'border: 1px solid yellow' in c.html()
    True

    Segments are rendered like rects with an additional line indicating the orientation

    >>> from geometry import Point
    >>> c = Canvas(100, 200)
    >>> c.append(Segment.from_start_end(Point(0, 0), Point(0, 100), 2))
    >>> 'height: 100%' in c.html()  # the vertical line
    True

    >>> c = Canvas(100, 200)
    >>> c.append(Segment.from_start_end(Point(0, 0), Point(100, 0), 2))
    >>> 'width: 100%' in c.html()  # the horizontal line
    True

    Groups are rendered as if the children were passed to the canvas individually

    >>> rect = Rect[20, 40]
    >>> segment = Segment.from_start_end(Point(0, 0), Point(10, 0), 2)
    >>> group = Group([rect, segment])
    >>> with_group = Canvas(100, 200)
    >>> with_group.append(group)
    >>> no_group = Canvas(100, 200)
    >>> no_group.append(rect)
    >>> no_group.append(segment)
    >>> with_group.html() == no_group.html()
    True

    If you try to render anything else, an error is raised

    >>> c = Canvas(100, 200)
    >>> c.append("This is not allowed")
    >>> c.html()
    Traceback (most recent call last):
    ...
    ValueError: cannot draw unknown shape of class <class 'str'>
    """

    def __init__(self, width: Number, height: Number, scale: Number = 1, **style: Any) -> None:
        self.scale = scale
        self.width = width
        self.height = height
        width *= scale
        height *= scale
        self.container = Html.div(position='relative', width=width, height=height)
        self.container.update(**style)
        self.axes = [
            Html.div(
                position='absolute',
                width=width / 2,
                height=height / 2,
                border='1px dotted black',
                box_sizing='border-box',
            )
            for _ in range(4)
        ]
        self.axes[0].left = 0
        self.axes[0].bottom = 0
        self.axes[1].right = 0
        self.axes[1].bottom = 0
        self.axes[2].left = 0
        self.axes[2].top = 0
        self.axes[3].right = 0
        self.axes[3].top = 0

        self.shapes: List[Shape] = []
        self._style_getter = lambda user_data: user_data
        self.default_color = 'black'
        self.default_line_color = 'white'

    @property
    def style_getter(self) -> StyleGetterCallable:
        """
        The style_getter is a function that turns the user data of a shape into something
        that can be used as an html style.

        The default style_getter just returns the user data as is.

        >>> c = Canvas(100, 200)
        >>> c.style_getter(Rect[2, 4, 'red'].user_data)
        'red'

        Two types of object are allowed to be returned by the style_getter:
        - str: this will be used as html color for the background
        - dict: this will be used as the complete css style of the element

        >>> always_blue = lambda user_data: 'blue'
        >>> c.style_getter = always_blue
        >>> c.style_getter(Rect[2, 4].user_data)
        'blue'

        The style_getter may also be a dictionary that maps user_data to a style

        >>> opposite = {'red': 'green', 'blue': 'yellow'}
        >>> c.style_getter = opposite
        >>> c.style_getter(Rect[2, 4, 'red'].user_data)
        'green'

        Anything else is not allowed

        >>> c.style_getter = 'blue'
        Traceback (most recent call last):
        ...
        ValueError: style getter must be either dict or callable
        """
        return self._style_getter

    @style_getter.setter
    def style_getter(self, new_getter: StyleGetterDict) -> None:
        if isinstance(new_getter, dict):

            def new_getter_function(user_data: Any) -> StyleGetterTarget:
                return new_getter.get(user_data, self.default_color)

            self._style_getter = new_getter_function
        elif callable(new_getter):
            self._style_getter = new_getter
        else:
            raise ValueError("style getter must be either dict or callable")

    def append(self, shape: Shape) -> None:
        """
        Add one shape to the Canvas

        >>> c = Canvas(100, 200)
        >>> c.append(Rect[2, 4])
        >>> len(c.shapes)
        1
        """
        self.shapes.append(shape)

    def __iadd__(self, shape: Rect) -> 'Canvas':
        """
        Operator version of Canvas.append

        >>> c = Canvas(100, 200)
        >>> c += Rect[2, 4]
        >>> len(c.shapes)
        1
        """
        self.append(shape)
        return self

    def _set_style(self, div: Html, user_data: Any, prefix: str, default: str) -> None:
        style = self.style_getter(user_data)

        if isinstance(style, str):
            div.update(background=style)
        elif isinstance(style, dict):
            div.update(**{key: value for key, value in style.items() if key.startswith(prefix)})

        div.background = div.background or default

    def _rect(self, rect: Union[Rect, Segment]) -> Generator[str, None, None]:
        left = (rect.left + self.width / 2) * self.scale
        bottom = (rect.bottom + self.height / 2) * self.scale
        width = rect.width * self.scale
        height = rect.height * self.scale
        div = Html.div(position='absolute', left=left, bottom=bottom, width=width, height=height)

        div.box_sizing = 'border-box'
        self._set_style(div, rect.user_data, '', self.default_color)
        inner_code = ""

        if isinstance(rect, Segment):
            div.display = 'flex'
            div.align_items = 'center'
            div.justify_content = 'center'

            line = Html.div()
            if rect.direction.is_horizontal:
                line.width = '100%'
                line.height = 2
            else:
                line.width = 2
                line.height = '100%'

            self._set_style(line, rect.user_data, 'path', self.default_line_color)
            inner_code = line.open_close()
        yield div.open()
        yield inner_code
        yield div.close()

    def _shapes(self, shapes: Optional[List[Shape]] = None) -> Generator[str, None, None]:
        if shapes is None:
            shapes = self.shapes

        for shape in shapes:
            if isinstance(shape, (Rect, Segment)):
                yield from self._rect(shape)
            elif isinstance(shape, Group):
                yield from self._shapes(shape.shapes)
            else:
                raise ValueError(f"cannot draw unknown shape of class {shape.__class__}")

    def _repr_html_(self) -> str:
        return '\n'.join(
            (
                self.container.open(),
                *(axis.open_close() for axis in self.axes),
                *self._shapes(),
                self.container.close(),
            )
        )

    def html(self) -> str:
        return self._repr_html_()
