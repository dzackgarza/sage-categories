"""Canonical transport: one image per value and reachable node, and the eager check.

Transport is canonical (POL-CAT-012, POL-KERNEL-001): at the first transport of a
value to a node every selected route is traversed in declaration order, the first
image is stored, and each later image must be the same object.  The node
``(Mor(C), object)`` *is* the node ``(C, morphism)`` (POL-CAT-021), so one morphism
has one cache entry however it is addressed.

Toy categories live only in this file (POL-TEST-006).  Each declares
``DeclaredObjectType``, ``DeclaredElementType``, and ``DeclaredMorphismType``, whose
local constructors take one exact typed datum (POL-KERNEL-028, POL-LEAF-047); the
kernel compiles the public ``ObjectType``, ``ElementType``, and ``MorphismType`` from
them.  Each selected functor is declared by its two image rules, which read one node's
local datum and return the value the toy's own constructor already made; the kernel
derives the construction inputs and the public actions, and the element conversion from
the morphism one (POL-FUN-002, POL-FUN-035).
Each row states one property of an image, never a functor law (D14).

Oracles: the definition of the canonical image (the value the selected functor's
own action returns); the identity of retained construction data (a chosen product
retains its apex and projections, POL-CAT-093); the definition of a lift of a
construction (the refined product is the same object of the ambient); the register's
stated construction-defect error naming both routes (POL-CAT-012).
"""

from dataclasses import dataclass

import pytest

from sage_categories.all import *
from sage_categories.kernel import compiler

from sage_categories.kernel.compiler import StructuralImageMismatch
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role
from sage_categories.kernel.transport import placement_node, role_node, transport


@dataclass(eq=False, slots=True)
class CarrierData:
    """The local datum of an object carrying one set."""

    carrier: object


@dataclass(frozen=True, eq=False, slots=True)
class CarrierMapData:
    """The local datum of a morphism carrying one set map."""

    set_map: object


# -- a ring-style toy: two routes to ``Sets()`` through an additive and a multiplicative leaf --
#
# Both leaves carry the same object with the same retained carrier, so the two
# routes agree by identity.  ``Rebuilding`` below is the leaf whose second route
# rebuilds the carrier instead; here the diamond agrees.


class Carrying(Category):
    """A category of ``Sets()``-carrying objects with one explicit forgetful functor.

    It declares no local operation beyond its retained data: two of these are
    incomparable, so one shared spelling would be a semantic collision
    (POL-CAT-011), which is a different row.
    """

    class DeclaredObjectType(ObjectOfCategory):
        def __init__(self, data):
            self._carrier_data = data
            super().__init__()

    class DeclaredElementType(ElementOfObject):
        """No local operation."""

    class DeclaredMorphismType(MorphismOfCategory):
        def __init__(self, data):
            self._carrier_map_data = data
            super().__init__()

    def __init__(self, name):
        self._name = name
        self._selected = {}
        super().__init__()

    def structure_functors(self):
        if "carrier" not in self._selected:
            self._selected["carrier"] = Fun(self, Sets()).Faithful().structural(
                lambda datum: datum.carrier,
                lambda datum: datum.set_map,
            )
        return (self._selected["carrier"],)

    def __call__(self, carrier):
        return self.ObjectType(self, CarrierData(carrier))

    def construct_morphism(self, domain, codomain, set_map):
        return self.MorphismType(Mor(self), domain, codomain, CarrierMapData(set_map))

    def __repr__(self):
        return self._name


@dataclass(eq=False, slots=True)
class RinglikeData:
    """One carrier and the two structures the selected functors return."""

    carrier: object
    additive: object
    multiplicative: object


@dataclass(frozen=True, eq=False, slots=True)
class RinglikeMapData:
    """The two structure morphisms the selected functors return, on one set map."""

    additive: object
    multiplicative: object


