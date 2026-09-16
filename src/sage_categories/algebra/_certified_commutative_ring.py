"""Reconstruct commutative rings whose representation certifies the ring laws."""

from __future__ import annotations

from collections.abc import Callable, Hashable

from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.certified_structures import certified_commutative_ring_from_operations
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.monoidal import Cartesian
from sage_categories.cat.morphisms import Mor, MorphismCategory


def certified_commutative_ring(
    carrier: CategoryOfCategories.ElementType,
    addition_rule: Callable[[tuple[Hashable, Hashable]], Hashable],
    multiplication_rule: Callable[[tuple[Hashable, Hashable]], Hashable],
    zero_value: Hashable,
    one_value: Hashable,
) -> CategoryOfCategories.ElementType:
    """Build an ordinary commutative ring from semantics that already guarantee its laws."""
    monoidal = Cartesian(Sets)
    product = binary_product_data(Sets, carrier, carrier).apex()
    addition = Mor(Sets)(product, carrier)(addition_rule)
    multiplication = Mor(Sets)(product, carrier)(multiplication_rule)
    zero = Mor(Sets)(monoidal.unit(), carrier)(lambda _: zero_value)
    one = Mor(Sets)(monoidal.unit(), carrier)(lambda _: one_value)

    return certified_commutative_ring_from_operations(
        Sets,
        carrier,
        addition,
        zero,
        multiplication,
        one,
        monoidal,
    )
