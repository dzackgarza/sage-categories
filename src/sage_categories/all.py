"""The primary import surface for the owned mathematical universe (POL-SHADOW-002).

One export per owner (POL-API-002): ``Cat``, ``Mor``, ``Fun``, ``Category``, and the
shape constructors ``Discrete`` and ``Thin`` from the theory of ``Cat()``; ``Sets``,
``Cardinal``, ``aleph0``, and ``continuum`` from the theory of sets; ``ask``,
``assume``, ``Predicate``, ``Unknown``, and ``Decision`` from the kernel's predicate
boundary.
"""

from sage_categories import (
    Cardinal,
    Cat,
    Category,
    Decision,
    Discrete,
    Fun,
    Mor,
    Predicate,
    Sets,
    Thin,
    Unknown,
    UnknownClass,
    __version__,
    aleph0,
    ask,
    assume,
    continuum,
    version,
)

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
