"""The primary import surface for the owned mathematical universe (POL-SHADOW-002).

One export per owner (POL-API-002): ``Cat``, ``Mor``, ``Fun``, ``Category``, and the
shape constructors ``Discrete`` and ``Thin`` from the theory of ``Cat()``;
``ask``, ``assume``, ``retract``, ``Predicate``, ``Unknown``, and ``Decision`` from the
kernel's predicate boundary.

A production leaf is imported here, and not in ``sage_categories`` itself, when its
phase of the production plan is accepted: a leaf implements a category ``Cat``
declared, and the kernel holds that declaration without it (D80, D81).
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
    TotalCones,
    Unknown,
    UnknownClass,
    __version__,
    ask,
    assume,
    retract,
    version,
)

__all__ = [
    "Adjunctions",
    "Cat",
    "Category",
    "Cones",
    "Decision",
    "Discrete",
    "Equivalences",
    "Fun",
    "LimitCones",
    "Mor",
    "Op",
    "Predicate",
    "Thin",
    "TotalCones",
    "Unknown",
    "UnknownClass",
    "__version__",
    "ask",
    "assume",
    "retract",
    "version",
]
