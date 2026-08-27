"""The method compiler: dynamic inheritance surface, compile-time ownership, collisions.

Toy categories live only in this file (POL-TEST-006).  Each witness calls inherited public
operations through the production compiler (POL-TEST-006).  A toy stores its own
members on its own objects; it reads no ambient private field.

Each toy declares only the roles whose mathematics it introduces, as
``DeclaredObjectType``, ``DeclaredElementType``, and ``DeclaredMorphismType``; the kernel
supplies the empty declaration for the rest and compiles the public ``ObjectType``,
``ElementType``, and ``MorphismType`` from them (POL-KERNEL-028).  A local constructor
takes one exact typed datum, and the datum of a declaration whose inherited methods must
return a value in that declaration's own category binds the canonical value of that
category (POL-LEAF-047, POL-CAT-062).
"""

from dataclasses import dataclass, field
from typing import Self

import pytest

from sage_categories.all import *
from sage_categories.kernel.compiler import SemanticCollisionError
from sage_categories.kernel.construction import retained_morphism_input, retained_object_input
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.category import SetMap


def _enumeration(finite_set):
    """The enumeration ``Sets().Finite()`` retained for a set of this toy's objects."""
    return Sets().Finite().chosen_enumeration(finite_set)


class PairSets(Category):
    """Two-element sets, declared a full subcategory of ``Sets()`` by one inclusion and nothing else."""

    def structure_functors(self):
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)

    def __call__(self, first, second):
        pair = Sets().Finite()((first, second))
        refine(pair, self)
        return pair

    def __repr__(self):
        return "PairSets"


class Left(Category):
    """A full subcategory of ``Sets()`` with one local object method."""

    class DeclaredObjectType(ObjectOfCategory):
        def left_datum(self) -> int:
            """The first datum of the chosen enumeration."""
            return _enumeration(self)[int(0)]

    def structure_functors(self):
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)

    def __repr__(self):
        return "Left"


class Right(Category):
    """A second full subcategory of ``Sets()``, incomparable with ``Left``."""

    class DeclaredObjectType(ObjectOfCategory):
        def right_datum(self) -> int:
            """The last datum of the chosen enumeration."""
            return _enumeration(self)[int(-1)]

    def structure_functors(self):
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)

    def __repr__(self):
        return "Right"


class Diamond(Category):
    """Included in both ``Left`` and ``Right``: two routes to the one owner ``Sets()``."""

    def __init__(self, left, right):
        self._left = left
        self._right = right
        super().__init__()

    def structure_functors(self):
        return (
            Fun(self, self._left).Monomorphisms().Isofibrations().Full()(),
            Fun(self, self._right).Monomorphisms().Isofibrations().Full()(),
        )

    def __call__(self, members):
        apex = Sets().Finite()(tuple(members))
        refine(apex, self)
        return apex

    def __repr__(self):
        return "Diamond"


class Colliding(Category):
    """A category declaring ``size`` with a meaning unrelated to ``Sizes.size``."""

    class DeclaredObjectType(ObjectOfCategory):
        def size(self) -> int:
            """The first enumerated datum, read as a linear extent."""
            return _enumeration(self)[int(0)]

    def structure_functors(self):
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)

    def __repr__(self):
        return "Colliding"


class Sizes(Category):
    """A category declaring ``size`` as the cardinality datum."""

    class DeclaredObjectType(ObjectOfCategory):
        def size(self) -> int:
            """The number of enumerated data."""
            return len(_enumeration(self))

    def structure_functors(self):
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)

    def __repr__(self):
        return "Sizes"


class BothSizes(Category):
    """Included in ``Colliding`` and ``Sizes``: one spelling, two unrelated owners."""

    def __init__(self, colliding, sizes):
        self._colliding = colliding
        self._sizes = sizes
        super().__init__()

    def structure_functors(self):
        return (
            Fun(self, self._colliding).Monomorphisms().Isofibrations().Full()(),
            Fun(self, self._sizes).Monomorphisms().Isofibrations().Full()(),
        )

    def __repr__(self):
        return "BothSizes"


class ElementWeight(Category):
    """A full subcategory of ``Sets()`` declaring ``weight`` on generalized elements."""

    class DeclaredElementType(ElementOfObject):
        def weight(self) -> int:
            return int(1)

    def structure_functors(self):
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)

    def __repr__(self):
        return "ElementWeight"


class ElementMass(Category):
    """A second full subcategory of ``Sets()`` declaring ``weight`` with an unrelated meaning."""

    class DeclaredElementType(ElementOfObject):
        def weight(self) -> int:
            return int(2)

    def structure_functors(self):
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)

    def __repr__(self):
        return "ElementMass"


