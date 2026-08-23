"""Constructors for finite total orders and simplex indexing."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from sage_categories.theories.poset_core import (
    PartiallyOrderedSets,
    PosetElement,
)
from sage_categories.theories.sets import (
    FiniteSet,
    NaturalNumbers,
    SetElement,
    SetElements,
)
from sage_categories.values import (
    UNKNOWN,
    MathematicalObject,
)

if TYPE_CHECKING:
    from sage_categories.theories.cardinals import Cardinal

from sage_categories.theories.total_orders import (
    _ORDERED_FINITE_SETS,
    FiniteTotallyOrderedSetObject,
    FiniteTotallyOrderedSets,
    TotallyOrderedSetObject,
    TotallyOrderedSets,
)


def ordered_set_owned_by(
    elements: Iterable[SetElement],
) -> FiniteTotallyOrderedSetObject:
    enumeration = tuple(dict.fromkeys(elements))
    cached = _ORDERED_FINITE_SETS.get(enumeration)
    if cached is None:
        underlying_set = FiniteSet(enumeration)
        owned_enumeration = tuple(
            underlying_set.element(element) for element in enumeration
        )
        positions: dict[SetElement, int] = {
            element: index for index, element in enumerate(owned_enumeration)
        }

        def ordered_relation(left: PosetElement, right: PosetElement) -> bool:
            forgetful_functor = PartiallyOrderedSets().forgetful_functor()
            left_element = forgetful_functor.on_element(left.ambient_poset(), left)
            right_element = forgetful_functor.on_element(right.ambient_poset(), right)
            assert SetElements().contains_set_element(left_element)
            assert SetElements().contains_set_element(right_element)
            return positions[left_element] <= positions[right_element]

        poset = PartiallyOrderedSets()(
            underlying_set,
            ordered_relation,
        )
        poset_enumeration = tuple(
            poset.element(element) for element in owned_enumeration
        )

        def position_of(member: PosetElement) -> int:
            forgetful_functor = PartiallyOrderedSets().forgetful_functor()
            set_member = forgetful_functor.on_element(member.ambient_poset(), member)
            assert SetElements().contains_set_element(set_member)
            return positions[set_member]

        total_order = TotallyOrderedSets()(
            poset,
            poset_enumeration.__getitem__,
            position_of,
            finite_enumeration=poset_enumeration,
        )
        assert FiniteTotallyOrderedSets().contains_finite_total_order(total_order)
        cached = total_order
        _ORDERED_FINITE_SETS[enumeration] = cached
    return cached


def finite_ordered_set(
    elements: Iterable[SetElement],
) -> FiniteTotallyOrderedSetObject:
    return ordered_set_owned_by(elements)


class SimplexOrderIndexing:
    """The canonical total orders ``Delta[n]`` and ``Delta[aleph0]``."""

    def __init__(self) -> None:
        self._countable_simplex: TotallyOrderedSetObject | None = None

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
                        left: PosetElement,
                        right: PosetElement,
                    ) -> bool:
                        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
                        left_element = forgetful_functor.on_element(
                            left.ambient_poset(), left
                        )
                        right_element = forgetful_functor.on_element(
                            right.ambient_poset(), right
                        )
                        assert SetElements().contains_set_element(left_element)
                        assert SetElements().contains_set_element(right_element)
                        left_ordinal = left_element.value()
                        right_ordinal = right_element.value()
                        assert Ordinals().contains_ordinal(left_ordinal)
                        assert Ordinals().contains_ordinal(right_ordinal)
                        decision = Ordinals()._is_lequal(left_ordinal, right_ordinal)
                        assert decision is not UNKNOWN
                        return decision

                    poset = PartiallyOrderedSets()(naturals, natural_order)

                    def natural_element(position: int) -> PosetElement:
                        return poset.element(naturals[position])

                    def natural_position(member: PosetElement) -> int:
                        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
                        set_member = forgetful_functor.on_element(
                            member.ambient_poset(), member
                        )
                        assert SetElements().contains_set_element(set_member)
                        return naturals.position(set_member)

                    self._countable_simplex = TotallyOrderedSets()(
                        poset,
                        natural_element,
                        natural_position,
                    )
                return self._countable_simplex
        else:
            maximum = index
        assert maximum >= -1
        naturals = NaturalNumbers()
        return finite_ordered_set(
            naturals.element(ordinal(position)) for position in range(maximum + 1)
        )

    def __repr__(self) -> str:
        return "Delta"


_SIMPLEX_ORDERS = SimplexOrderIndexing()


def SimplexOrders() -> SimplexOrderIndexing:
    return _SIMPLEX_ORDERS
