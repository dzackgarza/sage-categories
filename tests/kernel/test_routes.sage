"""The selected structural graph: its edges, its invariants, and the routes it supplies.

The selected graph is ``structure_functors()`` alone (POL-CAT-012, POL-KERNEL-001).
Each row here states one property of an edge or of the graph, not a functor law
(D14).  Toy categories live only in this file (POL-TEST-006).

Oracles: the definition of a functor (a constructed object and morphism action, not
a pair of endpoints); the definition of composition (``(G . F)(x) = G(F(x))``, in
categorical order); the definition of a simple directed path; the definition of a
full subcategory (a narrowing by more roots is a full subcategory of the narrowing
by fewer, ``specs/functor.md``, "Inclusion functors", POL-CAT-084); the compiler's
stated construction-defect messages (POL-CAT-012).
"""

import pytest

from sage_categories.all import *
from sage_categories.kernel import compiler
from sage_categories.kernel.refinement import is_placed, is_subcategory
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role


class Plain(Category):
    """A leaf whose one selected functor is a plain functor: no declared property."""

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
        if "carrier" not in self.__dict__.setdefault("_selected", {}):
            self._selected["carrier"] = Fun(self, Sets())(lambda member: member.carrier(), lambda morphism: morphism.underlying_map())
        return (self._selected["carrier"],)

    def __call__(self, carrier):
        return self.ObjectType(self, carrier)

    def __repr__(self):
        return "Plain"


class ForeignDomain(Category):
    """A leaf whose declared entry is a functor out of another category."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        return (Fun(Posets(), Sets()).Faithful()(lambda poset: poset.underlying_set(), lambda monotone: monotone.underlying_map()),)

    def __repr__(self):
        return "ForeignDomain"


class Duplicated(Category):
    """A leaf that declares one functor twice."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        inclusion = Fun(self, Sets()).FullyFaithful().inclusion()
        return (inclusion, inclusion)

    def __repr__(self):
        return "Duplicated"


class SelfLooped(Category):
    """A leaf that selects a functor from itself to itself: a cycle of length one."""

    class ObjectType(ObjectOfCategory):
        """No local operation."""

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        return (Fun(self, self)(lambda member: member, lambda morphism: morphism),)

    def __repr__(self):
        return "SelfLooped"


# -- rows -------------------------------------------------------------------------------------


def test_every_selected_edge_is_a_constructed_functor_and_selection_does_not_refine_it() -> None:
    """A selected edge is an object of ``Fun`` by placement; compiling its source states no property of it."""
    plain = Plain()
    (carrier,) = plain.structure_functors()

    assert is_placed(carrier, Fun)
    assert carrier.domain() is plain
    assert carrier.codomain() is Sets()
    assert not is_placed(carrier, Fun.Faithful())
    assert not is_placed(carrier, Fun.Full())
    assert not is_placed(carrier, Fun.FullyFaithful())
    assert ask(carrier.is_faithful()) is Unknown

    # Selecting the same functor again returns the retained edge, unrefined.
    assert plain.selected_functors() == (carrier,)
    assert not is_placed(carrier, Fun.Faithful())


def test_a_hom_category_of_cat_is_not_a_functor_and_supplies_no_action() -> None:
    """``Fun(C, D)`` is the category that owns construction of functors ``C -> D``, not one of them (POL-API-023)."""
    homs = Fun(Posets(), Sets())
    underlying = Posets().structure_functors()[int(0)]

    assert homs in Cat()
    assert not is_placed(homs, Fun)
    assert is_placed(underlying, Fun)
    assert underlying.domain() is homs.domain()
    assert underlying.codomain() is homs.codomain()

    # The endpoints select the hom category; they do not determine an object of it.
    with pytest.raises(AttributeError):
        homs.on_object

    # A functor exists only once both actions are supplied.
    chain = Posets().Simplex(int(2))
    constructed = homs.Faithful()(underlying.on_object, underlying.on_morphism)
    assert is_placed(constructed, Fun)
    assert constructed is not underlying
    assert constructed.on_object(chain) is underlying.on_object(chain)


