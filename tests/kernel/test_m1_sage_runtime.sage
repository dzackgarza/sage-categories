"""R1: synthetic acceptance for the private Sage-backed category compiler."""

from sage_categories.kernel.sage_runtime import Integer

import sys

from typing import Self

import pytest

from sage_categories.cat import Fun
from sage_categories.cat.category import Axiom, Cat, Category, CategoryOfCategories, ask, assume
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.compiler import SemanticCollisionError, declared_inheritance
from sage_categories.kernel.construction import active_object_context
from sage_categories.kernel.refinement import declares_point, traces_inheritance, traces_placement
from sage_categories.kernel.roles import CategoryPoint, Role
from sage_categories.kernel.sage_runtime import Unknown


_BASE_OBJECT_INITIALIZATIONS: list[CategoryPoint] = []
_BASE_ELEMENT_INITIALIZATIONS: list[CategoryPoint] = []
_BASE_MORPHISM_INITIALIZATIONS: list[CategoryPoint] = []
_DIAMOND_TO_LEFT_OBJECT_ACTIONS: list[CategoryPoint] = []
_DIAMOND_TO_LEFT_MORPHISM_ACTIONS: list[CategoryPoint] = []
_THREADED_TARGETS: list[tuple[str, CategoryPoint]] = []
_SCALAR_INITIALIZATIONS: list[tuple[CategoryPoint, Integer]] = []


class _SyntheticCategoryOperations:
    """The object constructor the synthetic R1 specimens share: one object per label."""

    def __call__(self, label: Integer) -> CategoryOfCategories.ElementType:
        return self.ObjectType(label)

    def _label(self, member_object: CategoryPoint) -> Integer:
        return member_object._synthetic_label


class BaseCategory(_SyntheticCategoryOperations, Category):
    class ObjectType:
        def __init__(self, label: Integer) -> None:
            _BASE_OBJECT_INITIALIZATIONS.append(self)
            self._base_state = label
            self._synthetic_label = label

        def base_object(self) -> tuple[Self, Integer]:
            return self, self._base_state

        def preferred_object(self) -> CategoryOfCategories.ElementType:
            return BASE(0)

        def __pos__(self) -> tuple[Self, Integer]:
            return self, self._base_state

    class ElementType:
        def __init__(self, data: None) -> None:
            _BASE_ELEMENT_INITIALIZATIONS.append(self)
            self._base_element_state = self.parent()._base_state

        def base_element(self) -> tuple[Self, Integer]:
            return self, self._base_element_state

    class MorphismType:
        def __init__(self, data: None) -> None:
            _BASE_MORPHISM_INITIALIZATIONS.append(self)
            self._base_morphism_state = self.domain()._base_state

        def base_morphism(self) -> tuple[Self, Integer]:
            return self, self._base_morphism_state


BASE = BaseCategory()


