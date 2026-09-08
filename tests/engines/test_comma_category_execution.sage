"""Finite comma structural data execute through the retained native pullback."""

from sage_categories.all import Cat, Fun
from sage_categories.cat.finite_categories import finite_category
from sage_categories.cat.predicates import Unknown


def test_native_comma_of_identity_functors() -> None:
    base = Cat().Simplex(1)
    identity = Fun(base, base).one()
    comma = Cat().Comma(identity, identity)
    data = finite_category(comma)
    assert data is not Unknown
    assert len(data.objects) == 3
    assert len(data.morphisms) == 6
    assert all(value.first() in base and value.second() in base for value in data.objects)
    assert all(value.arrow() in base.morphism_category(1) for value in data.objects)


test_native_comma_of_identity_functors()
