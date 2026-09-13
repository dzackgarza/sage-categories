"""Isomorphisms of Cat retain executable inverse functors."""

from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.shapes import Discrete
from sage_categories.kernel.refinement import refine
from sage_categories.sets.finite import Sets


def test_cat_isomorphism_requires_retained_executable_inverse() -> None:
    forward = Fun(Sets(), Sets())(lambda value: value, lambda arrow: arrow)
    inverse = Fun(Sets(), Sets())(lambda value: value, lambda arrow: arrow)
    isomorphisms = Fun(Sets(), Sets()).Isomorphisms()

    try:
        isomorphisms(
            lambda value: value,
            lambda arrow: arrow,
        )
    except AssertionError:
        pass
    else:
        raise AssertionError("Cat constructed an isomorphism without executable inverse data")

    try:
        refine(forward, isomorphisms)
    except AssertionError:
        pass
    else:
        raise AssertionError("Cat accepted an isomorphism without executable inverse data")

    Cat().retain_inverses(forward, inverse)
    assert forward.inverse() is inverse
    assert inverse.inverse() is forward
    carrier = Sets((0,))
    assert forward.inverse().on_object(carrier) is carrier
    identity = Mor(Sets())(carrier, carrier)(lambda value: value)
    assert forward.inverse().on_morphism(identity) is identity


def test_data_free_category_keeps_symbolic_inverse() -> None:
    labels = Sets(("x",))
    discrete = Discrete(labels)
    vertex = discrete(labels.point("x"))
    arrow = Mor(discrete)(vertex, vertex).Isomorphisms()()
    inverse = arrow.inverse()
    assert inverse.domain() is vertex
    assert inverse.codomain() is vertex


test_cat_isomorphism_requires_retained_executable_inverse()
test_data_free_category_keeps_symbolic_inverse()