class Ringlike(Category):
    """An object with an additive and a multiplicative structure on one retained carrier.

    Its two selected functors reach ``Sets()`` through two different leaves; both
    return the very same carrier, set map, and point (POL-FUN-029).
    """

    class DeclaredObjectType(ObjectOfCategory):
        def __init__(self, data):
            self._ringlike_data = data
            super().__init__()

        def carrier(self):
            return self._ringlike_data.carrier

        def additive_structure(self):
            return self._ringlike_data.additive

        def multiplicative_structure(self):
            return self._ringlike_data.multiplicative

    class DeclaredElementType(ElementOfObject):
        """No local operation."""

    class DeclaredMorphismType(MorphismOfCategory):
        def __init__(self, data):
            self._ringlike_map_data = data
            super().__init__()

    def __init__(self, additive, multiplicative):
        self._additive, self._multiplicative = additive, multiplicative
        self._selected = {}
        super().__init__()

    def additive(self):
        return self._additive

    def multiplicative(self):
        return self._multiplicative

    def structure_functors(self):
        if "routes" not in self._selected:
            to_additive = Fun(self, self._additive).Faithful().structural(
                lambda datum: datum.additive,
                lambda datum: datum.additive,
            )
            to_multiplicative = Fun(self, self._multiplicative).Faithful().structural(
                lambda datum: datum.multiplicative,
                lambda datum: datum.multiplicative,
            )
            self._selected["routes"] = (to_additive, to_multiplicative)
        return self._selected["routes"]

    def __call__(self, members):
        carrier = Sets().Finite()(tuple(members))
        return self.ObjectType(self, RinglikeData(carrier, self._additive(carrier), self._multiplicative(carrier)))

    def construct_morphism(self, domain, codomain, set_map):
        """A morphism of the toy is one set map, carried by both structures."""
        additive = Mor(self._additive)(domain.additive_structure(), codomain.additive_structure())(set_map)
        multiplicative = Mor(self._multiplicative)(domain.multiplicative_structure(), codomain.multiplicative_structure())(set_map)
        return self.MorphismType(Mor(self), domain, codomain, RinglikeMapData(additive, multiplicative))

    def __repr__(self):
        return "Ringlike"


# -- rows -------------------------------------------------------------------------------------


def test_two_structural_routes_to_one_category_return_one_underlying_set_map_and_point() -> None:
    """The additive and multiplicative routes of the ring-style toy agree by identity at ``Sets()``."""
    ringlike = Ringlike(Carrying("Additive"), Carrying("Multiplicative"))
    member = ringlike((int(0), int(1)))
    additive, multiplicative = ringlike.structure_functors()
    carrier = member.carrier()

    through_additive = ringlike.additive().structure_functors()[int(0)].on_object(additive.on_object(member))
    through_multiplicative = ringlike.multiplicative().structure_functors()[int(0)].on_object(multiplicative.on_object(member))
    assert additive.on_object(member) is not multiplicative.on_object(member)
    assert through_additive is carrier
    assert through_multiplicative is carrier

    image = transport(member, compiler.node(Sets(), Role.OBJECT))
    assert image is carrier
    assert ask(member.cardinality() == int(2)) is True
    assert member.point(int(1)) is carrier.point(int(1))

    # The same three statements on a morphism: one set map, reached by both routes.
    swap_map = Mor(Sets())(carrier, carrier)(lambda datum: int(1) - datum)
    swap = Mor(ringlike)(member, member)(swap_map)
    map_through_additive = ringlike.additive().structure_functors()[int(0)].on_morphism(additive.on_morphism(swap))
    map_through_multiplicative = ringlike.multiplicative().structure_functors()[int(0)].on_morphism(multiplicative.on_morphism(swap))
    assert additive.on_morphism(swap) is not multiplicative.on_morphism(swap)
    assert map_through_additive is swap_map
    assert map_through_multiplicative is swap_map
    assert transport(swap, compiler.node(Sets(), Role.MORPHISM)) is swap_map
    assert ask(swap(member.point(int(0))) == carrier.point(int(1))) is True


def test_the_finite_poset_diamond_returns_one_underlying_set_map_and_point() -> None:
    """``FinitePosets()`` reaches ``Sets()`` through ``Posets()`` and through ``Sets().Finite()``; the images coincide."""
    chain = Posets().Simplex(int(2))
    underlying = Posets().structure_functors()[int(0)]
    restricted = FinitePosets().structure_functors()[int(1)]
    fixed = Mor(FinitePosets())(chain, chain)(lambda point: point)

    assert chain in FinitePosets()
    assert underlying.on_object(chain) is restricted.on_object(chain)
    assert underlying.on_morphism(fixed) is restricted.on_morphism(fixed)
    assert transport(chain, compiler.node(Sets(), Role.OBJECT)) is underlying.on_object(chain)
    assert transport(fixed, compiler.node(Sets(), Role.MORPHISM)) is underlying.on_morphism(fixed)

    one = chain.element(underlying.on_object(chain).point(int(1)))
    assert transport(one, compiler.node(Sets(), Role.ELEMENT)) is underlying.on_element(one)


