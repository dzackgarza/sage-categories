"""Owned categories with Sage confined to explicit realizations."""

from importlib.metadata import version as _distribution_version

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.morphisms import Mor
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import ask, assume
from sage_categories.number_sets import NN, QQ, RR, ZZ, Primes
from sage_categories.ordinals import Ordinals, omega0
from sage_categories.sets.cardinals import Cardinal, aleph0, continuum
from sage_categories.sets.category import Sets

__all__ = [
    "NN",
    "QQ",
    "RR",
    "ZZ",
    "Cardinal",
    "Cat",
    "Category",
    "Decision",
    "Fun",
    "Mor",
    "Ordinals",
    "Primes",
    "Sets",
    "Unknown",
    "UnknownClass",
    "__version__",
    "aleph0",
    "ask",
    "assume",
    "continuum",
    "omega0",
    "version",
]

# One source of truth. The version is declared once, in pyproject.toml, and
# read back from the installed distribution metadata rather than restated
# here, so a package built from this tree cannot disagree with itself.
__version__: str = _distribution_version("sage-categories")


def version() -> str:
    """Return the installed version of this package.

    At a Sage prompt the result prints on its own, so this is also the
    version print: ``import sage_categories; sage_categories.version()``.
    """
    return __version__
