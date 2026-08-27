"""Cardinal arithmetic: the semiring axioms, the collapse rules, and what the continuum hypothesis decides.

Oracles, all inspected 2026-08-28: ``a + b = max(a, b)`` and ``a * b = max(a, b)`` for
infinite ``a, b`` (Mathlib ``Cardinal.add_eq_max``, ``Cardinal.mul_eq_max``); ``c ** n = c``
for infinite ``c`` and finite ``n >= 1`` (``Cardinal.power_nat_eq``).

The generalized continuum hypothesis, which this package assumes by default, decides every
infinite power: for ordinals ``a`` and ``b``, ``aleph(a) ** aleph(b) = aleph(b + 1)`` when
``a <= b + 1``, and when ``b + 1 < a`` it is ``aleph(a)`` if ``aleph(b) < cf(aleph(a))`` and
``aleph(a + 1)`` otherwise (Wikipedia, "Continuum hypothesis", section "Implications of GCH
for cardinal exponentiation", after Hayden and Kennison, *Zermelo-Fraenkel Set Theory*,
page 147).  The cofinalities those rules need are ``cf(omega_n) = aleph(n)`` for ``n >= 1``,
because ``aleph(n)`` is regular (``Cardinal.isRegular_aleph_add_one``), and
``cf(omega_omega) = cf(omega_0) = aleph0`` (``Ordinal.cof_omega``, ``Ordinal.cof_omega0``).

With the hypothesis retracted, ZFC alone decides far less: ``aleph 1 <= 2 ** aleph0``
because ``aleph 1`` is the least uncountable cardinal (``Cardinal.aleph_one_le_iff``) and
``2 ** aleph0`` is uncountable (``Cardinal.cantor'``), while neither order between
``aleph 2`` and ``2 ** aleph0`` follows, so that pair stays a formal supremum
(``specs/cardinality.md``, "Cardinal expression forms").  A power is monotone in its base
(``Cardinal.power_le_power_right``) and in its exponent (``Cardinal.power_le_power_left``),
so it distributes over the maximum that a finite supremum is.

The semiring axioms are not restated as assertions here.  ``Cardinal()`` declares its
arithmetic into ``Semirings().Commutative()`` rather than asserting associativity,
commutativity, distributivity, and the two identities one by one, and Sage's ``TestSuite``
is what checks that declaration.  The first row runs it, and names the cardinal semiring
directly because a Sage axiom suite runs on a Sage parent; every other row uses the owned
cardinal surface.
"""

import pytest
from sage.all import TestSuite

from sage_categories.all import *
from sage_categories.kernel.predicates import established, negation
from sage_categories.ordinals import omega
from sage_categories.sets.cardinals import CardinalSemiring


@pytest.fixture
def zermelo_fraenkel_only():
    """The session with the continuum hypothesis withdrawn, restored for every later row."""
    retract(generalized_continuum_hypothesis())
    yield
    assume(generalized_continuum_hypothesis())


def test_sage_checks_the_semiring_axioms_on_a_countable_and_an_uncountable_cardinal() -> None:
    semiring = CardinalSemiring()
    infinite = [value for value in semiring.some_elements() if established(negation(semiring.is_finite(value)))]

    assert len(infinite) == int(2)
    assert established(semiring.is_countable(infinite[int(0)]))
    assert established(negation(semiring.is_countable(infinite[int(1)])))
    TestSuite(semiring).run(catch=False, raise_on_failure=True)


def test_a_sum_or_product_of_infinite_cardinals_is_the_larger_one() -> None:
    cardinals = Cardinal()
    aleph1, aleph2 = cardinals.aleph(int(1)), cardinals.aleph(int(2))

    assert aleph1 + aleph2 is aleph2
    assert aleph2 + aleph1 is aleph2
    assert aleph0 + aleph1 is aleph1
    assert aleph2 * aleph1 is aleph2
    assert aleph1 * aleph1 is aleph1
    assert cardinals(int(7)) * aleph1 is aleph1
    assert cardinals(int(0)) * aleph1 is cardinals(int(0))
    assert cardinals(int(3)) + cardinals(int(4)) is cardinals(int(7))
    assert cardinals(int(3)) * cardinals(int(4)) is cardinals(int(12))


def test_the_assumed_continuum_hypothesis_decides_every_infinite_power() -> None:
    cardinals = Cardinal()
    aleph = cardinals.aleph
    aleph_omega = aleph(omega(int(0)))

    assert ask(generalized_continuum_hypothesis())
    assert cardinals(int(2)) ** aleph0 is aleph(int(1))
    assert continuum is aleph(int(1))
    assert cardinals(int(7)) ** aleph0 is aleph(int(1))
    assert aleph(int(0)) ** aleph(int(0)) is aleph(int(1))
    assert aleph(int(1)) ** aleph(int(0)) is aleph(int(1))
    assert aleph(int(2)) ** aleph(int(0)) is aleph(int(2))
    assert aleph(int(0)) ** aleph(int(2)) is aleph(int(3))
    # cf(aleph(omega)) = aleph0, which the exponent reaches, so the power is the successor.
    assert aleph_omega ** aleph(int(0)) is aleph(omega(int(0)) + int(1))
    assert aleph0 ** int(3) is aleph0
    assert cardinals(int(2)) ** int(3) is cardinals(int(8))
    assert cardinals(int(5)) ** cardinals(int(0)) is cardinals(int(1))
    assert cardinals(int(0)) ** aleph0 is cardinals(int(0))
    assert cardinals(int(1)) ** aleph0 is cardinals(int(1))


def test_retracting_the_continuum_hypothesis_restores_the_formal_powers_and_joins(zermelo_fraenkel_only) -> None:
    cardinals = Cardinal()
    two, aleph1, aleph2 = cardinals(int(2)), cardinals.aleph(int(1)), cardinals.aleph(int(2))
    power = two**aleph0
    undecided = aleph2 + power

    assert ask(generalized_continuum_hypothesis()) is Unknown
    assert power is not aleph1
    assert ask(aleph1 <= power)
    assert ask(aleph2 <= power) is Unknown
    assert ask(power <= aleph2) is Unknown
    assert ask(aleph2 == power) is Unknown
    assert ask(aleph2 <= undecided)
    assert ask(power <= undecided)
    assert ask(undecided <= aleph2) is Unknown
    assert ask(undecided.is_uncountable())
    # The hom category of the undecided pair keeps both conclusions open.
    assert ask(Mor(cardinals).Monomorphisms()(power, aleph2).is_inhabited()) is Unknown
    assert ask(Mor(cardinals).Isomorphisms()(aleph1, power).is_inhabited()) is Unknown
    # aleph1 <= 2 ** aleph0 <= sup, so the supremum absorbs it and keeps its two terms.
    assert undecided + aleph1 is undecided
    # In the exponent: 2 ** sup(a, b) = max(2 ** a, 2 ** b), which is their cardinal sum.
    assert two**undecided is (two**aleph2) + (two**power)
    # In the base: sup(a, b) ** aleph0 = max(a ** aleph0, b ** aleph0), and
    # 2 ** aleph0 <= aleph2 ** aleph0 by monotonicity in the base, so that maximum is the second.
    assert undecided**aleph0 is aleph2**aleph0
    # Cardinal.power_nat_eq applies to the maximum that the supremum is.
    assert undecided**two is undecided
