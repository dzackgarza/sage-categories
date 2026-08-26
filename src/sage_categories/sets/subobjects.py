"""Chosen subsets: ``X.subset_from(predicate)`` (POL-SET-007/008, POL-ENGINE-004, POL-FUN-013/014).

A chosen subset of ``X`` is a set ``A`` together with its inclusion monomorphism
``A -> X``.  ``Sets().ChosenSubsets()`` is the full subcategory of ``Sets()`` on the
chosen subsets.  Its constructor ``ChosenSubsets()(X, predicate)`` builds ``A`` as
the rule-defined set whose membership rule conjoins the rule of ``X`` with the
predicate, constructs the inclusion in ``Mor(Sets())(A, X).Monomorphisms()``, and
retains it by identity; ``A.inclusion()`` reads it back and ``A.underlying_set()``
is ``A.inclusion().codomain()``.

The predicate is a datum-level rule ``Callable[[Datum], Decision]``, the form of
``Sets()(rule)``.  It is applied only to data that the rule of ``X`` does not
reject, and an ``Unknown`` predicate value keeps membership ``Unknown``.

Cardinality and placement are decided by cited cases and are ``Unknown``
otherwise (D01):

- a subset of a set with a chosen enumeration whose predicate decides every member
  is constructed with the exact enumeration and count through ``Sets().Finite()``;
- a subset of a finite set is finite (Mathlib ``Set.Finite.subset``);
- a subset of a countable set is countable (Mathlib ``Set.Countable.mono``).

The image ``f.image()`` of a set map is the chosen subset of ``f.codomain()`` by
the rule "some point of the domain maps here" (POL-ENGINE-004): exact when the
domain has a chosen enumeration and the image data compare exactly, ``Unknown``
otherwise.  Its placement and cardinality follow the cited cases: the image of
a finite set is finite (Mathlib ``Set.Finite.image``), the image of a countable
set is countable (Mathlib ``Set.Countable.image``; both inspected 2026-08-27), and
the image of a map placed in ``Mor(Sets()).Monomorphisms()`` has the cardinality
of its domain (``specs/sets.md``, "Subobjects, images, and power objects": the
image of a monomorphism is the canonical chosen subset it represents).
"""

from __future__ import annotations

from sage.structure.coerce_dict import MonoDict

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun, Functor
from sage_categories.kernel.decisions import Decision, Unknown, decision_and, decision_or
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.elements import Datum
from sage_categories.sets.maps import Rule, SetMap
from sage_categories.sets.objects import MembershipRule, SetObject

__all__ = ["ChosenSubsetRole", "ChosenSubsetsCategory"]


class ChosenSubsetRole(ObjectOfCategory):
    """The local object role of ``Sets().ChosenSubsets()``: a set that retains its inclusion."""

    def inclusion(self) -> SetMap:
        """The retained inclusion monomorphism ``A -> X`` (POL-FUN-013)."""
        return _sets.Sets().ChosenSubsets().retained_inclusion(self)

    def underlying_set(self) -> SetObject:
        """``X``, read from the codomain of the inclusion (POL-FUN-014)."""
        return self.inclusion().codomain()


