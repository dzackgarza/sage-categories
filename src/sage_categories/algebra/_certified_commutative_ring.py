"""Reconstruct commutative rings whose representation certifies the ring laws."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import cast

from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.monoidal import Cartesian, MonoidalStructuresCategory
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.structured_objects import (
    AdditiveGroups,
    AdditiveMonoids,
    Groups,
    Magmas,
    Monoids,
    MultiplicativeMonoids,
    PointedMagmas,
    Rings,
    Semirings,
)
from sage_categories.kernel.refinement import refine


def _certified_monoid(
    carrier: CategoryOfCategories.ElementType,
    operation: MorphismCategory.ObjectType,
    unit: MorphismCategory.ObjectType,
    monoidal: MonoidalStructuresCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    """Raise certified associative/unit operations on ``carrier`` to the owned monoid category."""
    magma = Magmas(monoidal).algebra(carrier, operation)
    pointed = PointedMagmas(monoidal.tensor(), monoidal.unit()).algebra(magma, unit)
    refine(pointed, Monoids(monoidal))
    return cast(CategoryOfCategories.ElementType, pointed)


def _certified_additive_group(
    carrier: CategoryOfCategories.ElementType,
    addition: MorphismCategory.ObjectType,
    zero: MorphismCategory.ObjectType,
    monoidal: MonoidalStructuresCategory.ObjectType,
) -> tuple[CategoryOfCategories.ElementType, CategoryOfCategories.ElementType]:
    """Return the named commutative additive monoid and group certified by the carrier semantics."""
    additive_monoid = _certified_monoid(carrier, addition, zero, monoidal)
    refine(additive_monoid, Groups(monoidal))
    additive_monoids = AdditiveMonoids(monoidal)
    additive = additive_monoids.renamed(additive_monoid)
    refine(additive, additive_monoids.Commutative())
    additive_groups = AdditiveGroups(monoidal)
    group = additive_groups.renamed(additive_monoid)
    refine(group, additive_groups.Commutative())
    return additive, group


def _certified_multiplicative_monoid(
    carrier: CategoryOfCategories.ElementType,
    multiplication: MorphismCategory.ObjectType,
    one: MorphismCategory.ObjectType,
    monoidal: MonoidalStructuresCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    """Return the named multiplicative monoid certified by the carrier semantics."""
    return MultiplicativeMonoids(monoidal).renamed(_certified_monoid(carrier, multiplication, one, monoidal))


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

    additive, group = _certified_additive_group(carrier, addition, zero, monoidal)
    multiplicative = _certified_multiplicative_monoid(carrier, multiplication, one, monoidal)
    semirings = Semirings(Sets)
    pair = semirings._pairs((additive, multiplicative, carrier))
    refine(pair, semirings)
    rings = Rings(Sets)
    ring = rings._ring(pair, group, additive)
    refine(ring, rings.Commutative())
    return cast(CategoryOfCategories.ElementType, ring)
