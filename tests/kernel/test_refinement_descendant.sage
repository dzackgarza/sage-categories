"""Refining a category preserves objects already placed in descendants above it (#31)."""

from sage_categories.cat.category import Axiom, Category, ask
from sage_categories.cat.functors import Fun
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.properties import FullSubcategory, PropertySubcategory
from sage_categories.kernel.construction import retained_object_input
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.sets.finite import Sets


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

        def middle_arrow(self):
            return self

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

        def upper_arrow(self):
            return self

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
        def tagged_arrow(self):
            return self


class PlacementTarget(Category):
    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass


class PlacementSource(Category):
    class ObjectType:
        def __init__(self, value: int) -> None:
            self._placement_value = value

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, target: PlacementTarget) -> None:
        self._target = target
        super().__init__()

    def __call__(self, value: int) -> PlacementSource.ObjectType:
        return self.ObjectType(value)

    def structure_functors(self):
        return (Fun.full_subcategory_monomorphism(self, self._target),)


class DetachedPlacement(FullSubcategory):
    """A narrowing whose public structural graph deliberately omits its ambient inclusion."""

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self):
        return ()


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
    identity = Mor(tagged)(value, value).one()
    assert identity.middle_arrow() is identity
    assert identity.upper_arrow() is identity
    assert identity.tagged_arrow() is identity

    # Refining the intermediate category rebuilds every descendant runtime class.  The
    # already-placed object and arrow must move to those replacements without losing any
    # declaration or changing their retained identities.
    assert ask(middle.is_concrete()) is True
    assert value.category() is tagged
    assert value.middle_value() == 7
    assert value.upper_value() == 7
    assert value.tagged_value() == 7
    assert identity.domain() is value and identity.codomain() is value
    assert identity.middle_arrow() is identity
    assert identity.upper_arrow() is identity
    assert identity.tagged_arrow() is identity
    assert Mor(tagged)(value, value).one() is identity


def test_refined_value_still_traces_its_retained_construction_placement() -> None:
    target = PlacementTarget()
    source = PlacementSource(target)
    detached = DetachedPlacement(source)
    value = source(11)
    identity = Mor(source)(value, value).one()
    assert is_placed(value, target)
    assert is_placed(identity, Mor(target))

    refine(value, detached)
    refine(identity, Mor(detached))
    assert value.category() is detached
    assert is_placed(value, source)
    assert is_placed(value, target)
    assert is_placed(identity, Mor(detached))
    assert is_placed(identity, Mor(source))
    assert is_placed(identity, Mor(target))


test_refining_intermediate_category_preserves_existing_placed_descendant()
test_refined_value_still_traces_its_retained_construction_placement()
