"""Typed boundary for Sage's mature finite-poset implementation."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Protocol

type PartialOrder[Element] = Callable[[Element, Element], bool]
type ExternalPosetConstructor = Any


class ExternalFinitePoset[Element](Protocol):
    """The Sage finite-poset operations used by the owned wrapper."""

    def is_lequal(self, left: Element, right: Element) -> bool: ...

    def is_less_than(self, left: Element, right: Element) -> bool: ...

    def compare_elements(self, left: Element, right: Element) -> int | None: ...

    def covers(self, lower: Element, upper: Element) -> bool: ...

    def lower_covers(self, member: Element) -> Iterable[Element]: ...

    def upper_covers(self, member: Element) -> Iterable[Element]: ...

    def common_lower_covers(self, members: Iterable[Element]) -> Iterable[Element]: ...

    def common_upper_covers(self, members: Iterable[Element]) -> Iterable[Element]: ...

    def open_interval(self, lower: Element, upper: Element) -> Iterable[Element]: ...

    def closed_interval(self, lower: Element, upper: Element) -> Iterable[Element]: ...

    def order_ideal(self, members: Iterable[Element]) -> Iterable[Element]: ...

    def order_filter(self, members: Iterable[Element]) -> Iterable[Element]: ...

    def minimal_elements(self) -> Iterable[Element]: ...

    def maximal_elements(self) -> Iterable[Element]: ...

    def has_bottom(self) -> bool: ...

    def bottom(self) -> Element: ...

    def has_top(self) -> bool: ...

    def top(self) -> Element: ...

    def is_bounded(self) -> bool: ...

    def height(self) -> int: ...

    def width(self) -> int: ...

    def level_sets(self) -> Iterable[Iterable[Element]]: ...

    def is_ranked(self) -> bool: ...

    def is_graded(self) -> bool: ...


class SageFinitePosetBackend[Element]:
    """Use Sage algorithms behind an owned poset object.

    Sage's finite-poset value is an untyped external boundary. It never owns
    placement in the category graph of this package.
    """

    def __init__(
        self,
        members: tuple[Element, ...],
        relation: PartialOrder[Element],
    ) -> None:
        from sage.combinat.posets.posets import Poset

        constructor: ExternalPosetConstructor = Poset
        self._value: ExternalFinitePoset[Element] = constructor(
            (members, relation),
            facade=True,
        )

    def is_lequal(self, left: Element, right: Element) -> bool:
        return self._value.is_lequal(left, right)

    def is_less_than(self, left: Element, right: Element) -> bool:
        return self._value.is_less_than(left, right)

    def compare_elements(self, left: Element, right: Element) -> int | None:
        return self._value.compare_elements(left, right)

    def covers(self, lower: Element, upper: Element) -> bool:
        return self._value.covers(lower, upper)

    def lower_covers(self, member: Element) -> tuple[Element, ...]:
        return tuple(self._value.lower_covers(member))

    def upper_covers(self, member: Element) -> tuple[Element, ...]:
        return tuple(self._value.upper_covers(member))

    def common_lower_covers(
        self,
        members: Iterable[Element],
    ) -> tuple[Element, ...]:
        return tuple(self._value.common_lower_covers(tuple(members)))

    def common_upper_covers(
        self,
        members: Iterable[Element],
    ) -> tuple[Element, ...]:
        return tuple(self._value.common_upper_covers(tuple(members)))

    def open_interval(
        self,
        lower: Element,
        upper: Element,
    ) -> tuple[Element, ...]:
        return tuple(self._value.open_interval(lower, upper))

    def closed_interval(
        self,
        lower: Element,
        upper: Element,
    ) -> tuple[Element, ...]:
        return tuple(self._value.closed_interval(lower, upper))

    def order_ideal(self, members: Iterable[Element]) -> tuple[Element, ...]:
        return tuple(self._value.order_ideal(tuple(members)))

    def order_filter(self, members: Iterable[Element]) -> tuple[Element, ...]:
        return tuple(self._value.order_filter(tuple(members)))

    def minimal_elements(self) -> tuple[Element, ...]:
        return tuple(self._value.minimal_elements())

    def maximal_elements(self) -> tuple[Element, ...]:
        return tuple(self._value.maximal_elements())

    def has_bottom(self) -> bool:
        return self._value.has_bottom()

    def bottom(self) -> Element:
        return self._value.bottom()

    def has_top(self) -> bool:
        return self._value.has_top()

    def top(self) -> Element:
        return self._value.top()

    def is_bounded(self) -> bool:
        return self._value.is_bounded()

    def height(self) -> int:
        return int(self._value.height())

    def width(self) -> int:
        return int(self._value.width())

    def level_sets(self) -> tuple[tuple[Element, ...], ...]:
        return tuple(tuple(level) for level in self._value.level_sets())

    def is_ranked(self) -> bool:
        return self._value.is_ranked()

    def is_graded(self) -> bool:
        return self._value.is_graded()
