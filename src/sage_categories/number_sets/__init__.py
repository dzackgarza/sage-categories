"""The standard number sets as owned objects of ``Sets()`` (POL-SHADOW-001/002, POL-SET-004/032).

Each set is the sole object of its named-object leaf category (POL-CAT-083): a
rule-defined set placed in its established property category by the leaf's one
selected inclusion, with its exact cardinality recorded at construction.  These
names shadow Sage's inside the package universe.
"""

from sage_categories.number_sets.integers import ZZ, Integers
from sage_categories.number_sets.positive_integers import NN, PositiveIntegers
from sage_categories.number_sets.primes import Primes
from sage_categories.number_sets.rationals import QQ, Rationals
from sage_categories.number_sets.reals import RR, Reals

__all__ = ["NN", "QQ", "RR", "ZZ", "Integers", "PositiveIntegers", "Primes", "Rationals", "Reals"]
