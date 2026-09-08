"""Finite Grothendieck structural data execute through native finite-set joins."""

from sage_categories.all import Cat, Fun, Grothendieck, IndexedCategories
from sage_categories.cat.finite_categories import finite_category
from sage_categories.cat.predicates import Unknown


def test_constant_indexed_category_uses_native_total_join() -> None:
    base, fiber = Cat().Simplex(1), Cat().Simplex(1)
    identity = Fun(fiber, fiber).one()
    diagram = Fun(base.op(), Cat())(
        lambda vertex: fiber,
        lambda arrow: identity,
    )
    total = Grothendieck(IndexedCategories(base).strict(diagram))
    data = finite_category(total)
    assert data is not Unknown
    assert len(data.objects) == 4
    assert len(data.morphisms) == 9
    assert all(
        morphism.domain().base_object() is morphism.base_morphism().domain()
        and morphism.codomain().base_object() is morphism.base_morphism().codomain()
        for morphism in data.morphisms
    )


test_constant_indexed_category_uses_native_total_join()
