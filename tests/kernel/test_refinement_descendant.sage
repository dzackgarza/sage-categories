"""Refining a category preserves objects already placed in descendants above it (#31)."""

from sage_categories.all import Axiom, Category, Fun, Mor, Sets, ask
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.construction import retained_object_input


class RefinementMiddle(Category):
    class ObjectType:
        def __init__(self, value: int) -> None:
            self._middle_value = value

        def middle_value(self) -> int:
            return self._middle_value

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: None) -> None:
            pass

    def __call__(self, value: int) -> RefinementMiddle.ObjectType:
        return self.ObjectType(value)

    def structure_functors(self):
        def on_object(value):
            return Sets((value.middle_value(),))

        def on_morphism(arrow):
            return Mor(Sets)(on_object(arrow.domain()), on_object(arrow.codomain()))(
                lambda value: value
            )

        return (Fun(self, Sets).Faithful().Isofibrations()(on_object, on_morphism),)


class RefinementUpper(Category):
    Tagged = Axiom()

    class ObjectType:
        def __init__(self, value: int) -> None:
            self._upper_value = value

        def upper_value(self) -> int:
            return self._upper_value

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, data: None) -> None:
            pass

    def __init__(self, middle: RefinementMiddle) -> None:
        self._middle = middle

    def __call__(self, value: int) -> RefinementUpper.ObjectType:
        return self.ObjectType(value)

    def structure_functors(self):
        def on_object(value):
            return self._middle(value.upper_value())

        def on_morphism(arrow):
            image = on_object(arrow.domain())
            return Mor(self._middle)(image, image).one()

        return (Fun(self, self._middle).Isofibrations()(on_object, on_morphism),)


class TaggedRefinementUpper(PropertySubcategory):
    _base_category_class_and_axiom = (RefinementUpper, "Tagged")

    class ObjectType:
        def tagged_value(self) -> int:
            return self.upper_value()

    class ElementType:
        pass

    class MorphismType:
        pass


def test_refining_intermediate_category_preserves_existing_placed_descendant() -> None:
    middle = RefinementMiddle()
    upper = RefinementUpper(middle)
    tagged = upper.Tagged()

    # Property construction deliberately constructs in ``upper`` and then refines the
    # same object into ``tagged``.  This is the shape that issue #31 lost: the retained
    # construction owner and the object's current category are different.
    value = tagged(7)
    assert retained_object_input(value).identity.category is upper
    assert value.category() is tagged
    assert value.middle_value() == 7
    assert value.upper_value() == 7
    assert value.tagged_value() == 7

    # Refining the intermediate category rebuilds every descendant runtime class.  The
    # already-placed value must move to those replacements without losing any declaration.
    assert ask(middle.is_concrete()) is True
    assert value.category() is tagged
    assert value.middle_value() == 7
    assert value.upper_value() == 7
    assert value.tagged_value() == 7


test_refining_intermediate_category_preserves_existing_placed_descendant()
