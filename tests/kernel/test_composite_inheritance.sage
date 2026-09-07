"""A selected composite transports the defining state of its target operation."""

from __future__ import annotations

from sage_categories.all import Cat, Category, Fun, Mor


class IntegerValues(Category):
    class ObjectType:
        def __init__(self, value: Integer) -> None:
            self._integer_value = value

        def integer_value(self) -> Integer:
            return self._integer_value

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: None) -> None:
            assert self.domain() is self.codomain()

    def __call__(self, value: Integer) -> IntegerValues.ObjectType:
        return self.ObjectType(value)


class IntermediateIntegers(Category):
    class ObjectType:
        def __init__(self, value: Integer) -> None:
            self._intermediate_value = value

        def intermediate_value(self) -> Integer:
            return self._intermediate_value

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: None) -> None:
            assert self.domain() is self.codomain()

    def __call__(self, value: Integer) -> IntermediateIntegers.ObjectType:
        return self.ObjectType(value)


class TranslatedIntegers(Category):
    class ObjectType:
        def __init__(self, value: Integer) -> None:
            self._source_value = value

        def source_value(self) -> Integer:
            return self._source_value

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: None) -> None:
            assert self.domain() is self.codomain()

    def __init__(self, intermediate: IntermediateIntegers, doubling: Cat().MorphismType) -> None:
        self._intermediate = intermediate
        self._doubling = doubling

    def __call__(self, value: Integer) -> TranslatedIntegers.ObjectType:
        return self.ObjectType(value)

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        def on_object(value: TranslatedIntegers.ObjectType) -> IntermediateIntegers.ObjectType:
            return self._intermediate(value.source_value() + 1)

        def on_morphism(arrow: TranslatedIntegers.MorphismType) -> IntermediateIntegers.MorphismType:
            return Mor(self._intermediate)(on_object(arrow.domain()), on_object(arrow.codomain())).one()

        translation = Fun(self, self._intermediate).Isofibrations()(on_object, on_morphism)
        return (self._doubling * translation,)


def test_composite_inheritance_uses_the_composite_image() -> None:
    integers, intermediate = IntegerValues(), IntermediateIntegers()

    def on_object(value: IntermediateIntegers.ObjectType) -> IntegerValues.ObjectType:
        return integers(2 * value.intermediate_value())

    def on_morphism(arrow: IntermediateIntegers.MorphismType) -> IntegerValues.MorphismType:
        return Mor(integers)(on_object(arrow.domain()), on_object(arrow.codomain())).one()

    doubling = Fun(intermediate, integers).Isofibrations()(on_object, on_morphism)
    translated = TranslatedIntegers(intermediate, doubling)
    (composite,) = translated.selected_functors()
    translation, retained_doubling = composite.factors()
    assert retained_doubling is doubling
    assert Fun.declares_inheritance(translation)
    assert Fun.declares_inheritance(doubling)
    assert Fun.declares_inheritance(composite)

    value = translated(3)
    assert value.source_value() == 3
    assert value.integer_value() == 8
    assert composite.on_object(value) is integers(8)
    identity = Mor(translated)(value, value).one()
    image = composite.on_morphism(identity)
    assert image.domain() is integers(8) and image.codomain() is integers(8)


test_composite_inheritance_uses_the_composite_image()