class LeftCategory(_SyntheticCategoryOperations, Category):
    class ObjectType:
        def __init__(self, label: Integer) -> None:
            self._left_state = label
            self._synthetic_label = label

        def left_object(self) -> tuple[Self, Integer]:
            return self, self._left_state

    class ElementType:
        def __init__(self, data: None) -> None:
            self._left_element_state = self.parent()._left_state

        def left_element(self) -> tuple[Self, Integer]:
            return self, self._left_element_state

    class MorphismType:
        def __init__(self, data: None) -> None:
            self._left_morphism_state = self.domain()._left_state

        def left_morphism(self) -> tuple[Self, Integer]:
            return self, self._left_morphism_state

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(self, BASE).Isofibrations()(self._object_to_base, self._morphism_to_base),)

    def _object_to_base(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return BASE(self._label(member_object))

    def _morphism_to_base(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        domain = self._object_to_base(morphism.domain())
        codomain = self._object_to_base(morphism.codomain())
        return BASE.morphism_category(1)(domain, codomain).one()


LEFT = LeftCategory()


class RightCategory(_SyntheticCategoryOperations, Category):
    class ObjectType:
        def __init__(self, label: Integer) -> None:
            self._right_state = label
            self._synthetic_label = label

        def right_object(self) -> tuple[Self, Integer]:
            return self, self._right_state

    class ElementType:
        def __init__(self, data: None) -> None:
            self._right_element_state = self.parent()._right_state

        def right_element(self) -> tuple[Self, Integer]:
            return self, self._right_element_state

    class MorphismType:
        def __init__(self, data: None) -> None:
            self._right_morphism_state = self.domain()._right_state

        def right_morphism(self) -> tuple[Self, Integer]:
            return self, self._right_morphism_state

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(self, BASE).Isofibrations()(self._object_to_base, self._morphism_to_base),)

    def _object_to_base(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return BASE(self._label(member_object))

    def _morphism_to_base(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        domain = self._object_to_base(morphism.domain())
        codomain = self._object_to_base(morphism.codomain())
        return BASE.morphism_category(1)(domain, codomain).one()


RIGHT = RightCategory()


class DiamondCategory(_SyntheticCategoryOperations, Category):
    SyntheticR1Property = Axiom()

    class ObjectType:
        def __init__(self, label: Integer) -> None:
            self._diamond_state = label
            self._synthetic_label = label

        def diamond_object(self) -> tuple[Self, Integer]:
            return self, self._diamond_state

        def preferred_object(self) -> Self:
            return self

    class ElementType:
        def __init__(self, data: None) -> None:
            self._diamond_element_state = self.parent()._diamond_state

        def diamond_element(self) -> tuple[Self, Integer]:
            return self, self._diamond_element_state

    class MorphismType:
        def __init__(self, data: None) -> None:
            self._diamond_morphism_state = self.domain()._diamond_state

        def diamond_morphism(self) -> tuple[Self, Integer]:
            return self, self._diamond_morphism_state

    def structure_functors(self) -> tuple[Functor, ...]:
        def on_object(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            _DIAMOND_TO_LEFT_OBJECT_ACTIONS.append(member_object)
            return self._object_to_left(member_object)

        def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            _DIAMOND_TO_LEFT_MORPHISM_ACTIONS.append(morphism)
            return self._morphism_to_left(morphism)

        return (
            Fun(self, LEFT).Isofibrations()(on_object, on_morphism),
            Fun(self, RIGHT).Isofibrations()(self._object_to_right, self._morphism_to_right),
        )

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


class SyntheticR1PropertyCategory(PropertySubcategory):
    """The declared implementation of ``DiamondCategory.SyntheticR1Property`` (POL-LEAF-064)."""

    _base_category_class_and_axiom = (DiamondCategory, "SyntheticR1Property")


def _synthetic_isofibration(
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    on_object: object,
) -> Functor:
    """One selected isofibration of a synthetic specimen, over the label its objects carry."""

    def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        return target.morphism_category(1)(on_object(morphism.domain()), on_object(morphism.codomain())).one()

    return Fun(source, target).Isofibrations()(on_object, on_morphism)


class FirstDeclaredCategory(_SyntheticCategoryOperations, Category):
    """The older of a pair of targets; a specimen below declares it first."""

    class ObjectType:
        def __init__(self, label: Integer) -> None:
            _THREADED_TARGETS.append(("first declared", self))
            self._first_declared_state = label
            self._synthetic_label = label

        def first_declared_object(self) -> Integer:
            return self._first_declared_state

    class ElementType:
        pass

    class MorphismType:
        pass


FIRST_DECLARED = FirstDeclaredCategory()


class SecondDeclaredCategory(_SyntheticCategoryOperations, Category):
    """The newer of that pair; construction order would give it precedence."""

    class ObjectType:
        def __init__(self, label: Integer) -> None:
            _THREADED_TARGETS.append(("second declared", self))
            self._second_declared_state = label
            self._synthetic_label = label

        def second_declared_object(self) -> Integer:
            return self._second_declared_state

    class ElementType:
        pass

    class MorphismType:
        pass


SECOND_DECLARED = SecondDeclaredCategory()


class AgainstConstructionOrderCategory(_SyntheticCategoryOperations, Category):
    """Two selected isofibrations named against the order their targets were constructed."""

    class ObjectType:
        def __init__(self, label: Integer) -> None:
            _THREADED_TARGETS.append(("source", self))
            self._synthetic_label = label

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self) -> tuple[Functor, ...]:
        def to_second(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            # This action reads a method the value under construction inherits through the
            # isofibration declared before it, whose state the kernel has installed by now.
            return SECOND_DECLARED(member_object.first_declared_object())

        return (
            _synthetic_isofibration(self, FIRST_DECLARED, lambda member: FIRST_DECLARED(self._label(member))),
            _synthetic_isofibration(self, SECOND_DECLARED, to_second),
        )


AGAINST_CONSTRUCTION_ORDER = AgainstConstructionOrderCategory()


class WithConstructionOrderCategory(_SyntheticCategoryOperations, Category):
    """The same rule on a disjoint pair, which this one names newest first."""

    class ObjectType:
        def __init__(self, label: Integer) -> None:
            self._synthetic_label = label

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self) -> tuple[Functor, ...]:
        return (
            _synthetic_isofibration(self, SECOND_DECLARED, lambda member: SECOND_DECLARED(self._label(member))),
            _synthetic_isofibration(self, BASE, lambda member: BASE(self._label(member))),
        )


WITH_CONSTRUCTION_ORDER = WithConstructionOrderCategory()


class ModulesCategory(_SyntheticCategoryOperations, Category):
    """The modules over one ring: one written declaration, one category for each ring.

    A bimodule's two projections land in two categories of this one declaration, and the
    kernel runs its one initializer for each of them, with that owner's own datum (D167).
    """

    class ObjectType:
        def __init__(self, scalars: Integer) -> None:
            _SCALAR_INITIALIZATIONS.append((self, scalars))
            self._scalars = scalars

        def scalars(self) -> Integer:
            return self._scalars

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self, ring: str) -> None:
        self._ring = ring


LEFT_SCALARS = ModulesCategory("R")
RIGHT_SCALARS = ModulesCategory("S")
MIRROR_LEFT_SCALARS = ModulesCategory("R'")
MIRROR_RIGHT_SCALARS = ModulesCategory("S'")


class _BimoduleOperations:
    """A bimodule specimen: its object is the pair of scalars, one for each side."""

    def __call__(self, sides: tuple[Integer, Integer]) -> CategoryOfCategories.ElementType:
        return self.ObjectType(sides)

    def _sides(self, member_object: CategoryPoint) -> tuple[Integer, Integer]:
        return member_object._bimodule_sides


class LeftFirstBimodules(_BimoduleOperations, Category):
    """A bimodule declaring the projection to the left scalars first."""

    class ObjectType:
        def __init__(self, sides: tuple[Integer, Integer]) -> None:
            self._bimodule_sides = sides

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self) -> tuple[Functor, ...]:
        return (
            _synthetic_isofibration(self, LEFT_SCALARS, lambda member: LEFT_SCALARS(self._sides(member)[0])),
            _synthetic_isofibration(self, RIGHT_SCALARS, lambda member: RIGHT_SCALARS(self._sides(member)[1])),
        )


LEFT_FIRST = LeftFirstBimodules()


class RightFirstBimodules(_BimoduleOperations, Category):
    """The same two projections of a disjoint pair, declared in the other order.

    Its own pair, because a declaration orders the targets it names: two categories that
    order one pair oppositely state two relations no single order satisfies, which is the
    unresolved diamond of D37 rather than a precedence question.
    """

    class ObjectType:
        def __init__(self, sides: tuple[Integer, Integer]) -> None:
            self._bimodule_sides = sides

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self) -> tuple[Functor, ...]:
        return (
            _synthetic_isofibration(self, MIRROR_RIGHT_SCALARS, lambda member: MIRROR_RIGHT_SCALARS(self._sides(member)[1])),
            _synthetic_isofibration(self, MIRROR_LEFT_SCALARS, lambda member: MIRROR_LEFT_SCALARS(self._sides(member)[0])),
        )


