"""Composition of functors, the categories the binary operators construct in, and property narrowings.

Oracles: the definition of composition (``(G . F)(x) = G(F(x))``, in categorical
order); the definition of a full subcategory (a narrowing by more roots is a full
subcategory of the narrowing by fewer, ``specs/functor.md``, "Inclusion functors",
POL-CAT-084); the least common category of two operands along subcategory
monomorphisms (D02).
"""

import pytest

from sage_categories.all import *
from sage_categories.kernel.refinement import common_ancestor, is_placed, is_subcategory




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
    underlying_set = underlying.on_object(chain)
    fixed = Mor(posets)(chain, chain)(lambda point: point)

    assert composite.factors() == (underlying, Discrete)
    assert composite.domain() is posets
    assert composite.codomain() is Cat()
    assert composite.on_object(chain) is Discrete.on_object(underlying.on_object(chain))
    assert composite.on_morphism(fixed) is Discrete.on_morphism(underlying.on_morphism(fixed))

    shape = composite.on_object(chain)
    vertex = shape(underlying_set.point(int(1)))
    assert vertex in shape
    assert ask(vertex.point() == underlying_set.point(int(1)))
    assert ask(shape.object_set().cardinality() == int(3))


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
    assert ask(first.on_object(pair).cardinality() == int(2))
    assert ask(second.on_object(pair).cardinality() == int(1))


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
    assert ask(second_declared.on_object(chain).cardinality() == int(3))


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
    assert ask((finite * other).cardinality() == int(6))
    assert ask((finite + other).cardinality() == int(5))
    assert ask((other ** finite).cardinality() == int(8))


def test_a_poset_and_a_set_have_no_common_ancestor_and_do_not_combine() -> None:
    """``U: Posets() -> Sets()`` is not an monomorphism, so the two categories meet nowhere (POL-FUN-027)."""
    chain = Posets().Simplex(int(2))
    members = Sets().Finite()((int(0), int(1)))

    assert not is_subcategory(chain.category(), Sets())
    assert not is_subcategory(members.category(), Posets())
    for combine in (lambda: chain * members, lambda: chain + members, lambda: members ** chain):
        with pytest.raises(AssertionError):
            combine()


def test_star_on_a_morphism_is_composition_and_the_product_of_morphisms_is_named() -> None:
    """``*`` carries one meaning on the morphism role; the product of two objects of ``Mor(C)`` has no operator (D02)."""
    chain = Posets().Simplex(int(2))
    pair = Posets().Simplex(int(1))
    collapse = Mor(Posets())(chain, pair)(lambda datum: min(datum, int(1)))
    include = Mor(Posets())(pair, chain)(lambda datum: datum)

    composite = collapse * include
    assert composite.domain() is pair
    assert composite.codomain() is pair
    assert ask(composite == pair.identity())
    assert (include * collapse).domain() is chain

    # The product of the two morphisms is the product of two objects of ``Mor(C)``.
    # It is constructed by naming that category, and ``Mor(Posets())`` declares no
    # such construction: the refusal comes from the construction family, not from a
    # missing operator.
    morphisms = Mor(Posets())
    assert morphisms.Products() is not Posets().Products()
    with pytest.raises(AssertionError):
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
    members = Sets().Finite()((int(0), int(1)))
    order = (members * members).subset_from(lambda pair: pair(int(0)) <= pair(int(1)))
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
    members = Sets().Finite()((int(0), int(1)))
    order = (members * members).subset_from(lambda pair: pair(int(0)) <= pair(int(1)))
    chain = Posets()(order)

    # Compile the morphism property classes before narrowing, so the narrowing is
    # constructed after them: that is the order in which the linearization is hard.
    identity = chain.identity()
    assert identity in Mor(Posets()).Automorphisms()
    finite.intersection((finite.WithBottom(), finite.WithTop()))(chain)

    fixed = Mor(Posets())(chain, chain)(lambda point: point)
    assert ask(fixed * fixed == identity)
    assert (fixed * fixed).domain() is chain
    assert identity.inverse() is identity
    assert ask(chain.cardinality() == int(2))


def test_a_narrowed_object_composes_a_retracted_pair_through_the_isomorphism_categories() -> None:
    """The compiled class of a narrowing reached through several morphism properties.

    A retraction places its composites in the isomorphism and endomorphism categories
    of the narrowing, which is the node with the most morphism-property ancestors.
    """
    finite = FinitePosets()
    members = Sets().Finite()((int(0), int(1)))
    order = (members * members).subset_from(lambda pair: pair(int(0)) <= pair(int(1)))
    chain = Posets()(order)
    single = Sets().Finite()((int(0),))
    point = Posets()((single * single).subset_from(lambda pair: True))

    collapse = Mor(Posets())(chain, point)(lambda datum: int(0))
    include = Mor(Posets())(point, chain)(lambda datum: int(0))
    assert ask(collapse * include == point.identity())
    assert chain.identity() in Mor(Posets()).Automorphisms()

    finite.intersection((finite.WithBottom(), finite.WithTop()))(chain)

    assert not ask(include * collapse == chain.identity())
    assert chain.identity().inverse() is chain.identity()