def test_a_composite_retains_its_factors_and_applies_them_in_categorical_order() -> None:
    """``Cat()``'s composite names its construction: ``(second . first)(x) = second(first(x))``."""
    posets, sets = Posets(), Sets()
    underlying = posets.structure_functors()[int(0)]
    identity = Fun(posets, posets).Equivalences().identity()
    composite = Cat().compose_morphisms(underlying, identity)
    chain = posets.Simplex(int(2))
    fixed = Mor(posets)(chain, chain)(lambda point: point)

    assert composite.factors() == (identity, underlying)
    assert composite.domain() is posets
    assert composite.codomain() is sets
    assert composite.on_object(chain) is underlying.on_object(identity.on_object(chain))
    assert composite.on_morphism(fixed) is underlying.on_morphism(identity.on_morphism(fixed))
    assert composite.on_object(chain) is not chain


def test_two_functors_with_one_pair_of_endpoints_are_both_retained_and_both_applied() -> None:
    """The two projections of ``Sets() * Sets()`` share their endpoints; the endpoints select neither (POL-FUN-023)."""
    square = Cat().Products()((Sets(), Sets()))
    first, second = square.product_projection(int(0)), square.product_projection(int(1))
    left, right = Sets().Finite()((int(1), int(2))), Sets().Finite()((int(7),))
    pair = square((left, right))

    assert first is not second
    assert first.domain() is second.domain()
    assert first.codomain() is second.codomain()
    assert first.on_object(pair) is left
    assert second.on_object(pair) is right
    assert ask(first.on_object(pair).cardinality() == int(2)) is True
    assert ask(second.on_object(pair).cardinality() == int(1)) is True


def test_a_declared_functor_out_of_another_category_fails_at_construction() -> None:
    with pytest.raises(AssertionError, match="does not have domain ForeignDomain"):
        ForeignDomain()


def test_a_functor_declared_twice_fails_at_construction() -> None:
    with pytest.raises(AssertionError, match="Duplicated selects one functor twice"):
        Duplicated()


def test_a_cycle_in_the_selected_graph_fails_at_construction() -> None:
    with pytest.raises(AssertionError, match="the selected structural graph has a cycle through SelfLooped"):
        SelfLooped()


def test_the_routes_of_a_diamond_are_listed_in_declaration_order() -> None:
    """``FinitePosets()`` declares the inclusion into ``Posets()`` first, so every route through it precedes the rest."""
    source = compiler.node(FinitePosets(), Role.OBJECT)
    target = compiler.node(Sets(), Role.OBJECT)
    first_declared, second_declared = FinitePosets().structure_functors()
    found = compiler.routes(source, target)
    leading = [route[int(0)][int(0)] for route in found]

    assert len(found) > int(1)
    assert leading[int(0)] is first_declared
    assert leading == sorted(leading, key=lambda functor: int(0) if functor is first_declared else int(1))
    assert set(map(id, leading)) == {id(first_declared), id(second_declared)}
    assert all(step[int(1)] is Role.OBJECT for route in found for step in route)
    assert all(route[-int(1)][int(0)].codomain() is Sets() for route in found)


def test_a_narrowing_by_more_roots_includes_into_the_narrowing_by_fewer() -> None:
    """``D.P().Q()`` is a full subcategory of ``D.P()`` and of ``D.Q()``, so placement in it is placement in both."""
    finite = FinitePosets()
    with_bottom, with_top = finite.WithBottom(), finite.WithTop()
    both = finite.intersection((with_bottom, with_top))

    assert both is not with_bottom
    assert both is not with_top
    assert is_subcategory(both, with_bottom)
    assert is_subcategory(both, with_top)
    assert is_subcategory(both, finite)
    assert finite.intersection((with_top, with_bottom)) is both

    # The specimen is built here rather than taken from ``Posets().Simplex``: refining a
    # retained canonical object narrows it for every later reader of it.
    carrier = Sets().Finite()((int(0), int(1)))
    order = (carrier * carrier).subset_from(lambda pair: pair(int(0)) <= pair(int(1)))
    chain = Posets()(order)

    both(chain)
    assert is_placed(chain, both)
    assert is_placed(chain, with_bottom)
    assert is_placed(chain, with_top)
    assert chain in with_bottom
    assert chain in with_top