RIGHT_FIRST = RightFirstBimodules()


class StructuredCategory(Category):
    """A structured category whose objects are categories: the ``D`` of R1 criteria 6 and 7."""

    class ObjectType:
        def structured_object(self) -> Self:
            return self

    class ElementType:
        def structured_element(self) -> Self:
            return self

    class MorphismType:
        pass


STRUCTURED = StructuredCategory()


class NN(Category):
    """A named object: a new category that registers itself as a point in ``STRUCTURED``."""

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self) -> tuple[Functor, ...]:
        return (STRUCTURED.Point(),)


NATURALS = NN()


class QQ(Category):
    """A second named object, independent of ``NN`` and a point in the same ``STRUCTURED``."""

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self) -> tuple[Functor, ...]:
        return (STRUCTURED.Point(),)


RATIONALS = QQ()


class LabelledArrows(Category):
    """Objects and morphisms named by a label: the closed list of D77 and nothing else."""

    Marked = Axiom()

    class ObjectType:
        def __init__(self, label: str) -> None:
            self._label = label

        def __repr__(self) -> str:
            return f"object {self._label}"

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, label: str) -> None:
            self._label = label

        def __repr__(self) -> str:
            return f"arrow {self._label}"

    def __call__(self, label: str) -> CategoryOfCategories.ElementType:
        return self.ObjectType(label)


