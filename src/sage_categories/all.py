"""The primary import surface for the owned mathematical universe (POL-SHADOW-002).

One export per owner (POL-API-002): ``Cat``, ``Mor``, ``Fun``, ``Category``, and the
shape constructors ``Discrete`` and ``Thin`` from the theory of ``Cat()``;
``ask``, ``assume``, ``retract``, ``Predicate``, ``Unknown``, and ``Decision`` from
``Cat``'s predicate boundary.

A production leaf is imported here, and not in ``sage_categories`` itself, when its
phase of the production plan is accepted: a leaf implements a category ``Cat``
declared, and ``Cat`` holds that declaration without it (D80, D81).
"""

from sage_categories import (
    Adjunctions,
    Axiom,
    Cat,
    Category,
    Decision,
    Discrete,
    Equivalences,
    Fun,
    Cones,
    Cocones,
    ColimitCocones,
    LimitCones,
    Grothendieck,
    IndexedCategories,
    Mor,
    Op,
    Predicate,
    Query,
    Thin,
    TotalCones,
    Unknown,
    UnknownClass,
    __version__,
    ask,
    assume,
    retract,
    version,
    left_kan_desc,
    left_kan_extension,
    left_kan_unit,
    right_kan_counit,
    right_kan_extension,
    right_kan_lift,
)

__all__ = [
    "Adjunctions",
    "Axiom",
    "Cat",
    "Category",
    "Cones",
    "Cocones",
    "ColimitCocones",
    "Decision",
    "Discrete",
    "Equivalences",
    "Fun",
    "Grothendieck",
    "IndexedCategories",
    "LimitCones",
    "Mor",
    "Op",
    "Predicate",
    "Query",
    "Thin",
    "TotalCones",
    "Unknown",
    "UnknownClass",
    "__version__",
    "ask",
    "assume",
    "retract",
    "version",
    "left_kan_desc",
    "left_kan_extension",
    "left_kan_unit",
    "right_kan_counit",
    "right_kan_extension",
    "right_kan_lift",
]
