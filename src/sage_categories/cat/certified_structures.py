"""Cat-owned constructors for externally certified algebraic structure.

These constructors are for boundaries where another exact representation proves the
algebraic laws (for example a native computer-algebra ring).  Leaves provide ordinary
owned carriers and structure morphisms; all placement into law subcategories remains in
Cat.
"""

from __future__ import annotations

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.monoidal import MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory
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

__all__ = ["certified_additive_group", "certified_commutative_ring_from_operations", "certified_group", "certified_monoid"]


def certified_monoid(
    carrier: CategoryOfCategories.ElementType,
    operation: MorphismCategory.ObjectType,
    unit: MorphismCategory.ObjectType,
    monoidal: MonoidalStructuresCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    """Construct the monoid whose supplied operation/unit are externally certified."""
    magma = Magmas(monoidal).algebra(carrier, operation)
    pointed = PointedMagmas(monoidal.tensor(), monoidal.unit()).algebra(magma, unit)
    refine(pointed, Monoids(monoidal))
    return pointed


def certified_additive_group(
    carrier: CategoryOfCategories.ElementType,
    addition: MorphismCategory.ObjectType,
    zero: MorphismCategory.ObjectType,
    inverse_shear: MorphismCategory.ObjectType,
    monoidal: MonoidalStructuresCategory.ObjectType,
    *,
    commutative: bool = False,
) -> CategoryOfCategories.ElementType:
    """Construct a named additive group from externally certified group operations."""
    monoid = certified_group(carrier, addition, zero, inverse_shear, monoidal)
    group = AdditiveGroups(monoidal).renamed(monoid)
    if commutative:
        refine(group, AdditiveGroups(monoidal).Commutative())
    return group


def certified_group(
    carrier: CategoryOfCategories.ElementType,
    operation: MorphismCategory.ObjectType,
    unit: MorphismCategory.ObjectType,
    inverse_shear: MorphismCategory.ObjectType,
    monoidal: MonoidalStructuresCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    """Construct a group whose laws and supplied inverse-shear map are externally certified."""
    from sage_categories.cat.structured_objects import _shear

    monoid = certified_monoid(carrier, operation, unit, monoidal)
    refine(monoid, Groups(monoidal))
    monoidal.underlying_category().retain_inverses(_shear(monoid), inverse_shear)
    return monoid


def certified_commutative_ring_from_operations(
    base: Category,
    carrier: CategoryOfCategories.ElementType,
    addition: MorphismCategory.ObjectType,
    zero: MorphismCategory.ObjectType,
    multiplication: MorphismCategory.ObjectType,
    one: MorphismCategory.ObjectType,
    monoidal: MonoidalStructuresCategory.ObjectType,
) -> CategoryOfCategories.ElementType:
    """Construct a commutative ring from externally certified ring operations."""
    additive_monoid = certified_monoid(carrier, addition, zero, monoidal)
    refine(additive_monoid, Groups(monoidal))
    additive_monoids = AdditiveMonoids(monoidal)
    additive = additive_monoids.renamed(additive_monoid)
    refine(additive, additive_monoids.Commutative())
    group = AdditiveGroups(monoidal).renamed(additive_monoid)
    refine(group, AdditiveGroups(monoidal).Commutative())

    multiplicative = MultiplicativeMonoids(monoidal).renamed(certified_monoid(carrier, multiplication, one, monoidal))
    semirings = Semirings(base)
    pair = semirings._pairs((additive, multiplicative, carrier))
    refine(pair, semirings)
    rings = Rings(base)
    ring = rings._ring(pair, group, additive)
    refine(ring, rings.Commutative())
    return ring
