"""Points retain their source category through structured placement."""

from sage_categories.all import Cat, Category, Fun, Mor, Sets
from sage_categories.cat.functors import Functor, FunctorCategory, NaturalTransformation


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

    def structure_functors(self) -> tuple[Functor, ...]:
        return (STRUCTURED_POINTS.Point(),)


def test_named_point_retains_its_category_and_element_data() -> None:
    source = NamedPoints()
    point = source.ObjectType(7)
    defining = point.defining_morphism()
    assert point.parent() is source
    assert point.coordinate() == 7
    assert defining in Fun(Cat().Terminal(), source)
    assert defining.on_object(Cat().Terminal()(0)) is point
    assert source in STRUCTURED_POINTS
    assert source in Cat()


def test_set_point_is_a_functor_to_its_owned_parent() -> None:
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


def test_functor_transports_points_and_generalized_elements_by_composition() -> None:
    source = Cat().Simplex(2)
    edge = lambda i, j: Mor(source)(source(i), source(j))(
        tuple(f"{k}->{k + 1}" for k in range(i, j))
    )
    shift = Fun(source, source)(
        lambda vertex: source(max(1, source.label(vertex))),
        lambda arrow: edge(
            max(1, source.label(arrow.domain())), max(1, source.label(arrow.codomain()))
        ),
    )
    assert shift.on_element(source(0)) is source(1)
    generalized = Cat().element_from_defining_morphism(Fun(source, source).one())
    image = shift.on_element(generalized)
    assert image.parent() is source
    assert image.defining_morphism() is shift
    assert image.defining_morphism().on_morphism(edge(0, 2)).domain() is source(1)


class PresentedEndofunctors(Category[[NaturalTransformation], []]):
    class ObjectType:
        def __init__(self, functor: Functor) -> None:
            self._presented_functor = functor

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, transformation: NaturalTransformation) -> None:
            self._presented_transformation = transformation

    def __init__(self, target: FunctorCategory) -> None:
        self._target = target

    def structure_functors(self) -> tuple[Functor, ...]:
        def on_object(value: PresentedEndofunctors.ObjectType) -> Functor:
            return value._presented_functor

        def on_morphism(arrow: PresentedEndofunctors.MorphismType) -> NaturalTransformation:
            return arrow._presented_transformation

        return (Fun(self, self._target).Faithful().Isofibrations()(on_object, on_morphism),)


def test_functor_implementation_preserves_its_source_object_role() -> None:
    interval = Cat().Simplex(1)
    functors = Fun(interval, interval)
    source = PresentedEndofunctors(functors)
    represented = functors.constant(interval(1))
    value = source.ObjectType(represented)
    assert value in source
    assert value.parent() is source
    assert value.domain() is interval and value.codomain() is interval
    assert value.on_object(interval(0)) is interval(1)
    assert value.on_morphism(interval.generator("0->1")).domain() is interval(1)
    assert source.selected_functors()[0].on_object(value) is represented


test_named_point_retains_its_category_and_element_data()
test_set_point_is_a_functor_to_its_owned_parent()
test_functor_transports_points_and_generalized_elements_by_composition()
test_functor_implementation_preserves_its_source_object_role()
