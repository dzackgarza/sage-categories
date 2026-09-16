"""Finite-poset invariants retain their exact owned result domains statically."""

from typing import assert_type

from sage_categories.cat.functors import Functor
from sage_categories.cat.predicates import Proposition
from sage_categories.order.posets import (
    FiniteGradedPosetsCategory,
    FinitePosetsCategory,
    FinitePosetsWithBottomCategory,
    FinitePosetsWithTopCategory,
    FiniteRankedPosetsCategory,
    FiniteTotallyOrderedSetsCategory,
)
from sage_categories.sets.cardinals import CardinalCategory


def finite_poset_invariant_surface(
    poset: FinitePosetsCategory.ObjectType,
    member: FinitePosetsCategory.ElementType,
    ranked: FiniteRankedPosetsCategory.ObjectType,
    graded: FiniteGradedPosetsCategory.ObjectType,
    with_bottom: FinitePosetsWithBottomCategory.ObjectType,
    with_top: FinitePosetsWithTopCategory.ObjectType,
) -> None:
    assert_type(poset.covers(member, member), Proposition)
    assert_type(poset.height(), CardinalCategory.ObjectType)
    assert_type(poset.width(), CardinalCategory.ObjectType)
    assert_type(poset.linear_extension(), FiniteTotallyOrderedSetsCategory.ObjectType)
    assert_type(ranked.rank_of_element(member), CardinalCategory.ObjectType)
    assert_type(ranked.rank(), CardinalCategory.ObjectType)
    assert_type(ranked.level_sets(), Functor)
    assert_type(graded.rank(), CardinalCategory.ObjectType)
    assert_type(with_bottom.bottom(), FinitePosetsCategory.ElementType)
    assert_type(with_top.top(), FinitePosetsCategory.ElementType)
