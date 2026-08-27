"""Point categories and the level shift (POL-CAT-083, ``specs/functor.md``).

``Cat().Point(X)``, written ``{X}``, is the one-object category whose sole object is
``X`` and whose sole morphism is ``1_X``.  A point functor is its faithful inclusion into
a category that already has ``X`` among its objects.

For ``X`` a category ``C``, the surface of the target lands one level down, because
``Cat().ElementType`` is the role "generalized element of a category": its stage-``1``
points are the objects of ``C`` and its stage-``[1]`` points are the morphisms of ``C``.
Each row below is one line of the level-shift table.

Oracles: the definition of a one-object category; the definition of a generalized element
as a functor ``T -> C`` (``specs/functor.md``, "Generalized elements"); the level-shift
table in ``specs/functor.md``, "The level shift".  Toy categories live only in this file
(POL-TEST-006).
"""

from sage_categories.all import *
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role
from sage_categories.kernel import compiler


class Marked(Category):
    """A target category declaring one operation on each of its three roles."""

    class ObjectType(ObjectOfCategory):
        def object_mark(self) -> str:
            return "object"

    class ElementType(ElementOfObject):
        def element_mark(self) -> str:
            return "element"

    class MorphismType(MorphismOfCategory):
        def morphism_mark(self) -> str:
            return "morphism"

    def __repr__(self) -> str:
        return "Marked"


class Two(Category):
    """A toy category with two objects and the morphisms between them."""

    class ObjectType(ObjectOfCategory):
        def __init__(self, category, name):
            ObjectOfCategory.__init__(self, category)
            self._name = name

        def __repr__(self):
            return self._name

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def __init__(self):
        super().__init__()
        self._objects = {}

    def __call__(self, name):
        # Built on demand: a point category on ``Two`` recompiles this category's roles,
        # and an object built before that would carry the earlier class.
        if name not in self._objects:
            self._objects[name] = self.ObjectType(self, name)
        return self._objects[name]

    def construct_morphism(self, domain, codomain):
        return self.MorphismType(self.morphism_category(int(1)), domain, codomain)

    def construct_identity(self, member_object):
        return self.MorphismType(self.morphism_category(int(1)), member_object, member_object)

    def __repr__(self):
        return "Two"


def test_a_point_category_is_the_one_object_category_on_its_member() -> None:
    """``{X}`` has ``X`` as its sole object, and ``Cat()`` retains one per object."""
    marked = Marked()
    two = Two()
    point = Cat().Point(two, (marked,))

    assert point.member() is two
    assert point() is two
    assert Cat().Point(two) is point, "one point category per object, retained by identity"
    assert Cat().retained_point(two) is point, "the same table, read from the member"
    assert point is not Cat().Terminal(), "the terminal category's object is a vertex, not this member"


def test_a_point_functor_is_the_faithful_inclusion_of_the_point_category() -> None:
    """``{X}`` selects one point functor per target, constructed through ``Fun({X}, D)``."""
    marked = Marked()
    two = Two()
    point = Cat().Point(two, (marked,))

    selected = point.structure_functors()
    into_marked = [functor for functor in selected if functor.codomain() is marked]

    assert len(into_marked) == int(1), "one point functor per target category"
    assert into_marked[int(0)].domain() is point
    assert into_marked[int(0)] in Mor(Cat()).Faithful(), "every functor out of a one-hom category is faithful"


def test_the_point_functor_supplies_the_object_surface_to_the_member_itself() -> None:
    """Level-shift row 1: ``D.ObjectType`` lands on the category ``C``, a ``Cat().ObjectType`` value."""
    marked = Marked()
    two = Two()
    Cat().Point(two, (marked,))

    assert two.object_mark() == "object"


def test_the_point_functor_supplies_the_element_surface_one_level_down() -> None:
    """Level-shift rows 2 and 3: ``D.ElementType`` reaches the objects of ``C`` at stage ``1`` and its morphisms at stage ``[1]``."""
    marked = Marked()
    two = Two()
    Cat().Point(two, (marked,))
    left, right = two("left"), two("right")
    arrow = two.construct_morphism(left, right)

    assert left.element_mark() == "element", "an object of C is a stage-1 generalized element of C"
    assert arrow.element_mark() == "element", "a morphism of C is a stage-[1] generalized element of C"


def test_the_level_shift_applies_no_functor_and_is_split_by_stage() -> None:
    """The shift's step carries both roles and the stage it restricts to, and no functor acts."""
    marked = Marked()
    two = Two()
    point = Cat().Point(two, (marked,))
    target = compiler.node(point, Role.ELEMENT)

    from_objects = compiler.routes(compiler.node(two, Role.OBJECT), target)
    from_morphisms = compiler.routes(compiler.node(two, Role.MORPHISM), target)
    object_step = from_objects[int(0)][int(0)]
    morphism_step = from_morphisms[int(0)][int(0)]

    assert object_step.functor is None, "the shift is a reindexing, not a functor application"
    assert object_step.source_role is Role.OBJECT and object_step.target_role is Role.ELEMENT
    assert morphism_step.source_role is Role.MORPHISM and morphism_step.target_role is Role.ELEMENT
    assert object_step.stage is Cat().Terminal(), "objects are the stage-1 points"
    assert morphism_step.stage is Cat().Simplex(int(1)), "morphisms are the stage-[1] points"


def test_the_level_shift_contributes_no_class_base() -> None:
    """A shift is not a subcategory relation, so ``C.ObjectType`` does not derive from ``{C}.ElementType``."""
    marked = Marked()
    two = Two()
    point = Cat().Point(two, (marked,))

    assert not issubclass(two.ObjectType, point.ElementType)
    assert not issubclass(two.MorphismType, point.ElementType)
