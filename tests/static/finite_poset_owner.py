"""The finite-poset owner retains its exact roles through the static projection."""

from collections.abc import Iterator
from typing import assert_type

from sage_categories.order.posets import FinitePosets, FinitePosetsCategory


def finite_poset_owner_roles(
    poset: FinitePosetsCategory.ObjectType,
    point: FinitePosetsCategory.ElementType,
    monotone: FinitePosetsCategory.MorphismType,
) -> None:
    assert_type(FinitePosets(), FinitePosetsCategory)
    assert_type(iter(poset), Iterator[FinitePosetsCategory.ElementType])
    assert_type(poset.point(point.datum()), FinitePosetsCategory.ElementType)
    assert_type(monotone.domain(), FinitePosetsCategory.ObjectType)
    assert_type(monotone.codomain(), FinitePosetsCategory.ObjectType)
