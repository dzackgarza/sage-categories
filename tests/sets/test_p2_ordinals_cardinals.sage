"""P2 acceptance tests for internal algebra, ordinals, and cardinals.

Verifies the P2 acceptance criteria:
1. Magmas(V), Monoids(V), and Semirings(C) construct internal algebraic categories.
2. Cardinal() is an executable consumer of Semirings(Cat()) and retains its semiring projections.
3. Cardinal() retains its fully faithful representative functor Cardinal() -> Sets().
4. Ordinals(), OrdinalOrder(), Cardinal(), and CardinalOrder() return exact owned categories and objects.
5. Ordinal arithmetic (natural +, natural *, ordinal_sum, ordinal_product) returns exact values.
6. Cardinal arithmetic (+, *, **, %) and order comparisons return exact owned values.
7. Aleph and InitialOrdinal order functors map between OrdinalOrder() and CardinalOrder().
"""

from sage.rings.integer import Integer

import pytest

from sage_categories.algebra import Groups, Magmas, Monoids, Semirings
from sage_categories.cat import Cat
from sage_categories.cat.predicates import Unknown, ask
from sage_categories.ordinals import OrdinalObject, OrdinalOrder, Ordinals, omega, omega0
from sage_categories.sets.cardinals import (
    Aleph,
    Cardinal,
    CardinalObject,
    CardinalOrder,
    InitialOrdinal,
    aleph0,
    continuum,
    generalized_continuum_hypothesis,
)
from sage_categories.sets.category import Sets


# ---------------------------------------------------------------------------
# 1. Internal Algebraic Categories (specs/magmas-monoids-semirings.md)
# ---------------------------------------------------------------------------


def test_magmas_category() -> None:
    """Magmas(V) constructs internal magma category with Additive and Multiplicative subcategories."""
    sets = Sets()
    M = Magmas(sets)
    assert repr(M) == "Magmas(Sets)"
    assert M.Additive() is not None
    assert M.Multiplicative() is not None
    assert M.Commutative() is not None


def test_monoids_category() -> None:
    """Monoids(V) constructs internal monoid category with structure functor to Magmas(V)."""
    sets = Sets()
    Mon = Monoids(sets)
    assert repr(Mon) == "Monoids(Sets)"
    assert Mon.Additive() is not None
    assert Mon.Multiplicative() is not None
    assert len(Mon.structure_functors()) >= 1


def test_groups_category() -> None:
    """Groups(V) constructs internal group category with structure functor to Monoids(V)."""
    sets = Sets()
    Grp = Groups(sets)
    assert repr(Grp) == "Groups(Sets)"
    assert Grp.Additive() is not None
    assert Grp.Multiplicative() is not None
    assert len(Grp.structure_functors()) >= 1


def test_semirings_category() -> None:
    """Semirings(C) constructs strict internal semiring category with two monoid projections."""
    cat = Cat()
    SR = Semirings(cat)
    assert repr(SR) == "Semirings(Cat)"
    struct_functors = SR.structure_functors()
    assert len(struct_functors) == 2


# ---------------------------------------------------------------------------
# 2. Cardinal() as Consumer of Semirings(Cat()) (specs/cardinality.md)
# ---------------------------------------------------------------------------


def test_cardinal_semiring_object() -> None:
    """Cardinal() constructs an owned strict internal semiring object in Semirings(Cat())."""
    card = Cardinal()
    semiring_obj = card.semiring_object()
    assert semiring_obj is not None
    assert semiring_obj.carrier() is card
    assert semiring_obj.zero() is card.zero()
    assert semiring_obj.one() is card.one()


def test_cardinal_representative_functor() -> None:
    """Cardinal() retains its fully faithful representative functor to Sets()."""
    card = Cardinal()
    rep_functor = card.representative_functor()
    assert rep_functor is not None
    assert rep_functor.domain() is card
    assert rep_functor.codomain() is Sets()

    # Finite representative is {0, ..., n - 1}
    c3 = card(3)
    r3 = card.representative(c3)
    assert repr(r3) == "{0, 1, 2}"

    # Zero representative is {}
    c0 = card.zero()
    r0 = card.representative(c0)
    assert repr(r0) == "{}"


# ---------------------------------------------------------------------------
# 3. Ordinals and Ordinal Arithmetic (specs/ordinals.md)
# ---------------------------------------------------------------------------


def test_ordinal_construction() -> None:
    """Ordinals() constructs exact finite and initial ordinals."""
    O = Ordinals()
    assert O(0) is O.zero()
    assert O(1) is O.one()
    assert repr(O(5)) == "5"

    w0 = omega(0)
    assert w0 is omega0
    assert repr(w0) == "ω_0"
    assert repr(omega(1)) == "ω_1"


