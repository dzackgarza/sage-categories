"""Owned categories with Sage confined to explicit realizations.

This package is the kernel: ``Cat()``, functors, the ``Mor(n, C)`` tower, the shapes,
the predicate boundary, and the categories ``Cat`` declares.  Importing it loads no
leaf, because information flows from the kernel into the leaves and never back (D81).
``sage_categories.all`` is the import surface for the whole owned universe.
"""

from importlib.metadata import version as _distribution_version

from sage_categories.cat.category import Category
from sage_categories.cat.declarations import (
    NN,
    ZZ,
    MagmaObjects,
    MonoidObjects,
    Posets,
    RingObjects,
    SemiringObjects,
    Sets,
    TotallyOrderedSets,
    omega,
)
from sage_categories.cat.functors import Cat, Fun
from sage_categories.cat.morphisms import Mor
from sage_categories.cat.shapes import Discrete, Thin
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import Predicate, ask, assume, retract

__all__ = [
    "NN",
    "ZZ",
    "Cat",
    "Category",
    "Decision",
    "Discrete",
    "Fun",
    "MagmaObjects",
    "Mor",
    "MonoidObjects",
    "Posets",
    "Predicate",
    "RingObjects",
    "SemiringObjects",
    "Sets",
    "Thin",
    "TotallyOrderedSets",
    "Unknown",
    "UnknownClass",
    "__version__",
    "ask",
    "assume",
    "omega",
    "retract",
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
