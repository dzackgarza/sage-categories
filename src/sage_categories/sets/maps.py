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

Each handler compares image data pairwise at the private computation boundary, where
``==`` is exact for an engine value, ``Unknown`` for a rule-defined family or the name
of a map with an unenumerated domain, and a proposition for an owned mathematical
value, so each comparison is asked (POL-MATH-034).  The handlers combine those answers
three-valued: they never decide through a hash table on data whose equality may be
``Unknown``.

A retained inverse is construction data owned by ``Sets()`` (``inverse_morphism``),
not a field of every map.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import ask, conjunction, disjunction, negation
from sage_categories.sets.elements import Datum

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.sets.category import SetElement, SetMap, SetObject

__all__ = ["Rule", "SetMorphismData", "injective_on_finite_domain", "maps_equal", "surjective_on_finite_domain"]

type Rule = Callable[[Datum], Datum]


@dataclass(eq=False, slots=True)
class SetMorphismData:
    """The private state used by the complete set-morphism implementation."""

    rule: Rule


class SetMapDeclaration:
    """The local ``Sets().MorphismType`` declaration."""

    def __init__(self, data: SetMorphismData) -> None:
        self._set_morphism_data = data
        super().__init__()

    def __call__(self, element: SetElement) -> SetElement:
        """Compose with a generalized element; evaluate its datum at the terminal object (POL-CAT-040)."""
        assert element in self.domain(), f"{element!r} is not an element of {self.domain()!r}"
        sets = _sets.Sets()
        underlying_map = sets.structural_image(self)
        underlying = sets.structural_image(element)
        if underlying.defining_morphism().domain() is sets.Terminal():
            return underlying_map.codomain().point(self._set_morphism_data.rule(underlying._point_datum_()))
        return sets.element_from_defining_morphism(underlying_map * underlying.defining_morphism())

    def image(self) -> SetObject:
        """The chosen subset of the codomain of the points with a preimage, with its monomorphism (POL-ENGINE-004; ``sets/subobjects.py``)."""
        return _sets.Sets().ChosenSubsets().image_of(_sets.Sets().structural_image(self))

    def __repr__(self) -> str:
        return f"SetMap({self.domain()!r} -> {self.codomain()!r})"


def maps_equal(first: CategoryOfCategories.ElementType, candidate: Any) -> Decision:
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
    first_rule = first._set_morphism_data.rule
    candidate_rule = candidate._set_morphism_data.rule
    return ask(conjunction(first_rule(datum) == candidate_rule(datum) for datum in finite.chosen_enumeration(first.domain())))


def injective_on_finite_domain(morphism: SetMap) -> Decision:
    """Injective exactly when no two distinct points of the enumerated domain have equal images."""
    sets = _sets.Sets()
    if morphism not in sets.morphism_category(1) or not sets.Finite().has_chosen_enumeration(morphism.domain()):
        return Unknown
    rule = morphism._set_morphism_data.rule
    images = [rule(datum) for datum in sets.Finite().chosen_enumeration(morphism.domain())]
    collisions = (images[i] == images[j] for i in range(len(images)) for j in range(i + 1, len(images)))
    return ask(negation(disjunction(collisions)))


def surjective_on_finite_domain(morphism: SetMap) -> Decision:
    """Surjective exactly when every point of the enumerated codomain is an image."""
    sets = _sets.Sets()
    finite = sets.Finite()
    if morphism not in sets.morphism_category(1):
        return Unknown
    if not finite.has_chosen_enumeration(morphism.domain()) or not finite.has_chosen_enumeration(morphism.codomain()):
        return Unknown
    rule = morphism._set_morphism_data.rule
    images = [rule(datum) for datum in finite.chosen_enumeration(morphism.domain())]
    return ask(conjunction(disjunction(image == datum for image in images) for datum in finite.chosen_enumeration(morphism.codomain())))


def bijective_on_finite_domain(morphism: SetMap) -> Decision:
    return ask(conjunction((injective_on_finite_domain(morphism), surjective_on_finite_domain(morphism))))
