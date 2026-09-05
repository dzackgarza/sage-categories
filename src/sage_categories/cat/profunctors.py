"""Set-valued profunctors and their coend composition.

Reference: Loregian, Coend calculus, section 5.1. Products and coends own
the action on arrows and on natural transformations.
"""

from __future__ import annotations

__all__ = [
    "Profunctors",
    "compose_profunctors",
    "compose_profunctor_transformations",
    "identity_profunctor",
    "profunctor_unitor",
]

from collections.abc import Hashable

from sage_categories.cat.calculus import binary_product_data, pair_maps, product_functor
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.weighted import (
    coend,
    coend_weight,
    hom_functor,
    weighted_colimit_map,
)
from sage_categories.cat.weighted import weighted_colimit_desc, weighted_injection
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function


def Profunctors(first: Category, second: Category, sets: Category) -> Category:
    return Fun(Cat().Products()((first.op(), second)), sets)


@cached_function(key=identity_key)
def _integrand(
    first: Functor, second: Functor, outer: CategoryOfCategories.ElementType
) -> Functor:
    middle = first.domain().product_projection(1).codomain()
    middle_pairs = Cat().Products()((middle.op(), middle))
    sets = first.codomain()
    tensor = product_functor(sets)
    pairs = tensor.domain()
    left, right = first.domain(), second.domain()
    a, c = outer.component(0), outer.component(1)

    def factors(
        value: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return pairs(
            (
                first.on_object(left((a, value.component(1)))),
                second.on_object(right((value.component(0), c))),
            )
        )

    def on_morphism(arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        p = left.construct_morphism(
            left((a, arrow.domain().component(1))),
            left((a, arrow.codomain().component(1))),
            (Mor(left.factor(0))(a, a).one(), arrow.component(1)),
        )
        q = right.construct_morphism(
            right((arrow.domain().component(0), c)),
            right((arrow.codomain().component(0), c)),
            (arrow.component(0), Mor(right.factor(1))(c, c).one()),
        )
        return tensor.on_morphism(
            pairs.construct_morphism(
                factors(arrow.domain()),
                factors(arrow.codomain()),
                (first.on_morphism(p), second.on_morphism(q)),
            )
        )

    return Fun(middle_pairs, sets)(
        lambda value: tensor.on_object(factors(value)), on_morphism
    )


@cached_function(key=identity_key)
def compose_profunctors(first: Functor, second: Functor, hom: Functor) -> Functor:
    """``(P ; Q)(a,c) = integral^b P(a,b) × Q(b,c)``."""
    middle = first.domain().product_projection(1).codomain()
    assert second.domain().product_projection(0).codomain() is middle.op()
    assert hom.domain() is Cat().Products()((middle.op(), middle))
    assert first.codomain() is second.codomain() is hom.codomain()
    sets, tensor = first.codomain(), product_functor(first.codomain())
    source = Cat().Products()((first.domain().factor(0), second.domain().factor(1)))

    def on_morphism(arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        start, end = (
            _integrand(first, second, arrow.domain()),
            _integrand(first, second, arrow.codomain()),
        )

        def component(
            value: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            left, right = first.domain(), second.domain()
            p = left.construct_morphism(
                left((arrow.domain().component(0), value.component(1))),
                left((arrow.codomain().component(0), value.component(1))),
                (
                    arrow.component(0),
                    Mor(middle)(value.component(1), value.component(1)).one(),
                ),
            )
            q = right.construct_morphism(
                right((value.component(0), arrow.domain().component(1))),
                right((value.component(0), arrow.codomain().component(1))),
                (
                    Mor(middle.op())(value.component(0), value.component(0)).one(),
                    arrow.component(1),
                ),
            )
            factors = tensor.domain()
            return tensor.on_morphism(
                factors.construct_morphism(
                    factors(
                        (first.on_object(p.domain()), second.on_object(q.domain()))
                    ),
                    factors(
                        (first.on_object(p.codomain()), second.on_object(q.codomain()))
                    ),
                    (first.on_morphism(p), second.on_morphism(q)),
                )
            )

        transformation = Mor(Fun(hom.domain(), sets))(start, end)(component)
        return weighted_colimit_map(coend_weight(hom), transformation)

    return Fun(source, sets)(
        lambda value: coend(_integrand(first, second, value), hom), on_morphism
    )


def compose_profunctor_transformations(
    first: NaturalTransformation, second: NaturalTransformation, hom: Functor
) -> NaturalTransformation:
    """Horizontal composition of transformations of profunctors."""
    source = compose_profunctors(first.domain(), second.domain(), hom)
    target = compose_profunctors(first.codomain(), second.codomain(), hom)
    tensor = product_functor(hom.codomain())

    def component(
        outer: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        start, end = (
            _integrand(first.domain(), second.domain(), outer),
            _integrand(first.codomain(), second.codomain(), outer),
        )

        def at(value: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            p = first.component(
                first.domain().domain()((outer.component(0), value.component(1)))
            )
            q = second.component(
                second.domain().domain()((value.component(0), outer.component(1)))
            )
            pairs = tensor.domain()
            return tensor.on_morphism(
                pairs.construct_morphism(
                    pairs((p.domain(), q.domain())),
                    pairs((p.codomain(), q.codomain())),
                    (p, q),
                )
            )

        return weighted_colimit_map(
            coend_weight(hom), Mor(Fun(hom.domain(), hom.codomain()))(start, end)(at)
        )

    return Mor(Fun(source.domain(), source.codomain()))(source, target)(component)


def identity_profunctor(category: Category, sets: Category) -> Functor:
    return hom_functor(category, sets)


@cached_function(key=identity_key)
def _unitor_components(
    profunctor: Functor,
    hom: Functor,
    left: bool,
    outer: CategoryOfCategories.ElementType,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    first, second = (hom, profunctor) if left else (profunctor, hom)
    composite = compose_profunctors(first, second, hom)
    diagram, weight = _integrand(first, second, outer), coend_weight(hom)
    sets = profunctor.codomain()
    target = profunctor.on_object(outer)
    a, c = outer.component(0), outer.component(1)
    middle = hom.domain().factor(1)

    def component(
        index: CategoryOfCategories.ElementType, point: CategoryOfCategories.ElementType
    ) -> MorphismCategory.ObjectType:
        p = first.on_object(first.domain()((a, index.component(1))))
        q = second.on_object(second.domain()((index.component(0), c)))
        product = binary_product_data(sets, p, q)
        connecting = point.datum()

        def action(datum: Hashable) -> Hashable:
            value = product.apex().point(datum)
            x, y = product.leg(0)(value), product.leg(1)(value)
            pairs = profunctor.domain()
            if left:
                arrow = connecting * x.datum()
                transport = pairs.construct_morphism(
                    pairs((index.component(0), c)),
                    outer,
                    (opposite_morphism(arrow), Mor(pairs.factor(1))(c, c).one()),
                )
                return profunctor.on_morphism(transport)(y).datum()
            arrow = y.datum() * connecting
            transport = pairs.construct_morphism(
                pairs((a, index.component(1))),
                outer,
                (Mor(pairs.factor(0))(a, a).one(), arrow),
            )
            return profunctor.on_morphism(transport)(x).datum()

        return Mor(sets)(product.apex(), target)(action)

    forward = weighted_colimit_desc(weight, diagram, target, component)
    vertex = a if left else c
    index = hom.domain()((vertex, vertex))
    identity = Mor(middle)(vertex, vertex).one()
    weight_point = weight.on_object(index).point(identity)
    hom_point = hom.on_object(index).point(identity)
    injection = weighted_injection(weight, diagram, index, weight_point)

    def inverse_action(datum: Hashable) -> Hashable:
        value = target.point(datum)
        p, q = (hom_point, value) if left else (value, hom_point)
        paired = sets.element_from_defining_morphism(
            pair_maps(sets, p.defining_morphism(), q.defining_morphism())
        )
        return injection(paired).datum()

    inverse = Mor(sets)(target, composite.on_object(outer))(inverse_action)
    sets.retain_inverses(forward, inverse)
    return forward, inverse


@cached_function(key=identity_key)
def profunctor_unitor(
    profunctor: Functor, hom: Functor, left: bool = True
) -> NaturalTransformation:
    """The co-Yoneda isomorphism for composition with the identity profunctor."""
    composite = (
        compose_profunctors(hom, profunctor, hom)
        if left
        else compose_profunctors(profunctor, hom, hom)
    )
    functors = Fun(profunctor.domain(), profunctor.codomain())
    forward = Mor(functors)(composite, profunctor)(
        lambda value: _unitor_components(profunctor, hom, left, value)[0]
    )
    inverse = Mor(functors)(profunctor, composite)(
        lambda value: _unitor_components(profunctor, hom, left, value)[1]
    )
    functors.retain_inverses(forward, inverse)
    return forward
