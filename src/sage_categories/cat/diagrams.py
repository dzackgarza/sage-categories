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

from sage_categories.cat.category import Category
from sage_categories.cat.cones import LimitConesCategory, cocone, cocone_apex, cone, cone_apex, cones
from sage_categories.cat.declarations import Sets
from sage_categories.cat.dual_functor_categories import dual_functor_category_equivalence
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import endpoints
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.shapes import Discrete, DiscreteCategory
from sage_categories.cat.predicates import Decision
from sage_categories.cat.predicates import ask
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import MonoDict, cached_function

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.functors import FunctorCategory
    from sage_categories.cat.morphisms import MorphismCategory

type Datum = Hashable
type _PointwiseLimitMediator = Callable[[NaturalTransformation], NaturalTransformation]

__all__ = [
    "codomain_lift",
    "constant",
    "diagonal",
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


@cached_function(key=identity_key)
def evaluation(functors: FunctorCategory, vertex: CategoryOfCategories.ElementType) -> Functor:
    """``ev_i: Fun(I, C) -> C`` for an object ``i`` of ``I``, retained per ``i``.

    For ``I = [1]`` the evaluation ``ev_1`` retains its cartesian lifts by pullback and
    ``ev_0`` its cocartesian lifts by pushout (POL-FUN-029).
    """
    assert vertex in functors.domain(), f"{vertex!r} is not an object of {functors.domain()!r}"
    evaluation_functor = Fun(functors, functors.codomain())(
        lambda diagram: functors.diagram(diagram).on_object(vertex),
        lambda transformation: transformation._component_family[vertex],
    )
    if functors.domain() is Cat().Simplex(1) and functors.domain().label(vertex) == 1:
        evaluation_functor.retain_cartesian_lifts(lambda morphism, member_object: codomain_lift(functors, morphism, member_object))
    if functors.domain() is Cat().Simplex(1) and functors.domain().label(vertex) == 0:
        evaluation_functor.retain_cocartesian_lifts(lambda morphism, member_object: domain_lift(functors, morphism, member_object))
    return evaluation_functor


@cached_function(key=identity_key)
def constant(functors: FunctorCategory, value: CategoryOfCategories.ElementType) -> Functor:
    """The constant diagram at ``value``, retained per value."""
    assert value in functors.codomain(), f"{value!r} is not an object of {functors.codomain()!r}"
    identity = functors.codomain().morphism_category(1)(value, value).one()
    diagram = functors(lambda vertex: value, lambda morphism: identity)
    functors._constant_values[diagram] = value
    return diagram


@cached_function(key=identity_key)
def diagonal(functors: FunctorCategory) -> Functor:
    """Return the diagonal functor ``C -> Fun(I, C)``."""
    return Fun(functors.codomain(), functors)(
        lambda member_object: functors.constant(member_object),
        lambda morphism: functors.morphism_category(1)(
            functors.constant(morphism.domain()),
            functors.constant(morphism.codomain()),
        )(lambda vertex: morphism),
    )


def from_object_rule(functors: FunctorCategory, rule: Callable[[DiscreteCategory.ObjectType], CategoryOfCategories.ElementType]) -> Functor:
    """The diagram determined by a discrete shape and its object rule."""
    assert functors.domain().is_discrete(), f"{functors.domain()!r} is not a discrete shape; supply a morphism rule"
    diagram = _discrete_diagram(functors, rule)
    assert diagram.codomain() is functors.codomain(), f"{rule!r} already defines a diagram in {diagram.codomain()!r}"
    return diagram


@cached_function(key=lambda functors, rule: identity_key(functors.domain(), rule))
def _discrete_diagram(functors: FunctorCategory, rule: Callable[[DiscreteCategory.ObjectType], CategoryOfCategories.ElementType]) -> Functor:
    """A discrete diagram sends each identity to the identity of its image."""
    def image_identity(identity: DiscreteCategory.MorphismType) -> MorphismCategory.ObjectType:
        image = rule(identity.domain())
        return image.category().morphism_category(1)(image, image).one()

    return functors(rule, image_identity)


def sequence_position(vertex: DiscreteCategory.ObjectType) -> int:
    """The position ``k`` of an object of ``Discrete([n])`` at the point ``k`` of ``[n]``."""
    from sage_categories.cat.canonical import FinitePresentedCategory

    shape = vertex.category().narrowing_base()
    if isinstance(shape, FinitePresentedCategory):
        return int(shape.label(vertex))
    simplex = vertex.category().index_set()
    enumeration = Sets.Finite().chosen_enumeration(simplex)
    return next(position for position, datum in enumerate(enumeration) if ask(vertex.point() == simplex.point(datum)))


@cached_function(
    key=lambda ambient, sequence: (
        (id(ambient), ambient),
        tuple((id(member_object), member_object) for member_object in sequence),
    )
)
def from_sequence(ambient: Category, sequence: tuple[CategoryOfCategories.ElementType, ...]) -> Functor:
    """The finite discrete sequence diagram used before the owned Sets leaf exists."""
    from sage_categories.cat.canonical import _finite_discrete

    shape = _finite_discrete(len(sequence))
    return from_object_rule(Fun(shape, ambient), lambda vertex: sequence[shape.label(vertex)])


# -- the commuting squares of ``Fun([1], C)`` as a finite set (specs/functor.md, "Diagram shapes and universal constructions") ---------------------------


def square_set(functors: FunctorCategory) -> CategoryOfCategories.ElementType:
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


def square_at(functors: FunctorCategory, point: CategoryOfCategories.ElementType) -> NaturalTransformation:
    """The square selected by a point of ``square_set``."""
    square_set(functors)
    base, quadruples = functors.codomain(), functors._finite_data["quadruples"]
    f, g, a, b = (base.morphism_at(quadruples.product_projection(position)(point)) for position in range(4))
    components = {0: a, 1: b}
    return functors.morphism_category(1)(f, g)(lambda vertex: components[functors.domain().label(vertex)])


# -- the lifts of ``ev_1`` and ``ev_0`` on ``Fun([1], C)`` (POL-FUN-029) ----------------------------------


def _vertex_identity(
    objects: dict[int, CategoryOfCategories.ElementType],
    shape: Category,
    vertex: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    """``1_X`` at the object a horn vertex is labelled with (POL-CAT-023)."""
    member_object = objects[shape.label(vertex)]
    return member_object.category().morphism_category(1)(member_object, member_object).one()


def _fold(
    images: dict[str, MorphismCategory.ObjectType],
    identities: Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType],
    path: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    if not path.word():
        return identities(path.domain())
    first, *rest = path.word()
    image = images[first]
    for name in rest:
        image = images[name] * image
    return image


@cached_function(key=identity_key)
def cospan_diagram(
    base: Category,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> Functor:
    """The diagram ``L(2, 2) -> C`` with legs ``first: 0 -> 2`` and ``second: 1 -> 2``, retained per legs and base."""
    assert first.codomain() is second.codomain()
    cospan = Cat().WalkingCospan()
    objects = {0: first.domain(), 1: second.domain(), 2: first.codomain()}
    images = {"0->2": first, "1->2": second}
    return Fun(cospan, base)(lambda vertex: objects[cospan.label(vertex)], lambda path: _fold(images, lambda vertex: _vertex_identity(objects, cospan, vertex), path))


@cached_function(key=identity_key)
def span_diagram(
    base: Category,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> Functor:
    """The diagram ``L(2, 0) -> C`` with legs ``first: 0 -> 1`` and ``second: 0 -> 2``, retained per legs and base."""
    assert first.domain() is second.domain()
    span = Cat().WalkingSpan()
    objects = {0: first.domain(), 1: first.codomain(), 2: second.codomain()}
    images = {"0->1": first, "0->2": second}
    return Fun(span, base)(lambda vertex: objects[span.label(vertex)], lambda path: _fold(images, lambda vertex: _vertex_identity(objects, span, vertex), path))


def codomain_lift(
    functors: FunctorCategory,
    morphism: MorphismCategory.ObjectType,
    member_object: MorphismCategory.ObjectType,
) -> NaturalTransformation:
    """The cartesian lift of ``f: y -> x`` at ``p: z -> x`` for ``ev_1``: the square ``(pi_z, f)`` from ``pi_y: z *_x y -> y`` to ``p``."""
    base, arrow = functors.codomain(), functors.domain()
    assert arrow is Cat().Simplex(1) and morphism.codomain() is member_object.codomain(), f"{morphism!r} does not end at the codomain of {member_object!r}"
    cospan = Cat().WalkingCospan()
    pullback = base.Pullbacks()(cospan_diagram(base, member_object, morphism))
    to_first, to_second = pullback.projection(cospan(0)), pullback.projection(cospan(1))
    components = {0: to_first, 1: morphism}
    return functors.morphism_category(1)(to_second, member_object)(lambda vertex: components[arrow.label(vertex)])


def domain_lift(
    functors: FunctorCategory,
    morphism: MorphismCategory.ObjectType,
    member_object: MorphismCategory.ObjectType,
) -> NaturalTransformation:
    """The cocartesian lift of ``f: x -> y`` at ``p: x -> z`` for ``ev_0``: the square ``(f, iota_z)`` from ``p`` to ``iota_y: y -> z +_x y``."""
    base, arrow = functors.codomain(), functors.domain()
    assert arrow is Cat().Simplex(1) and morphism.domain() is member_object.domain(), f"{morphism!r} does not start at the domain of {member_object!r}"
    span = Cat().WalkingSpan()
    pushout = base.Pushouts()(span_diagram(base, member_object, morphism))
    from_first, from_second = pushout.injection(span(1)), pushout.injection(span(2))
    components = {0: morphism, 1: from_first}
    return functors.morphism_category(1)(member_object, from_second)(lambda vertex: components[arrow.label(vertex)])


# -- limits and colimits in ``Fun(I, C)``, pointwise (specs/functor.md, "Diagram shapes and universal constructions") -----------------------------------------


def _pointwise_limit_data(
    diagram: Functor,
) -> tuple[Functor, NaturalTransformation, _PointwiseLimitMediator]:
    """Build the pointwise apex, cone, and mediator without retaining an outer construction."""
    from sage_categories.cat.constructions import constructed_data

    functors, shape = diagram.codomain(), diagram.domain()
    assert functors is not Fun, f"{diagram!r} is not a diagram in a fixed-endpoint functor category"
    target = functors.codomain()
    limits = target.Limits(shape)
    from sage_categories.cat.calculus import transpose

    transposed = transpose(diagram)
    composites: MonoDict = MonoDict()

    def at(vertex: CategoryOfCategories.ElementType) -> LimitConesCategory.ObjectType:
        """The limiting cone of the pointwise diagram at ``vertex``."""
        if vertex not in composites:
            presentation = constructed_data(limits, transposed.on_object(vertex))
            assert isinstance(presentation, LimitConesCategory.ObjectType)
            composites[vertex] = presentation
        return composites[vertex]

    apex = limits.limit_functor() * transposed
    projections: MonoDict = MonoDict()

    def projection(vertex: CategoryOfCategories.ElementType) -> NaturalTransformation:
        if vertex not in projections:
            projections[vertex] = functors.morphism_category(1)(apex, diagram.on_object(vertex))(lambda index_object: at(index_object).leg(vertex))
        return projections[vertex]

    def mediator(candidate_cone: NaturalTransformation) -> NaturalTransformation:
        source = cone_apex(candidate_cone)
        return functors.morphism_category(1)(source, apex)(
            lambda index_object: at(index_object).lift(
                cones(at(index_object).diagram())(
                    cone(
                        at(index_object).diagram(),
                        source.on_object(index_object),
                        lambda vertex: candidate_cone.component(vertex).component(index_object),
                    )
                )
            )
        )

    return apex, cone(diagram, apex, projection), mediator


def pointwise_limit(diagram: Functor) -> CategoryOfCategories.ElementType:
    """``Fun(I, C).Limits(J)(D)``: the functor ``i |-> lim_J (ev_i * D)`` with the pointwise cone and mediator."""
    apex, limiting_cone, mediator = _pointwise_limit_data(diagram)

    family = Fun.Limits(diagram.domain())
    lowered = family.lowered(diagram)
    return family.with_universal_data(
        lowered,
        apex,
        cone(lowered, apex, lambda vertex: limiting_cone.component(vertex)),
        mediator,
    )


def pointwise_colimit(diagram: Functor) -> CategoryOfCategories.ElementType:
    """Derive a pointwise colimit from the pointwise limit in the dual functor category."""
    from sage_categories.cat.constructions import constructed_data

    functors, shape = diagram.codomain(), diagram.domain()
    assert functors is not Fun, f"{diagram!r} is not a diagram in a fixed-endpoint functor category"
    duality = dual_functor_category_equivalence(functors.domain(), functors.codomain())
    to_dual = duality.forward().op()
    transported = to_dual * diagram.op()
    assert isinstance(transported, Functor)
    dual_apex = pointwise_limit(transported)
    dual_family = Fun.Limits(transported.domain())
    presentation = constructed_data(dual_family, transported)
    assert isinstance(presentation, LimitConesCategory.ObjectType)
    inverse = duality.inverse()
    dual_functors = to_dual.codomain()
    apex = inverse.on_object(dual_functors.op()(dual_apex))

    def injection(vertex: CategoryOfCategories.ElementType) -> NaturalTransformation:
        dual_leg = presentation.leg(transported.domain()(vertex))
        injection = inverse.on_morphism(opposite_morphism(dual_leg))
        assert isinstance(injection, NaturalTransformation)
        return injection

    def mediator(candidate_cocone: NaturalTransformation) -> NaturalTransformation:
        destination = cocone_apex(candidate_cocone)
        opposite_functors = functors.op()
        opposite_destination = opposite_functors(destination)
        dual_destination = to_dual.on_object(opposite_destination)
        dual_candidate = cone(
            transported,
            dual_destination,
            lambda vertex: to_dual.on_morphism(candidate_cocone.op().component(vertex)),
        )
        dual_mediator = presentation.lift(cones(transported)(dual_candidate))
        mediator = inverse.on_morphism(opposite_morphism(dual_mediator))
        assert isinstance(mediator, NaturalTransformation)
        return mediator

    family = Fun.Colimits(shape)
    lowered = family.lowered(diagram)
    return family.with_universal_data(
        lowered,
        apex,
        cocone(lowered, apex, injection),
        mediator,
    )
