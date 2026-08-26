"""Canonical transport: one image per value and reachable node, and the eager check.

Transport is canonical (POL-CAT-012, POL-KERNEL-001): at the first transport of a
value to a node every selected route is traversed in declaration order, the first
image is stored, and each later image must be the same object.  The node
``(Mor(C), object)`` *is* the node ``(C, morphism)`` (POL-CAT-021), so one morphism
has one cache entry however it is addressed.

Toy categories live only in this file (POL-TEST-006).  Each row states one property
of an image, never a functor law (D14).

Oracles: the definition of the canonical image (the value the selected functor's
own action returns); the identity of retained construction data (a chosen product
retains its apex and projections, POL-CAT-093); the definition of a lift of a
construction (the refined product is the same object of the ambient); the register's
stated construction-defect error naming both routes (POL-CAT-012).
"""

import pytest

from sage_categories.all import *
from sage_categories.kernel import compiler
from sage_categories.kernel.caches import canonical_images
from sage_categories.kernel.compiler import StructuralImageMismatch
from sage_categories.kernel.descriptors import placement_node, transport
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role


def _finite_rule(members):
    return lambda datum: any(datum == member for member in members)


# -- a ring-style toy: two routes to ``Sets()`` through an additive and a multiplicative leaf --
#
# Both leaves carry the same object with the same retained carrier, so the two
# routes agree by identity.  ``Rebuilt`` in ``tests/kernel/test_elements.sage`` is the
# leaf whose second route rebuilds the carrier instead; here the diamond agrees.


class Carrying(Category):
    """A category of ``Sets()``-carrying objects with one explicit forgetful functor.

    It declares no local operation: two of these are incomparable, so one shared
    spelling would be a semantic collision (POL-CAT-011), which is a different row.
    """

    class ObjectType(ObjectOfCategory):
        def __init__(self, category, carrier):
            ObjectOfCategory.__init__(self, category)
            self._carrier = carrier

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def __init__(self, name):
        self._name = name
        super().__init__()

    def structure_functors(self):
        if "carrier" not in self.__dict__.setdefault("_selected", {}):
            self._selected["carrier"] = Fun(self, Sets()).Faithful()(lambda member: member._carrier, lambda morphism: morphism)
        return (self._selected["carrier"],)

    def __call__(self, carrier):
        return self.ObjectType(self, carrier)

    def __repr__(self):
        return self._name


class Ringlike(Category):
    """An object with an additive and a multiplicative structure on one retained carrier.

    Its two selected functors reach ``Sets()`` through two different leaves; both
    return the very same carrier, set map, and point (POL-FUN-029).
    """

    class ObjectType(ObjectOfCategory):
        def __init__(self, category, carrier):
            ObjectOfCategory.__init__(self, category)
            self._carrier = carrier
            self._additive = category.additive()(carrier)
            self._multiplicative = category.multiplicative()(carrier)

        def additive_structure(self) -> ObjectOfCategory:
            return self._additive

        def multiplicative_structure(self) -> ObjectOfCategory:
            return self._multiplicative

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def __init__(self, additive, multiplicative):
        self._additive, self._multiplicative = additive, multiplicative
        super().__init__()

    def additive(self):
        return self._additive

    def multiplicative(self):
        return self._multiplicative

    def structure_functors(self):
        if "routes" not in self.__dict__.setdefault("_selected", {}):
            self._selected["routes"] = (
                Fun(self, self._additive).Faithful()(lambda member: member.additive_structure(), lambda morphism: morphism),
                Fun(self, self._multiplicative).Faithful()(lambda member: member.multiplicative_structure(), lambda morphism: morphism),
            )
        return self._selected["routes"]

    def __call__(self, members):
        return self.ObjectType(self, Sets().Finite()(tuple(members)))

    def __repr__(self):
        return "Ringlike"


# -- rows -------------------------------------------------------------------------------------


def test_two_structural_routes_to_one_category_return_one_underlying_set_map_and_point() -> None:
    """The additive and multiplicative routes of the ring-style toy agree by identity at ``Sets()``."""
    ringlike = Ringlike(Carrying("Additive"), Carrying("Multiplicative"))
    member = ringlike((int(0), int(1)))
    additive, multiplicative = ringlike.structure_functors()
    carrier = member._carrier

    through_additive = ringlike.additive().structure_functors()[int(0)].on_object(additive.on_object(member))
    through_multiplicative = ringlike.multiplicative().structure_functors()[int(0)].on_object(multiplicative.on_object(member))
    assert additive.on_object(member) is not multiplicative.on_object(member)
    assert through_additive is carrier
    assert through_multiplicative is carrier

    image = transport(member, compiler.node(Sets(), Role.OBJECT))
    assert image is carrier
    assert ask(member.cardinality() == int(2)) is True
    assert member.point(int(1)) is carrier.point(int(1))


