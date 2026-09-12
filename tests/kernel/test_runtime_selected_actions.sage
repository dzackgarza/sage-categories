"""Runtime construction preserves selected-action order and retained images."""

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.morphisms import Mor


class Scalars(Category):
    class ObjectType:
        def __init__(self, value: int) -> None:
            self._scalar = value

        def scalar(self) -> int:
            return self._scalar

    class ElementType:
        pass

    class MorphismType:
        pass

    def __call__(self, value: int) -> Scalars.ObjectType:
        return self.ObjectType(value)


class ScalarPair(Category):
    class ObjectType:
        def __init__(self, values: tuple[int, int]) -> None:
            self._coordinates = values

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, first: Scalars, second: Scalars, reverse: bool) -> None:
        self._targets = (first, second)
        self._reverse = reverse

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        def projection(index: int, target: Scalars) -> Cat().MorphismType:
            return Fun(self, target).Isofibrations()(
                lambda value: target(value._coordinates[index]),
                lambda arrow: Mor(target)(
                    target(arrow.domain()._coordinates[index]),
                    target(arrow.codomain()._coordinates[index]),
                ).one(),
            )

        selected = tuple(projection(index, target) for index, target in enumerate(self._targets))
        return selected[::-1] if self._reverse else selected

    def __call__(self, values: tuple[int, int]) -> ScalarPair.ObjectType:
        return self.ObjectType(values)


def test_runtime_selected_actions() -> None:
    first, second = Scalars(), Scalars()
    forward = ScalarPair(first, second, False)
    reverse = ScalarPair(first, second, True)

    forward_value = forward((3, 5))
    reverse_value = reverse((7, 11))
    assert forward_value.scalar() == 3
    assert reverse_value.scalar() == 11

    forward_identity = Mor(forward)(forward_value, forward_value).one()
    images = tuple(functor.on_object(forward_value) for functor in forward.selected_functors())
    arrow_images = tuple(functor.on_morphism(forward_identity) for functor in forward.selected_functors())

    assert tuple(image.scalar() for image in images) == (3, 5)
    assert all(functor.on_object(forward_value) is image for functor, image in zip(forward.selected_functors(), images))
    assert all(functor.on_morphism(forward_identity) is image for functor, image in zip(forward.selected_functors(), arrow_images))
    assert forward_value.scalar() == 3
    assert Mor(forward)(forward_value, forward_value).one() is forward_identity


test_runtime_selected_actions()
