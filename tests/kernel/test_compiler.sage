"""The method compiler: dynamic inheritance surface, compile-time ownership, collisions.

Toy categories live only in this file (POL-TEST-006).  Each witness calls inherited public
operations through the production compiler (POL-TEST-006).  A toy stores its own
members on its own objects; it reads no ambient private field.
"""

import pytest

from sage_categories.all import *
from sage_categories.kernel.compiler import SemanticCollisionError
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory


def _finite_rule(members):
    return lambda datum: any(datum == member for member in members)


class PairSets(Category):
    """Two-element sets, declared a full subcategory of ``Sets()`` by one inclusion and nothing else."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)

    def __call__(self, first, second):
        return self.ObjectType(self, _finite_rule((first, second)), Cardinal()(int(2)))

    def __repr__(self):
        return "PairSets"


class Left(Category):
    """A full subcategory of ``Sets()`` with one local object method."""

    class ObjectType(ObjectOfCategory):
        def left_datum(self) -> int:
            return self._members[0]

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)

    def __repr__(self):
        return "Left"


class Right(Category):
    """A second full subcategory of ``Sets()``, incomparable with ``Left``."""

    class ObjectType(ObjectOfCategory):
        def right_datum(self) -> int:
            return self._members[-1]

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)

    def __repr__(self):
        return "Right"


class Diamond(Category):
    """Included in both ``Left`` and ``Right``: two routes to the one owner ``Sets()``."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def __init__(self, left, right):
        self._left = left
        self._right = right
        super().__init__()

    def structure_functors(self):
        return (
            Fun(self, self._left).FullyFaithful().inclusion(),
            Fun(self, self._right).FullyFaithful().inclusion(),
        )

    def __call__(self, members):
        members = tuple(members)
        apex = self.ObjectType(self, _finite_rule(members), Cardinal()(len(members)))
        apex._members = members
        return apex

    def __repr__(self):
        return "Diamond"


class Colliding(Category):
    """A category declaring ``size`` with a meaning unrelated to ``Sizes.size``."""

    class ObjectType(ObjectOfCategory):
        def size(self) -> int:
            return self._members[0]

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)

    def __repr__(self):
        return "Colliding"


class Sizes(Category):
    """A category declaring ``size`` as the cardinality datum."""

    class ObjectType(ObjectOfCategory):
        def size(self) -> int:
            return len(self._members)

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)

    def __repr__(self):
        return "Sizes"


class BothSizes(Category):
    """Included in ``Colliding`` and ``Sizes``: one spelling, two unrelated owners."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def __init__(self, colliding, sizes):
        self._colliding = colliding
        self._sizes = sizes
        super().__init__()

    def structure_functors(self):
        return (
            Fun(self, self._colliding).FullyFaithful().inclusion(),
            Fun(self, self._sizes).FullyFaithful().inclusion(),
        )

    def __repr__(self):
        return "BothSizes"


class Carried(Category):
    """Objects carrying a set, related to ``Sets()`` by an explicit forgetful functor, not an inclusion."""

    class ObjectType(ObjectOfCategory):
        def __init__(self, category, carrier):
            ObjectOfCategory.__init__(self, category)
            self._carrier = carrier

        def carrier(self) -> ObjectOfCategory:
            return self._carrier

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        def underlying_map(self) -> MorphismOfCategory:
            return self._underlying

    def structure_functors(self):
        return (Fun(self, Sets()).Faithful()(lambda member: member.carrier(), lambda morphism: morphism.underlying_map()),)

    def __call__(self, carrier):
        return self.ObjectType(self, carrier)

    def __repr__(self):
        return "Carried"


def test_a_selected_functor_that_is_not_an_inclusion_places_nothing() -> None:
    """Placement follows retained inclusions only; the forgetful image still supplies inherited values."""
    carried = Carried()
    pair = carried(Sets().Finite()((int(3), int(4))))

    assert pair in carried
    assert pair not in Sets()
    assert pair not in Sets().Finite()
    assert ask(pair.cardinality() == int(2)) is True
    assert ask(pair.is_finite()) is True


def test_dynamic_inheritance_surface_of_one_inclusion() -> None:
    """One selected inclusion exposes the object, element, and morphism surface of ``Sets()``."""
    pairs = PairSets()
    pair = pairs(int(3), int(4))

    assert pair in pairs
    assert pair in Sets()
    assert ask(pair.cardinality() == int(2)) is True
    assert ask(pair.is_finite()) is True

    three = pair.point(int(3))
    assert three in pair
    assert ask(three == pair.point(int(3))) is True
    assert three.parent() is pair

    swap = Mor(pairs)(pair, pair)(lambda datum: int(7) - datum)
    assert swap in Mor(pairs)
    assert swap in Mor(Sets())
    assert ask(swap(three) == pair.point(int(4))) is True
    assert ask(swap * swap == pair.identity()) is Unknown
    with pytest.raises(AssertionError, match="element=3 is not an owned element"):
        swap(int(3))


def test_two_paths_to_one_owner_install_one_method_before_any_value_exists() -> None:
    """The diamond compiles ``cardinality`` once from ``Sets()`` while no object of it exists."""
    diamond = Diamond(Left(), Right())

    surface = vars(diamond.ObjectType)
    assert "cardinality" in surface
    assert "left_datum" in surface
    assert "right_datum" in surface

    apex = diamond((int(5), int(8)))
    assert apex.left_datum() == int(5)
    assert apex.right_datum() == int(8)
    assert ask(apex.cardinality() == int(2)) is True
    assert apex in Sets()


def test_incomparable_owners_of_one_spelling_are_a_semantic_collision() -> None:
    """Two unrelated owners of ``size`` cannot be compiled onto one category."""
    with pytest.raises(SemanticCollisionError):
        BothSizes(Colliding(), Sizes())
