"""The subobject families: monomorphisms into ``x`` as objects of ``C.SliceOver(x)``, covering objects as pairs, subobjects of a product.

Oracles: a subobject of ``x`` is a monomorphism into ``x`` and monomorphisms of sets
are the injective maps (POL-FUN-013, Mathlib ``CategoryTheory.mono_iff_injective``);
a covering object of ``y`` is the pair ``(X, p: X -> y)`` with ``p`` an epimorphism
(POL-CAT-026); a subobject ``j: S -> P`` of a product apex has components
``pi_i * j`` (POL-CAT-094).
"""

import pytest

from sage_categories.all import *
from sage_categories.cat.properties import PropertySubcategory


def test_a_monomorphism_into_x_is_a_subobject_and_a_non_monomorphism_is_not() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    include = Mor(Sets())(two, three)(lambda datum: datum)
    collapse = Mor(Sets())(three, three)(lambda datum: min(datum, int(1)))
    parity = Mor(Sets())(three, two)(lambda datum: datum % int(2))
    subobjects = three.subobjects()

    assert subobjects is Sets().Subobjects()(three)
    assert include in Sets().Subobjects()
    assert collapse not in Sets().Subobjects()
    assert include in subobjects
    assert collapse not in subobjects
    assert ask(subobjects.membership_proposition(collapse)) is False
    assert parity not in subobjects
    presented = subobjects(include)
    assert presented in subobjects
    assert presented in Sets().SliceOver(three)
    assert presented.first() is include
    assert Sets().SliceOver(three).fixed_projection().on_object(presented) is two
    with pytest.raises(AssertionError):
        subobjects(collapse)

    increment = Mor(Sets())(ZZ, ZZ)(lambda datum: datum + int(1))
    assert ask(ZZ.subobjects().membership_proposition(increment)) is Unknown
    assert ZZ.subobjects()(increment).first() is increment


def test_a_covering_object_is_the_pair_of_the_object_with_its_epimorphism() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    parity = Mor(Sets())(three, two)(lambda datum: datum % int(2))
    include = Mor(Sets())(two, three)(lambda datum: datum)
    coverings = two.covering_objects()

    assert parity in coverings
    assert include not in three.covering_objects()
    covering = coverings(parity)
    assert covering in coverings
    assert covering.first() is parity
    assert Sets().SliceOver(two).fixed_projection().on_object(covering) is three
    assert covering is not parity

    superobjects = two.superobjects()
    assert include in superobjects
    assert parity not in three.superobjects()
    assert superobjects(include).first() is include
    assert Sets().CosliceUnder(two).fixed_projection().on_object(superobjects(include)) is three
    assert parity in three.covered_objects()
    assert three.covered_objects()(parity).first() is parity


def test_a_subobject_of_a_product_of_categories_derives_its_component_functors() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    successor = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    arrow = Cat().Simplex(int(1))
    product = Cat().Products()((arrow, Sets()))
    chosen = PropertySubcategory(product, "Chosen", {}, ())
    monomorphism = chosen.selected_functors()[int(0)]
    subobjects = Cat().Products().ChosenSubobjects()

    presented = subobjects(monomorphism)
    assert presented in subobjects
    assert presented is chosen
    assert presented.monomorphism() is monomorphism
    assert presented.product() is product
    component = presented.product_projection(int(1))
    assert component in Fun(chosen, Sets())
    assert component.domain() is chosen and component.codomain() is Sets()
    pair = chosen(product((arrow(int(0)), two)))
    other = chosen(product((arrow(int(1)), three)))
    assert component.on_object(pair) is two
    assert presented.product_projection(int(0)).on_object(other) is arrow(int(1))
    morphism = Mor(chosen)(pair, other)((arrow.generator("0->1"), successor))
    assert component.on_morphism(morphism) is successor
