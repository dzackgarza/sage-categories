"""Finite slice triangles are owned by GAP SliceCategories."""

from sage_categories.all import Cat
from sage_categories.cat.finite_categories import finite_category
from sage_categories.cat.predicates import Unknown


def test_native_slice_structural_data() -> None:
    base = Cat().Simplex(2)
    category = base.SliceOver(base(2))
    data = finite_category(category)
    assert data is not Unknown
    assert len(data.objects) == 3
    assert len(data.morphisms) == 6
    assert all(any(arrow.domain() is value for value in data.objects) for arrow in data.morphisms)
    assert all(any(arrow.codomain() is value for value in data.objects) for arrow in data.morphisms)


test_native_slice_structural_data()
