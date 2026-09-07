"""A named set receives its point category from its declared Sets point."""

from pytest import raises

from sage_categories.cat.declarations import NN
from sage_categories.all import Cat, Fun, Sets

declared = NN
import sage_categories.sets.natural


def test_named_positive_integers_retain_their_declaration_and_points() -> None:
    assert NN is declared
    assert NN in Sets()
    point = NN.point(3)
    assert point.parent() is NN
    assert point.datum() == 3
    assert NN.point(3) is point
    defining = point.defining_morphism()
    assert defining in Fun(Cat().Terminal(), NN)
    assert defining.on_object(Cat().Terminal()(0)) is point
    with raises(AssertionError):
        NN.point(0)


test_named_positive_integers_retain_their_declaration_and_points()
