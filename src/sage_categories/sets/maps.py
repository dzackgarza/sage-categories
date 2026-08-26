"""``Sets().MorphismType``: total maps by rule (POL-SET-002/019, POL-SET-026, POL-FUN-024).

``Mor(Sets())(X, Y)(rule)`` constructs a total map from a rule on private data;
the constructor trusts totality and codomain closure (POL-MATH-037).  ``f(x)``
requires ``x in X`` and returns a point of ``Y``.  The exact handlers this module
owns, each on its declared decidable domain (POL-MATH-042):

- equality of two maps with one finite enumerable domain, pointwise (POL-MATH-034);
- injectivity and surjectivity of a map with finite enumerable domain and codomain,
  registered on ``Mor(Sets()).Monomorphisms()`` and ``.Epimorphisms()`` because in
  ``Sets()`` monomorphisms are the injective maps and epimorphisms the surjective
  maps (Mathlib ``CategoryTheory.mono_iff_injective``, ``epi_iff_surjective``;
  inspected 2026-08-26);
- an isomorphism of sets is a bijection (Mathlib ``CategoryTheory.isIso_iff_bijective``;
  inspected 2026-08-26), so ``Isomorphisms()`` decides through both.

Each handler compares image data pairwise.  A comparison of two data at the
private boundary is exact (a ``bool``) or ``Unknown`` (a rule-defined family or
the name of a map with an unenumerated domain), and the handlers combine those
answers three-valued: they never decide through a hash table on data whose
equality may be ``Unknown``.

A retained inverse is construction data owned by ``Sets()`` (``inverse_morphism``),
not a field of every map.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.kernel.decisions import Decision, Unknown, decision_and, decision_not, decision_or
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory
from sage_categories.sets.elements import Datum, SetPoint
from sage_categories.sets.objects import SetObject

__all__ = ["Rule", "SetMap", "injective_on_finite_domain", "maps_equal", "surjective_on_finite_domain"]

type Rule = Callable[[Datum], Datum]


class SetMap(MorphismOfCategory):
    """A total map ``X -> Y`` given by a rule on data."""

    def __init__(self, category: Category, domain: SetObject, codomain: SetObject, rule: Rule) -> None:
        super().__init__(category, domain, codomain)
        self._rule = rule

    def __call__(self, element: SetPoint) -> SetPoint:
        """The image of a point of the domain: a point of the codomain (POL-CAT-040)."""
        assert element in self.domain(), f"{element!r} is not an element of {self.domain()!r}"
        return self.codomain().point(self._rule(element._datum))

    def image(self) -> SetObject:
        """The chosen subset of the codomain of the points with a preimage, with its inclusion (POL-ENGINE-004; ``sets/subobjects.py``)."""
        return _sets.Sets().ChosenSubsets().image_of(self)

    def __repr__(self) -> str:
        return f"SetMap({self.domain()!r} -> {self.codomain()!r})"


def _data_equal(first: Datum, second: Datum) -> Decision:
    """The engine comparison of two data: exact, or ``Unknown`` for rule-defined data."""
    return first == second


def maps_equal(first: CategoryPoint, candidate: Any) -> Decision:
    """Two maps with one finite enumerable domain are equal exactly when they agree on every point."""
    sets = _sets.Sets()
    morphisms = sets.morphism_category(1)
    if first not in morphisms or candidate not in morphisms:
        return Unknown
    if first.domain() is not candidate.domain() or first.codomain() is not candidate.codomain():
        return Unknown
    finite = sets.Finite()
    if not finite.has_chosen_enumeration(first.domain()):
        return Unknown
    return decision_and(*(_data_equal(first._rule(datum), candidate._rule(datum)) for datum in finite.chosen_enumeration(first.domain())))


def injective_on_finite_domain(morphism: MorphismOfCategory) -> Decision:
    """Injective exactly when no two distinct points of the enumerated domain have equal images."""
    sets = _sets.Sets()
    if morphism not in sets.morphism_category(1) or not sets.Finite().has_chosen_enumeration(morphism.domain()):
        return Unknown
    images = [morphism._rule(datum) for datum in sets.Finite().chosen_enumeration(morphism.domain())]
    collisions = (_data_equal(images[i], images[j]) for i in range(len(images)) for j in range(i + 1, len(images)))
    return decision_not(decision_or(*collisions))


def surjective_on_finite_domain(morphism: MorphismOfCategory) -> Decision:
    """Surjective exactly when every point of the enumerated codomain is an image."""
    sets = _sets.Sets()
    finite = sets.Finite()
    if morphism not in sets.morphism_category(1):
        return Unknown
    if not finite.has_chosen_enumeration(morphism.domain()) or not finite.has_chosen_enumeration(morphism.codomain()):
        return Unknown
    images = [morphism._rule(datum) for datum in finite.chosen_enumeration(morphism.domain())]
    return decision_and(*(decision_or(*(_data_equal(image, datum) for image in images)) for datum in finite.chosen_enumeration(morphism.codomain())))


def bijective_on_finite_domain(morphism: MorphismOfCategory) -> Decision:
    return decision_and(injective_on_finite_domain(morphism), surjective_on_finite_domain(morphism))