def test_the_image_a_compiled_method_uses_is_the_image_the_selected_functor_returns() -> None:
    """Two distinct public entry points, one canonical image (POL-CAT-012); no call is repeated to prove it."""
    chain = Posets().Simplex(int(2))
    underlying = Posets().structure_functors()[int(0)]
    target = compiler.node(Sets(), Role.OBJECT)

    # ``chain.cardinality()`` is compiled from ``Sets()``: it runs on the transported image.
    assert ask(chain.cardinality() == int(3)) is True
    assert transport(chain, target) is underlying.on_object(chain)
    assert chain.cardinality() is underlying.on_object(chain).cardinality()


def test_a_category_reads_the_image_of_a_descendant_value_in_itself() -> None:
    """``C.image_of(x)`` is the image ``C``'s selected route retained: what a method ``C`` declares is about (POL-KERNEL-018)."""
    chain = Posets().Simplex(int(2))
    fixed = Mor(Posets())(chain, chain)(lambda point: point)
    underlying = Posets().structure_functors()[int(0)]
    carrier = underlying.on_object(chain)
    zero = chain.element(carrier.point(int(0)))

    assert Sets().image_of(chain) is carrier, "the underlying set of the poset, not the poset"
    assert Sets().image_of(fixed) is underlying.on_morphism(fixed)
    assert Sets().image_of(zero) is underlying.on_element(zero)

    # A method ``Sets()`` declares reads the carrier's cardinality, which is the poset's.
    assert ask(Sets().image_of(chain).cardinality() == chain.cardinality()) is True


def test_a_category_reads_its_own_value_as_its_own_image() -> None:
    """The route from a category to itself is empty, so ``C.image_of(x)`` is ``x`` for a value of ``C``."""
    members = Sets().Finite()((int(0), int(1)))
    identity = Mor(Sets())(members, members).identity()

    assert Sets().image_of(members) is members
    assert Sets().image_of(identity) is identity
    assert Posets().image_of(Posets().Simplex(int(2))) is Posets().Simplex(int(2))


def test_an_object_image_and_a_morphism_image_of_one_value_are_one_cache_entry() -> None:
    """A morphism of ``C`` is an object of ``Mor(C)``: ``(Mor(C), object)`` is the node ``(C, morphism)`` (POL-CAT-021)."""
    chain = Posets().Simplex(int(2))
    fixed = Mor(Posets())(chain, chain)(lambda point: point)
    underlying = Posets().structure_functors()[int(0)]

    assert compiler.same_node(compiler.node(Mor(Posets()), Role.OBJECT), compiler.node(Posets(), Role.MORPHISM))
    assert compiler.same_node(role_node(fixed), compiler.node(Posets(), Role.MORPHISM))
    assert compiler.same_node(placement_node(fixed), compiler.node(Mor(Posets())(chain, chain), Role.OBJECT)), (
        "constructing through Mor(C)(A, B) places the morphism there"
    )

    as_morphism = transport(fixed, compiler.node(Sets(), Role.MORPHISM))
    as_object_of_mor = transport(fixed, compiler.node(Mor(Sets()), Role.OBJECT))
    assert as_morphism is as_object_of_mor
    assert as_morphism is underlying.on_morphism(fixed)


