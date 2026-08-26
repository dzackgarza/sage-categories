"""Acceptance tests for selected ordinary-functor routes."""

from sage_categories.abstract_categories.functors import Functor
from sage_categories.kernel.structural_routes import StructuralRoute


def test_empty_structural_route_is_identity_on_its_category() -> None:
    category = Sets()
    value = FiniteSet((ZZ(0), ZZ(1)))
    route = StructuralRoute(category, ())

    assert route.target() is category
    assert route.on_object(value) is value


def test_structural_route_composes_exact_selected_functor_objects() -> None:
    category = FiniteTotallyOrderedSets()
    ordered_set = finite_ordered_set((ZZ(0), ZZ(1)))
    factors = category.structure_functors()

    assert factors
    assert all(isinstance(functor, Functor) for functor in factors)

    route = StructuralRoute(category, (factors[0],))
    assert route.on_object(ordered_set) is factors[0].on_object(ordered_set)
