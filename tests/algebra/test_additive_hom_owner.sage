"""Exact Ab Hom ownership survives the forgetful map on a nonidentity arrow."""

import pytest
from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup

from sage_categories.algebra import (
    AbelianGroups,
    abelian_homomorphism,
    integer_group,
    presented_abelian_group,
)
from sage_categories.cat.monoidal import Cartesian
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.structured_objects import AdditiveGroups
from sage_categories.sets.finite import Sets


def test_additive_hom_owner_and_forgetful_image() -> None:
    abelian = AbelianGroups()
    integers = integer_group()
    engine = AdditiveAbelianGroup([4])
    cyclic = presented_abelian_group(engine)
    generator = engine.gen(0)

    reduction = abelian_homomorphism(integers, cyclic, lambda value: 3 * value * generator)
    assert reduction in Mor(abelian)(integers, cyclic)
    assert reduction.base_category() is abelian
    assert reduction.domain() is integers
    assert reduction.codomain() is cyclic

    groups = AdditiveGroups(Cartesian(Sets()))
    monoids = groups.named_monoids()
    magmas = monoids.named_magmas()
    forgetful = magmas.to_carrier() * monoids.to_named_magmas() * groups.to_named_monoids() * abelian.subcategory_monomorphism()
    source = forgetful.on_object(integers)
    target = forgetful.on_object(cyclic)
    image = forgetful.on_morphism(reduction)
    assert image.domain() is source
    assert image.codomain() is target
    assert image(source.point(1)) is target.point(3 * generator)
    assert image(source.point(2)) is target.point(2 * generator)
    assert image(source.point(4)) is target.point(engine.zero())
    assert image in Mor(Sets)(source, target)


def test_presented_homomorphism_relations_are_checked_by_cap() -> None:
    source_engine = AdditiveAbelianGroup([2])
    target_engine = AdditiveAbelianGroup([4])
    source = presented_abelian_group(source_engine)
    target = presented_abelian_group(target_engine)
    with pytest.raises(AssertionError):
        abelian_homomorphism(source, target, lambda _value: target_engine.gen(0))


test_additive_hom_owner_and_forgetful_image()
test_presented_homomorphism_relations_are_checked_by_cap()
