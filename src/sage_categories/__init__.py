"""Owned categories with Sage confined to explicit realizations."""

from importlib.metadata import version as _distribution_version

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.shapes import Discrete, Thin
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import Predicate, ask, assume
from sage_categories.sets.cardinals import Cardinal, aleph0, continuum
from sage_categories.sets.category import Sets

__all__ = [
    "Cardinal",
    "Cat",
    "Category",
    "Decision",
    "Discrete",
    "Fun",
    "Mor",
    "Predicate",
    "Sets",
    "Thin",
    "Unknown",
    "UnknownClass",
    "__version__",
    "aleph0",
    "ask",
    "assume",
    "continuum",
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