def test_ordinal_arithmetic() -> None:
    """Ordinals support Hessenberg natural operations and ordinary operations."""
    O = Ordinals()
    a = O(3)
    b = O(4)

    # Natural operations
    assert a + b is O(7)
    assert a * b is O(12)

    # Ordinary operations
    assert a.ordinal_sum(b) is O(7)
    assert a.ordinal_product(b) is O(12)
    assert a.ordinal_power(O(2)) is O(9)

    # Infinite with finite: the ordinary sum stays symbolic and retained by expression,
    # and its equality with ω_0 is Unknown -- distinct expressions never decide
    # inequality by themselves (specs/ordinals.md, "Ordinary ordinal arithmetic").
    w = omega0
    assert repr(w + a) == "3 # ω_0" or repr(w + a) == "ω_0 # 3"
    absorbed = a.ordinal_sum(w)
    assert absorbed is O.ordinal_sum(a, w)
    assert ask(absorbed == w) is Unknown


def test_ordinal_order_category() -> None:
    """OrdinalOrder() is the thin category of the ordinal order."""
    OO = OrdinalOrder()
    assert OO is not None
    O = Ordinals()
    p1 = OO(O(2))
    p2 = OO(O(5))
    assert p1 is not None and p2 is not None

    arrow = OO.construct_morphism(p1, p2)
    assert arrow.domain() is p1
    assert arrow.codomain() is p2


# ---------------------------------------------------------------------------
# 4. Cardinals and Cardinal Arithmetic (specs/cardinality.md)
# ---------------------------------------------------------------------------


def test_cardinal_construction_and_constants() -> None:
    """Cardinal() constructs exact finite and aleph cardinals."""
    C = Cardinal()
    assert C(0) is C.zero()
    assert C(1) is C.one()
    assert repr(C(4)) == "4"
    assert repr(aleph0) == "ℵ_0"
    assert continuum is not None


def test_cardinal_arithmetic() -> None:
    """Cardinals support exact finite and infinite arithmetic."""
    C = Cardinal()
    c2 = C(2)
    c3 = C(3)

    # Finite arithmetic
    assert c2 + c3 is C(5)
    assert c2 * c3 is C(6)
    assert c2 ** c3 is C(8)
    assert C(7) % 3 is C(1)

    # Infinite arithmetic
    assert aleph0 + c3 is aleph0
    assert aleph0 * c3 is aleph0
    assert aleph0 + aleph0 is aleph0
    assert aleph0 * aleph0 is aleph0


def test_cardinal_order_category() -> None:
    """CardinalOrder() is the thin category of the cardinal order."""
    CO = CardinalOrder()
    assert CO is not None
    C = Cardinal()
    p1 = CO(C(2))
    p2 = CO(C(5))
    assert p1 is not None and p2 is not None

    arrow = CO.construct_morphism(p1, p2)
    assert arrow.domain() is p1
    assert arrow.codomain() is p2


# ---------------------------------------------------------------------------
# 5. Order Functors Aleph and InitialOrdinal (specs/cardinality.md)
# ---------------------------------------------------------------------------


def test_order_functors() -> None:
    """Aleph and InitialOrdinal map between OrdinalOrder() and CardinalOrder()."""
    OO = OrdinalOrder()
    CO = CardinalOrder()
    O = Ordinals()
    C = Cardinal()

    # Aleph: OrdinalOrder() -> CardinalOrder()
    assert Aleph.domain() is OO
    assert Aleph.codomain() is CO

    alpha_pt = OO(O.zero())
    aleph_img = Aleph.on_object(alpha_pt)
    assert CO.object_point(aleph_img) is aleph0

    # InitialOrdinal: CardinalOrder() -> OrdinalOrder()
    assert InitialOrdinal.domain() is CO
    assert InitialOrdinal.codomain() is OO

    kappa_pt = CO(aleph0)
    omega_img = InitialOrdinal.on_object(kappa_pt)
    assert OO.object_point(omega_img) is omega0

    # Monotonicity on morphisms
    alpha1 = OO(O(0))
    alpha2 = OO(O(1))
    arrow_o = OO.construct_morphism(alpha1, alpha2)
    arrow_c = Aleph.on_morphism(arrow_o)
    assert arrow_c.domain() is Aleph.on_object(alpha1)
    assert arrow_c.codomain() is Aleph.on_object(alpha2)


# ---------------------------------------------------------------------------
# 6. Order Comparison Predicates (specs/cardinality.md, specs/ordinals.md)
# ---------------------------------------------------------------------------


def test_cardinal_and_ordinal_comparisons() -> None:
    """Comparisons return SymPy propositions evaluated by ask()."""
    C = Cardinal()
    O = Ordinals()

    assert ask(C(2) <= C(5)) is True
    assert ask(C(5) <= C(2)) is False
    assert ask(C(2) < C(5)) is True
    assert ask(aleph0 <= continuum) is True
    assert ask(C(100) < aleph0) is True

    assert ask(O(2) <= O(5)) is True
    assert ask(O(5) <= O(2)) is False
    assert ask(O(2) < O(5)) is True
    assert ask(O(100) < omega0) is True
