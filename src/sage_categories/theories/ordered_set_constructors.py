"""Constructors for finite total orders and simplex indexing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.theories.sets import (
    EnumerationInjection,
    FiniteSet,
    NaturalNumbers,
)
from sage_categories.values import MathematicalObject

if TYPE_CHECKING:
    from sage_categories.theories.cardinals import Cardinal

from sage_categories.theories.total_orders import (
    FiniteTotallyOrderedSets,
    TotallyOrderedSets,
)


class SimplexOrderIndexing:
    """The canonical total orders ``Delta[n]`` and ``Delta[aleph0]``."""

    def __init__(self) -> None:
        self._countable_simplex: MathematicalObject | None = None

    def __getitem__(self, index: int | Cardinal) -> MathematicalObject:
        from sage_categories.theories.cardinals import is_cardinal
        from sage_categories.theories.ordinals import ordinal

        if is_cardinal(index):
            if index.is_finite() is True:
                maximum = index.finite_value()
            else:
                assert index.is_countably_infinite()
                if self._countable_simplex is None:
                    self._countable_simplex = (
                        TotallyOrderedSets().natural_numbers_order()
                    )
                return self._countable_simplex
        else:
            maximum = index
        assert maximum >= -1
        naturals = NaturalNumbers()
        values = tuple(
            naturals.element(ordinal(position))
            for position in range(maximum + 1)
        )
        underlying_set = FiniteSet(values)
        positions = {value: position for position, value in enumerate(values)}
        enumeration = EnumerationInjection(
            underlying_set,
            lambda member: positions[member.value()],
        )
        return FiniteTotallyOrderedSets()(enumeration)

    def __repr__(self) -> str:
        return "Delta"


_SIMPLEX_ORDERS = SimplexOrderIndexing()


def SimplexOrders() -> SimplexOrderIndexing:
    return _SIMPLEX_ORDERS