class MorphismDegree(Category):
    """A full subcategory of ``Sets()`` declaring ``degree`` on morphisms."""

    class DeclaredMorphismType(MorphismOfCategory):
        def degree(self) -> int:
            return int(1)

    def structure_functors(self):
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)

    def __repr__(self):
        return "MorphismDegree"


class MorphismOrder(Category):
    """A second full subcategory of ``Sets()`` declaring ``degree`` with an unrelated meaning."""

    class DeclaredMorphismType(MorphismOfCategory):
        def degree(self) -> int:
            return int(2)

    def structure_functors(self):
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)

    def __repr__(self):
        return "MorphismOrder"


class BothRoles(Category):
    """Included in two categories that collide on one role's spelling."""

    def __init__(self, first, second):
        self._first = first
        self._second = second
        super().__init__()

    def structure_functors(self):
        return (
            Fun(self, self._first).Monomorphisms().Isofibrations().Full()(),
            Fun(self, self._second).Monomorphisms().Isofibrations().Full()(),
        )

    def __repr__(self):
        return "BothRoles"


@dataclass(eq=False, slots=True)
class CarrierData:
    """The local datum of an object carrying one set."""

    carrier: object


@dataclass(frozen=True, eq=False, slots=True)
class CarrierMapData:
    """The local datum of a morphism carrying one set map."""

    set_map: object


class Carried(Category):
    """Objects carrying a set, related to ``Sets()`` by an explicit forgetful functor, not an inclusion."""

    class DeclaredObjectType(ObjectOfCategory):
        def __init__(self, data):
            self._carrier_data = data
            super().__init__()

        def carrier(self) -> ObjectOfCategory:
            return self._carrier_data.carrier

    class DeclaredMorphismType(MorphismOfCategory):
        def __init__(self, data):
            self._carrier_map_data = data
            super().__init__()

        def underlying_map(self) -> MorphismOfCategory:
            return self._carrier_map_data.set_map

    def __init__(self):
        self._selected = {}
        super().__init__()

    def structure_functors(self):
        if "carrier" not in self._selected:
            underlying = Fun(self, Sets()).Faithful()(lambda member: member.carrier(), lambda morphism: morphism.underlying_map())
            underlying.retain_object_constructor_conversion(lambda source: retained_object_input(source.datum.carrier))
            underlying.retain_morphism_constructor_conversion(lambda source: retained_morphism_input(source.datum.set_map))
            self._selected["carrier"] = underlying
        return (self._selected["carrier"],)

    def __call__(self, carrier):
        return self.ObjectType(self, CarrierData(carrier))

    def __repr__(self):
        return "Carried"


@dataclass(eq=False, slots=True)
class SkeletalData:
    """The carrier of a skeletal object, and the canonical object it belongs to."""

    carrier: object
    canonical: object = field(init=False)

    def bind(self, canonical) -> None:
        """Bind direct construction once; inherited construction reuses that state."""
        if not hasattr(self, "canonical"):
            self.canonical = canonical


class Skeletal(Category):
    """A skeletal category of sets: one object per isomorphism class, so each object is its own chosen representative.

    It declares the two result roles no category in ``src/`` currently declares: an
    operation valued in its own category and a set-map-valued one.
    """

    class DeclaredObjectType(ObjectOfCategory):
        def __init__(self, data):
            data.bind(self)
            self._skeletal_data = data
            super().__init__()

        def carrier(self) -> ObjectOfCategory:
            return self._skeletal_data.carrier

        def chosen_representative(self) -> Self:
            """The representative of this object's isomorphism class: the object ``SkeletalData`` bound at its first construction.

            The body reads stored state, not the receiver, so this declaration does not
            witness the receiver-valued clause of ``D18``; the specimen for that clause,
            whose body is literally ``return self``, is in
            ``tests/cat/test_two_morphisms.sage``.
            """
            return self._skeletal_data.canonical

        def carrier_identity(self) -> SetMap:
            """The identity of the underlying set: a morphism of ``Sets()``, whatever category the receiver lives in."""
            return self._skeletal_data.carrier.identity()

    def __call__(self, carrier):
        return self.ObjectType(self, SkeletalData(carrier))

    def __repr__(self):
        return "Skeletal"


@dataclass(eq=False, slots=True)
class PresentedData:
    """The skeletal object a presented object presents."""

    presented: object


@dataclass(frozen=True, eq=False, slots=True)
class PresentedMapData:
    """The skeletal morphism a presented morphism presents."""

    underlying: object


