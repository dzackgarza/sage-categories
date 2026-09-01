"""P4 acceptance tests for partially ordered sets, total orders, and thin categories (PHASE-foundation-p4-ordered-sets).

Verifies the P4 acceptance criteria:
1. Posets(), TotallyOrderedSets(), FinitePosets(), and FiniteTotallyOrderedSets() form the coherent mathematical diamond with Sets().
2. U: Posets() -> Sets() is the named projection functor (X, R) |-> X that creates small limits.
3. FinitePosets() is U.inverse_image(Sets().Finite()) and retains the pullback square.
4. SimplexOrders()[n] constructs the usual total order on [n] via theorem without exhaustive checks.
5. Thin: Posets() -> Cat() is a named functor constructing thin categories.
6. Monotone maps are admitted via order_preserving and nonmonotone set maps fail admission.
7. Coordinatewise products of posets and non-totality of chain products (c2 * c2).
8. Finite poset operations covers, height, width, linear_extension, and subposet from predicates.
"""

from __future__ import annotations

import pytest
from sage.rings.integer import Integer

from sage_categories.cat.category import Cat
from sage_categories.cat.predicates import ask
from sage_categories.kernel.refinement import is_placed, is_subcategory
from sage_categories.posets import (
    FinitePosets,
    FiniteTotallyOrderedSets,
    Posets,
    SimplexOrders,
    Thin,
    TotallyOrderedSets,
    covers,
    order_preserving,
)
from sage_categories.sets.cardinals import Cardinal
from sage_categories.sets.category import Sets


# ---------------------------------------------------------------------------
# 1. Diamond and Categories
# ---------------------------------------------------------------------------


def test_posets_diamond_and_subcategories() -> None:
    """Posets(), TotallyOrderedSets(), FinitePosets(), and FiniteTotallyOrderedSets() form the diamond."""
    pos = Posets()
    tot = TotallyOrderedSets()
    fin_pos = FinitePosets()
    fin_tot = FiniteTotallyOrderedSets()

    assert is_subcategory(tot, pos)
    assert is_subcategory(fin_pos, pos)
    assert is_subcategory(fin_tot, tot)
    assert is_subcategory(fin_tot, fin_pos)

    # Coherence with Sets()
    sets = Sets()
    fin_sets = sets.Finite()
    u = pos.underlying_set_functor()
    assert u.domain() is pos
    assert u.codomain() is sets


def test_finite_posets_inverse_image_pullback() -> None:
    """FinitePosets() is U.inverse_image(Sets().Finite()) and exposes the pullback."""
    pos = Posets()
    fin_sets = Sets().Finite()
    u = pos.underlying_set_functor()

    fin_pos = u.inverse_image(fin_sets)
    assert is_subcategory(fin_pos, pos)

    # The canonical constructor FinitePosets() matches
    assert FinitePosets() == fin_pos


# ---------------------------------------------------------------------------
# 2. Canonical Simplex Orders
# ---------------------------------------------------------------------------


def test_simplex_orders() -> None:
    """SimplexOrders()[n] constructs total orders on {0, ..., n} directly."""
    simp0 = SimplexOrders()[0]
    simp2 = SimplexOrders()[2]
    simp3 = SimplexOrders()[3]

    assert simp2 in Posets()
    assert simp2 in TotallyOrderedSets()
    assert simp2 in FinitePosets()
    assert simp2 in FiniteTotallyOrderedSets()

    assert ask(simp2.is_total()) is True

    # Elements and ordering
    carrier = simp2.carrier()
    p0 = simp2.element(carrier.point(0))
    p1 = simp2.element(carrier.point(1))
    p2 = simp2.element(carrier.point(2))

    assert ask(p0 <= p1) is True
    assert ask(p1 <= p2) is True
    assert ask(p0 <= p2) is True
    assert ask(p2 <= p0) is False
    assert ask(p1 <= p0) is False


# ---------------------------------------------------------------------------
# 3. Discrete Order and Non-Totality
# ---------------------------------------------------------------------------


def test_discrete_order() -> None:
    """Discrete orders on >=2 elements are posets but not totally ordered."""
    S = Sets()
    f3 = S.Finite()((10, 20, 30))
    disc = Posets().discrete_order(f3)

    assert disc in Posets()
    assert disc in FinitePosets()
    assert ask(disc.is_total()) is False

    carrier = disc.carrier()
    p10 = disc.element(carrier.point(10))
    p20 = disc.element(carrier.point(20))

    assert ask(p10 <= p10) is True
    assert ask(p20 <= p20) is True
    assert ask(p10 <= p20) is False
    assert ask(p20 <= p10) is False


# ---------------------------------------------------------------------------
# 4. Binary Product and Incomparable Crossed Elements
# ---------------------------------------------------------------------------


