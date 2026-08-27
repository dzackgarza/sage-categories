"""The method compiler: dynamic inheritance surface, compile-time ownership, collisions.

Toy categories live only in this file (POL-TEST-006).  Each witness calls inherited public
operations through the production compiler (POL-TEST-006).  A toy stores its own
members on its own objects; it reads no ambient private field.
"""

from typing import Self

import pytest

from sage_categories.all import *
from sage_categories.kernel.compiler import SemanticCollisionError
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.maps import SetMap


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
        pair = Sets().Finite()((first, second))
        refine(pair, self)
        return pair

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


class ElementWeight(Category):
    """A full subcategory of ``Sets()`` declaring ``weight`` on generalized elements."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        def weight(self) -> int:
            return int(1)

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)

    def __repr__(self):
        return "ElementWeight"


class ElementMass(Category):
    """A second full subcategory of ``Sets()`` declaring ``weight`` with an unrelated meaning."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        def weight(self) -> int:
            return int(2)

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)

    def __repr__(self):
        return "ElementMass"


class MorphismDegree(Category):
    """A full subcategory of ``Sets()`` declaring ``degree`` on morphisms."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        def degree(self) -> int:
            return int(1)

    def structure_functors(self):
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)

    def __repr__(self):
        return "MorphismDegree"


class MorphismOrder(Category):
    """A second full subcategory of ``Sets()`` declaring ``degree`` with an unrelated meaning."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        def degree(self) -> int:
            return int(2)

    def structure_functors(self):
        return (Fun(self, Sets()).FullyFaithful().inclusion(),)

    def __repr__(self):
        return "MorphismOrder"


class BothRoles(Category):
    """Included in two categories that collide on one role's spelling."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def __init__(self, first, second):
        self._first = first
        self._second = second
        super().__init__()

    def structure_functors(self):
        return (
            Fun(self, self._first).FullyFaithful().inclusion(),
            Fun(self, self._second).FullyFaithful().inclusion(),
        )

    def __repr__(self):
        return "BothRoles"


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


class Skeletal(Category):
    """A skeletal category of sets: one object per isomorphism class, so each object is its own chosen representative.

    It declares the two result roles no category in ``src/`` currently declares: a
    receiver-valued operation and a set-map-valued one.
    """

    class ObjectType(ObjectOfCategory):
        def __init__(self, category, carrier):
            ObjectOfCategory.__init__(self, category)
            self._carrier = carrier

        def carrier(self) -> ObjectOfCategory:
            return self._carrier

        def chosen_representative(self) -> Self:
            """The representative of this object's isomorphism class: in a skeletal category, itself."""
            return self

        def carrier_identity(self) -> SetMap:
            """The identity of the underlying set: a morphism of ``Sets()``, whatever category the receiver lives in."""
            return self._carrier.identity()

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def __call__(self, carrier):
        return self.ObjectType(self, carrier)

    def __repr__(self):
        return "Skeletal"


class Presented(Category):
    """Objects with a chosen presentation of a skeletal object, related to it by a forgetful functor.

    The functor is not an inclusion, so the image of a presented object is a different
    object, and an inherited result that stayed with the receiver would be visible.
    """

    class ObjectType(ObjectOfCategory):
        def __init__(self, category, presented):
            ObjectOfCategory.__init__(self, category)
            self._presented = presented

        def presented_object(self) -> ObjectOfCategory:
            return self._presented

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        def underlying_morphism(self) -> MorphismOfCategory:
            return self._underlying

    def __init__(self, skeletal):
        self._skeletal = skeletal
        super().__init__()

    def structure_functors(self):
        return (Fun(self, self._skeletal).Faithful()(lambda member: member.presented_object(), lambda morphism: morphism.underlying_morphism()),)

    def __call__(self, presented):
        return self.ObjectType(self, presented)

    def __repr__(self):
        return "Presented"


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
    assert ask(swap * swap == pair.identity()) is True
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


def test_two_paths_to_one_owner_install_one_element_and_morphism_method_before_any_value_exists() -> None:
    """Compilation constructs no image (POL-KERNEL-001): the element and morphism surfaces exist with no value of the diamond."""
    diamond = Diamond(Left(), Right())

    # ``__hash__`` and ``__call__`` are the special-method witnesses: a forwarding
    # descriptor must install them on the class, not on an instance.
    assert "__hash__" in vars(diamond.ElementType)
    assert "__call__" in vars(diamond.MorphismType)
    assert "image" in vars(diamond.MorphismType)
    assert diamond.ElementType is not Sets().ElementType
    assert diamond.MorphismType is not Sets().MorphismType

    apex = diamond((int(5), int(8)))
    point = apex.point(int(5))
    fixed = Mor(diamond)(apex, apex)(lambda datum: datum)

    # The inherited special methods run the declaring method on the transported value.
    assert hash(point) == hash(int(5))
    assert ask(fixed(point) == point) is True
    assert fixed.image() in Sets().ChosenSubsets()
    assert fixed.image().inclusion().codomain() is apex


def test_incomparable_owners_of_one_spelling_are_a_semantic_collision() -> None:
    """Two unrelated owners of ``size`` cannot be compiled onto one category."""
    with pytest.raises(SemanticCollisionError):
        BothSizes(Colliding(), Sizes())


def test_incomparable_owners_of_one_element_spelling_are_a_semantic_collision() -> None:
    """The collision rule is the same for the element role (POL-CAT-011, POL-API-011)."""
    with pytest.raises(SemanticCollisionError, match="'weight' is declared by both"):
        BothRoles(ElementWeight(), ElementMass())


def test_incomparable_owners_of_one_morphism_spelling_are_a_semantic_collision() -> None:
    """The collision rule is the same for the morphism role (POL-CAT-011, POL-API-011)."""
    with pytest.raises(SemanticCollisionError, match="'degree' is declared by both"):
        BothRoles(MorphismDegree(), MorphismOrder())


def test_a_receiver_valued_and_a_map_valued_inherited_result_stay_in_the_declaring_category() -> None:
    """``X.f() := F(X).f()``: nothing is transported back (POL-CAT-062).

    ``Presented`` selects one forgetful functor into ``Skeletal``, so the image of a
    presented object is the skeletal object it presents, a different object.  The
    receiver-valued declaration therefore returns that image, and the set-map-valued
    declaration returns an object of ``Mor(Sets())``; neither result is lifted back into
    ``Presented``.  ``Sets()`` declares no method of either result role, so the poset
    specimen in ``tests/posets/test_posets.sage`` cannot state these two.
    """
    skeletal = Skeletal()
    presented = Presented(skeletal)
    (forgetful,) = presented.structure_functors()
    carrier = Sets().Finite()((int(3), int(4)))
    representative = skeletal(carrier)
    member = presented(representative)

    assert forgetful.on_object(member) is representative
    assert representative is not member

    assert member.chosen_representative() is representative
    assert representative.chosen_representative() is representative

    assert member.carrier_identity() is carrier.identity()
    assert member.carrier_identity() in Mor(Sets())(carrier, carrier)
    assert member.carrier_identity() not in Mor(presented)