LABELLED = LabelledArrows()


class Unpointed(Category):
    """The control of criteria 6 and 7: a new category that declares no point."""

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass


UNPOINTED = Unpointed()


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
    to_left = DIAMOND.selected_functors()[0]
    left_to_base = LEFT.selected_functors()[0]

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
    assert DIAMOND.selected_functors()[0] is to_left


def test_the_declared_order_of_the_selected_isofibrations_ranks_inheritance() -> None:
    # The two targets stand in the order the declaration names, which is the reverse of the
    # order they were constructed in (D165, D166, D167).
    assert FIRST_DECLARED.ordinal() < SECOND_DECLARED.ordinal()
    assert [
        declaration.__qualname__
        for declaration in declared_inheritance(AGAINST_CONSTRUCTION_ORDER, Role.OBJECT)
    ][:3] == [
        "AgainstConstructionOrderCategory.ObjectType",
        "FirstDeclaredCategory.ObjectType",
        "SecondDeclaredCategory.ObjectType",
    ]

    # What decides is the declared order and not the reverse of the construction order: a
    # declaration naming the newer target first stands that way too.
    assert BASE.ordinal() < SECOND_DECLARED.ordinal()
    assert [
        declaration.__qualname__
        for declaration in declared_inheritance(WITH_CONSTRUCTION_ORDER, Role.OBJECT)
    ][:3] == [
        "WithConstructionOrderCategory.ObjectType",
        "SecondDeclaredCategory.ObjectType",
        "BaseCategory.ObjectType",
    ]


def test_a_selected_action_runs_on_a_value_the_targets_ahead_of_it_have_initialized() -> None:
    del _THREADED_TARGETS[:]

    member_object = AGAINST_CONSTRUCTION_ORDER(9)

    # The second action called ``first_declared_object()``, which the value inherits through
    # the isofibration declared before it (D13; ``specs/leaves.md``, "An action receives a
    # fully initialized source value").
    assert member_object.second_declared_object() == 9
    assert member_object.first_declared_object() == 9
    # The kernel ran this value's own initializer, then the two targets in declared order.
    assert [name for name, value in _THREADED_TARGETS if value is member_object] == [
        "source",
        "first declared",
        "second declared",
    ]


def test_two_owners_of_one_declaration_read_the_first_declared_state() -> None:
    # ``LEFT_SCALARS`` and ``RIGHT_SCALARS`` are two categories of the one written
    # ``ModulesCategory.ObjectType``: a bimodule's two projections, which is the case D167
    # names.  The kernel runs that one initializer for each of them, with that owner's own
    # datum, so both write the state ``scalars()`` reads.  The declared order fixes which
    # write the value reads, and it is the first, with coherence assumed (D37, D56, D165,
    # D166, D167; ``specs/resolution.md``, "Sage class construction").
    assert [functor.codomain() for functor in LEFT_FIRST.selected_functors()] == [LEFT_SCALARS, RIGHT_SCALARS]
    assert LEFT_SCALARS.ordinal() < RIGHT_SCALARS.ordinal()

    del _SCALAR_INITIALIZATIONS[:]
    left_first = LEFT_FIRST((3, 5))
    assert [scalars for value, scalars in _SCALAR_INITIALIZATIONS if value is left_first] == [3, 5]
    assert left_first.scalars() == 3

    # The same object datum, the same one declaration reached twice, the other declared
    # order: the answer follows the declaration and not the datum's position, the class,
    # or the order the two categories were constructed in.
    assert [functor.codomain() for functor in RIGHT_FIRST.selected_functors()] == [
        MIRROR_RIGHT_SCALARS,
        MIRROR_LEFT_SCALARS,
    ]
    assert MIRROR_LEFT_SCALARS.ordinal() < MIRROR_RIGHT_SCALARS.ordinal()

    del _SCALAR_INITIALIZATIONS[:]
    right_first = RIGHT_FIRST((3, 5))
    assert [scalars for value, scalars in _SCALAR_INITIALIZATIONS if value is right_first] == [5, 3]
    assert right_first.scalars() == 5


