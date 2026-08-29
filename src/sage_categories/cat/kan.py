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
``d: 1 -> D`` is the retained point functor of ``d``.  The extension and its unit
or counit are retained once per pair ``(K, F)``; the unit and counit are
morphisms of the fixed-endpoint functor category ``Fun(C, E)``.
"""

from __future__ import annotations

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat.constructions import cocone, cone
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.slices import comma_category
from sage_categories.kernel.roles import MorphismOfCategory, ObjectOfCategory

__all__ = ["left_kan_extension", "left_kan_unit", "right_kan_counit", "right_kan_extension"]

_left: TripleDict = TripleDict(weak_values=False)
_right: TripleDict = TripleDict(weak_values=False)


def _star() -> ObjectOfCategory:
    return Cat().Terminal()(0)


def _cospan() -> ObjectOfCategory:
    """``L(2, 2)``, the shape of the pullback square a comma category is."""
    return Cat().Horn(2, 2)


def _pairs_projection(shape: ObjectOfCategory) -> Functor:
    """The leg of a comma category at the first vertex of its cospan: its projection to the product of the two domains."""
    return shape.projection(_cospan()(0))


def _comma_pair(vertex: ObjectOfCategory) -> ObjectOfCategory:
    """The component of an object of a comma category at the first vertex: the pair ``(a, b)``."""
    return vertex.component(_cospan()(0))


def _comma_arrow(vertex: ObjectOfCategory) -> MorphismOfCategory:
    """The component at the second vertex: the arrow ``F a -> G b``."""
    return vertex.component(_cospan()(1))


def _comma_object(shape: ObjectOfCategory, pair: ObjectOfCategory, arrow: MorphismOfCategory) -> ObjectOfCategory:
    """The object of a comma category with those two components; the diagram forces the third, the endpoints of the arrow."""
    cospan = _cospan()
    components = {0: pair, 1: arrow, 2: shape.diagram().on_morphism(cospan.generator("1->2")).on_object(arrow)}
    return shape(lambda vertex: components[cospan.label(vertex)])


def _left_data(along: Functor, functor: Functor) -> tuple[Functor, NaturalTransformation]:
    source, target, values = along.domain(), along.codomain(), functor.codomain()
    product = Cat().Products()((source, Cat().Terminal()))
    colimits: MonoDict = MonoDict()

    def comma(member_object: ObjectOfCategory) -> ObjectOfCategory:
        return comma_category(along, target.point_functor(member_object))

    def at(member_object: ObjectOfCategory) -> ObjectOfCategory:
        """The chosen colimit over ``(K, d)`` of ``F`` after the projection to ``C``."""
        if member_object not in colimits:
            shape = comma(member_object)
            diagram = functor * (product.product_projection(0) * _pairs_projection(shape))
            colimits[member_object] = values.Colimits(shape)(diagram)
        return colimits[member_object]

    def on_morphism(morphism: MorphismOfCategory) -> MorphismOfCategory:
        lower, upper = at(morphism.domain()), at(morphism.codomain())
        destination = comma(morphism.codomain())
        induced = cocone(lower.diagram(), upper, lambda vertex: upper.injection(_comma_object(destination, _comma_pair(vertex), morphism * _comma_arrow(vertex))))
        return lower.universal_morphism(induced)

    # ``at`` is the chosen colimit, an object of ``values`` owning the injections and
    # the mediator; the extension is the functor sending ``d`` to it.
    extension = Fun(target, values)(at, on_morphism)

    def unit_component(member_object: ObjectOfCategory) -> MorphismOfCategory:
        image = along.on_object(member_object)
        identity = image.category().morphism_category(1)(image, image).one()
        return at(image).injection(_comma_object(comma(image), product((member_object, _star())), identity))

    unit = Fun(source, values).morphism_category(1)(functor, extension * along)(unit_component)
    return extension, unit


def _right_data(along: Functor, functor: Functor) -> tuple[Functor, NaturalTransformation]:
    source, target, values = along.domain(), along.codomain(), functor.codomain()
    product = Cat().Products()((Cat().Terminal(), source))
    limits: MonoDict = MonoDict()

    def comma(member_object: ObjectOfCategory) -> ObjectOfCategory:
        return comma_category(target.point_functor(member_object), along)

    def at(member_object: ObjectOfCategory) -> ObjectOfCategory:
        """The chosen limit over ``(d, K)`` of ``F`` after the projection to ``C``."""
        if member_object not in limits:
            shape = comma(member_object)
            diagram = functor * (product.product_projection(1) * _pairs_projection(shape))
            limits[member_object] = values.Limits(shape)(diagram)
        return limits[member_object]

    def on_morphism(morphism: MorphismOfCategory) -> MorphismOfCategory:
        lower, upper = at(morphism.domain()), at(morphism.codomain())
        origin = comma(morphism.domain())
        induced = cone(upper.diagram(), lower, lambda vertex: lower.projection(_comma_object(origin, _comma_pair(vertex), _comma_arrow(vertex) * morphism)))
        return upper.universal_morphism(induced)

    # ``at`` is the chosen limit, an object of ``values`` owning the projections and
    # the mediator; the extension is the functor sending ``d`` to it.
    extension = Fun(target, values)(at, on_morphism)

    def counit_component(member_object: ObjectOfCategory) -> MorphismOfCategory:
        image = along.on_object(member_object)
        identity = image.category().morphism_category(1)(image, image).one()
        return at(image).projection(_comma_object(comma(image), product((_star(), member_object)), identity))

    counit = Fun(source, values).morphism_category(1)(extension * along, functor)(counit_component)
    return extension, counit


def _left_retained(along: Functor, functor: Functor) -> tuple[Functor, NaturalTransformation]:
    assert along.domain() is functor.domain(), f"{along!r} and {functor!r} have different domains"
    key = (along, functor, Cat())
    if key not in _left:
        _left[key] = _left_data(along, functor)
    return _left[key]


def _right_retained(along: Functor, functor: Functor) -> tuple[Functor, NaturalTransformation]:
    assert along.domain() is functor.domain(), f"{along!r} and {functor!r} have different domains"
    key = (along, functor, Cat())
    if key not in _right:
        _right[key] = _right_data(along, functor)
    return _right[key]


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
