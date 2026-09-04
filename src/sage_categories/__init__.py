"""Owned categories with Sage confined to explicit realizations.

Importing this package loads ``Cat``: ``Cat()``, functors, the ``Mor(n, C)`` tower, the
shapes, the predicate boundary, and the categories ``Cat`` declares.  It loads no leaf,
because information flows from ``Cat`` into the leaves and never back (D81).
``sage_categories.all`` is the import surface for the whole owned universe.

The four layers, in the order of dependence D173 and D175 fix: the kernel
(``sage_categories.kernel``), which is engineering and states no mathematics; ``Cat``
(``sage_categories.cat``), which owns the mathematics every category shares;
``cat_kernel``, the work that needs both; then the leaves.
"""

from importlib.metadata import version as _distribution_version

from sage_categories import cat_kernel as _cat_kernel

# ``cat_kernel`` is downstream of both layers below it (D175), so neither imports it and
# this package installs it.  Before ``Cat`` is loaded: the kernel asks whether a functor
# carries placement and inheritance while ``Fun`` is still building its own property
# categories, and each reader reaches ``Fun`` when it is called.
_cat_kernel.install()
del _cat_kernel

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
from sage_categories.cat.adjunctions import Adjunctions, Equivalences
from sage_categories.cat.cones import cones as Cones, limit_cones as LimitCones
from sage_categories.cat.opposites import Op
from sage_categories.cat.total_cones import total_cones as TotalCones
from sage_categories.cat.shapes import Discrete, Thin
from sage_categories.cat.predicates import Decision, Unknown, UnknownClass
from sage_categories.cat.predicates import Predicate, ask, assume, retract

__all__ = [
    "Adjunctions",
    "NN",
    "ZZ",
    "Cat",
    "Category",
    "Cones",
    "Decision",
    "Discrete",
    "Equivalences",
    "Fun",
    "LimitCones",
    "MagmaObjects",
    "Mor",
    "MonoidObjects",
    "Op",
    "Posets",
    "Predicate",
    "RingObjects",
    "SemiringObjects",
    "Sets",
    "Thin",
    "TotallyOrderedSets",
    "TotalCones",
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
