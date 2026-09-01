"""P5 acceptance tests for algebraic families (PHASE-foundation-p5-algebraic-families).

Verifies the P5 acceptance criteria:
1. Magmas(V), Monoids(V), Groups(V), Semirings(C), and Rings(C) construct the algebraic families for any ambient category.
2. Magmas(V).product_projection(0) forgets multiplication and is the sole structure functor.
3. Monoids(V).to_magmas() forgets the unit morphism and associativity.
4. Groups(V).to_monoids() forgets the inversion morphism.
5. Semirings(C) projects to additive commutative monoids and multiplicative monoids.
6. Rings(C) is the pullback of Semirings(C) and Groups(C).Additive().Commutative() over Monoids(C).Additive().Commutative(), retaining both projections.
7. The infinite-cyclic group Z is constructed as a projective generator in Groups(Sets()).
8. Finite group presentations retain generators, relations, evaluation morphism, and coequalizer data.
"""

from __future__ import annotations

import pytest
from sage.rings.integer import Integer

from sage_categories.algebra import (
    GroupPresentation,
    Groups,
    Magmas,
    Monoids,
    Rings,
    Semirings,
)
from sage_categories.cat.category import Cat
from sage_categories.sets.category import Sets


# ---------------------------------------------------------------------------
# 1. Magmas and Product Projection
# ---------------------------------------------------------------------------


def test_magmas_construction_and_structure_functors() -> None:
    """Magmas(V) constructs magma objects and retains product_projection(0)."""
    S = Sets()
    M = Magmas(S)
    assert M.ambient() is S


    # Carrier and multiplication
    carrier = S.Simplex(2)
    square = carrier * carrier
    mult = S.morphism_category(1)(square, carrier)(lambda fam: fam(0))
    magma = M(carrier, mult)

    assert magma.carrier() is carrier
    assert magma.multiplication() is mult

    # Structure functors
    struct = M.structure_functors()
    assert len(struct) == 1
    proj0 = M.product_projection(0)
    assert struct[0] == proj0

    # Projecting magma object yields the carrier
    assert proj0.on_object(magma) is carrier

    # Subcategories
    assert M.Additive() is not None
    assert M.Multiplicative() is not None
    assert M.Commutative() is not None


# ---------------------------------------------------------------------------
# 2. Monoids and Magma Forgetting Functor
# ---------------------------------------------------------------------------


def test_monoids_construction_and_to_magmas() -> None:
    """Monoids(V) constructs monoid objects and retains to_magmas()."""
    S = Sets()
    Mon = Monoids(S)
    assert Mon.ambient() is S

    carrier = S.Simplex(2)
    square = carrier * carrier
    mult = S.morphism_category(1)(square, carrier)(lambda fam: fam(0))
    unit = S.morphism_category(1)(S.Terminal(), carrier)(lambda _: 0)

    monoid = Mon(carrier, mult, unit)
    assert monoid.carrier() is carrier
    assert monoid.multiplication() is mult
    assert monoid.unit_morphism() is unit
    assert monoid.zero() is unit
    assert monoid.one() is unit

    # to_magmas structure functor
    struct = Mon.structure_functors()
    assert len(struct) == 1
    to_mag = Mon.to_magmas()
    assert struct[0] == to_mag

    magma = to_mag.on_object(monoid)
    assert magma.carrier() is carrier
    assert magma.multiplication() is mult

    # Subcategories
    assert Mon.Additive() is not None
    assert Mon.Multiplicative() is not None
    assert Mon.Additive().Commutative() is not None
    assert Mon.Multiplicative().Commutative() is not None


# ---------------------------------------------------------------------------
# 3. Groups and Monoid Forgetting Functor
# ---------------------------------------------------------------------------


def test_groups_construction_and_to_monoids() -> None:
    """Groups(V) constructs group objects and retains to_monoids()."""
    S = Sets()
    Grp = Groups(S)
    assert Grp.ambient() is S

    carrier = S.Simplex(2)
    square = carrier * carrier
    mult = S.morphism_category(1)(square, carrier)(lambda fam: fam(0))
    unit = S.morphism_category(1)(S.Terminal(), carrier)(lambda _: 0)
    inv = S.morphism_category(1)(carrier, carrier)(lambda x: x)

    grp = Grp(carrier, mult, unit, inv)
    assert grp.carrier() is carrier
    assert grp.multiplication() is mult
    assert grp.unit_morphism() is unit
    assert grp.inversion() is inv

    # to_monoids structure functor
    struct = Grp.structure_functors()
    assert len(struct) == 1
    to_mon = Grp.to_monoids()
    assert struct[0] == to_mon

    mon = to_mon.on_object(grp)
    assert mon.carrier() is carrier
    assert mon.multiplication() is mult
    assert mon.unit_morphism() is unit

    # Subcategories
    assert Grp.Additive() is not None
    assert Grp.Multiplicative() is not None


