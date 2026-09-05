"""Cartesian closure and change of variables in functor categories.

The actions are the exponential adjunction in Cat, including natural
transformations. Reference: Riehl, Category Theory in Context, section 4.3.
"""

from __future__ import annotations

__all__ = [
    "binary_product_data",
    "pair_maps",
    "power_data",
    "terminal_map",
    "power_functor",
    "product_functor",
    "precompose",
    "curry",
    "uncurry",
    "transpose",
    "evaluation",
    "currying",
    "natural_isomorphism",
]

from collections.abc import Callable

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function


def pair_maps(
    base: Category,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """Pair two arrows through a chosen binary product."""
    from sage_categories.cat.cones import cone

    assert first.domain() is second.domain()
    from sage_categories.cat.cones import cones

    data = binary_product_data(base, first.codomain(), second.codomain())
    diagram = data.diagram()
    return data.lift(
        cones(diagram)(
            cone(
                diagram,
                first.domain(),
                lambda index: (first, second)[diagram.domain().label(index)],
            )
        )
    )


def binary_product_data(
    base: Category,
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
) -> LimitConesCategory.ObjectType:
    """The chosen binary product presentation, even when its apex presents other diagrams."""
    from sage_categories.cat.constructions import constructed_data
    from sage_categories.cat.diagrams import from_sequence

    diagram = from_sequence(base, (first, second))
    return constructed_data(base.Limits(diagram.domain()), diagram)


def power_data(
    base: Category, value: CategoryOfCategories.ElementType, degree: int
) -> LimitConesCategory.ObjectType:
    from sage_categories.cat.constructions import constructed_data
    from sage_categories.cat.diagrams import from_sequence

    diagram = from_sequence(base, (value,) * degree)
    return constructed_data(base.Limits(diagram.domain()), diagram)


def terminal_map(
    base: Category, value: CategoryOfCategories.ElementType
) -> MorphismCategory.ObjectType:
    from sage_categories.cat.cones import cone, cones

    data = power_data(base, value, 0)
    return data.lift(cones(data.diagram())(cone(data.diagram(), value, data.leg)))


@cached_function
def power_functor(base: Category, degree: int) -> Functor:
    from sage_categories.cat.cones import cone, cones

    def action(arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        source, target = (
            power_data(base, arrow.domain(), degree),
            power_data(base, arrow.codomain(), degree),
        )
        return target.lift(
            cones(target.diagram())(
                cone(
                    target.diagram(),
                    source.apex(),
                    lambda vertex: arrow * source.leg(vertex),
                )
            )
        )

    return Fun(base, base)(lambda value: power_data(base, value, degree).apex(), action)


@cached_function(key=identity_key)
def product_functor(base: Category) -> Functor:
    """The chosen binary-product functor ``C × C -> C``."""
    pairs = Cat().Products()((base, base))
    result = Fun(pairs, base)(
        lambda pair: base.Products()((pair.component(0), pair.component(1))),
        lambda arrow: pair_maps(
            base,
            arrow.component(0)
            * binary_product_data(
                base, arrow.domain().component(0), arrow.domain().component(1)
            ).leg(0),
            arrow.component(1)
            * binary_product_data(
                base, arrow.domain().component(0), arrow.domain().component(1)
            ).leg(1),
        ),
    )
    return result


@cached_function(key=identity_key)
def precompose(along: Functor, target: Category) -> Functor:
    """Restriction ``along*: Fun(B,C) -> Fun(A,C)``."""
    return Fun(Fun(along.codomain(), target), Fun(along.domain(), target))(
        lambda functor: functor * along,
        lambda transformation: transformation.whisker_right(along),
    )


@cached_function(key=identity_key)
def curry(functor: Functor) -> Functor:
    """Curry a functor on a chosen binary product of categories."""
    pairs, target = functor.domain(), functor.codomain()
    first, second = (
        pairs.product_projection(0).codomain(),
        pairs.product_projection(1).codomain(),
    )

    def at(value: CategoryOfCategories.ElementType) -> Functor:
        identity = Mor(first)(value, value).one()
        return Fun(second, target)(
            lambda other: functor.on_object(pairs((value, other))),
            lambda arrow: functor.on_morphism(
                pairs.construct_morphism(
                    pairs((value, arrow.domain())),
                    pairs((value, arrow.codomain())),
                    (identity, arrow),
                )
            ),
        )

    def on_morphism(arrow: MorphismCategory.ObjectType) -> NaturalTransformation:
        return Mor(Fun(second, target))(
            result.on_object(arrow.domain()), result.on_object(arrow.codomain())
        )(
            lambda value: functor.on_morphism(
                pairs.construct_morphism(
                    pairs((arrow.domain(), value)),
                    pairs((arrow.codomain(), value)),
                    (arrow, Mor(second)(value, value).one()),
                )
            )
        )

    result = Fun(first, Fun(second, target))(at, on_morphism)
    return result


@cached_function(key=identity_key)
def uncurry(functor: Functor) -> Functor:
    """Uncurry ``A -> Fun(B,C)`` on objects and pairs of morphisms."""
    first, functors = functor.domain(), functor.codomain()
    second, target = functors.domain(), functors.codomain()
    pairs = Cat().Products()((first, second))

    def on_morphism(arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        left, right = arrow.component(0), arrow.component(1)
        return functor.on_morphism(left).component(right.codomain()) * functors.diagram(
            functor.on_object(left.domain())
        ).on_morphism(right)

    return Fun(pairs, target)(
        lambda value: functors.diagram(functor.on_object(value.component(0))).on_object(
            value.component(1)
        ),
        on_morphism,
    )


@cached_function(key=identity_key)
def transpose(functor: Functor) -> Functor:
    """Interchange the variables of ``A -> Fun(B,C)``."""
    first, functors = functor.domain(), functor.codomain()
    second, target = functors.domain(), functors.codomain()

    def at(value: CategoryOfCategories.ElementType) -> Functor:
        return Fun(first, target)(
            lambda other: functors.diagram(functor.on_object(other)).on_object(value),
            lambda arrow: functor.on_morphism(arrow).component(value),
        )

    result = Fun(second, Fun(first, target))(
        at,
        lambda arrow: Mor(Fun(first, target))(
            result.on_object(arrow.domain()), result.on_object(arrow.codomain())
        )(lambda value: functors.diagram(functor.on_object(value)).on_morphism(arrow)),
    )
    return result


@cached_function(key=identity_key)
def evaluation(first: Category, target: Category) -> Functor:
    """The evaluation functor ``Fun(A,C) × A -> C``."""
    functors = Fun(first, target)
    return uncurry(Fun(functors, functors).one())


@cached_function(key=identity_key)
def currying(
    first: Category, second: Category, target: Category
) -> CategoryOfCategories.ElementType:
    """The selected equivalence of functor categories given by currying."""
    from sage_categories.cat.adjunctions import Equivalences

    pairs = Cat().Products()((first, second))
    source, destination = Fun(pairs, target), Fun(first, Fun(second, target))
    forward = Fun(source, destination)(
        curry,
        lambda transformation: Mor(destination)(
            curry(transformation.domain()), curry(transformation.codomain())
        )(
            lambda value: Mor(Fun(second, target))(
                curry(transformation.domain()).on_object(value),
                curry(transformation.codomain()).on_object(value),
            )(lambda other: transformation.component(pairs((value, other))))
        ),
    )
    inverse = Fun(destination, source)(
        uncurry,
        lambda transformation: Mor(source)(
            uncurry(transformation.domain()), uncurry(transformation.codomain())
        )(
            lambda pair: transformation.component(pair.component(0)).component(
                pair.component(1)
            )
        ),
    )

    @cached_function(key=identity_key)
    def unit_component(functor: Functor) -> NaturalTransformation:
        roundtrip = uncurry(curry(functor))
        identity = lambda pair: Mor(target)(
            functor.on_object(pair), functor.on_object(pair)
        ).one()
        return natural_isomorphism(functor, roundtrip, identity, identity)

    @cached_function(key=identity_key)
    def counit_component(functor: Functor) -> NaturalTransformation:
        roundtrip = curry(uncurry(functor))

        @cached_function(key=identity_key)
        def component(value: CategoryOfCategories.ElementType) -> NaturalTransformation:
            original = functor.on_object(value)
            identity = lambda other: Mor(target)(
                original.on_object(other), original.on_object(other)
            ).one()
            return natural_isomorphism(
                roundtrip.on_object(value), original, identity, identity
            )

        return natural_isomorphism(
            roundtrip, functor, component, lambda value: component(value).inverse()
        )

    unit = natural_isomorphism(
        Fun(source, source).one(),
        inverse * forward,
        unit_component,
        lambda functor: unit_component(functor).inverse(),
    )
    counit = natural_isomorphism(
        forward * inverse,
        Fun(destination, destination).one(),
        counit_component,
        lambda functor: counit_component(functor).inverse(),
    )
    return Equivalences(source, destination)(forward, inverse, unit, counit)


def natural_isomorphism(
    first: Functor,
    second: Functor,
    components: Callable[
        [CategoryOfCategories.ElementType], MorphismCategory.ObjectType
    ],
    inverses: Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType],
) -> NaturalTransformation:
    """Retain a natural isomorphism with both executable component assignments."""
    category = Fun(first.domain(), first.codomain())
    forward = Mor(category)(first, second)(components)
    backward = Mor(category)(second, first)(inverses)
    category.retain_inverses(forward, backward)
    return forward
