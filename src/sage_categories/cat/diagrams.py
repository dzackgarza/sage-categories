"""Diagrams: evaluation functors of ``Fun(I, C)``, constant and discrete diagrams (POL-FUN-027, POL-FUN-029, POL-SET-013).

A diagram of shape ``I`` in ``C`` is an object of ``Fun(I, C)``.  ``Fun(I, C)``
retains one evaluation functor ``ev_i: Fun(I, C) -> C`` per object ``i`` of ``I``,
constructed through ``Fun(Fun(I, C), C)`` (Mathlib ``CategoryTheory.evaluation``;
inspected 2026-08-26): on a diagram it returns ``D(i)`` and on a natural
transformation its component at ``i``.  For ``I = [1]`` the evaluations at ``0``
and ``1`` are ``ev_0`` and ``ev_1``, the domain and codomain of a morphism, since
the objects of ``Fun([1], C)`` are the morphisms of ``C`` (specs/functor.md, "The Mor(n, C) tower").

The constant diagram at ``X`` sends every object to ``X`` and every morphism to
its identity (Mathlib ``CategoryTheory.Functor.const``; inspected 2026-08-26); it
is retained once per ``X`` so that a construction can recognize a retained
constant diagram.  A diagram over ``Discrete(S)`` is determined by its object rule
alone, since the only morphisms are identities; the sequence convenience
``(X_0, ..., X_n)`` denotes the diagram over ``Discrete([n])`` for
``[n] = Sets().Simplex(n)``.

``Fun(I, C)`` has the ``J``-limits and ``J``-colimits that ``C`` has, computed
pointwise: the apex at ``i`` is the limit of ``ev_i * D``, the cone components and
the mediator are assembled from the pointwise ones (Mathlib
``CategoryTheory.Limits.evaluationJointlyReflectsLimits``, ``combinedIsLimit``,
``functorCategoryHasLimitsOfShape`` and their colimit duals; inspected
2026-08-27).

The commuting squares of ``Fun([1], C)`` form a finite set when ``C`` chooses a
finite set of morphisms.  The cartesian lift of ``f: y -> x`` at ``p: z -> x``
for ``ev_1`` is the square from the pullback projection ``z *_x y -> y`` to ``p``
(nLab "codomain fibration", inspected 2026-08-27), and the cocartesian lift of
``f: x -> y`` at ``p: x -> z`` for ``ev_0`` is the square from ``p`` to the
pushout injection ``y -> z +_x y``, dually.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import TYPE_CHECKING

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat.category import Category
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import endpoints
from sage_categories.cat.shapes import Discrete, DiscreteCategory, is_discrete
from sage_categories.kernel.caches import SequenceTable
from sage_categories.kernel.decisions import Decision
from sage_categories.kernel.predicates import ask
from sage_categories.kernel.roles import ElementOfObject, ObjectOfCategory

if TYPE_CHECKING:
    from sage_categories.cat.constructions import UniversalData
    from sage_categories.cat.functors import FunctorCategory

type Datum = Hashable

__all__ = [
    "codomain_lift",
    "constant",
    "domain_lift",
    "evaluation",
    "from_object_rule",
    "from_sequence",
    "pointwise_colimit",
    "pointwise_limit",
    "sequence_position",
    "square_at",
    "square_set",
]


def evaluation(functors: FunctorCategory, vertex: ObjectOfCategory) -> Functor:
    """``ev_i: Fun(I, C) -> C`` for an object ``i`` of ``I``, retained per ``i``.

    For ``I = [1]`` the evaluation ``ev_1`` retains its cartesian lifts by pullback and
    ``ev_0`` its cocartesian lifts by pushout (POL-FUN-029).
    """
    assert vertex in functors.domain(), f"{vertex!r} is not an object of {functors.domain()!r}"
    if vertex not in functors._evaluations:
        evaluation_functor = Fun(functors, functors.codomain())(
            lambda diagram: functors.diagram(diagram).on_object(vertex),
            lambda transformation: transformation.component(vertex),
        )
        functors._evaluations[vertex] = evaluation_functor
        if functors.domain() is Cat().Simplex(1) and functors.domain().label(vertex) == 1:
            evaluation_functor.retain_cartesian_lifts(lambda morphism, member_object: codomain_lift(functors, morphism, member_object))
        if functors.domain() is Cat().Simplex(1) and functors.domain().label(vertex) == 0:
            evaluation_functor.retain_cocartesian_lifts(lambda morphism, member_object: domain_lift(functors, morphism, member_object))
    return functors._evaluations[vertex]


def constant(functors: FunctorCategory, value: ObjectOfCategory) -> Functor:
    """The constant diagram at ``value``, retained per value."""
    assert value in functors.codomain(), f"{value!r} is not an object of {functors.codomain()!r}"
    if value not in functors._constants:
        diagram = functors(lambda vertex: value, lambda morphism: value.identity())
        functors._constants[value] = diagram
        functors._constant_values[diagram] = value
    return functors._constants[value]


# A diagram constructor called on identical data returns the retained functor
# (POL-CAT-083): object rules per rule, sequences per sequence and ambient, cospans
# and spans per pair of legs and base.  Every table keys by identity.
_object_rule_diagrams: MonoDict = MonoDict()
_sequence_diagrams: MonoDict = MonoDict()
_cospan_diagrams: TripleDict = TripleDict(weak_values=False)
_span_diagrams: TripleDict = TripleDict(weak_values=False)


def from_object_rule(functors: FunctorCategory, rule: Callable[[DiscreteCategory.ObjectType], ObjectOfCategory]) -> Functor:
    """A diagram over a discrete shape from its object rule, retained per rule; the morphism rule is forced."""
    assert is_discrete(functors.domain()), f"{functors.domain()!r} is not a discrete shape; supply a morphism rule"
    if rule not in _object_rule_diagrams:
        _object_rule_diagrams[rule] = functors(rule, lambda identity: rule(identity.domain()).identity())
    diagram = _object_rule_diagrams[rule]
    assert diagram.codomain() is functors.codomain(), f"{rule!r} already defines a diagram in {diagram.codomain()!r}"
    return diagram


def sequence_position(vertex: DiscreteCategory.ObjectType) -> int:
    """The position ``k`` of an object of ``Discrete([n])`` at the point ``k`` of ``[n]``."""
    simplex = vertex.category().index_set()
    enumeration = Sets.Finite().chosen_enumeration(simplex)
    return next(position for position, datum in enumerate(enumeration) if ask(vertex.point() == simplex.point(datum)))


def from_sequence(ambient: Category, sequence: tuple[ObjectOfCategory, ...]) -> Functor:
    """The diagram ``(X_0, ..., X_n)`` over ``Discrete([n])``, retained per sequence and ambient; the empty sequence is over ``Discrete({})``."""
    if ambient not in _sequence_diagrams:
        _sequence_diagrams[ambient] = SequenceTable()
    table = _sequence_diagrams[ambient]
    if sequence not in table:
        index_set = Sets.Simplex(len(sequence) - 1) if sequence else Sets.Empty()
        table[sequence] = from_object_rule(Fun(Discrete(index_set), ambient), lambda vertex: sequence[sequence_position(vertex)])
    return table[sequence]


# -- the commuting squares of ``Fun([1], C)`` as a finite set (specs/functor.md, "Diagram shapes and universal constructions") ---------------------------


def square_set(functors: FunctorCategory) -> ObjectOfCategory:
    """The finite set of commuting squares ``(f, g, a, b)`` with ``g * a == b * f`` in ``C``, when ``C`` chooses a finite set of morphisms."""
    base = functors.codomain()
    if "squares" not in functors._finite_data:
        morphisms = ask(base.morphism_set())
        quadruples = Sets.Products()((morphisms, morphisms, morphisms, morphisms))

        def commutes(datum: Datum) -> Decision:
            point = quadruples.point(datum)
            f, g, a, b = (base.morphism_at(quadruples.product_projection(position)(point)) for position in range(4))
            # The corners are a guarded proposition: ``g * a`` and ``b * f`` exist only once
            # the endpoints hold, so they are asked first and an undecided corner stays
            # undecided rather than reporting the quadruple as no square.
            corners = ask(endpoints(a, f.domain(), g.domain()) & endpoints(b, f.codomain(), g.codomain()))
            if corners is not True:
                return corners
            return ask(g * a == b * f)

        functors._finite_data["quadruples"] = quadruples
        functors._finite_data["squares"] = quadruples.subset_from(commutes)
    return functors._finite_data["squares"]


def square_at(functors: FunctorCategory, point: ElementOfObject) -> NaturalTransformation:
    """The square selected by a point of ``square_set``."""
    square_set(functors)
    base, quadruples = functors.codomain(), functors._finite_data["quadruples"]
    f, g, a, b = (base.morphism_at(quadruples.product_projection(position)(point)) for position in range(4))
    components = {0: a, 1: b}
    return functors.morphism_category(1)(f, g)(lambda vertex: components[functors.domain().label(vertex)])


# -- the lifts of ``ev_1`` and ``ev_0`` on ``Fun([1], C)`` (POL-FUN-029) ----------------------------------


def _fold(images: dict[str, MorphismOfCategory], identities: Callable[[ObjectOfCategory], MorphismOfCategory], path: MorphismOfCategory) -> MorphismOfCategory:
    if not path.word():
        return identities(path.domain())
    first, *rest = path.word()
    image = images[first]
    for name in rest:
        image = images[name] * image
    return image


def cospan_diagram(base: Category, first: MorphismOfCategory, second: MorphismOfCategory) -> Functor:
    """The diagram ``L(2, 2) -> C`` with legs ``first: 0 -> 2`` and ``second: 1 -> 2``, retained per legs and base."""
    assert first.codomain() is second.codomain()
    key = (first, second, base)
    if key not in _cospan_diagrams:
        cospan = Cat().Horn(2, 2)
        objects = {0: first.domain(), 1: second.domain(), 2: first.codomain()}
        images = {"0->2": first, "1->2": second}
        _cospan_diagrams[key] = Fun(cospan, base)(lambda vertex: objects[cospan.label(vertex)], lambda path: _fold(images, lambda vertex: objects[cospan.label(vertex)].identity(), path))
    return _cospan_diagrams[key]


def span_diagram(base: Category, first: MorphismOfCategory, second: MorphismOfCategory) -> Functor:
    """The diagram ``L(2, 0) -> C`` with legs ``first: 0 -> 1`` and ``second: 0 -> 2``, retained per legs and base."""
    assert first.domain() is second.domain()
    key = (first, second, base)
    if key not in _span_diagrams:
        span = Cat().Horn(2, 0)
        objects = {0: first.domain(), 1: first.codomain(), 2: second.codomain()}
        images = {"0->1": first, "0->2": second}
        _span_diagrams[key] = Fun(span, base)(lambda vertex: objects[span.label(vertex)], lambda path: _fold(images, lambda vertex: objects[span.label(vertex)].identity(), path))
    return _span_diagrams[key]


def codomain_lift(functors: FunctorCategory, morphism: MorphismOfCategory, member_object: MorphismOfCategory) -> NaturalTransformation:
    """The cartesian lift of ``f: y -> x`` at ``p: z -> x`` for ``ev_1``: the square ``(pi_z, f)`` from ``pi_y: z *_x y -> y`` to ``p``."""
    base, arrow = functors.codomain(), functors.domain()
    assert arrow is Cat().Simplex(1) and morphism.codomain() is member_object.codomain(), f"{morphism!r} does not end at the codomain of {member_object!r}"
    cospan = Cat().Horn(2, 2)
    pullback = base.Pullbacks()(cospan_diagram(base, member_object, morphism))
    to_first, to_second = pullback.projection(cospan(0)), pullback.projection(cospan(1))
    components = {0: to_first, 1: morphism}
    return functors.morphism_category(1)(to_second, member_object)(lambda vertex: components[arrow.label(vertex)])


def domain_lift(functors: FunctorCategory, morphism: MorphismOfCategory, member_object: MorphismOfCategory) -> NaturalTransformation:
    """The cocartesian lift of ``f: x -> y`` at ``p: x -> z`` for ``ev_0``: the square ``(f, iota_z)`` from ``p`` to ``iota_y: y -> z +_x y``."""
    base, arrow = functors.codomain(), functors.domain()
    assert arrow is Cat().Simplex(1) and morphism.domain() is member_object.domain(), f"{morphism!r} does not start at the domain of {member_object!r}"
    span = Cat().Horn(2, 0)
    pushout = base.Pushouts()(span_diagram(base, member_object, morphism))
    from_first, from_second = pushout.injection(span(1)), pushout.injection(span(2))
    components = {0: morphism, 1: from_first}
    return functors.morphism_category(1)(member_object, from_second)(lambda vertex: components[arrow.label(vertex)])


# -- limits and colimits in ``Fun(I, C)``, pointwise (specs/functor.md, "Diagram shapes and universal constructions") -----------------------------------------


def pointwise_limit(diagram: Functor) -> ObjectOfCategory:
    """``Fun(I, C).Limits(J)(D)``: the functor ``i |-> lim_J (ev_i * D)`` with the pointwise cone and mediator."""
    from sage_categories.cat.constructions import cone, cone_apex, constructed_data

    functors, shape = diagram.codomain(), diagram.domain()
    assert functors is not Fun, f"{diagram!r} is not a diagram in a fixed-endpoint functor category"
    target = functors.codomain()
    limits = target.Limits(shape)
    composites: MonoDict = MonoDict()

    def at(vertex: ObjectOfCategory) -> UniversalData:
        """The universal data of the pointwise limit at ``vertex``: the diagram owns it, so the object need not."""
        if vertex not in composites:
            composites[vertex] = constructed_data(limits, functors.evaluation(vertex) * diagram)
        return composites[vertex]

    def on_morphism(morphism: MorphismOfCategory) -> MorphismOfCategory:
        source, destination = at(morphism.domain()).diagram, at(morphism.codomain()).diagram
        transformation = Fun(shape, target).morphism_category(1)(source, destination)(lambda vertex: functors.diagram(diagram.on_object(vertex)).on_morphism(morphism))
        return limits.limit_functor().on_morphism(transformation)

    apex = functors(lambda vertex: at(vertex).constructed, on_morphism)
    projections: MonoDict = MonoDict()

    def projection(vertex: ObjectOfCategory) -> NaturalTransformation:
        if vertex not in projections:
            projections[vertex] = functors.morphism_category(1)(apex, diagram.on_object(vertex))(lambda index_object: at(index_object).transformation.component(vertex))
        return projections[vertex]

    def mediator(candidate_cone: NaturalTransformation) -> NaturalTransformation:
        source = cone_apex(candidate_cone)
        return functors.morphism_category(1)(source, apex)(
            lambda index_object: at(index_object).mediator(
                cone(at(index_object).diagram, source.on_object(index_object), lambda vertex: candidate_cone.component(vertex).component(index_object))
            )
        )

    family = Fun.Products() if is_discrete(shape) else Fun.Limits(shape)
    lowered = family.lowered(diagram)
    return family.with_universal_data(lowered, apex, cone(lowered, apex, projection), mediator)


def pointwise_colimit(diagram: Functor) -> ObjectOfCategory:
    """``Fun(I, C).Colimits(J)(D)``: the functor ``i |-> colim_J (ev_i * D)`` with the pointwise cocone and mediator."""
    from sage_categories.cat.constructions import cocone, cocone_apex, constructed_data

    functors, shape = diagram.codomain(), diagram.domain()
    assert functors is not Fun, f"{diagram!r} is not a diagram in a fixed-endpoint functor category"
    target = functors.codomain()
    colimits = target.Colimits(shape)
    composites: MonoDict = MonoDict()

    def at(vertex: ObjectOfCategory) -> UniversalData:
        if vertex not in composites:
            composites[vertex] = constructed_data(colimits, functors.evaluation(vertex) * diagram)
        return composites[vertex]

    def on_morphism(morphism: MorphismOfCategory) -> MorphismOfCategory:
        source, destination = at(morphism.domain()).diagram, at(morphism.codomain()).diagram
        transformation = Fun(shape, target).morphism_category(1)(source, destination)(lambda vertex: functors.diagram(diagram.on_object(vertex)).on_morphism(morphism))
        return colimits.colimit_functor().on_morphism(transformation)

    apex = functors(lambda vertex: at(vertex).constructed, on_morphism)
    injections: MonoDict = MonoDict()

    def injection(vertex: ObjectOfCategory) -> NaturalTransformation:
        if vertex not in injections:
            injections[vertex] = functors.morphism_category(1)(diagram.on_object(vertex), apex)(lambda index_object: at(index_object).transformation.component(vertex))
        return injections[vertex]

    def mediator(candidate_cocone: NaturalTransformation) -> NaturalTransformation:
        destination = cocone_apex(candidate_cocone)
        return functors.morphism_category(1)(apex, destination)(
            lambda index_object: at(index_object).mediator(
                cocone(at(index_object).diagram, destination.on_object(index_object), lambda vertex: candidate_cocone.component(vertex).component(index_object))
            )
        )

    family = Fun.Coproducts() if is_discrete(shape) else Fun.Colimits(shape)
    lowered = family.lowered(diagram)
    return family.with_universal_data(lowered, apex, cocone(lowered, apex, injection), mediator)