# ---------------------------------------------------------------------------
# 4. Infinite-Cyclic Projective Generator and Group Presentations
# ---------------------------------------------------------------------------


def test_infinite_cyclic_generator_and_presentation() -> None:
    """Groups(Sets()) constructs Z and finite presentations with coequalizer data."""
    Grp = Groups(Sets())
    Z = Grp.infinite_cyclic()

    assert Z in Grp
    assert Z.carrier() is not None
    assert Z.multiplication() is not None
    assert Z.unit_morphism() is not None
    assert Z.inversion() is not None

    # Finite group presentation: <a, b | a^2, b^2, (ab)^2>
    pres = Grp.presentation(("a", "b"), ("a^2", "b^2", "(ab)^2"))
    assert isinstance(pres, GroupPresentation)
    assert pres.generators == ("a", "b")
    assert pres.relations == ("a^2", "b^2", "(ab)^2")
    assert pres.presented_group in Grp
    assert pres.free_group_on_generators in Grp
    assert pres.free_group_on_relations in Grp

    # Coequalizer presentation data
    iota1, iota2, eval_map = pres.coequalizer_presentation()
    assert iota1.domain() is pres.free_group_on_relations
    assert iota1.codomain() is pres.free_group_on_generators
    assert iota2.domain() is pres.free_group_on_relations
    assert iota2.codomain() is pres.free_group_on_generators
    assert eval_map.domain() is pres.free_group_on_generators
    assert eval_map.codomain() is pres.presented_group


# ---------------------------------------------------------------------------
# 5. Semirings and Projections
# ---------------------------------------------------------------------------


def test_semirings_projections() -> None:
    """Semirings(C) projects to additive commutative and multiplicative monoids."""
    S = Sets()
    Semi = Semirings(S)
    assert Semi.ambient() is S

    carrier = S.Simplex(2)
    square = carrier * carrier
    add = S.morphism_category(1)(square, carrier)(lambda fam: fam(0))
    zero = S.morphism_category(1)(S.Terminal(), carrier)(lambda _: 0)
    mult = S.morphism_category(1)(square, carrier)(lambda fam: fam(0))
    one = S.morphism_category(1)(S.Terminal(), carrier)(lambda _: 1)

    semi = Semi(carrier, add, zero, mult, one)
    assert semi.carrier() is carrier
    assert semi.addition() is add
    assert semi.zero() is zero
    assert semi.multiplication() is mult
    assert semi.one() is one

    # Structure functors
    struct = Semi.structure_functors()
    assert len(struct) == 2
    proj0 = Semi.product_projection(0)
    proj1 = Semi.product_projection(1)
    assert struct[0] == proj0
    assert struct[1] == proj1

    add_mon = proj0.on_object(semi)
    assert add_mon.carrier() is carrier
    assert add_mon.multiplication() is add
    assert add_mon.unit_morphism() is zero

    mul_mon = proj1.on_object(semi)
    assert mul_mon.carrier() is carrier
    assert mul_mon.multiplication() is mult
    assert mul_mon.unit_morphism() is one


# ---------------------------------------------------------------------------
# 6. Rings and Pullback Projections
# ---------------------------------------------------------------------------


def test_rings_pullback_projections() -> None:
    """Rings(C) retains both semiring and additive group projections."""
    S = Sets()
    Rng = Rings(S)
    assert Rng.ambient() is S

    carrier = S.Simplex(2)
    square = carrier * carrier
    add = S.morphism_category(1)(square, carrier)(lambda fam: fam(0))
    zero = S.morphism_category(1)(S.Terminal(), carrier)(lambda _: 0)
    mult = S.morphism_category(1)(square, carrier)(lambda fam: fam(0))
    one = S.morphism_category(1)(S.Terminal(), carrier)(lambda _: 1)
    inv = S.morphism_category(1)(carrier, carrier)(lambda x: x)

    ring = Rng(carrier, add, zero, mult, one, inv)
    assert ring.carrier() is carrier
    assert ring.addition() is add
    assert ring.zero() is zero
    assert ring.multiplication() is mult
    assert ring.one() is one
    assert ring.inversion() is inv

    # Pullback structure functors
    struct = Rng.structure_functors()
    assert len(struct) == 2
    proj0 = Rng.product_projection(0)
    proj1 = Rng.product_projection(1)
    assert struct[0] == proj0
    assert struct[1] == proj1

    semi = proj0.on_object(ring)
    assert semi.carrier() is carrier
    assert semi.addition() is add
    assert semi.zero() is zero
    assert semi.multiplication() is mult
    assert semi.one() is one

    grp = proj1.on_object(ring)
    assert grp.carrier() is carrier
    assert grp.multiplication() is add
    assert grp.unit_morphism() is zero
    assert grp.inversion() is inv

    # Commutative subcategory
    assert Rng.Commutative() is not None
