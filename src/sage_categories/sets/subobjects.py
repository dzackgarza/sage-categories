"""Chosen subsets and chosen quotients: ``X.subset_from(predicate)`` and ``Sets().ChosenQuotients()`` (POL-SET-007/008, POL-ENGINE-004, POL-FUN-013/014).

A chosen subset of ``X`` is a set ``A`` together with its inclusion monomorphism
``A -> X``.  ``Sets().ChosenSubsets()`` is the construction family of the chosen
subsets: a full subcategory of ``Sets()`` whose membership is placement by
construction, and a root of the narrowings of ``Sets()`` like every full
subcategory, so that a chosen subset combines with every other placement (a
finite set, a chosen limit).  Its constructor ``ChosenSubsets()(X, predicate)``
builds ``A`` as the rule-defined set whose membership rule conjoins the rule of
``X`` with the predicate, constructs the inclusion in
``Mor(Sets())(A, X).Monomorphisms()``, and retains it by identity;
``A.inclusion()`` reads it back and ``A.underlying_set()`` is
``A.inclusion().codomain()``.

The predicate is a datum-level rule ``Callable[[Datum], Decision]``, the form of
``Sets()(rule)``.  It is applied only to data that the rule of ``X`` does not
reject, and an ``Unknown`` predicate value keeps membership ``Unknown``.

Cardinality and placement are decided by cited cases and are ``Unknown``
otherwise (POL-ASSUME-004):

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

The chosen subsets of one set ``X`` carry the subset algebra (``specs/sets.md``,
"Subobjects, images, and power objects"): ``A <= B`` is the applied predicate
``subset_of(A, B)``, decided by identity, and exactly when ``A`` has a chosen
enumeration each of whose members ``B`` decides; ``A.union(B)``,
``A.intersection(B)``, ``A.difference(B)``, ``A.symmetric_difference(B)``, and
``A.complement()`` are the chosen subsets of ``X`` cut out by the Kleene
combinations of the two membership rules (the definitions ``Set.mem_union``,
``Set.mem_inter_iff``, ``Set.mem_diff``, ``Set.mem_symmDiff``, ``Set.mem_compl_iff``);
``|`` and ``&`` are union and intersection.  ``A.characteristic_morphism()`` is
``chi_A: X -> 2`` with ``chi_A(x) = 1`` exactly when ``x in A`` (nLab "subobject
classifier": in ``Set`` the classifier is ``2`` and the characteristic function of
``S`` sends ``x`` to true exactly when ``x in S``; Mathlib ``Set.boolIndicator``
with ``Set.mem_iff_boolIndicator``; both inspected 2026-08-27), retained once per
subset; it has no value at a datum whose membership is ``Unknown``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sage.structure.coerce_dict import MonoDict

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.cat.properties import FullSubcategory
from sage_categories.kernel.decisions import Decision, Unknown, decision_and, decision_not, decision_or
from sage_categories.kernel.predicates import AppliedPredicate, Predicate
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import CategoryPoint, ObjectOfCategory, Role
from sage_categories.sets.cardinals import CardinalObject
from sage_categories.sets.elements import Datum
from sage_categories.sets.maps import Rule, SetMap
from sage_categories.sets.objects import MembershipRule, SetObject

__all__ = ["ChosenQuotientRole", "ChosenQuotientsCategory", "ChosenSubsetRole", "ChosenSubsetsCategory", "subset_of"]

# ``subset_of(A, B)``: every member of the chosen subset ``A`` is a member of the
# chosen subset ``B`` of the same set.
subset_of = Predicate("subset_of", 2, True)


def _subset_by_identity(first: CategoryPoint, candidate: Any) -> Decision:
    return True if first is candidate else Unknown


def _subset_by_enumeration(first: CategoryPoint, candidate: Any) -> Decision:
    """Exact when ``A`` has a chosen enumeration: ``B`` decides each member of ``A``."""
    sets = _sets.Sets()
    chosen, finite = sets.ChosenSubsets(), sets.Finite()
    if first not in chosen or candidate not in chosen:
        return Unknown
    if first.underlying_set() is not candidate.underlying_set():
        return Unknown
    if not finite.has_chosen_enumeration(first):
        return Unknown
    rule = candidate._set_object_data.membership_rule
    return decision_and(*(rule(datum) for datum in finite.chosen_enumeration(first)))


subset_of.register_handler(_subset_by_identity)
subset_of.register_handler(_subset_by_enumeration)


class ChosenSubsetRole(ObjectOfCategory):
    """The local object role of ``Sets().ChosenSubsets()``: a set that retains its inclusion and carries the subset algebra of its base set."""

    def inclusion(self) -> SetMap:
        """The retained inclusion monomorphism ``A -> X`` (POL-FUN-013)."""
        return _sets.Sets().ChosenSubsets().retained_inclusion(self)

    def underlying_set(self) -> SetObject:
        """``X``, read from the codomain of the inclusion (POL-FUN-014)."""
        return self.inclusion().codomain()

    def characteristic_morphism(self) -> SetMap:
        """``chi_A: X -> 2 = [1]``, ``1`` on the members of ``A`` and ``0`` elsewhere, retained once."""
        return _sets.Sets().ChosenSubsets().characteristic_morphism_of(self)

    def __le__(self, other: SetObject) -> AppliedPredicate:
        """``A <= B``: the proposition that ``A`` is contained in ``B``."""
        return subset_of(self, other)

    def union(self, other: SetObject) -> SetObject:
        return self._combined(other, decision_or)

    def intersection(self, other: SetObject) -> SetObject:
        return self._combined(other, decision_and)

    def difference(self, other: SetObject) -> SetObject:
        return self._combined(other, lambda in_first, in_second: decision_and(in_first, decision_not(in_second)))

    def symmetric_difference(self, other: SetObject) -> SetObject:
        return self._combined(other, lambda in_first, in_second: decision_or(decision_and(in_first, decision_not(in_second)), decision_and(in_second, decision_not(in_first))))

    def complement(self) -> SetObject:
        rule = self._set_object_data.membership_rule
        return self.underlying_set().subset_from(lambda datum: decision_not(rule(datum)))

    def __or__(self, other: SetObject) -> SetObject:
        return self.union(other)

    def __and__(self, other: SetObject) -> SetObject:
        return self.intersection(other)

    def _combined(self, other: SetObject, combine: Callable[[Decision, Decision], Decision]) -> SetObject:
        """The chosen subset of ``X`` whose membership is the combination of the two membership decisions."""
        assert other in _sets.Sets().ChosenSubsets() and other.underlying_set() is self.underlying_set(), f"{other!r} is not a chosen subset of {self.underlying_set()!r}"
        first_rule = self._set_object_data.membership_rule
        second_rule = other._set_object_data.membership_rule
        return self.underlying_set().subset_from(lambda datum: combine(first_rule(datum), second_rule(datum)))


class ChosenSubsetsCategory(FullSubcategory[[Rule], []]):
    """``Sets().ChosenSubsets()``: the construction family of the chosen subsets; owns their construction and retains each inclusion."""

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        self._inclusions: MonoDict = MonoDict()
        self._images: MonoDict = MonoDict()
        self._characteristics: MonoDict = MonoDict()
        super().__init__(ambient)

    def name(self) -> str:
        return "ChosenSubsets"

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.{self.name()}()"

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        if role is Role.OBJECT:
            return ChosenSubsetRole
        return super().local_role_class(role)

    def with_cardinality(self, base_set: SetObject, predicate: MembershipRule, cardinality: CardinalObject) -> SetObject:
        """The chosen subset ``{x in X : predicate(x)}`` whose exact cardinality a construction theorem supplies (POL-SET-031)."""
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        base_rule = base_set._set_object_data.membership_rule

        def rule(datum: Datum) -> Decision:
            in_base = base_rule(datum)
            if in_base is False:
                return False
            return decision_and(in_base, predicate(datum))

        subset = sets.with_cardinality(rule, cardinality)
        refine(subset, self)
        return self._retain_inclusion(subset, base_set)

    def from_enumeration(self, base_set: SetObject, members: tuple[Datum, ...]) -> SetObject:
        """The chosen subset of ``X`` with the given finite enumeration of member data, each admitted by ``X``."""
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        base_rule = base_set._set_object_data.membership_rule
        assert all(base_rule(member) is not False for member in members), f"{members!r} are not all members of {base_set!r}"
        subset = sets.Finite()(members)
        refine(subset, self)
        return self._retain_inclusion(subset, base_set)

    def characteristic_morphism_of(self, subset: SetObject) -> SetMap:
        """``chi_A``, retained per chosen subset."""
        if subset not in self._characteristics:
            sets = _sets.Sets()
            rule = subset._set_object_data.membership_rule

            def indicator(datum: Datum) -> Datum:
                decision = rule(datum)
                assert decision is not Unknown, f"membership of {datum!r} in {subset!r} is not decided, so its characteristic morphism has no value there"
                return 1 if decision is True else 0

            self._characteristics[subset] = sets.morphism_category(1)(subset.underlying_set(), sets.Simplex(1))(indicator)
        return self._characteristics[subset]

    def __call__(self, base_set: SetObject, predicate: MembershipRule) -> SetObject:
        """The chosen subset ``{x in X : predicate(x)}`` with its inclusion into ``X``."""
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        finite = sets.Finite()
        base_rule = base_set._set_object_data.membership_rule

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
        subset = sets(rule)
        refine(subset, self)
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
        codomain_rule = codomain._set_object_data.membership_rule
        if finite.has_chosen_enumeration(domain):
            rule = set_map._set_morphism_data.rule
            images = tuple(rule(datum) for datum in finite.chosen_enumeration(domain))
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
        subset = sets(has_preimage) if cardinality is Unknown else sets.with_cardinality(has_preimage, cardinality)
        refine(subset, self)
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


class ChosenQuotientRole(ObjectOfCategory):
    """The local object role of ``Sets().ChosenQuotients()``: a set that retains its quotient map."""

    def quotient_map(self) -> SetMap:
        """The retained quotient epimorphism ``X -> X/~``."""
        return _sets.Sets().ChosenQuotients().retained_quotient_map(self)

    def underlying_set(self) -> SetObject:
        """``X``, read from the domain of the quotient map."""
        return self.quotient_map().domain()


class ChosenQuotientsCategory(FullSubcategory[[Rule], []]):
    """``Sets().ChosenQuotients()``: the construction family of the chosen quotients, dual to ``ChosenSubsets()``; owns their construction and retains each quotient map.

    ``ChosenQuotients()(X, class_of, membership_rule)`` builds the quotient ``X/~``
    whose data are the class data ``class_of(x)`` of the data ``x`` of ``X``; the
    membership rule recognizes a class datum of this quotient.  When ``X`` carries a
    chosen enumeration and the class data compare exactly, the quotient is
    constructed through ``Sets().Finite()`` with one representative per class;
    otherwise it is rule-valued with cardinality ``Unknown``.  The quotient map is
    surjective by construction (Mathlib ``Quot.mk_surjective``; inspected
    2026-08-27) and is retained in ``Epimorphisms()``.
    """

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        self._quotient_maps: MonoDict = MonoDict()
        super().__init__(ambient)

    def name(self) -> str:
        return "ChosenQuotients"

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.{self.name()}()"

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        if role is Role.OBJECT:
            return ChosenQuotientRole
        return super().local_role_class(role)

    def __call__(self, base_set: SetObject, class_of: Callable[[Datum], Datum], membership_rule: MembershipRule) -> SetObject:
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        finite = sets.Finite()
        if finite.has_chosen_enumeration(base_set):
            classes = tuple(class_of(datum) for datum in finite.chosen_enumeration(base_set))
            comparisons = tuple(classes[i] == classes[j] for i in range(len(classes)) for j in range(i))
            if all(decision is not Unknown for decision in comparisons):
                distinct = tuple(datum for position, datum in enumerate(classes) if not any((datum == earlier) is True for earlier in classes[:position]))
                quotient = finite(distinct)
                refine(quotient, self)
                return self._retain_quotient_map(base_set, quotient, class_of)
        quotient = sets.rule_valued(membership_rule, Unknown)
        refine(quotient, self)
        return self._retain_quotient_map(base_set, quotient, class_of)

    def _retain_quotient_map(self, base_set: SetObject, quotient: SetObject, class_of: Callable[[Datum], Datum]) -> SetObject:
        epimorphisms = _sets.Sets().morphism_category(1)(base_set, quotient).Epimorphisms()
        self._quotient_maps[quotient] = epimorphisms(class_of)
        return quotient

    def retained_quotient_map(self, quotient: SetObject) -> SetMap:
        """The quotient map this category retained for ``quotient``."""
        assert quotient in self._quotient_maps, f"{quotient!r} retains no quotient map"
        return self._quotient_maps[quotient]
