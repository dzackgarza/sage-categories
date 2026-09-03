"""The retained duality equivalence for functor categories.

For ``D: I -> C``, dualization gives ``D.op(): I.op() -> C.op()``.  A
transformation ``eta: D => E`` gives ``eta.op(): E.op() => D.op()``; regarding
that transformation as a morphism in the opposite functor category restores
the original direction.  Thus

``Fun(I, C) ≃ Fun(I.op(), C.op()).op()``.
"""

from __future__ import annotations

from sage_categories.cat.adjunctions import Equivalences, EquivalencesCategory
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Fun, FunctorCategory, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.kernel.sage_runtime import MonoDict

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
        lambda vertex: source_diagram.codomain()
        .morphism_category(1)(
            source_diagram.on_object(vertex),
            target_diagram.on_object(vertex),
        )
        .one()
    )


_dual_functor_category_equivalences: MonoDict = MonoDict()


def dual_functor_category_equivalence(
    shape: Category,
    target: Category,
) -> EquivalencesCategory.ObjectType:
    """Return ``Fun(I, C) ≃ Fun(I.op(), C.op()).op()`` with retained data."""
    source = Fun(shape, target)
    if source in _dual_functor_category_equivalences:
        return _dual_functor_category_equivalences[source]

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

    source_endofunctors = Fun(source, source)
    source_identity = source_endofunctors.one()
    source_round_trip = inverse * forward
    unit = source_endofunctors.morphism_category(1)(
        source_identity,
        source_round_trip,
    )(
        lambda diagram: _identity_transformation(
            source,
            diagram,
            source_round_trip.on_object(diagram),
        )
    )
    unit_inverse = source_endofunctors.morphism_category(1)(
        source_round_trip,
        source_identity,
    )(
        lambda diagram: _identity_transformation(
            source,
            source_round_trip.on_object(diagram),
            diagram,
        )
    )
    source_endofunctors.retain_inverses(unit, unit_inverse)

    target_endofunctors = Fun(opposite_dual, opposite_dual)
    target_round_trip = forward * inverse
    target_identity = target_endofunctors.one()

    def counit_component(
        diagram: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        dual_identity = _identity_transformation(
            dual,
            diagram,
            target_round_trip.on_object(diagram),
        )
        return opposite_morphism(dual_identity)

    def counit_inverse_component(
        diagram: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        dual_identity = _identity_transformation(
            dual,
            target_round_trip.on_object(diagram),
            diagram,
        )
        return opposite_morphism(dual_identity)

    counit = target_endofunctors.morphism_category(1)(
        target_round_trip,
        target_identity,
    )(counit_component)
    counit_inverse = target_endofunctors.morphism_category(1)(
        target_identity,
        target_round_trip,
    )(counit_inverse_component)
    target_endofunctors.retain_inverses(counit, counit_inverse)

    equivalence = Equivalences(source, opposite_dual)(
        forward,
        inverse,
        unit,
        counit,
    )
    _dual_functor_category_equivalences[source] = equivalence
    return equivalence
