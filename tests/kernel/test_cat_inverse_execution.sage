"""Isomorphisms of Cat retain executable inverse functors."""

import pytest

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.morphisms import Mor, endpoints
from sage_categories.cat.predicates import ask, assume, retract
from sage_categories.sets.finite import Sets


class DataFreeCategory(Category):
    """A category whose arrows have endpoints and no further datum."""

    class ObjectType:
        def __init__(self, label: str) -> None:
            self.label = label

    class ElementType:
        pass

    class MorphismType:
        pass

    def __call__(self, label: str) -> CategoryOfCategories.ElementType:
        return self.ObjectType(label)


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

    proposition = isomorphisms.membership_proposition(forward)
    with pytest.raises(AssertionError):
        assume(proposition)
    retract(proposition)

    Cat().retain_inverses(forward, inverse)
    assert forward.inverse() is inverse
    assert inverse.inverse() is forward
    carrier = Sets((0,))
    assert forward.inverse().on_object(carrier) is carrier
    identity = Mor(Sets())(carrier, carrier)(lambda value: value)
    assert forward.inverse().on_morphism(identity) is identity


def test_exact_functor_endpoints_are_decided_by_identity_without_evaluation() -> None:
    def no_object_action(_value):
        raise AssertionError("exact endpoint admission evaluated the functor")

    def no_morphism_action(_arrow):
        raise AssertionError("exact endpoint admission evaluated the functor")

    sets = Sets()
    functor = Fun(sets, sets)(no_object_action, no_morphism_action)
    assert ask(endpoints(functor, sets, sets)) is True


def test_data_free_category_keeps_symbolic_inverse() -> None:
    category = DataFreeCategory()
    source, target = category("source"), category("target")
    arrow = Mor(category)(source, target).Isomorphisms()()
    inverse = arrow.inverse()
    assert inverse.domain() is target
    assert inverse.codomain() is source


test_cat_isomorphism_requires_retained_executable_inverse()
test_exact_functor_endpoints_are_decided_by_identity_without_evaluation()
test_data_free_category_keeps_symbolic_inverse()