def test_unresolved_structural_diamond_is_debug_only(caplog: pytest.LogCaptureFixture) -> None:
    import logging

    caplog.set_level(logging.DEBUG, logger="sage_categories.kernel.compiler")

    class LoggedDiamond(_SyntheticCategoryOperations, Category):
        class ObjectType:
            pass

        class ElementType:
            pass

        class MorphismType:
            pass

        def structure_functors(self) -> tuple[Functor, ...]:
            return (
                Fun(self, LEFT).Isofibrations()(lambda member: LEFT(self._label(member)), lambda morphism: LEFT.morphism_category(1)(LEFT(self._label(morphism.domain())), LEFT(self._label(morphism.codomain()))).one()),
                Fun(self, RIGHT).Isofibrations()(lambda member: RIGHT(self._label(member)), lambda morphism: RIGHT.morphism_category(1)(RIGHT(self._label(morphism.domain())), RIGHT(self._label(morphism.codomain()))).one()),
            )

    LoggedDiamond()

    records = [record for record in caplog.records if "unresolved structural diamond" in record.getMessage()]
    assert records
    assert all(record.levelno == logging.DEBUG for record in records)

def test_point_functor_places_the_class_and_shifts_the_level() -> None:
    # ``STRUCTURED.Point()`` constructs the arrow ``* -> STRUCTURED`` selecting the class
    # in ``Fun(*, STRUCTURED).Monomorphisms()``, and that call is the whole declaration.
    # The arrow is not an isofibration, so what carries placement and inheritance is the
    # inclusion ``<X> -> STRUCTURED`` of the replete full subcategory its image generates
    # (D146, D154, D161, D169).
    for named in (NATURALS, RATIONALS):
        (point,) = named.selected_functors()
        assert declares_point(point)
        assert point is STRUCTURED.point_functor(named)
        assert not traces_placement(point)
        assert not traces_inheritance(point)

        inclusion = STRUCTURED.EssentialImage(point).inclusion_functor()
        assert inclusion.codomain() is STRUCTURED
        assert traces_placement(inclusion)
        assert traces_inheritance(inclusion)

        assert named.category() is STRUCTURED
        assert named in STRUCTURED

        # The level shift: the category itself carries the object surface of
        # ``STRUCTURED``, and its objects carry the element surface (D128, D161).
        assert isinstance(named, STRUCTURED.ObjectType)
        assert named.structured_object() is named
        assert issubclass(named.ObjectType, STRUCTURED.ElementType)
        assert named.ObjectType.structured_element is STRUCTURED.ElementType.structured_element

    assert STRUCTURED.point_functor(NATURALS) is not STRUCTURED.point_functor(RATIONALS)

    # The control declares no point: it is an object of its universe and receives neither
    # surface of ``STRUCTURED``.
    assert UNPOINTED.category() is not STRUCTURED
    assert not isinstance(UNPOINTED, STRUCTURED.ObjectType)
    assert not issubclass(UNPOINTED.ObjectType, STRUCTURED.ElementType)


