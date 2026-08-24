"""Constructors for finite total orders and simplex indexing."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from sage_categories.theories.poset_core import (
    PartiallyOrderedSets,
)
from sage_categories.theories.sets import (
    FiniteSet,
    NaturalNumbers,
    SetElement,
    Sets,
)
from sage_categories.values import MathematicalObject

if TYPE_CHECKING:
    from sage_categories.theories.cardinals import Cardinal

from sage_categories.theories.total_orders import (
    FiniteTotallyOrderedSets,
    TotallyOrderedSets,
)


def ordered_set_owned_by(
    elements: Iterable[SetElement],
) -> MathematicalObject:
    enumeration = tuple(dict.fromkeys(elements))
    underlying_set = FiniteSet(enumeration)
    owned_enumeration = tuple(underlying_set.element(element) for element in enumeration)
    positions: dict[SetElement, int] = {element: index for index, element in enumerate(owned_enumeration)}

    def ordered_relation(left: SetElement, right: SetElement) -> bool:
        return positions[left] <= positions[right]

    finite_total_order = FiniteTotallyOrderedSets().ordered_set(
        underlying_set,
        Sets().relation(
            underlying_set,
            Sets().binary_predicate(underlying_set, ordered_relation),
        ),
    )
    return finite_total_order


def finite_ordered_set(
    elements: Iterable[SetElement],
) -> MathematicalObject:
    return ordered_set_owned_by(elements)


class SimplexOrderIndexing:
    """The canonical total orders ``Delta[n]`` and ``Delta[aleph0]``."""

    def __init__(self) -> None:
        self._countable_simplex: MathematicalObject | None = None

    def __getitem__(self, index: int | Cardinal) -> MathematicalObject:
        from sage_categories.theories.cardinals import is_cardinal
        from sage_categories.theories.ordinals import Ordinals, ordinal

        if is_cardinal(index):
            if index.is_finite() is True:
                maximum = index.finite_value()
            else:
                assert index.is_countably_infinite()
                if self._countable_simplex is None:
                    naturals = NaturalNumbers()

                    def natural_order(
                        left: SetElement,
                        right: SetElement,
                    ) -> bool:
                        left_ordinal = left.value()
                        right_ordinal = right.value()
                        assert Ordinals().contains_ordinal(left_ordinal)
                        assert Ordinals().contains_ordinal(right_ordinal)
                        decision = Ordinals()._is_lequal(left_ordinal, right_ordinal)
                        assert decision is True or decision is False
                        return decision

                    # Theorem: the natural order on ordinals is a total order
                    # (well-ordering of ordinals, Sierpiński §II.7).
                    poset = PartiallyOrderedSets()._ordinal_order(
                        naturals,
                        Sets().relation(
                            naturals,
                            Sets().binary_predicate(naturals, natural_order),
                        ),
                    )

                    self._countable_simplex = TotallyOrderedSets().refine_from_theorem(
                        poset,
                        PartiallyOrderedSets(),
                    )
                return self._countable_simplex
        else:
            maximum = index
        assert maximum >= -1
        naturals = NaturalNumbers()
        return finite_ordered_set(naturals.element(ordinal(position)) for position in range(maximum + 1))

    def __repr__(self) -> str:
        return "Delta"


_SIMPLEX_ORDERS = SimplexOrderIndexing()


def SimplexOrders() -> SimplexOrderIndexing:
    return _SIMPLEX_ORDERS
