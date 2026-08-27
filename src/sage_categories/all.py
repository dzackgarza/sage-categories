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
"""

from sage_categories import (
    NN,
    QQ,
    RR,
    ZZ,
    Cardinal,
    Cat,
    Category,
    Decision,
    Discrete,
    FinitePosets,
    FiniteTotallyOrderedSets,
    Fun,
    Mor,
    Ordinals,
    Posets,
    Predicate,
    Primes,
    Sets,
    Thin,
    TotallyOrderedSets,
    Unknown,
    UnknownClass,
    __version__,
    aleph0,
    ask,
    assume,
    continuum,
    generalized_continuum_hypothesis,
    omega0,
    retract,
    version,
)

__all__ = [
    "NN",
    "QQ",
    "RR",
    "ZZ",
    "Cardinal",
    "Cat",
    "Category",
    "Decision",
    "Discrete",
    "FinitePosets",
    "FiniteTotallyOrderedSets",
    "Fun",
    "Mor",
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
