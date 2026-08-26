"""``Primes``: the prime integers as the chosen subset ``ZZ.subset_from(is_prime)`` (POL-SET-008).

Primality is decided by Sage's exact ``Integer.is_prime`` at the private boundary.
The predicate receives only data that the rule of ``ZZ`` admits.
"""

from __future__ import annotations

from sage.rings.integer import Integer

from sage_categories.kernel.decisions import Decision
from sage_categories.number_sets.integers import ZZ
from sage_categories.sets.elements import Datum

__all__ = ["Primes"]


def _is_prime(datum: Datum) -> Decision:
    return Integer(datum).is_prime()


Primes = ZZ.subset_from(_is_prime)
