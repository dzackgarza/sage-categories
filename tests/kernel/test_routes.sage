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

from dataclasses import dataclass

import pytest

from sage_categories.all import *
from sage_categories.kernel.construction import retained_morphism_input, retained_object_input
from sage_categories.kernel.refinement import common_ancestor, is_placed, is_subcategory
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory


@dataclass(eq=False, slots=True)
class CarrierData:
    """The local datum of an object carrying one set."""

    carrier: object


@dataclass(frozen=True, eq=False, slots=True)
class CarrierMapData:
    """The local datum of a morphism carrying one set map."""

    set_map: object


class Plain(Category):
    """A leaf whose one selected functor is a plain functor: no declared property."""

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
            underlying = Fun(self, Sets())(lambda member: member.carrier(), lambda morphism: morphism.underlying_map())
            underlying.retain_object_constructor_conversion(lambda source: retained_object_input(source.datum.carrier))
            underlying.retain_morphism_constructor_conversion(lambda source: retained_morphism_input(source.datum.set_map))
            self._selected["carrier"] = underlying
        return (self._selected["carrier"],)

    def __call__(self, carrier):
        return self.ObjectType(self, CarrierData(carrier))

    def __repr__(self):
        return "Plain"


class ForeignDomain(Category):
    """A leaf whose declared entry is a functor out of another category."""

    def structure_functors(self):
        return (Posets().structure_functors()[int(0)],)

    def __repr__(self):
        return "ForeignDomain"


class Duplicated(Category):
    """A leaf that declares one functor twice."""

    def structure_functors(self):
        monomorphism = Fun(self, Sets()).Monomorphisms().Isofibrations().Full()()
        return (monomorphism, monomorphism)

    def __repr__(self):
        return "Duplicated"


class SelfLooped(Category):
    """A leaf that selects a functor from itself to itself: a cycle of length one."""

    def structure_functors(self):
        return (Fun(self, self).Equivalences().identity(),)

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
    """``Cat()``'s composite names its construction: ``(second . first)(x) = second(first(x))``.

    Neither factor is an identity: ``U: Posets() -> Sets()`` then ``Discrete: Sets() -> Cat()``.
    The image of the chain is therefore the discrete category on the three points of its
    underlying set, which a composite that applied only one of its factors cannot return.
    """
    posets = Posets()
    underlying = posets.structure_functors()[int(0)]
    composite = Cat().compose_morphisms(Discrete, underlying)
    chain = posets.Simplex(int(2))
    carrier = underlying.on_object(chain)
    fixed = Mor(posets)(chain, chain)(lambda point: point)

    assert composite.factors() == (underlying, Discrete)
    assert composite.domain() is posets
    assert composite.codomain() is Cat()
    assert composite.on_object(chain) is Discrete.on_object(underlying.on_object(chain))
    assert composite.on_morphism(fixed) is Discrete.on_morphism(underlying.on_morphism(fixed))

    shape = composite.on_object(chain)
    vertex = shape(carrier.point(int(1)))
    assert vertex in shape
    assert ask(vertex.point() == carrier.point(int(1))) is True
    assert ask(shape.object_set().cardinality() == int(3)) is True


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


def test_the_first_declared_functor_of_a_diamond_decides_the_ambient_category() -> None:
    """``FinitePosets()`` declares the monomorphism into ``Posets()`` first, so ``Posets()`` is its ambient (POL-CAT-016, POL-FUN-027).

    Both declared functors of the diamond reach ``Sets()``, and the second reaches it in
    one step where the first needs two.  The ambient is the codomain of the first
    declared subcategory monomorphism, so it is ``Posets()``.  The second functor is faithful
    and not an monomorphism: it places nothing and still acts.
    """
    finite_posets = FinitePosets()
    first_declared, second_declared = finite_posets.structure_functors()
    chain = Posets().Simplex(int(2))

    assert first_declared.codomain() is Posets()
    assert second_declared.codomain() is Sets().Finite()
    assert finite_posets.ambient() is Posets()
    assert Sets().Finite().ambient() is Sets()

    assert chain in finite_posets
    assert chain in Posets()
    assert chain not in Sets().Finite()
    assert first_declared.on_object(chain) is chain
    assert second_declared.on_object(chain) in Sets().Finite()
    assert ask(second_declared.on_object(chain).cardinality() == int(3)) is True


