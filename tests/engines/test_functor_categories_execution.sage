"""Finite arrow-category naturality is owned by GAP FunctorCategories."""

from sage_categories.all import Cat, Fun
from sage_categories.cat.finite_categories import finite_category
from sage_categories.cat.predicates import Unknown


def test_native_arrow_category_structural_data() -> None:
    category = Fun(Cat().Simplex(1), Cat().Simplex(2))
    data = finite_category(category)
    assert data is not Unknown
    assert len(data.objects) == 6
    assert len(data.morphisms) == 20
    assert all(any(morphism.domain() is value for value in data.objects) for morphism in data.morphisms)
    assert all(any(morphism.codomain() is value for value in data.objects) for morphism in data.morphisms)


test_native_arrow_category_structural_data()
