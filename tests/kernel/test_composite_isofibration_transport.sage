"""Composite isofibrations transport inherited state through the selected chain."""

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.predicates import ask


class TransportBase(Category):
    class ObjectType:
        def __init__(self, value: int) -> None:
            self._base_value = value

        def base_value(self) -> int:
            return self._base_value

    class ElementType:
        pass

    class MorphismType:
        pass

    def __call__(self, value: int) -> TransportBase.ObjectType:
        return self.ObjectType(value)


class TransportMiddle(Category):
    class ObjectType:
        def __init__(self, value: int) -> None:
            self._middle_value = value

        def middle_value(self) -> int:
            return self._middle_value

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, base: TransportBase) -> None:
        self._base = base

    def __call__(self, value: int) -> TransportMiddle.ObjectType:
        return self.ObjectType(value)

    def structure_functors(self):
        def on_object(value):
            return self._base(value.middle_value() + 1)

        def on_morphism(arrow):
            image = on_object(arrow.domain())
            return Mor(self._base)(image, image).one()

        return (Fun(self, self._base).Isofibrations()(on_object, on_morphism),)


class TransportSource(Category):
    class ObjectType:
        def __init__(self, value: int) -> None:
            self._source_value = value

        def source_value(self) -> int:
            return self._source_value

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, middle: TransportMiddle) -> None:
        self._middle = middle

    def __call__(self, value: int) -> TransportSource.ObjectType:
        return self.ObjectType(value)

    def structure_functors(self):
        def on_object(value):
            return self._middle(2 * value.source_value())

        def on_morphism(arrow):
            image = on_object(arrow.domain())
            return Mor(self._middle)(image, image).one()

        return (Fun(self, self._middle).Isofibrations()(on_object, on_morphism),)


def test_composite_isofibration_transports_generic_state() -> None:
    base = TransportBase()
    middle = TransportMiddle(base)
    source = TransportSource(middle)
    to_middle = source.selected_functors()[0]
    to_base = middle.selected_functors()[0]
    composite = to_base * to_middle

    assert ask(composite.is_isofibrations()) is True
    value = source(7)
    assert value.source_value() == 7
    assert value.middle_value() == 14
    assert value.base_value() == 15

    middle_image = to_middle.on_object(value)
    base_image = to_base.on_object(middle_image)
    assert middle_image.middle_value() == 14
    assert base_image.base_value() == 15
    assert composite.on_object(value) is base_image


test_composite_isofibration_transports_generic_state()
