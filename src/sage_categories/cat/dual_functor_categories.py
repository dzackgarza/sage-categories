"""The retained duality equivalence for functor categories.

For ``D: I -> C``, dualization gives ``D.op(): I.op() -> C.op()``.  A
transformation ``eta: D => E`` gives ``eta.op(): E.op() => D.op()``; regarding
that transformation as a morphism in the opposite functor category restores
the original direction.  Thus

``Fun(I, C) ≃ Fun(I.op(), C.op()).op()``.
"""

from __future__ import annotations

from collections.abc import Callable

from sage_categories.cat.adjunctions import Equivalences, EquivalencesCategory
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor, FunctorCategory, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

__all__ = ["dual_functor_category_equivalence"]


def _identity_transformation(
    functors: FunctorCategory,
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
) -> NaturalTransformation:
    """The componentwise identity between two presentations of one diagram."""
    source_diagram = functors.diagram(source)
    target_diagram = functors.diagram(target)
    return functors.morphism_category(1)(source, target)(
        lambda vertex: (
            source_diagram.codomain()
            .morphism_category(1)(
                source_diagram.on_object(vertex),
                target_diagram.on_object(vertex),
            )
            .one()
        )
    )


def _identity_round_trip(
    category: Category,
    round_trip: Functor,
    component: Callable[
        [CategoryOfCategories.ElementType, CategoryOfCategories.ElementType],
        MorphismCategory.ObjectType,
    ],
) -> tuple[NaturalTransformation, NaturalTransformation]:
    """Retain and return both directions of ``Id ≅ round_trip`` from one component rule."""
    endofunctors = Fun(category, category)
    identity = endofunctors.one()
    forward = endofunctors.morphism_category(1)(identity, round_trip)(lambda value: component(value, round_trip.on_object(value)))
    inverse = endofunctors.morphism_category(1)(round_trip, identity)(lambda value: component(round_trip.on_object(value), value))
    endofunctors.retain_inverses(forward, inverse)
    return forward, inverse


@cached_function(key=identity_key)
def dual_functor_category_equivalence(
    shape: Category,
    target: Category,
) -> EquivalencesCategory.ObjectType:
    """Return ``Fun(I, C) ≃ Fun(I.op(), C.op()).op()`` with retained data."""
    source = Fun(shape, target)
    dual = Fun(shape.op(), target.op())
    opposite_dual = dual.op()

    def forward_object(
        diagram: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return opposite_dual(source.diagram(diagram).op())

    def forward_morphism(
        transformation: NaturalTransformation,
    ) -> MorphismCategory.ObjectType:
        return opposite_morphism(transformation.op())

    forward = Fun(source, opposite_dual)(forward_object, forward_morphism)

    def inverse_object(
        diagram: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return dual.diagram(diagram).op()

    def inverse_morphism(
        transformation: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        return opposite_morphism(transformation).op()

    inverse = Fun(opposite_dual, source)(inverse_object, inverse_morphism)

    source_round_trip = inverse * forward
    unit, _unit_inverse = _identity_round_trip(
        source,
        source_round_trip,
        lambda first, second: _identity_transformation(source, first, second),
    )

    target_round_trip = forward * inverse
    _counit_inverse, counit = _identity_round_trip(
        opposite_dual,
        target_round_trip,
        lambda first, second: opposite_morphism(_identity_transformation(dual, first, second)),
    )

    return Equivalences(source, opposite_dual)(
        forward,
        inverse,
        unit,
        counit,
    )
