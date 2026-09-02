"""R1: synthetic acceptance for the private Sage-backed category compiler."""

from sage.rings.integer import Integer

import sys

from typing import Self

import pytest

from sage_categories.cat import Fun
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.compiler import SemanticCollisionError
from sage_categories.kernel.roles import CategoryPoint


_BASE_OBJECT_INITIALIZATIONS: list[CategoryPoint] = []
_BASE_ELEMENT_INITIALIZATIONS: list[CategoryPoint] = []
_BASE_MORPHISM_INITIALIZATIONS: list[CategoryPoint] = []
_SELECTED_FUNCTORS: dict[int, tuple[Functor, ...]] = {}
_DIAMOND_TO_LEFT_OBJECT_ACTIONS: list[CategoryPoint] = []
_DIAMOND_TO_LEFT_MORPHISM_ACTIONS: list[CategoryPoint] = []


class _SyntheticCategoryOperations:
    """Construction operations shared only by the synthetic R1 specimens."""

    def __init__(self) -> None:
        self._synthetic_objects: dict[int | Integer, CategoryOfCategories.ElementType] = {}
        super().__init__()

    def __call__(self, label: int | Integer) -> CategoryOfCategories.ElementType:
        if label not in self._synthetic_objects:
            self._synthetic_objects[label] = self.ObjectType(self, label)
        return self._synthetic_objects[label]

    def _label(self, member_object: CategoryPoint) -> int | Integer:
        return member_object._synthetic_label

    def element_from_defining_morphism(self, defining_morphism: MorphismCategory.ObjectType) -> CategoryPoint:
        if defining_morphism not in self._elements:
            self._elements[defining_morphism] = defining_morphism.codomain().category().ElementType(
                defining_morphism,
                self._label(defining_morphism.codomain()),
            )
        return self._elements[defining_morphism]

    def construct_morphism(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        assert domain is codomain
        return self.MorphismType(
            self.morphism_category(1),
            domain,
            codomain,
            self._label(domain),
        )

    def construct_identity(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        return self.MorphismType(
            self.morphism_category(1),
            member_object,
            member_object,
            self._label(member_object),
        )

    def composite(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        assert first.codomain() is second.domain()
        return first


class BaseCategory(_SyntheticCategoryOperations, Category[[], []]):
    class ObjectType:
        def __init__(self, label: int | Integer) -> None:
            _BASE_OBJECT_INITIALIZATIONS.append(self)
            self._base_state = label
            self._synthetic_label = label

        def base_object(self) -> tuple[Self, int | Integer]:
            return self, self._base_state

        def preferred_object(self) -> CategoryOfCategories.ElementType:
            return BASE(0)

        def __pos__(self) -> tuple[Self, int | Integer]:
            return self, self._base_state

    class ElementType:
        def __init__(self, label: int | Integer) -> None:
            _BASE_ELEMENT_INITIALIZATIONS.append(self)
            self._base_element_state = label
            self._synthetic_label = label

        def base_element(self) -> tuple[Self, int | Integer]:
            return self, self._base_element_state

    class MorphismType:
        def __init__(self, label: int | Integer) -> None:
            _BASE_MORPHISM_INITIALIZATIONS.append(self)
            self._base_morphism_state = label
            self._synthetic_label = label

        def base_morphism(self) -> tuple[Self, int | Integer]:
            return self, self._base_morphism_state


BASE = BaseCategory()


class LeftCategory(_SyntheticCategoryOperations, Category[[], []]):
    class ObjectType:
        def __init__(self, label: int | Integer) -> None:
            self._left_state = label
            self._synthetic_label = label

        def left_object(self) -> tuple[Self, int | Integer]:
            return self, self._left_state

    class ElementType:
        def __init__(self, label: int | Integer) -> None:
            self._left_element_state = label
            self._synthetic_label = label

        def left_element(self) -> tuple[Self, int | Integer]:
            return self, self._left_element_state

    class MorphismType:
        def __init__(self, label: int | Integer) -> None:
            self._left_morphism_state = label
            self._synthetic_label = label

        def left_morphism(self) -> tuple[Self, int | Integer]:
            return self, self._left_morphism_state

    def structure_functors(self) -> tuple[Functor, ...]:
        key = id(self)
        if key not in _SELECTED_FUNCTORS:
            _SELECTED_FUNCTORS[key] = (
                Fun(self, BASE)(self._object_to_base, self._morphism_to_base),
            )
        return _SELECTED_FUNCTORS[key]

    def _object_to_base(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return BASE(self._label(member_object))

    def _morphism_to_base(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        domain = self._object_to_base(morphism.domain())
        codomain = self._object_to_base(morphism.codomain())
        return BASE.morphism_category(1)(domain, codomain).one()


LEFT = LeftCategory()


class RightCategory(_SyntheticCategoryOperations, Category[[], []]):
    class ObjectType:
        def __init__(self, label: int | Integer) -> None:
            self._right_state = label
            self._synthetic_label = label

        def right_object(self) -> tuple[Self, int | Integer]:
            return self, self._right_state

    class ElementType:
        def __init__(self, label: int | Integer) -> None:
            self._right_element_state = label
            self._synthetic_label = label

        def right_element(self) -> tuple[Self, int | Integer]:
            return self, self._right_element_state

    class MorphismType:
        def __init__(self, label: int | Integer) -> None:
            self._right_morphism_state = label
            self._synthetic_label = label

        def right_morphism(self) -> tuple[Self, int | Integer]:
            return self, self._right_morphism_state

    def structure_functors(self) -> tuple[Functor, ...]:
        key = id(self)
        if key not in _SELECTED_FUNCTORS:
            _SELECTED_FUNCTORS[key] = (
                Fun(self, BASE)(self._object_to_base, self._morphism_to_base),
            )
        return _SELECTED_FUNCTORS[key]

    def _object_to_base(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return BASE(self._label(member_object))

    def _morphism_to_base(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        domain = self._object_to_base(morphism.domain())
        codomain = self._object_to_base(morphism.codomain())
        return BASE.morphism_category(1)(domain, codomain).one()


RIGHT = RightCategory()


class DiamondCategory(_SyntheticCategoryOperations, Category[[], []]):
    class ObjectType:
        def __init__(self, label: int | Integer) -> None:
            self._diamond_state = label
            self._synthetic_label = label

        def diamond_object(self) -> tuple[Self, int | Integer]:
            return self, self._diamond_state

        def preferred_object(self) -> Self:
            return self

    class ElementType:
        def __init__(self, label: int | Integer) -> None:
            self._diamond_element_state = label
            self._synthetic_label = label

        def diamond_element(self) -> tuple[Self, int | Integer]:
            return self, self._diamond_element_state

    class MorphismType:
        def __init__(self, label: int | Integer) -> None:
            self._diamond_morphism_state = label
            self._synthetic_label = label

        def diamond_morphism(self) -> tuple[Self, int | Integer]:
            return self, self._diamond_morphism_state

    def structure_functors(self) -> tuple[Functor, ...]:
        key = id(self)
        if key not in _SELECTED_FUNCTORS:
            def on_object(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
                _DIAMOND_TO_LEFT_OBJECT_ACTIONS.append(member_object)
                return self._object_to_left(member_object)

            def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
                _DIAMOND_TO_LEFT_MORPHISM_ACTIONS.append(morphism)
                return self._morphism_to_left(morphism)

            _SELECTED_FUNCTORS[key] = (
                Fun(self, LEFT)(on_object, on_morphism),
                Fun(self, RIGHT)(self._object_to_right, self._morphism_to_right),
            )
        return _SELECTED_FUNCTORS[key]

    def _object_to_left(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return LEFT(self._label(member_object))

    def _morphism_to_left(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        domain = self._object_to_left(morphism.domain())
        codomain = self._object_to_left(morphism.codomain())
        return LEFT.morphism_category(1)(domain, codomain).one()

    def _object_to_right(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return RIGHT(self._label(member_object))

    def _morphism_to_right(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        domain = self._object_to_right(morphism.domain())
        codomain = self._object_to_right(morphism.codomain())
        return RIGHT.morphism_category(1)(domain, codomain).one()


DIAMOND = DiamondCategory()


def test_kernel_imports_without_production_leaves() -> None:
    import subprocess
    cmd = (
        "import sys, sage_categories.cat.category, sage_categories.cat.functors, "
        "sage_categories.cat.properties, sage_categories.cat.constructions, "
        "sage_categories.cat.canonical, sage_categories.cat.declarations, "
        "sage_categories.kernel.compiler; "
        "prefixes = ('sage_categories.sets', 'sage_categories.posets', 'sage_categories.number_sets', 'sage_categories.ordinals'); "
        "leaves = [m for m in sys.modules if any(m == p or m.startswith(p + '.') for p in prefixes)]; "
        "assert not leaves, f'Kernel imported production leaves: {leaves}'"
    )
    subprocess.run([sys.executable, "-c", cmd], check=True)


def test_sage_compiler_runs_the_object_element_and_morphism_diamond() -> None:
    member_object = DIAMOND(7)
    identity = DIAMOND.morphism_category(1)(member_object, member_object).one()
    element = DIAMOND.element_from_defining_morphism(identity)

    for source, state in (
        member_object.diamond_object(),
        member_object.left_object(),
        member_object.right_object(),
        member_object.base_object(),
    ):
        assert source is member_object
        assert state == 7
    assert member_object.preferred_object() is member_object
    special_source, special_state = +member_object
    assert special_source is member_object
    assert special_state == 7

    for source, state in (
        element.diamond_element(),
        element.left_element(),
        element.right_element(),
        element.base_element(),
    ):
        assert source is element
        assert state == 7

    for source, state in (
        identity.diamond_morphism(),
        identity.left_morphism(),
        identity.right_morphism(),
        identity.base_morphism(),
    ):
        assert source is identity
        assert state == 7

    assert sum(initialized is member_object for initialized in _BASE_OBJECT_INITIALIZATIONS) == 1
    assert sum(initialized is element for initialized in _BASE_ELEMENT_INITIALIZATIONS) == 1
    assert sum(initialized is identity for initialized in _BASE_MORPHISM_INITIALIZATIONS) == 1


def test_construction_runs_each_selected_action_once_and_retains_its_image() -> None:
    object_calls_before = len(_DIAMOND_TO_LEFT_OBJECT_ACTIONS)
    morphism_calls_before = len(_DIAMOND_TO_LEFT_MORPHISM_ACTIONS)
    to_left = DIAMOND.structure_functors()[0]
    left_to_base = LEFT.structure_functors()[0]

    # Constructing an object runs the selected object action once, on the value under
    # construction; the datum that action feeds to LEFT's constructor initializes the
    # inherited LEFT implementation on the same value (D13).  The declaration writes no
    # initializer chain of its own.
    member_object = DIAMOND(11)
    assert _DIAMOND_TO_LEFT_OBJECT_ACTIONS[object_calls_before:] == [member_object]
    assert len(_DIAMOND_TO_LEFT_MORPHISM_ACTIONS) == morphism_calls_before
    inherited_source, inherited_state = member_object.left_object()
    assert inherited_source is member_object and inherited_state == 11

    # The same for a morphism and the selected morphism action.
    identity = DIAMOND.morphism_category(1)(member_object, member_object).one()
    assert _DIAMOND_TO_LEFT_MORPHISM_ACTIONS[morphism_calls_before:] == [identity]
    inherited_morphism, inherited_morphism_state = identity.left_morphism()
    assert inherited_morphism is identity and inherited_morphism_state == 11

    # Public application returns the image retained at construction; the action does
    # not run again.
    object_image = to_left.on_object(member_object)
    assert len(_DIAMOND_TO_LEFT_OBJECT_ACTIONS) == object_calls_before + 1
    assert to_left.on_object(member_object) is object_image

    morphism_image = to_left.on_morphism(identity)
    assert len(_DIAMOND_TO_LEFT_MORPHISM_ACTIONS) == morphism_calls_before + 1
    assert to_left.on_morphism(identity) is morphism_image

    base_image = left_to_base.on_object(object_image)
    assert object_image is LEFT(11)
    assert object_image is not member_object
    assert base_image is BASE(11)
    image_source, image_state = object_image.left_object()
    assert image_source is object_image and image_state == inherited_state == 11
    assert morphism_image is LEFT.morphism_category(1)(object_image, object_image).one()
    assert morphism_image is not identity
    image_morphism, image_morphism_state = morphism_image.left_morphism()
    assert image_morphism is morphism_image
    assert image_morphism_state == inherited_morphism_state == 11
    assert DIAMOND.structure_functors()[0] is to_left



def test_unresolved_structural_diamond_is_debug_only(caplog: pytest.LogCaptureFixture) -> None:
    import logging

    caplog.set_level(logging.DEBUG, logger="sage_categories.kernel.compiler")

    class LoggedDiamond(_SyntheticCategoryOperations, Category[[], []]):
        class ObjectType:
            pass

        class ElementType:
            pass

        class MorphismType:
            pass

        def structure_functors(self) -> tuple[Functor, ...]:
            key = id(self)
            if key not in _SELECTED_FUNCTORS:
                _SELECTED_FUNCTORS[key] = (
                    Fun(self, LEFT)(lambda member: LEFT(self._label(member)), lambda morphism: LEFT.morphism_category(1)(LEFT(self._label(morphism.domain())), LEFT(self._label(morphism.codomain()))).one()),
                    Fun(self, RIGHT)(lambda member: RIGHT(self._label(member)), lambda morphism: RIGHT.morphism_category(1)(RIGHT(self._label(morphism.domain())), RIGHT(self._label(morphism.codomain()))).one()),
                )
            return _SELECTED_FUNCTORS[key]

    LoggedDiamond()

    records = [record for record in caplog.records if "unresolved structural diamond" in record.getMessage()]
    assert records
    assert all(record.levelno == logging.DEBUG for record in records)

def test_property_refinement_preserves_object_identity() -> None:
    member_object = DIAMOND(13)
    property_category = PropertySubcategory(DIAMOND, "SyntheticR1Property", ())

    refined = property_category(member_object)

    assert refined is member_object
    assert refined in property_category
    left_source, left_state = refined.left_object()
    right_source, right_state = refined.right_object()
    assert left_source is refined and left_state == 13
    assert right_source is refined and right_state == 13


def test_incomparable_method_owners_fail_at_compilation() -> None:
    class CollisionLeft(_SyntheticCategoryOperations, Category[[], []]):
        class ObjectType:
            def collision(self) -> Self:
                return self

        class ElementType:
            pass

        class MorphismType:
            pass

    collision_left = CollisionLeft()

    class CollisionRight(_SyntheticCategoryOperations, Category[[], []]):
        class ObjectType:
            def collision(self) -> Self:
                return self

        class ElementType:
            pass

        class MorphismType:
            pass

    collision_right = CollisionRight()

    class CollisionDiamond(_SyntheticCategoryOperations, Category[[], []]):
        class ObjectType:
            pass

        class ElementType:
            pass

        class MorphismType:
            pass

        def structure_functors(self) -> tuple[Functor, ...]:
            key = id(self)
            if key not in _SELECTED_FUNCTORS:
                _SELECTED_FUNCTORS[key] = (
                    Fun(self, collision_left)(lambda member: collision_left(0), lambda morphism: collision_left.morphism_category(1)(collision_left(0), collision_left(0)).one()),
                    Fun(self, collision_right)(lambda member: collision_right(0), lambda morphism: collision_right.morphism_category(1)(collision_right(0), collision_right(0)).one()),
                )
            return _SELECTED_FUNCTORS[key]

    with pytest.raises(SemanticCollisionError, match="collision"):
        CollisionDiamond()
