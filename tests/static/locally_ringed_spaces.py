"""Static projection for the locally ringed-space owner."""

from typing import assert_type, cast

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Proposition
from sage_categories.geometry.locally_ringed_spaces import (
    LocallyRingedSpaces,
    LocallyRingedSpacesCategory,
)
from sage_categories.geometry.ringed_spaces import RingedSpacesCategory
from sage_categories.geometry.sheaves import RingSheaf
from sage_categories.geometry.spaces import TopologicalSpacesCategory


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


def stalk_rule(
    point: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    return point


def stalk_map_rule(
    _point: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    return cast(MorphismCategory.ObjectType, object())


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
    assert_type(arrow.sheaf_map(), NaturalTransformation)
    assert_type(arrow.continuous_map(), TopologicalSpacesCategory.MorphismType)
    assert_type(arrow.local_map_condition(point), Proposition)
    explicit = locally.with_stalks(ringed_space, stalk_rule, local_ring_rule)
    assert_type(explicit, LocallyRingedSpacesCategory.ObjectType)
    explicit_arrow = locally.homomorphism_with_stalks(
        explicit,
        explicit,
        ringed_map,
        stalk_map_rule,
        local_map_rule,
    )
    assert_type(explicit_arrow, LocallyRingedSpacesCategory.MorphismType)
    assert_type(explicit_arrow.stalk_map(point), MorphismCategory.ObjectType)
    assert_type(locally.to_ringed_spaces(), Functor)


def locally_ringed_open_key_types(
    ringed_space: RingedSpacesCategory.ObjectType[tuple[str, int]],
) -> None:
    locally = LocallyRingedSpaces()
    value = locally(ringed_space, local_ring_rule)
    assert_type(value, LocallyRingedSpacesCategory.ObjectType[tuple[str, int]])
    assert_type(value.ringed_space(), RingedSpacesCategory.ObjectType[tuple[str, int]])
    assert_type(value.space(), TopologicalSpacesCategory.ObjectType[tuple[str, int]])
    assert_type(value.sheaf(), RingSheaf[tuple[str, int]])
    assert_type(
        value.sheaf().presheaf.section_ring(("chart", 2)),
        CategoryOfCategories.ElementType,
    )
    explicit = locally.with_stalks(ringed_space, stalk_rule, local_ring_rule)
    assert_type(explicit, LocallyRingedSpacesCategory.ObjectType[tuple[str, int]])
    assert_type(explicit.sheaf(), RingSheaf[tuple[str, int]])
