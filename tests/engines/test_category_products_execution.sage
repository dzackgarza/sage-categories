"""Finite products in Cat execute through CAP ProductCategory."""

from sage_categories.all import Cat
from sage_categories.cat.finite_categories import finite_category
from sage_categories.cat.predicates import Unknown


def test_native_category_product_structural_data() -> None:
    first, second = Cat().Simplex(1), Cat().Simplex(2)
    product = Cat().Products()((first, second))
    data = finite_category(product)
    assert data is not Unknown
    assert len(data.objects) == 6
    assert len(data.morphisms) == 18
    assert all(
        any(morphism.domain() is value for value in data.objects)
        and any(morphism.codomain() is value for value in data.objects)
        for morphism in data.morphisms
    )
    assert any(
        value.family_component(0) is first(1)
        and value.family_component(1) is second(2)
        for value in data.objects
    )


test_native_category_product_structural_data()