def test_an_arrow_that_writes_no_point_declaration_places_nothing() -> None:
    # The same two actions and the same endpoints as ``STRUCTURED.Point()``, constructed
    # outside ``Fun(*, STRUCTURED).Monomorphisms()``.  Only the declaration separates the
    # two, so a placement decided by anything else -- the endpoints, a table of arrows
    # already built, Python inheritance -- would place this one as well (POL-FUN-036).
    class UndeclaredPoint(Category):
        class ObjectType:
            pass

        class ElementType:
            pass

        class MorphismType:
            pass

        def structure_functors(self) -> tuple[Functor, ...]:
            member = active_object_context().canonical_image
            return (
                Fun(Cat().Terminal(), STRUCTURED)(
                    lambda vertex: member,
                    lambda path: STRUCTURED.morphism_category(1)(member, member).one(),
                ),
            )

    with pytest.raises(AssertionError):
        UndeclaredPoint()


def test_property_subcategory_constructs_through_its_ambient() -> None:
    """``C.P()`` has exactly the constructors of ``C``, and construction places the result (D150)."""
    property_category = DIAMOND.SyntheticR1Property()

    constructed = property_category(17)

    assert constructed in property_category
    assert constructed in DIAMOND
    assert isinstance(constructed, property_category.ObjectType)
    diamond_source, diamond_state = constructed.diamond_object()
    left_source, left_state = constructed.left_object()
    right_source, right_state = constructed.right_object()
    assert diamond_source is constructed and diamond_state == 17
    assert left_source is constructed and left_state == 17
    assert right_source is constructed and right_state == 17


def test_assumed_membership_places_an_already_constructed_object() -> None:
    """The route for a value already constructed is ``assume(X.is_p())``, not a constructor (D150)."""
    member_object = DIAMOND(13)
    property_category = DIAMOND.SyntheticR1Property()
    member_identity = id(member_object)

    assume(member_object.is_synthetic_r1_property())

    assert id(member_object) == member_identity
    assert member_object in property_category
    left_source, left_state = member_object.left_object()
    right_source, right_state = member_object.right_object()
    assert left_source is member_object and left_state == 13
    assert right_source is member_object and right_state == 13


def test_incomparable_method_owners_fail_at_compilation() -> None:
    class CollisionLeft(_SyntheticCategoryOperations, Category):
        class ObjectType:
            def collision(self) -> Self:
                return self

        class ElementType:
            pass

        class MorphismType:
            pass

    collision_left = CollisionLeft()

    class CollisionRight(_SyntheticCategoryOperations, Category):
        class ObjectType:
            def collision(self) -> Self:
                return self

        class ElementType:
            pass

        class MorphismType:
            pass

    collision_right = CollisionRight()

    class CollisionDiamond(_SyntheticCategoryOperations, Category):
        class ObjectType:
            pass

        class ElementType:
            pass

        class MorphismType:
            pass

        def structure_functors(self) -> tuple[Functor, ...]:
            return (
                Fun(self, collision_left).Isofibrations()(lambda member: collision_left(0), lambda morphism: collision_left.morphism_category(1)(collision_left(0), collision_left(0)).one()),
                Fun(self, collision_right).Isofibrations()(lambda member: collision_right(0), lambda morphism: collision_right.morphism_category(1)(collision_right(0), collision_right(0)).one()),
            )

    with pytest.raises(SemanticCollisionError, match="collision"):
        CollisionDiamond()


def test_the_identity_is_the_unit_of_the_endomorphism_monoid() -> None:
    """``1_X`` is the unit of ``End_C(X)`` for a morphism reached through either placement.

    ``Mor(C)(A, B)`` is the full subcategory of ``Mor(C)`` on the morphisms ``A -> B``, so
    its objects are the morphisms of ``C``: one implementation type, one value, two
    placements (``specs/functor.md``, "The ``Mor(n, C)`` tower"; D44, D85).  A morphism
    built through the hom category and one built by composition therefore both reach the
    equality ``Mor(C).ObjectType`` declares, and ``f * 1_X`` is ``f`` for each (D84, D86).
    """
    source, target = LABELLED("source"), LABELLED("target")
    endomorphism = Mor(LABELLED)(source, source)("e")
    arrow = Mor(LABELLED)(source, target)("a")
    identity = Mor(LABELLED)(source, source).one()
    composite = endomorphism * endomorphism

    assert ask(identity.is_identity()) is True
    assert ask(identity * identity == identity) is True
    assert ask(endomorphism * identity == endomorphism) is True
    assert ask(identity * endomorphism == endomorphism) is True
    assert ask(arrow * identity == arrow) is True
    assert ask(composite * identity == composite) is True
    assert ask((arrow * endomorphism) * endomorphism == arrow * (endomorphism * endomorphism)) is True
    # The unit law decides because the two words agree, not because equality answers True:
    # ``e * e`` is a two-factor word and ``e`` a one-factor word, and no category-owned
    # datum separates or joins them.
    assert ask(composite == endomorphism) is Unknown
    # An endomorphism's two endpoints are one object, which the same declaration decides.
    assert endomorphism in Mor(LABELLED).Endomorphisms()


