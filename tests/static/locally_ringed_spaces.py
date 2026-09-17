"""Static projection for the locally ringed-space owner."""

from typing import assert_type, cast

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Proposition
from sage_categories.geometry.locally_ringed_spaces import (
    LocallyRingedSpaces,
    LocallyRingedSpacesCategory,
)
from sage_categories.geometry.ringed_spaces import RingedSpacesCategory


def local_ring_rule(
    _point: CategoryOfCategories.ElementType,
    _stalk: CategoryOfCategories.ElementType,
) -> Proposition:
    return cast(Proposition, True)


def local_map_rule(
    _point: CategoryOfCategories.ElementType,
    _mapping: MorphismCategory.ObjectType,
) -> Proposition:
    return cast(Proposition, True)


def locally_ringed_types(
    ringed_space: RingedSpacesCategory.ObjectType,
    ringed_map: RingedSpacesCategory.MorphismType,
    point: CategoryOfCategories.ElementType,
) -> None:
    locally = LocallyRingedSpaces()
    assert_type(locally, LocallyRingedSpacesCategory)
    value = locally(ringed_space, local_ring_rule)
    assert_type(value, LocallyRingedSpacesCategory.ObjectType)
    assert_type(value.stalk(point), CategoryOfCategories.ElementType)
    assert_type(value.local_ring_condition(point), Proposition)
    arrow = locally.homomorphism(
        value,
        value,
        ringed_map,
        local_map_rule,
    )
    assert_type(arrow, LocallyRingedSpacesCategory.MorphismType)
    assert_type(arrow.stalk_map(point), MorphismCategory.ObjectType)
    assert_type(arrow.local_map_condition(point), Proposition)
    assert_type(locally.to_ringed_spaces(), Functor)
