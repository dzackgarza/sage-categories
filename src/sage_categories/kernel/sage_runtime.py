"""The one module through which the kernel and ``Cat`` import Sage's runtime facilities (specs/resolution.md, "Fixed private dependencies")."""

from __future__ import annotations

from sage.categories.category import Category as SageCategory
from sage.categories.category_with_axiom import uncamelcase
from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
from sage.libs.gap.element import GapElement
from sage.libs.gap.libgap import libgap
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.lazy_attribute import lazy_attribute
from sage.misc.unknown import Unknown, UnknownClass
from sage.rings.integer import Integer
from sage.sets.disjoint_set import DisjointSet
from sage.sets.family import LazyFamily
from sage.structure.coerce_dict import MonoDict, TripleDict
from sage.structure.dynamic_class import dynamic_class
from sage.version import version as sage_version

__all__ = [
    "AdditiveAbelianGroup",
    "DisjointSet",
    "GapElement",
    "Integer",
    "LazyFamily",
    "MonoDict",
    "SageCategory",
    "TripleDict",
    "Unknown",
    "UnknownClass",
    "cached_function",
    "cached_method",
    "dynamic_class",
    "lazy_attribute",
    "libgap",
    "sage_version",
    "uncamelcase",
]
