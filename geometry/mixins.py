from typing import TypeVar, Iterable, Generic, TYPE_CHECKING

Item = TypeVar('Item', contravariant=True)


if TYPE_CHECKING:  # pragma: no cover
    from typing import Protocol

    class HasAppend(Protocol[Item]):
        def append(self, item: Item) -> None:
            ...


else:

    class HasAppend(Generic[Item]):
        pass


class _DummyContainer:
    def append(self, item: int) -> None:
        pass

    def extend(self, items: Iterable[int]) -> None:
        pass

    def extend_star(self, *item: int) -> None:
        pass


container = _DummyContainer()


class AppendMany(HasAppend[Item]):
    def extend(self, items: Iterable[Item]) -> None:
        """
        Append items from an iterable to the collection.

        >>> container.extend([1, 2, 3])

        This is equivalent to

        >>> for item in [1, 2, 3]:
        ...     container.append(item)


        E.g. Groups support these methods

        >>> from geometry import Group, Rect
        >>> g = Group()
        >>> g.extend([Rect[2, 4], Rect[4, 2]])
        >>> g
        {[-1:1, -2:2], [-2:2, -1:1]} ...
        """
        for item in items:
            self.append(item)

    def extend_star(self, *items: Item) -> None:
        """
        Append items from var args

        >>> container.extend_star(1, 2, 3)

        This is equivalent to

        >>> for item in [1, 2, 3]:
        ...     container.append(item)

        E.g. Groups support these methods

        >>> from geometry import Group, Rect
        >>> g = Group()
        >>> g.extend_star(Rect[2, 4], Rect[4, 2])
        >>> g
        {[-1:1, -2:2], [-2:2, -1:1]} ...
        """
        self.extend(items)
