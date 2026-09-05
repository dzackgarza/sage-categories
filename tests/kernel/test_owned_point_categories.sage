"""Points retain their source category through structured placement."""

from sage_categories.all import Cat, Category, Fun, Mor, Sets


class StructuredPoints(Category):
    class ObjectType:
        pass

    class ElementType:
        def __init__(self, value: int) -> None:
            self._coordinate = value

        def coordinate(self) -> int:
            return self._coordinate

    class MorphismType:
        pass


STRUCTURED_POINTS = StructuredPoints()


class NamedPoints(Category):
    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self):
        return (STRUCTURED_POINTS.Point(),)


def test_named_point_retains_its_category_and_element_data():
    source = NamedPoints()
    point = source.ObjectType(7)
    defining = point.defining_morphism()
    assert point.parent() is source
    assert point.coordinate() == 7
    assert defining in Fun(Cat().Terminal(), source)
    assert defining.on_object(Cat().Terminal()(0)) is point
    assert source in STRUCTURED_POINTS
    assert source in Cat()


def test_set_point_is_a_functor_to_its_owned_parent():
    source, target = Sets((0, 1, 2)), Sets((0, 1))
    point = source.point(2)
    defining = point.defining_morphism()
    assert defining in Fun(Cat().Terminal(), source)
    assert defining.on_object(Cat().Terminal()(0)) is point
    arrow = Mor(Sets)(source, target)(lambda value: value % 2)
    image = arrow(point)
    assert image.parent() is target
    assert image.datum() == 0
    assert image.defining_morphism().codomain() is target


test_named_point_retains_its_category_and_element_data()
test_set_point_is_a_functor_to_its_owned_parent()