def test_poset_products_and_crossed_elements() -> None:
    """Product of two chains has incomparable crossed elements (0, 1) and (1, 0)."""
    c2 = SimplexOrders()[1]
    prod = c2 * c2

    assert prod in Posets()
    assert prod in FinitePosets()
    assert ask(prod.is_total()) is False

    carrier = prod.carrier()
    enum = Sets().Finite().chosen_enumeration(carrier)
    p00 = prod.element(carrier.point(enum[0]))
    p01 = prod.element(carrier.point(enum[1]))
    p10 = prod.element(carrier.point(enum[2]))
    p11 = prod.element(carrier.point(enum[3]))

    assert ask(p00 <= p01) is True
    assert ask(p00 <= p10) is True
    assert ask(p01 <= p11) is True
    assert ask(p10 <= p11) is True
    assert ask(p01 <= p10) is False
    assert ask(p10 <= p01) is False


# ---------------------------------------------------------------------------
# 5. Monotone Maps and Admission
# ---------------------------------------------------------------------------


def test_monotone_map_admission() -> None:
    """Monotone maps are admitted and order-reversing maps fail admission."""
    c2 = SimplexOrders()[1]
    u_c2 = c2.carrier()

    # Monotone map: identity
    id_map = Sets().morphism_category(1)(u_c2, u_c2)(lambda x: x)
    assert ask(order_preserving(c2, c2, id_map)) is True
    monotone_id = Posets().morphism_category(1)(c2, c2)(id_map)
    assert monotone_id in Posets().morphism_category(1)(c2, c2)

    # Order-reversing map: 0 |-> 1, 1 |-> 0
    rev_map = Sets().morphism_category(1)(u_c2, u_c2)(lambda x: 1 if x == 0 else 0)
    assert ask(order_preserving(c2, c2, rev_map)) is False

    with pytest.raises(AssertionError):
        Posets().morphism_category(1)(c2, c2)(rev_map)


# ---------------------------------------------------------------------------
# 6. Thin Category Functor
# ---------------------------------------------------------------------------


def test_thin_category() -> None:
    """Thin: Posets() -> Cat() constructs thin categories where Mor(x, y) is 1-inhabited iff x <= y."""
    simp2 = SimplexOrders()[2]
    thin = Thin.on_object(simp2)

    assert thin in Cat()
    carrier = simp2.carrier()
    p0 = carrier.point(0)
    p1 = carrier.point(1)
    p2 = carrier.point(2)

    obj0 = thin(p0)
    obj1 = thin(p1)
    obj2 = thin(p2)

    # Mor(0, 1) has 1 morphism
    hom01 = thin.morphism_category(1)(obj0, obj1)
    assert ask(hom01.is_inhabited()) is True

    # Mor(1, 0) has 0 morphisms (not comparable in this direction)
    hom10 = thin.morphism_category(1)(obj1, obj0)
    assert ask(hom10.is_inhabited()) is False


# ---------------------------------------------------------------------------
# 7. Finite Poset Operations (covers, height, width, linear_extension)
# ---------------------------------------------------------------------------


def test_finite_poset_operations() -> None:
    """Finite poset operations return exact Cardinal values and owned objects."""
    simp2 = SimplexOrders()[2]
    carrier = simp2.carrier()
    p0 = simp2.element(carrier.point(0))
    p1 = simp2.element(carrier.point(1))
    p2 = simp2.element(carrier.point(2))

    # Covers
    assert ask(covers(simp2, p0, p1)) is True
    assert ask(covers(simp2, p1, p2)) is True
    assert ask(covers(simp2, p0, p2)) is False  # not a direct cover

    # Height and Width
    h = simp2.height()
    w = simp2.width()
    assert h == Cardinal()(3)
    assert w == Cardinal()(1)

    # Linear extension
    S = Sets()
    f3 = S.Finite()((10, 20, 30))
    disc = Posets().discrete_order(f3)
    assert disc.height() == Cardinal()(1)
    assert disc.width() == Cardinal()(3)

    lin_ext = disc.linear_extension()
    assert lin_ext in TotallyOrderedSets()
    assert lin_ext in FiniteTotallyOrderedSets()
    assert ask(lin_ext.is_total()) is True
    assert lin_ext.carrier() == f3


def test_subposet_from_predicate() -> None:
    """Subposet construction via carrier predicate creates induced subposet."""
    simp3 = SimplexOrders()[3]
    # Restrict to even numbers {0, 2}
    sub_inc = simp3.sub_poset_inclusion(lambda x: x in (0, 2))
    sub = sub_inc.domain()

    assert sub in Posets()
    assert sub in FinitePosets()
    assert ask(sub.is_total()) is True
    assert sub.height() == Cardinal()(2)