def test_the_identity_is_the_unit_of_the_endomorphism_monoid_of_a_property_subcategory() -> None:
    """``1_X`` is the unit of ``End_{C.P()}(X)``, in both orders.

    A subcategory contains the identities of its objects, so ``C.P()`` reaches the one
    identity ``C`` owns for ``X`` and both unit laws decide there (D84, D86,
    ``POL-CAT-023``).  The placement that identity takes narrows ``Mor(C)`` by
    ``Mor(C.P())``, ``Isomorphisms`` and ``Identity``; the narrowing by
    ``{Mor(C.P()), Identity}`` is ``Mor(C.P()).Identity()``, and dropping one root at a
    time is what declares the monomorphism into it (D83, ``POL-CAT-084``).  Without that
    declaration ``f * 1_X`` keeps two factors against ``f``'s one and the right unit law
    reads ``Unknown`` while the left one reads ``True``.
    """
    marked = LABELLED.Marked()
    source, target = marked("marked source"), marked("marked target")
    arrow = Mor(marked)(source, target)("marked arrow")
    identity = Mor(marked)(source, source).one()
    target_identity = Mor(marked)(target, target).one()

    # One object has one identity, whichever of the two categories holding it is asked.
    assert identity is Mor(LABELLED)(source, source).one()
    assert ask(arrow * identity == arrow) is True
    assert ask(target_identity * arrow == arrow) is True
    # A subcategory is closed under composition, so each composite the unit laws compare
    # is itself a morphism of ``C.P()``, in either order of the pair.
    assert ask(Mor(marked).membership_proposition(arrow * identity)) is True
    assert ask(Mor(marked).membership_proposition(target_identity * arrow)) is True


def test_a_predicate_decides_on_a_class_no_atom_was_built_for_yet() -> None:
    """A value's engine atom is a projection of its compiled class alone (D130, D131).

    ``Mor(C.P())(X, X).one()`` is compiled at a node under the narrowings of ``Mor(C)``,
    and ``C.P()`` writes no morphism class of its own, so its node and several nodes
    below it are all compiled from the one declaration they inherit.  Reading that
    declaration at the first of those nodes rather than the last states an order no
    linearization satisfies, and the projection then has no class to build for this
    value: every predicate on it stops deciding rather than answering.

    The category is declared here, inside the claim, so that no earlier test has built
    an atom for anything it compiles.  What the answer must not depend on is what was
    asked before it, so the measurement is worth nothing on a warmed process.
    """

    class Fresh(Category):
        """A category from the closed list of D77, reached by nothing else in this file."""

        Selected = Axiom()

        class ObjectType:
            def __init__(self, label: str) -> None:
                self._fresh_label = label

        class ElementType:
            pass

        class MorphismType:
            def __init__(self, label: str) -> None:
                self._fresh_label = label

        def __call__(self, label: str) -> CategoryOfCategories.ElementType:
            return self.ObjectType(label)

    ambient = Fresh()
    selected = ambient.Selected()
    member_object = selected("cold")
    identity = Mor(selected)(member_object, member_object).one()

    assert ask(identity.is_identity()) is True
    assert identity in Mor(selected)
    # The same claim on the value reached through the ambient's hom, which is the route a
    # longer script warms first: one object has one identity, and one answer.
    assert identity is Mor(ambient)(member_object, member_object).one()
    assert ask(Mor(ambient)(member_object, member_object).one().is_identity()) is True