class Presented(Category):
    """Objects with a chosen presentation of a skeletal object, related to it by a forgetful functor.

    The functor is not an inclusion, so the image of a presented object is a different
    object, and an inherited result that stayed with the receiver would be visible.
    """

    class DeclaredObjectType(ObjectOfCategory):
        def __init__(self, data):
            self._presented_data = data
            super().__init__()

        def presented_object(self) -> ObjectOfCategory:
            return self._presented_data.presented

    class DeclaredMorphismType(MorphismOfCategory):
        def __init__(self, data):
            self._presented_map_data = data
            super().__init__()

        def underlying_morphism(self) -> MorphismOfCategory:
            return self._presented_map_data.underlying

    def __init__(self, skeletal):
        self._skeletal = skeletal
        self._selected = {}
        super().__init__()

    def structure_functors(self):
        if "forgetful" not in self._selected:
            forgetful = Fun(self, self._skeletal).Faithful()(
                lambda member: member.presented_object(),
                lambda morphism: morphism.underlying_morphism(),
            )
            forgetful.retain_object_constructor_conversion(lambda source: retained_object_input(source.datum.presented))
            forgetful.retain_morphism_constructor_conversion(lambda source: retained_morphism_input(source.datum.underlying))
            self._selected["forgetful"] = forgetful
        return (self._selected["forgetful"],)

    def __call__(self, presented):
        return self.ObjectType(self, PresentedData(presented))

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


def test_two_paths_to_one_owner_install_one_method_before_any_value_exists() -> None:
    """The diamond compiles ``cardinality`` once from ``Sets()`` while no object of it exists.

    Two routes reach one declaring owner, so the compiled role has one entry for the
    spelling and one occurrence of that owner's role in its linearization
    (``specs/resolution.md``, rule 2; POL-CAT-016).
    """
    left, right = Left(), Right()
    diamond = Diamond(left, right)

    linearization = diamond.ObjectType.__mro__
    assert list(linearization).count(Sets().ObjectType) == int(1)
    assert diamond.ObjectType.cardinality is Sets().ObjectType.cardinality
    assert diamond.ObjectType.left_datum is left.ObjectType.left_datum
    assert diamond.ObjectType.right_datum is right.ObjectType.right_datum
    assert "left_datum" in vars(left.ObjectType)
    assert "right_datum" in vars(right.ObjectType)

    apex = diamond((int(5), int(8)))
    assert apex.left_datum() == int(5)
    assert apex.right_datum() == int(8)
    assert ask(apex.cardinality() == int(2)) is True
    assert apex in Sets()


def test_two_paths_to_one_owner_install_one_element_and_morphism_method_before_any_value_exists() -> None:
    """Compilation constructs no image (POL-KERNEL-001): the element and morphism surfaces exist with no value of the diamond."""
    diamond = Diamond(Left(), Right())

    # ``__hash__`` and ``__call__`` are the special-method witnesses: Python resolves a
    # special method on the class, so the compiled role must carry the declaring role
    # in its own linearization rather than on an instance.
    assert diamond.ElementType.__hash__ is Sets().ElementType.__hash__
    assert diamond.MorphismType.__call__ is Sets().MorphismType.__call__
    assert diamond.MorphismType.image is Sets().MorphismType.image
    assert list(diamond.ElementType.__mro__).count(Sets().ElementType) == int(1)
    assert list(diamond.MorphismType.__mro__).count(Sets().MorphismType) == int(1)
    assert diamond.ElementType is not Sets().ElementType
    assert diamond.MorphismType is not Sets().MorphismType

    apex = diamond((int(5), int(8)))
    point = apex.point(int(5))
    fixed = Mor(diamond)(apex, apex)(lambda datum: datum)

    # The inherited special methods run the declaring method on the transported value.
    assert hash(point) == hash(int(5))
    assert ask(fixed(point) == point) is True
    assert fixed.image() in Sets().ChosenSubsets()
    assert fixed.image().monomorphism().codomain() is apex


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


def test_inherited_results_stay_in_their_declaring_category() -> None:
    """``X.f() := F(X).f()``: nothing is transported back (POL-CAT-062).

    ``Presented`` selects one forgetful functor into ``Skeletal``, so the image of a
    presented object is the skeletal object it presents, a different object.  The
    declaration valued in ``Skeletal`` returns the skeletal object its shared state binds,
    and the set-map-valued declaration returns an object of ``Mor(Sets())``; neither
    result is lifted back into ``Presented``.  ``Sets()`` declares no method of either
    result role, so the poset specimen in ``tests/posets/test_posets.sage`` cannot state
    these two.
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
