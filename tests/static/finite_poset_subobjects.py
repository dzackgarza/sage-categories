"""Finite-poset collection operations retain the owned subobject result domain."""

from typing import assert_type

from sage_categories.cat.predicates import Proposition
from sage_categories.order.posets import (
    FinitePosetsCategory,
    PosetSubobjects,
)


def finite_poset_subobject_surface(
    poset: FinitePosetsCategory.ObjectType,
    member: FinitePosetsCategory.ElementType,
    members: PosetSubobjects.ObjectType,
    subobjects: PosetSubobjects,
) -> None:
    assert_type(subobjects.from_predicate(lambda point: point <= member), PosetSubobjects.ObjectType)
    assert_type(poset.lower_covers(member), PosetSubobjects.ObjectType)
    assert_type(poset.upper_covers(member), PosetSubobjects.ObjectType)
    assert_type(poset.open_interval(member, member), PosetSubobjects.ObjectType)
    assert_type(poset.closed_interval(member, member), PosetSubobjects.ObjectType)
    assert_type(poset.principal_order_ideal(member), PosetSubobjects.ObjectType)
    assert_type(poset.principal_order_filter(member), PosetSubobjects.ObjectType)
    assert_type(poset.order_ideal(members), PosetSubobjects.ObjectType)
    assert_type(poset.order_filter(members), PosetSubobjects.ObjectType)
    assert_type(poset.common_lower_covers(members), PosetSubobjects.ObjectType)
    assert_type(poset.common_upper_covers(members), PosetSubobjects.ObjectType)
    assert_type(poset.minimal_elements(), PosetSubobjects.ObjectType)
    assert_type(poset.maximal_elements(), PosetSubobjects.ObjectType)
    assert_type(poset.is_chain_of_poset(members), Proposition)
    assert_type(poset.is_antichain_of_poset(members), Proposition)
