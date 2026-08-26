"""``Sets().MorphismType``: total maps by rule (D03, D09, D17, POL-SET-002/019).

``Mor(Sets())(X, Y)(rule)`` constructs a total map from a rule on private data;
the constructor trusts totality and codomain closure (POL-MATH-037).  ``f(x)``
requires ``x in X`` and returns a point of ``Y``.  The exact handlers this module
owns, each on its declared decidable domain (POL-MATH-042):

- equality of two maps with one finite enumerable domain, pointwise (D17);
- injectivity and surjectivity of a map with finite enumerable domain and codomain,
  registered on ``Mor(Sets()).Monomorphisms()`` and ``.Epimorphisms()`` because in
  ``Sets()`` monomorphisms are the injective maps and epimorphisms the surjective
  maps (Mathlib ``CategoryTheory.mono_iff_injective``, ``epi_iff_surjective``;
  inspected 2026-08-26);
- an isomorphism of sets is a bijection (Mathlib ``CategoryTheory.isIso_iff_bijective``;
  inspected 2026-08-26), so ``Isomorphisms()`` decides through both.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass, decision_and
from sage_categories.kernel.roles import MorphismOfCategory
from sage_categories.sets.elements import Datum, SetPoint
from sage_categories.sets.objects import SetObject

__all__ = ["Rule", "SetMap", "injective_on_finite_domain", "maps_equal", "surjective_on_finite_domain"]

type Rule = Callable[[Datum], Datum]


class SetMap(MorphismOfCategory):
    """A total map ``X -> Y`` given by a rule on data; retains its inverse when the construction supplied one."""

    def __init__(
        self,
        category: Category,
        domain: SetObject,
        codomain: SetObject,
        rule: Rule,
        inverse: SetMap | UnknownClass,
    ) -> None:
        super().__init__(category, domain, codomain)
        self._rule = rule
        self._inverse = inverse

    def __call__(self, element: SetPoint) -> SetPoint:
        """The image of a point of the domain: a point of the codomain (POL-CAT-040)."""
        assert element in self.domain(), f"{element!r} is not an element of {self.domain()!r}"
        return self.codomain().point(self._rule(element._datum))

    def __repr__(self) -> str:
        return f"SetMap({self.domain()!r} -> {self.codomain()!r})"


def _finite_enumeration(ambient: SetObject) -> tuple[Datum, ...] | UnknownClass:
    return ambient._enumeration


def maps_equal(first: Any, second: Any) -> Decision:
    """Two maps with one finite enumerable domain are equal exactly when they agree on every point."""
    morphisms = _sets.Sets().morphism_category(1)
    if first not in morphisms or second not in morphisms:
        return Unknown
    if first.domain() is not second.domain() or first.codomain() is not second.codomain():
        return Unknown
    enumeration = _finite_enumeration(first.domain())
    if enumeration is Unknown:
        return Unknown
    return all(first._rule(datum) == second._rule(datum) for datum in enumeration)


def injective_on_finite_domain(morphism: Any) -> Decision:
    morphisms = _sets.Sets().morphism_category(1)
    if morphism not in morphisms:
        return Unknown
    enumeration = _finite_enumeration(morphism.domain())
    if enumeration is Unknown:
        return Unknown
    images = [morphism._rule(datum) for datum in enumeration]
    return len(set(images)) == len(images)


def surjective_on_finite_domain(morphism: Any) -> Decision:
    morphisms = _sets.Sets().morphism_category(1)
    if morphism not in morphisms:
        return Unknown
    enumeration = _finite_enumeration(morphism.domain())
    codomain_enumeration = _finite_enumeration(morphism.codomain())
    if enumeration is Unknown or codomain_enumeration is Unknown:
        return Unknown
    images = {morphism._rule(datum) for datum in enumeration}
    return all(datum in images for datum in codomain_enumeration)


def bijective_on_finite_domain(morphism: Any) -> Decision:
    return decision_and(injective_on_finite_domain(morphism), surjective_on_finite_domain(morphism))
