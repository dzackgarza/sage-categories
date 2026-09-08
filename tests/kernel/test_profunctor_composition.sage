"""Coend composition of profunctors and horizontal natural transformations."""

from sage_categories.all import Cat, Fun, Mor, ask
from sage_categories.sets import FiniteSets as S
from sage_categories.cat.profunctors import (
    Profunctors,
    compose_profunctors,
    compose_profunctor_transformations,
    profunctor_unitor,
)
from sage_categories.cat.weighted import hom_functor


def test_hom_profunctor_composition_and_nonidentity_two_cells():
    base = Cat().Simplex(1)
    hom = hom_functor(base, S)
    composite = compose_profunctors(hom, hom, hom)
    assert len(tuple(composite.on_object(composite.domain()((base(0), base(1)))))) == 1
    assert len(tuple(composite.on_object(composite.domain()((base(1), base(0)))))) == 0
    values, singleton = S((0, 1)), S((2,))
    category = Profunctors(base, base, S)
    first, second = category.constant(values), category.constant(singleton)
    flip = Mor(S)(values, values)(lambda x: 1 - x)
    alpha = Mor(category)(first, first)(lambda pair: flip)
    beta = Mor(category)(second, second).one()
    horizontal = compose_profunctor_transformations(alpha, beta, hom)
    pair = horizontal.domain().domain()((base(0), base(1)))
    component = horizontal.component(pair)
    assert len(tuple(component.domain())) == 2
    for point in component.domain():
        assert ask(component(point) == point) is False
        assert ask(component(component(point)) == point) is True
    for left in (True, False):
        unitor = profunctor_unitor(first, hom, left)
        forward = unitor.component(first.domain()((base(0), base(1))))
        inverse = unitor.inverse().component(first.domain()((base(0), base(1))))
        for point in values:
            assert ask(forward(inverse(point)) == point) is True


test_hom_profunctor_composition_and_nonidentity_two_cells()
