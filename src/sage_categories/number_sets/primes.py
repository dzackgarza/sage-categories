"""``Primes``: the prime integers as the chosen subset ``ZZ.subset_from(is_prime)`` (POL-SET-008).

Primality is decided by Sage's exact ``Integer.is_prime`` at the private boundary.
The predicate receives only data that the rule of ``ZZ`` admits.

The subset inherits ``Sets().Countable()`` from ``ZZ``; Euclid's theorem establishes
the further placement in ``Sets().Infinite()`` (POL-MATH-040), and the two together
give ``#Primes = aleph_0``.
"""

from __future__ import annotations

from sage.rings.integer import Integer

from sage_categories.kernel.decisions import Decision
from sage_categories.kernel.refinement import refine
from sage_categories.number_sets.integers import ZZ
from sage_categories.sets.category import Sets
from sage_categories.sets.elements import Datum

__all__ = ["Primes"]


def _is_prime(datum: Datum) -> Decision:
    return Integer(datum).is_prime()


Primes = ZZ.subset_from(_is_prime)

# Euclid's theorem on the infinitude of primes: Mathlib
# ``Mathlib/Data/Nat/Prime/Infinite.lean:31-33``, "Euclid's theorem on the
# **infinitude of primes**.  Here given in the form: for every ``n``, there exists a
# prime number ``p >= n``", ``theorem exists_infinite_primes (n : N) : exists p, n <= p
# and Prime p``; as a statement about the set, ``Mathlib/Data/Nat/PrimeFin.lean:25-26``,
# ``theorem infinite_setOfPred_prime : { p | Prime p }.Infinite``.  Both inspected
# 2026-08-27.  Sage's ``Integer.is_prime`` admits exactly the positive primes, so this
# subset of ``ZZ`` is that set.
refine(Primes, Sets().Infinite())