def test_the_finite_poset_diamond_returns_one_underlying_set_map_and_point() -> None:
    """``FinitePosets()`` reaches ``Sets()`` through ``Posets()`` and through ``Sets().Finite()``; the images coincide."""
    chain = Posets().Simplex(int(2))
    underlying = Posets().structure_functors()[int(0)]
    restricted = FinitePosets().structure_functors()[int(1)]
    fixed = Mor(Posets())(chain, chain)(lambda point: point)

    assert chain in FinitePosets()
    assert underlying.on_object(chain) is restricted.on_object(chain)
    assert underlying.on_morphism(fixed) is restricted.on_morphism(fixed)
    assert transport(chain, compiler.node(Sets(), Role.OBJECT)) is underlying.on_object(chain)
    assert transport(fixed, compiler.node(Sets(), Role.MORPHISM)) is underlying.on_morphism(fixed)

    one = chain.element(underlying.on_object(chain).point(int(1)))
    assert transport(one, compiler.node(Sets(), Role.ELEMENT)) is restricted.on_element(one)


def test_the_image_a_compiled_method_uses_is_the_image_the_selected_functor_returns() -> None:
    """Two distinct public entry points, one canonical image (POL-CAT-012); no call is repeated to prove it."""
    chain = Posets().Simplex(int(2))
    underlying = Posets().structure_functors()[int(0)]
    target = compiler.node(Sets(), Role.OBJECT)

    # ``chain.cardinality()`` is compiled from ``Sets()``: it runs on the transported image.
    assert ask(chain.cardinality() == int(3)) is True
    assert (chain, chain, Sets()) in canonical_images[Role.OBJECT]
    assert canonical_images[Role.OBJECT][chain, chain, Sets()] is underlying.on_object(chain)
    assert transport(chain, target) is underlying.on_object(chain)


def test_an_object_image_and_a_morphism_image_of_one_value_are_one_cache_entry() -> None:
    """A morphism of ``C`` is an object of ``Mor(C)``: ``(Mor(C), object)`` is the node ``(C, morphism)`` (POL-CAT-021)."""
    chain = Posets().Simplex(int(2))
    fixed = Mor(Posets())(chain, chain)(lambda point: point)
    underlying = Posets().structure_functors()[int(0)]

    assert compiler.same_node(compiler.node(Mor(Posets()), Role.OBJECT), compiler.node(Posets(), Role.MORPHISM))
    assert compiler.same_node(placement_node(fixed), compiler.node(Posets(), Role.MORPHISM))

    as_morphism = transport(fixed, compiler.node(Sets(), Role.MORPHISM))
    as_object_of_mor = transport(fixed, compiler.node(Mor(Sets()), Role.OBJECT))
    assert as_morphism is as_object_of_mor
    assert as_morphism is underlying.on_morphism(fixed)
    assert canonical_images[Role.MORPHISM][fixed, fixed, Sets()] is as_morphism


def test_the_cache_key_separates_the_value_and_the_target_category() -> None:
    """The key is ``(key, value, target category)``: two elements are two entries, and two targets are two entries."""
    chain = Posets().Simplex(int(2))
    carrier = Posets().structure_functors()[int(0)].on_object(chain)
    zero, one = chain.element(carrier.point(int(0))), chain.element(carrier.point(int(1)))

    first_image = transport(zero, compiler.node(Sets(), Role.ELEMENT))
    second_image = transport(one, compiler.node(Sets(), Role.ELEMENT))
    assert first_image is not second_image
    assert canonical_images[Role.ELEMENT][zero.parent(), zero, Sets()] is first_image
    assert canonical_images[Role.ELEMENT][one.parent(), one, Sets()] is second_image

    # A second target category is a second entry even when the two images coincide,
    # because ``Sets().Finite()`` is a full subcategory of ``Sets()`` on the same sets.
    finite_node = compiler.node(Sets().Finite(), Role.OBJECT)
    assert transport(chain, compiler.node(Sets(), Role.OBJECT)) is transport(chain, finite_node)
    assert (chain, chain, Sets()) in canonical_images[Role.OBJECT]
    assert (chain, chain, Sets().Finite()) in canonical_images[Role.OBJECT]


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
    assert transport(member, target) is member._carrier
    assert ask(member.cardinality() == int(3)) is True


def test_the_eager_check_names_both_routes_and_the_shared_category() -> None:
    """A leaf whose second route rebuilds the ancestor fails at the first transport, naming both routes (POL-CAT-012)."""

    class Rebuilding(Category):
        class ObjectType(ObjectOfCategory):
            def __init__(self, category, members):
                ObjectOfCategory.__init__(self, category)
                self._members = members
                self._carrier = Sets().Finite()(members)

        class ElementType(ElementOfObject):
            """No local operation."""

        class MorphismType(MorphismOfCategory):
            """No local operation."""

        def structure_functors(self):
            if "routes" not in self.__dict__.setdefault("_selected", {}):
                self._selected["routes"] = (
                    Fun(self, Sets())(lambda member: member._carrier, lambda morphism: morphism),
                    Fun(self, Sets())(lambda member: Sets().Finite()(member._members), lambda morphism: morphism),
                )
            return self._selected["routes"]

        def __repr__(self):
            return "Rebuilding"

    rebuilding = Rebuilding()
    member = rebuilding.ObjectType(rebuilding, (int(8), int(9)))
    first, second = rebuilding.structure_functors()

    with pytest.raises(StructuralImageMismatch) as raised:
        transport(member, compiler.node(Sets(), Role.OBJECT))
    message = str(raised.value)
    assert repr(first) in message
    assert repr(second) in message
    assert repr(Sets()) in message