def test_elements_differing_in_their_domain_or_defining_morphism_do_not_share_an_image() -> None:
    """POL-CAT-066: an element's image is keyed by its domain, defining morphism, and codomain."""
    chain = Posets().Simplex(int(2))
    underlying = Posets().structure_functors()[int(0)]
    carrier = underlying.on_object(chain)
    zero, one = chain.element(carrier.point(int(0))), chain.element(carrier.point(int(1)))

    assert zero.parent() is one.parent()
    assert zero.defining_morphism().domain() is one.defining_morphism().domain()
    assert zero.defining_morphism() is not one.defining_morphism()

    first_image = transport(zero, compiler.node(Sets(), Role.ELEMENT))
    second_image = transport(one, compiler.node(Sets(), Role.ELEMENT))
    assert first_image is not second_image
    assert first_image is carrier.point(int(0))
    assert second_image is carrier.point(int(1))

    # The domain axis: ``1_P`` is a generalized element of ``P`` with the same parent as
    # the points above and the domain ``P``.  Its image is the set map ``1_U(P)``
    # read as a generalized element, not a point of ``U(P)``.
    fixed = Mor(Posets())(chain, chain)(lambda point: point)
    at_the_chain = Posets().element_from_defining_morphism(fixed)
    assert at_the_chain.parent() is zero.parent()
    assert at_the_chain.defining_morphism().domain() is chain
    assert at_the_chain.defining_morphism().domain() is not zero.defining_morphism().domain()

    domain_image = transport(at_the_chain, compiler.node(Sets(), Role.ELEMENT))
    assert domain_image is underlying.on_element(at_the_chain)
    assert domain_image is not first_image
    assert domain_image.defining_morphism().domain() is carrier
    assert domain_image.defining_morphism() is underlying.on_morphism(fixed)

    # One value transports once per target: ``Sets().Finite()`` is a full subcategory of
    # ``Sets()`` on the same sets, so the two targets return the very same image.
    finite_node = compiler.node(Sets().Finite(), Role.OBJECT)
    assert transport(chain, compiler.node(Sets(), Role.OBJECT)) is transport(chain, finite_node)


def test_a_lifted_product_reuses_the_retained_ancestor_apex_and_its_projections() -> None:
    """A chosen product refined through ``Sets().Finite()`` is the very same object and the very same projections."""
    left, right = Sets().Finite()((int(1), int(2))), Sets().Finite()((int(3),))
    ancestor = Sets().Products()((left, right))
    lifted = Sets().Finite().Products()((left, right))

    assert lifted is ancestor
    assert (left * right) is ancestor
    assert lifted.product_projection(int(0)) is ancestor.product_projection(int(0))
    assert lifted.product_projection(int(1)) is ancestor.product_projection(int(1))
    assert lifted.product_projection(int(0)).codomain() is left
    assert lifted.product_projection(int(1)).codomain() is right
    assert ancestor in Sets().Finite()
    assert ask(ancestor.cardinality() == int(2)) is True


def test_two_routes_that_agree_by_identity_transport_without_error() -> None:
    """The eager check traverses every route and raises nothing when they agree."""
    ringlike = Ringlike(Carrying("Additive2"), Carrying("Multiplicative2"))
    member = ringlike((int(4), int(5), int(6)))
    target = compiler.node(Sets(), Role.OBJECT)

    assert len(compiler.routes(placement_node(member), target)) == int(2)
    assert transport(member, target) is member._ringlike_data.carrier
    assert ask(member.cardinality() == int(3)) is True


def test_the_eager_check_names_both_routes_and_the_shared_category() -> None:
    """A leaf whose second route rebuilds the ancestor fails at the first transport, naming both routes (POL-CAT-012)."""

    @dataclass(eq=False, slots=True)
    class RebuiltData:
        members: tuple
        carrier: object

    class Rebuilding(Category):
        class DeclaredObjectType(ObjectOfCategory):
            def __init__(self, data):
                self._rebuilt_data = data
                super().__init__()

        class DeclaredElementType(ElementOfObject):
            """No local operation."""

        class DeclaredMorphismType(MorphismOfCategory):
            def __init__(self, data):
                self._rebuilt_map_data = data
                super().__init__()

        def __init__(self):
            self._selected = {}
            super().__init__()

        def structure_functors(self):
            if "routes" not in self._selected:
                retained = Fun(self, Sets()).structural(lambda datum: datum.carrier, lambda datum: datum)
                # The second route builds a new set from the same members instead of
                # returning the retained one, which is the defect this row states.
                rebuilt = Fun(self, Sets()).structural(lambda datum: Sets().Finite()(datum.members), lambda datum: datum)
                self._selected["routes"] = (retained, rebuilt)
            return self._selected["routes"]

        def __call__(self, members):
            return self.ObjectType(self, RebuiltData(members, Sets().Finite()(members)))

        def __repr__(self):
            return "Rebuilding"

    rebuilding = Rebuilding()
    first, second = rebuilding.structure_functors()

    with pytest.raises(StructuralImageMismatch) as raised:
        rebuilding((int(8), int(9)))
    message = str(raised.value)
    assert repr(first) in message
    assert repr(second) in message
    assert repr(Sets()) in message
