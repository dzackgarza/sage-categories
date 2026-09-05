"""Left and right Kan extensions, computed pointwise over comma categories (POL-FUN-029, POL-FUN-032).

For ``K: C -> D`` and ``F: C -> E``, the left Kan extension ``Lan_K F: D -> E`` is
computed pointwise: ``(Lan_K F)(d)`` is the colimit over the comma category
``(K, d)``, whose objects are the pairs ``(c, K c -> d)``, of ``F`` composed with
the projection to ``C``; on ``g: d -> d'`` it is the induced morphism of colimits.
The unit ``F => Lan_K F * K`` has component at ``c`` the colimit injection at
``(c, id_{K c})``.  The right Kan extension ``Ran_K F`` is the limit over the comma
category ``(d, K)`` of objects ``(c, d -> K c)``, with counit ``Ran_K F * K => F``
given by the projections at ``(c, id_{K c})``.  (Mathlib
``CategoryTheory.Functor.pointwiseLeftKanExtension``: the value at ``Y`` is the
colimit of ``CostructuredArrow.proj L Y ⋙ F`` with ``CostructuredArrow L Y =
Comma L (fromPUnit Y)``; ``pointwiseRightKanExtension``: the limit of
``StructuredArrow.proj Y L ⋙ F`` with ``StructuredArrow Y L = Comma (fromPUnit Y)
L``; inspected 2026-08-27.)  The extension exists when ``E`` owns the required
colimits or limits; otherwise construction fails loudly (POL-CAT-051).

The comma categories are the strict pullbacks of ``cat/slices.py``; the point
``d: * -> D`` is the retained point functor of ``d``.  The extension and its unit
or counit are retained once per pair ``(K, F)``; the unit and counit are
morphisms of the fixed-endpoint functor category ``Fun(C, E)``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.cat.constructions import cocone, cone
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.slices import CommaCategory, comma_category
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.morphisms import MorphismCategory

__all__ = ["left_kan_desc", "left_kan_extension", "left_kan_unit", "right_kan_counit", "right_kan_extension", "right_kan_lift"]


def _star() -> CategoryOfCategories.ElementType:
    return Cat().Terminal()(0)


@cached_function(key=identity_key)
def _left_retained(along: Functor, functor: Functor) -> tuple[Functor, NaturalTransformation]:
    assert along.domain() is functor.domain(), f"{along!r} and {functor!r} have different domains"
    source, target, values = along.domain(), along.codomain(), functor.codomain()

    def comma(member_object: CategoryOfCategories.ElementType) -> CommaCategory:
        return comma_category(along, target.point_functor(member_object))

    @cached_function(key=identity_key)
    def at(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        """The chosen colimit over ``(K, d)`` of ``F`` after the projection to ``C``."""
        shape = comma(member_object)
        return values.Colimits(shape)(functor * shape.first_projection())

    def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        lower, upper = at(morphism.domain()), at(morphism.codomain())
        destination = comma(morphism.codomain())
        induced = cocone(lower.diagram(), upper, lambda vertex: upper.injection(destination.from_arrow(vertex.first(), vertex.second(), morphism * vertex.arrow())))
        return lower.universal_morphism(induced)

    # ``at`` is the chosen colimit, an object of ``values`` owning the injections and
    # the mediator; the extension is the functor sending ``d`` to it.
    extension = Fun(target, values)(at, on_morphism)

    def unit_component(member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        image = along.on_object(member_object)
        identity = image.category().morphism_category(1)(image, image).one()
        return at(image).injection(comma(image).from_arrow(member_object, _star(), identity))

    unit = Fun(source, values).morphism_category(1)(functor, extension * along)(unit_component)
    return extension, unit


@cached_function(key=identity_key)
def _right_retained(along: Functor, functor: Functor) -> tuple[Functor, NaturalTransformation]:
    assert along.domain() is functor.domain(), f"{along!r} and {functor!r} have different domains"
    source, target, values = along.domain(), along.codomain(), functor.codomain()

    def comma(member_object: CategoryOfCategories.ElementType) -> CommaCategory:
        return comma_category(target.point_functor(member_object), along)

    @cached_function(key=identity_key)
    def at(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        """The chosen limit over ``(d, K)`` of ``F`` after the projection to ``C``."""
        shape = comma(member_object)
        return values.Limits(shape)(functor * shape.second_projection())

    def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        lower, upper = at(morphism.domain()), at(morphism.codomain())
        origin = comma(morphism.domain())
        induced = cone(upper.diagram(), lower, lambda vertex: lower.projection(origin.from_arrow(vertex.first(), vertex.second(), vertex.arrow() * morphism)))
        return upper.universal_morphism(induced)

    # ``at`` is the chosen limit, an object of ``values`` owning the projections and
    # the mediator; the extension is the functor sending ``d`` to it.
    extension = Fun(target, values)(at, on_morphism)

    def counit_component(member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        image = along.on_object(member_object)
        identity = image.category().morphism_category(1)(image, image).one()
        return at(image).projection(comma(image).from_arrow(_star(), member_object, identity))

    counit = Fun(source, values).morphism_category(1)(extension * along, functor)(counit_component)
    return extension, counit


def left_kan_extension(along: Functor, functor: Functor) -> Functor:
    """``Lan_K F: D -> E`` for ``K: C -> D`` and ``F: C -> E``, pointwise by colimits over ``(K, d)``."""
    return _left_retained(along, functor)[0]


def left_kan_unit(along: Functor, functor: Functor) -> NaturalTransformation:
    """The unit ``F => Lan_K F * K`` retained by the left Kan extension construction."""
    return _left_retained(along, functor)[1]


def right_kan_extension(along: Functor, functor: Functor) -> Functor:
    """``Ran_K F: D -> E``, pointwise by limits over ``(d, K)``."""
    return _right_retained(along, functor)[0]


def right_kan_counit(along: Functor, functor: Functor) -> NaturalTransformation:
    """The counit ``Ran_K F * K => F`` retained by the right Kan extension construction."""
    return _right_retained(along, functor)[1]


@cached_function(key=identity_key)
def right_kan_lift(along: Functor, functor: Functor, candidate: Functor, transformation: NaturalTransformation) -> NaturalTransformation:
    """The unique ``H => Ran_K(F)`` induced by ``H K => F``."""
    extension = right_kan_extension(along, functor)
    assert candidate in Fun(along.codomain(), functor.codomain())
    assert transformation in Fun(along.domain(), functor.codomain()).morphism_category(1)(candidate * along, functor)
    def component(value: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        limit = extension.on_object(value)
        return limit.universal_morphism(cone(
            limit.diagram(), candidate.on_object(value),
            lambda vertex: transformation.component(vertex.second())
            * candidate.on_morphism(vertex.arrow()),
        ))

    return Fun(along.codomain(), functor.codomain()).morphism_category(1)(candidate, extension)(component)


@cached_function(key=identity_key)
def left_kan_desc(along: Functor, functor: Functor, candidate: Functor, transformation: NaturalTransformation) -> NaturalTransformation:
    """The unique ``Lan_K(F) => H`` induced by ``F => H K``."""
    extension = left_kan_extension(along, functor)
    assert candidate in Fun(along.codomain(), functor.codomain())
    assert transformation in Fun(along.domain(), functor.codomain()).morphism_category(1)(functor, candidate * along)
    def component(value: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        colimit = extension.on_object(value)
        return colimit.universal_morphism(cocone(
            colimit.diagram(), candidate.on_object(value),
            lambda vertex: candidate.on_morphism(vertex.arrow())
            * transformation.component(vertex.first()),
        ))

    return Fun(along.codomain(), functor.codomain()).morphism_category(1)(extension, candidate)(component)
