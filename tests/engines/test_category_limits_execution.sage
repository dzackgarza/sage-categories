"""Finite non-discrete limits in Cat use native finite-set compatibility."""

from sage_categories.all import Cat, Fun
from sage_categories.cat.cat_constructions import limit_of_categories
from sage_categories.cat.finite_categories import finite_category
from sage_categories.cat.predicates import Unknown


def test_native_structural_limit_of_constant_arrow_diagram() -> None:
    shape, base = Cat().Simplex(1), Cat().Simplex(2)
    diagram = Fun(shape, Cat()).constant(base)
    limit = limit_of_categories(diagram, Cat().Limits(shape))
    data = finite_category(limit)
    assert data is not Unknown
    assert len(data.objects) == 3
    assert len(data.morphisms) == 6
    assert all(
        value.family_component(shape(0)) is value.family_component(shape(1))
        for value in data.objects
    )
    assert all(
        value.family_component(shape(0)) is value.family_component(shape(1))
        for value in data.morphisms
    )


test_native_structural_limit_of_constant_arrow_diagram()
