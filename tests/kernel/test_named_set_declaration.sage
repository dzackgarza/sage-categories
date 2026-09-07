"""A named set receives its point category from its declared Sets point."""

from pytest import raises

from sage_categories.cat.declarations import NN
from sage_categories.all import Cat, Category, Fun, Sets

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


TwoLabels = Cat().declare("TwoLabels")


class TwoLabelsCategory(Category):
    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def set_presentation(self) -> tuple[str, ...]:
        return ("left", "right")

    def structure_functors(self) -> tuple[Fun.ObjectType, ...]:
        return (Fun(TwoLabels, TwoLabels).one(), Sets.Point())


Cat().implement(TwoLabelsCategory)


def test_named_finite_set_uses_its_defining_presentation() -> None:
    point = TwoLabels.point("right")
    assert point.parent() is TwoLabels
    assert point.datum() == "right"
    enumeration = Sets.chosen_enumeration(TwoLabels)
    assert enumeration(enumeration.domain().point(2)) is point


test_named_positive_integers_retain_their_declaration_and_points()
test_named_finite_set_uses_its_defining_presentation()