def test_the_binary_operators_construct_in_the_least_common_ancestor() -> None:
    """The operand precondition is a least common ancestor along subcategory monomorphisms (D02)."""
    finite = Sets().Finite()((int(0), int(1), int(2)))
    other = Sets().Finite()((int(7), int(8)))

    # A finite set and a countable set meet at ``Sets().Countable()``, whose
    # construction family is that of ``Sets()``: the product is owned by ``Sets()``.
    assert common_ancestor(finite.category(), QQ.category()) is Sets().Countable()
    assert Sets().Countable().Products() is Sets().Products()
    product = finite * QQ
    assert product in Sets().Products()
    assert product.product_projection(int(0)).codomain() is finite
    assert product.product_projection(int(1)).codomain() is QQ

    # Two finite sets combine in the narrowest category that receives both.
    assert common_ancestor(finite.category(), other.category()) is Sets().Finite()
    assert (finite * other) is Sets().Finite().Products()((finite, other))
    assert (finite + other) is Sets().Finite().Coproducts()((finite, other))
    assert (other ** finite) is Sets().Finite().exponential(finite, other)
    assert ask((finite * other).cardinality() == int(6)) is True
    assert ask((finite + other).cardinality() == int(5)) is True
    assert ask((other ** finite).cardinality() == int(8)) is True


def test_a_poset_and_a_set_have_no_common_ancestor_and_do_not_combine() -> None:
    """``U: Posets() -> Sets()`` is not an monomorphism, so the two categories meet nowhere (POL-FUN-027)."""
    chain = Posets().Simplex(int(2))
    carrier = Sets().Finite()((int(0), int(1)))

    assert not is_subcategory(chain.category(), Sets())
    assert not is_subcategory(carrier.category(), Posets())
    for combine in (lambda: chain * carrier, lambda: chain + carrier, lambda: carrier ** chain):
        with pytest.raises(AssertionError, match="have no least common category along subcategory monomorphisms"):
            combine()

    message = ""
    try:
        chain * carrier
    except AssertionError as rejected:
        message = str(rejected)
    assert repr(chain.category()) in message
    assert repr(carrier.category()) in message
    assert "Posets" in message
    assert "Sets" in message


def test_star_on_a_morphism_is_composition_and_the_product_of_morphisms_is_named() -> None:
    """``*`` carries one meaning on the morphism role; the product of two objects of ``Mor(C)`` has no operator (D02)."""
    chain = Posets().Simplex(int(2))
    pair = Posets().Simplex(int(1))
    collapse = Mor(Posets())(chain, pair)(lambda datum: min(datum, int(1)))
    include = Mor(Posets())(pair, chain)(lambda datum: datum)

    composite = collapse * include
    assert composite.domain() is pair
    assert composite.codomain() is pair
    assert ask(composite == pair.identity()) is True
    assert (include * collapse).domain() is chain

    # The product of the two morphisms is the product of two objects of ``Mor(C)``.
    # It is constructed by naming that category, and ``Mor(Posets())`` declares no
    # such construction: the refusal comes from the construction family, not from a
    # missing operator.
    morphisms = Mor(Posets())
    assert morphisms.Products() is not Posets().Products()
    with pytest.raises(AssertionError, match="owns no .*-limit construction"):
        morphisms.Products()((collapse, include))


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


def test_an_object_narrowed_by_two_independent_roots_still_composes_its_morphisms() -> None:
    """The compiled class of a narrowing by independent roots is built from Sage's controlled C3 bases."""
    finite = FinitePosets()
    carrier = Sets().Finite()((int(0), int(1)))
    order = (carrier * carrier).subset_from(lambda pair: pair(int(0)) <= pair(int(1)))
    chain = Posets()(order)

    # Compile the morphism property classes before narrowing, so the narrowing is
    # constructed after them: that is the order in which the linearization is hard.
    identity = chain.identity()
    assert identity in Mor(Posets()).Automorphisms()
    finite.intersection((finite.WithBottom(), finite.WithTop()))(chain)

    fixed = Mor(Posets())(chain, chain)(lambda point: point)
    assert ask(fixed * fixed == identity) is True
    assert (fixed * fixed).domain() is chain
    assert identity.inverse() is identity
    assert ask(chain.cardinality() == int(2)) is True


def test_a_narrowed_object_composes_a_retracted_pair_through_the_isomorphism_categories() -> None:
    """The compiled class of a narrowing reached through several morphism properties.

    A retraction places its composites in the isomorphism and endomorphism categories
    of the narrowing, which is the node with the most morphism-property ancestors.
    """
    finite = FinitePosets()
    carrier = Sets().Finite()((int(0), int(1)))
    order = (carrier * carrier).subset_from(lambda pair: pair(int(0)) <= pair(int(1)))
    chain = Posets()(order)
    single = Sets().Finite()((int(0),))
    point = Posets()((single * single).subset_from(lambda pair: True))

    collapse = Mor(Posets())(chain, point)(lambda datum: int(0))
    include = Mor(Posets())(point, chain)(lambda datum: int(0))
    assert ask(collapse * include == point.identity()) is True
    assert chain.identity() in Mor(Posets()).Automorphisms()

    finite.intersection((finite.WithBottom(), finite.WithTop()))(chain)

    assert ask(include * collapse == chain.identity()) is False
    assert chain.identity().inverse() is chain.identity()
