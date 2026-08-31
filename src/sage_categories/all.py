"""The primary import surface for the owned mathematical universe (POL-SHADOW-002).

One export per owner (POL-API-002): ``Cat``, ``Mor``, ``Fun``, ``Category``, and the
shape constructors ``Discrete`` and ``Thin`` from the theory of ``Cat()``; ``Sets``,
``Cardinal``, ``aleph0``, ``continuum``, and ``generalized_continuum_hypothesis`` from the theory of sets; ``Ordinals`` and
``omega0`` from the theory of ordinals; ``NN``, ``ZZ``, ``QQ``, ``RR``, and ``Primes``
from the owned number sets, which shadow Sage's names inside the package universe;
``Posets``, ``FinitePosets``, ``TotallyOrderedSets``, and ``FiniteTotallyOrderedSets`` from the
theory of ordered sets;
``ask``, ``assume``, ``retract``, ``Predicate``, ``Unknown``, and ``Decision`` from the
kernel's predicate boundary.

The leaves are imported here and not in ``sage_categories`` itself: a leaf implements a
category ``Cat`` declared, and the kernel holds that declaration without it (D80, D81).
"""

from sage_categories import (
    Adjunctions,
    Cat,
    Category,
    Decision,
    Discrete,
    Equivalences,
    Fun,
    Cones,
    LimitCones,
    Mor,
    Op,
    Predicate,
    Thin,
    Unknown,
    UnknownClass,
    __version__,
    ask,
    assume,
    retract,
    version,
)
from sage_categories.number_sets import NN, QQ, RR, ZZ, Primes
from sage_categories.ordinals import Ordinals, omega0
from sage_categories.posets import FinitePosets, FiniteTotallyOrderedSets, Posets, TotallyOrderedSets
from sage_categories.sets.cardinals import Cardinal, aleph0, continuum, generalized_continuum_hypothesis
from sage_categories.sets.category import Sets

__all__ = [
    "Adjunctions",
    "NN",
    "QQ",
    "RR",
    "ZZ",
    "Cardinal",
    "Cat",
    "Category",
    "Decision",
    "Discrete",
    "Equivalences",
    "FinitePosets",
    "FiniteTotallyOrderedSets",
    "Fun",
    "Cones",
    "LimitCones",
    "Mor",
    "Op",
    "Ordinals",
    "Posets",
    "Predicate",
    "Primes",
    "Sets",
    "Thin",
    "TotallyOrderedSets",
    "Unknown",
    "UnknownClass",
    "__version__",
    "aleph0",
    "ask",
    "assume",
    "continuum",
    "generalized_continuum_hypothesis",
    "omega0",
    "retract",
    "version",
]
