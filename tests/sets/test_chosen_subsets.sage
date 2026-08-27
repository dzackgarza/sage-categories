"""Chosen subsets: ``X.subset_from(predicate)`` retains its inclusion and decides membership.

Oracles: the definition of a subset ``{x in X : P(x)}`` and of its inclusion;
monomorphisms of ``Sets()`` are the injective maps and an inclusion is injective
(Mathlib ``CategoryTheory.mono_iff_injective``, ``Set.inclusion_injective``); a
subset of a countable set is countable (Mathlib ``Set.Countable.mono``) and of a
finite set finite (``Set.Finite.subset``); Euclid's theorem on the infinitude of
primes (Mathlib ``Nat.exists_infinite_primes``,
``Mathlib/Data/Nat/Prime/Infinite.lean:31-33``; as a statement about the set,
``Nat.infinite_setOfPred_prime``, ``Mathlib/Data/Nat/PrimeFin.lean:25-26``), with
``#X = aleph_0`` for a countably infinite ``X`` (Mathlib ``Cardinal.mk_eq_aleph0``);
POL-ASSUME-004 for ``Unknown``
cardinality; the Kleene conjunction of decisions (POL-MATH-034) for ``Unknown``
membership; the characteristic function of a subset takes ``1`` exactly on its
members (nLab "subobject classifier" in ``Set``; Mathlib ``Set.mem_iff_boolIndicator``).
"""

import pytest

from sage_categories.all import *


def test_a_predicate_subset_of_the_integers_retains_its_inclusion() -> None:
    even = ZZ.subset_from(lambda n: n % 2 == 0)
    inclusion = even.monomorphism()

    assert inclusion in Mor(Sets())(even, ZZ).Monomorphisms()
    assert inclusion in Mor(Sets()).Monomorphisms()
    assert inclusion.domain() is even
    assert inclusion.codomain() is ZZ
    assert even.underlying_set() is ZZ
    assert even in Sets()
    assert even in Sets().Countable()

    assert ZZ(4) in even
    assert ZZ(3) not in even
    assert ask(inclusion(ZZ(4)) == ZZ(4)) is True
    assert even.cardinality() is Unknown
    assert ask(even.is_countable()) is True
    assert ask(even.is_finite()) is Unknown


def test_the_primes_decide_membership_exactly() -> None:
    assert ZZ(7) in Primes
    assert ZZ(9) not in Primes
    assert ZZ(2) in Primes
    assert ZZ(-7) not in Primes
    assert QQ(1 / 2) not in Primes
    assert Primes.underlying_set() is ZZ
    assert Primes.monomorphism() in Mor(Sets())(Primes, ZZ).Monomorphisms()
    assert Primes in Sets().Countable()
    assert Primes in Sets().Infinite()
    assert Primes.cardinality() is aleph0
    assert ask(Primes.is_infinite()) is True
    assert ask(Primes.is_finite()) is False


def test_an_undecided_predicate_keeps_membership_unknown() -> None:
    undecided = ZZ.subset_from(lambda n: Unknown)

    assert ask(undecided.membership_proposition(ZZ(0))) is Unknown
    assert ask(undecided.membership_proposition(QQ(1 / 2))) is False
    assert undecided.cardinality() is Unknown
    assert undecided in Sets().Countable()


def test_a_subset_of_a_finite_enumerated_set_has_the_exact_count() -> None:
    triple = Sets().Finite()((int(1), int(2), int(3)))
    odd = triple.subset_from(lambda datum: datum % int(2) == int(1))

    assert odd in Sets().Finite()
    assert ask(odd.cardinality() == int(2)) is True
    assert odd.underlying_set() is triple
    assert odd.monomorphism() in Mor(Sets())(odd, triple).Monomorphisms()
    assert triple.point(int(1)) in odd
    assert triple.point(int(2)) not in odd
    points = list(odd)
    assert len(points) == int(2)
    assert all(any(ask(point == odd.point(datum)) is True for point in points) for datum in (int(1), int(3)))
    assert ask(odd.monomorphism()(odd.point(int(3))) == triple.point(int(3))) is True
    assert odd.monomorphism()(odd.point(int(3))).parent() is triple

    undecided = triple.subset_from(lambda datum: Unknown)
    assert undecided in Sets().Finite()
    assert undecided.cardinality() is Unknown
    assert ask(undecided.membership_proposition(triple.point(int(1)))) is Unknown


def test_every_chosen_subset_has_a_characteristic_morphism_into_two() -> None:
    two = Sets().Simplex(int(1))
    even = ZZ.subset_from(lambda n: n % 2 == 0)
    characteristic = even.characteristic_morphism()

    assert characteristic in Mor(Sets())(ZZ, two)
    assert characteristic.domain() is ZZ and characteristic.codomain() is two
    assert ask(characteristic(ZZ(4)) == two.point(int(1))) is True
    assert ask(characteristic(ZZ(3)) == two.point(int(0))) is True
    assert Sets().name_of(characteristic) in two ** ZZ
    assert Primes.characteristic_morphism() in Mor(Sets())(ZZ, two)
    assert ask(Primes.characteristic_morphism()(ZZ(7)) == two.point(int(1))) is True

    undecided = ZZ.subset_from(lambda n: Unknown)
    with pytest.raises(AssertionError):
        undecided.characteristic_morphism()(ZZ(0))