class ChosenSubsetsCategory(Category[[Rule], []]):
    """The full subcategory of ``Sets()`` on the chosen subsets; owns their construction."""

    ObjectType = ChosenSubsetRole

    class ElementType(ElementOfObject):
        """A generalized element of a chosen subset; no local operation."""

    class MorphismType(MorphismOfCategory):
        """A map between chosen subsets; no local operation."""

    def __init__(self) -> None:
        self._inclusions: MonoDict = MonoDict()
        self._images: MonoDict = MonoDict()
        super().__init__()

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(self, _sets.Sets()).FullyFaithful().inclusion(),)

    def __call__(self, base_set: SetObject, predicate: MembershipRule) -> SetObject:
        """The chosen subset ``{x in X : predicate(x)}`` with its inclusion into ``X``."""
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        finite = sets.Finite()
        base_rule = base_set._membership_rule

        def rule(datum: Datum) -> Decision:
            in_base = base_rule(datum)
            if in_base is False:
                return False
            return decision_and(in_base, predicate(datum))

        if finite.has_chosen_enumeration(base_set):
            decided = tuple((datum, predicate(datum)) for datum in finite.chosen_enumeration(base_set))
            if all(decision is not Unknown for _, decision in decided):
                subset = finite(tuple(datum for datum, decision in decided if decision is True))
                refine(subset, self)
                return self._retain_inclusion(subset, base_set)
        subset = self.ObjectType(self, rule, Unknown)
        if base_set in finite:
            # A subset of a finite set is finite: Mathlib ``Set.Finite.subset``
            # (Mathlib.Data.Set.Finite.Basic; inspected 2026-08-26).
            finite(subset)
        elif base_set in sets.Countable():
            # A subset of a countable set is countable: Mathlib ``Set.Countable.mono``
            # (Mathlib.Data.Set.Countable; inspected 2026-08-26).
            sets.Countable()(subset)
        return self._retain_inclusion(subset, base_set)

    def image_of(self, set_map: SetMap) -> SetObject:
        """``f.image()``: the chosen subset of the codomain of the points with a preimage, retained per map."""
        sets = _sets.Sets()
        finite, countable, monomorphisms = sets.Finite(), sets.Countable(), sets.morphism_category(1).Monomorphisms()
        assert set_map in sets.morphism_category(1), f"{set_map!r} is not a set map"
        if set_map in self._images:
            return self._images[set_map]
        domain, codomain = set_map.domain(), set_map.codomain()
        codomain_rule = codomain._membership_rule
        if finite.has_chosen_enumeration(domain):
            images = tuple(set_map._rule(datum) for datum in finite.chosen_enumeration(domain))
            comparisons = tuple(images[i] == images[j] for i in range(len(images)) for j in range(i))
            if all(decision is not Unknown for decision in comparisons):
                # The image of a finite set is finite (Mathlib ``Set.Finite.image``): the
                # distinct image data, each pairwise comparison exact.
                distinct = tuple(image for position, image in enumerate(images) if not any((image == earlier) is True for earlier in images[:position]))
                subset = finite(distinct)
                refine(subset, self)
                self._images[set_map] = self._retain_inclusion(subset, codomain)
                return subset

            def has_preimage(datum: Datum) -> Decision:
                in_codomain = codomain_rule(datum)
                if in_codomain is False:
                    return False
                return decision_and(in_codomain, decision_or(*(image == datum for image in images)))

        else:

            def has_preimage(datum: Datum) -> Decision:
                in_codomain = codomain_rule(datum)
                if in_codomain is False:
                    return False
                return Unknown

        cardinality = domain.cardinality() if set_map in monomorphisms else Unknown
        subset = self.ObjectType(self, has_preimage, cardinality)
        if domain in finite:
            # Mathlib ``Set.Finite.image`` (Mathlib.Data.Set.Finite.Basic; inspected 2026-08-27).
            finite(subset)
        elif domain in countable:
            # Mathlib ``Set.Countable.image`` (Mathlib.Data.Set.Countable; inspected 2026-08-27).
            countable(subset)
        elif codomain in finite:
            finite(subset)
        elif codomain in countable:
            countable(subset)
        self._images[set_map] = self._retain_inclusion(subset, codomain)
        return subset

    def _retain_inclusion(self, subset: SetObject, base_set: SetObject) -> SetObject:
        # The inclusion of a subset is injective: Mathlib ``Set.inclusion_injective``
        # (Mathlib.Data.Set.Inclusion; inspected 2026-08-26).
        monomorphisms = _sets.Sets().morphism_category(1)(subset, base_set).Monomorphisms()
        self._inclusions[subset] = monomorphisms(lambda datum: datum)
        return subset

    def retained_inclusion(self, subset: SetObject) -> SetMap:
        """The inclusion this category retained for ``subset``."""
        assert subset in self._inclusions, f"{subset!r} retains no inclusion"
        return self._inclusions[subset]

    def __repr__(self) -> str:
        return "Sets.ChosenSubsets()"
