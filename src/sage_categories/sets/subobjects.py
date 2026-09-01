"""Chosen subsets, chosen quotients, and their local operations."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from sage.misc.cachefunc import cached_method

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.cat.predicates import (
    AppliedPredicate,
    Decision,
    Predicate,
    Unknown,
    UnknownClass,
    ask,
    conjunction,
    disjunction,
    established,
    negation,
    predicate,
)
from sage_categories.cat.properties import FullSubcategory
from sage_categories.cat.slices import SliceLikeCategory, SliceProperty
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.sets.cardinals import CardinalObject
from sage_categories.sets.elements import Datum
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import MembershipRule, SetObject

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.sets.category import SetMap

__all__ = ["ChosenQuotientsCategory", "ChosenSubsetsCategory", "SetSubobjects", "subset_of"]


class SetSubobjects(SliceProperty):
    """``Sets().Subobjects(X)``: set subobjects add construction from a membership predicate (D84, POL-CAT-092)."""

    class ElementType:
        """A point of a set subobject."""

    class MorphismType:
        """A triangle of the slice between two set subobjects."""

    class ObjectType:
        """A subobject ``j: A -> X`` of a set."""

    def from_predicate(self, predicate: MembershipRule) -> SliceLikeCategory.ObjectType:
        """The subobject selected by a predicate on the data of the fixed set: its chosen subset with its monomorphism."""
        subset = self._ambient.fixed_object().subset_from(predicate)
        return self(subset.monomorphism())

# ``subset_of(A, B)``: every member of the chosen subset ``A`` is a member of the
# chosen subset ``B`` of the same set.
subset_of: Predicate = predicate("subset_of")


def _restricted_rule(base_set: SetObject, predicate: MembershipRule) -> MembershipRule:
    """The membership rule of ``{x in X : predicate(x)}``: the rule of ``X`` conjoined with the predicate.

    The predicate is applied only to data that ``X`` does not reject, so a predicate
    written for the members of ``X`` never sees another datum.
    """
    base_rule = base_set._set_object_data.membership_rule

    def rule(datum: Datum) -> Decision:
        in_base = base_rule(datum)
        if established(negation(in_base)):
            return False
        return ask(conjunction((in_base, predicate(datum))))

    return rule


def _distinct(data: tuple[Datum, ...]) -> tuple[Datum, ...] | UnknownClass:
    """The exactly distinct members of a finite list of data, or ``Unknown`` when a pair does not compare.

    An enumeration lists each member once (POL-SET-011/027), so an undecided pairwise
    comparison leaves the list unusable as one and the caller keeps its set rule-defined.

    Each comparison goes through ``ask``: ``==`` on an owned datum returns a
    proposition, not a decision (POL-MATH-034/035), so only ``ask`` yields the
    ``True``/``False``/``Unknown`` this deduplication branches on.
    """
    if any(
        ask(first == second) is Unknown
        for position, first in enumerate(data)
        for second in data[:position]
    ):
        return Unknown
    return tuple(
        datum
        for position, datum in enumerate(data)
        if not any(ask(datum == earlier) for earlier in data[:position])
    )


def _subset_by_identity(
    first: CategoryOfCategories.ElementType, candidate: Any
) -> Decision:
    return True if first is candidate else Unknown


def _subset_by_enumeration(
    first: CategoryOfCategories.ElementType, candidate: Any
) -> Decision:
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
    return ask(conjunction(rule(datum) for datum in finite.chosen_enumeration(first)))


subset_of.register_handler(_subset_by_identity)
subset_of.register_handler(_subset_by_enumeration)


class ChosenSubsetObject:
    """The local object role of ``Sets().ChosenSubsets()``: a set that retains its presenting monomorphism and carries the subset algebra of its base set."""

    def monomorphism(self) -> SetMap:
        """The retained monomorphism ``A -> X`` that presents this subobject (POL-FUN-013)."""
        return _sets.Sets().ChosenSubsets().retained_datum(self)

    def underlying_set(self) -> SetObject:
        """``X``, read from the codomain of the presenting monomorphism (POL-FUN-014)."""
        return self.monomorphism().codomain()

    def characteristic_morphism(self) -> SetMap:
        """``chi_A: X -> 2 = [1]``, ``1`` on the members of ``A`` and ``0`` elsewhere, retained once."""
        return _sets.Sets().ChosenSubsets().characteristic_morphism_of(self)

    def __le__(self, other: SetObject) -> AppliedPredicate:
        """``A <= B``: the proposition that ``A`` is contained in ``B``."""
        return subset_of(self, other)

    def union(self, other: SetObject) -> SetObject:
        return self._combined(
            other, lambda in_first, in_second: ask(disjunction((in_first, in_second)))
        )

    def intersection(self, other: SetObject) -> SetObject:
        return self._combined(
            other, lambda in_first, in_second: ask(conjunction((in_first, in_second)))
        )

    def difference(self, other: SetObject) -> SetObject:
        return self._combined(
            other,
            lambda in_first, in_second: ask(
                conjunction((in_first, negation(in_second)))
            ),
        )

    def symmetric_difference(self, other: SetObject) -> SetObject:
        return self._combined(
            other,
            lambda in_first, in_second: ask(
                disjunction(
                    (
                        conjunction((in_first, negation(in_second))),
                        conjunction((in_second, negation(in_first))),
                    )
                )
            ),
        )

    def complement(self) -> SetObject:
        rule = self._set_object_data.membership_rule
        return self.underlying_set().subset_from(
            lambda datum: ask(negation(rule(datum)))
        )

    def __or__(self, other: SetObject) -> SetObject:
        return self.union(other)

    def __and__(self, other: SetObject) -> SetObject:
        return self.intersection(other)

    def _combined(
        self, other: SetObject, combine: Callable[[Decision, Decision], Decision]
    ) -> SetObject:
        """The chosen subset of ``X`` whose membership is the combination of the two membership decisions."""
        assert (
            other in _sets.Sets().ChosenSubsets()
            and other.underlying_set() is self.underlying_set()
        ), f"{other!r} is not a chosen subset of {self.underlying_set()!r}"
        first_rule = self._set_object_data.membership_rule
        second_rule = other._set_object_data.membership_rule
        return self.underlying_set().subset_from(
            lambda datum: combine(first_rule(datum), second_rule(datum))
        )


class ChosenSubsetsCategory(FullSubcategory[[Rule], []]):
    """``Sets().ChosenSubsets()``: the construction family of the chosen subsets; owns their construction and retains each presenting monomorphism."""

    ObjectType = ChosenSubsetObject

    class ElementType:
        """A generalized element of a chosen subset."""

    class MorphismType:
        """A map between chosen subsets."""

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        super().__init__(ambient)

    def name(self) -> str:
        return "ChosenSubsets"

    def construction_owner(self) -> Category:
        """Chosen subsets own their construction surface: ``from_enumeration`` and ``with_cardinality``."""
        return self

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.{self.name()}()"

    def with_cardinality(
        self,
        base_set: SetObject,
        predicate: MembershipRule,
        cardinality: CardinalObject,
    ) -> SetObject:
        """The chosen subset ``{x in X : predicate(x)}`` whose exact cardinality a construction theorem supplies (POL-SET-031)."""
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        subset = sets.with_cardinality(
            _restricted_rule(base_set, predicate), cardinality
        )
        refine(subset, self)
        return self._retain_monomorphism(subset, base_set)

    def from_enumeration(
        self, base_set: SetObject, members: tuple[Datum, ...]
    ) -> SetObject:
        """The chosen subset of ``X`` with the given finite enumeration of member data, each admitted by ``X``."""
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        base_rule = base_set._set_object_data.membership_rule
        assert all(base_rule(member) is not False for member in members), (
            f"{members!r} are not all members of {base_set!r}"
        )
        subset = sets.Finite().from_enumeration(members)
        refine(subset, self)
        return self._retain_monomorphism(subset, base_set)

    @cached_method(key=lambda self, subset: (id(subset), subset))
    def characteristic_morphism_of(self, subset: SetObject) -> SetMap:
        """``chi_A``, retained per chosen subset."""
        sets = _sets.Sets()
        rule = subset._set_object_data.membership_rule

        def indicator(datum: Datum) -> Datum:
            decision = rule(datum)
            assert decision is not Unknown, (
                f"membership of {datum!r} in {subset!r} is not decided, so its characteristic morphism has no value there"
            )
            return 1 if decision else 0

        return sets.morphism_category(1)(subset.underlying_set(), sets.Simplex(1))(
            indicator
        )

    def __call__(self, base_set: SetObject, predicate: MembershipRule) -> SetObject:
        """The chosen subset ``{x in X : predicate(x)}`` with its monomorphism into ``X``."""
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        finite = sets.Finite()
        if finite.has_chosen_enumeration(base_set):
            decided = tuple(
                (datum, predicate(datum))
                for datum in finite.chosen_enumeration(base_set)
            )
            if all(decision is not Unknown for _, decision in decided):
                subset = finite(tuple(datum for datum, decision in decided if decision))
                refine(subset, self)
                return self._retain_monomorphism(subset, base_set)
        subset = sets(_restricted_rule(base_set, predicate))
        refine(subset, self)
        if is_placed(base_set, finite):
            # A subset of a finite set is finite: Mathlib ``Set.Finite.subset``
            # (Mathlib.Data.Set.Finite.Basic; inspected 2026-08-26).
            finite(subset)
        elif is_placed(base_set, sets.Countable()):
            # A subset of a countable set is countable: Mathlib ``Set.Countable.mono``
            # (Mathlib.Data.Set.Countable; inspected 2026-08-26).
            sets.Countable()(subset)
        return self._retain_monomorphism(subset, base_set)

    @cached_method(key=lambda self, set_map: (id(set_map), set_map))
    def image_of(self, set_map: SetMap) -> SetObject:
        """``f.image()``: the chosen subset of the codomain of the points with a preimage, retained per map."""
        sets = _sets.Sets()
        finite, countable, monomorphisms = (
            sets.Finite(),
            sets.Countable(),
            sets.morphism_category(1).Monomorphisms(),
        )
        assert set_map in sets.morphism_category(1), f"{set_map!r} is not a set map"
        domain, codomain = set_map.domain(), set_map.codomain()
        codomain_rule = codomain._set_object_data.membership_rule
        if finite.has_chosen_enumeration(domain):
            rule = set_map._set_morphism_data.rule
            images = tuple(rule(datum) for datum in finite.chosen_enumeration(domain))
            distinct = _distinct(images)
            if distinct is not Unknown:
                # The image of a finite set is finite (Mathlib ``Set.Finite.image``): the
                # distinct image data, each pairwise comparison exact.
                subset = finite(distinct)
                refine(subset, self)
                return self._retain_monomorphism(subset, codomain)

            def has_preimage(datum: Datum) -> Decision:
                in_codomain = codomain_rule(datum)
                if established(negation(in_codomain)):
                    return False
                return ask(
                    conjunction(
                        (in_codomain, disjunction(image == datum for image in images))
                    )
                )

        else:

            def has_preimage(datum: Datum) -> Decision:
                in_codomain = codomain_rule(datum)
                if established(negation(in_codomain)):
                    return False
                return Unknown

        cardinality = ask(domain.cardinality()) if set_map in monomorphisms else Unknown
        subset = (
            sets(has_preimage)
            if cardinality is Unknown
            else sets.with_cardinality(has_preimage, cardinality)
        )
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
        return self._retain_monomorphism(subset, codomain)

    def _retain_monomorphism(self, subset: SetObject, base_set: SetObject) -> SetObject:
        # The monomorphism of a subset is injective: Mathlib ``Set.inclusion_injective``
        # (Mathlib.Data.Set.Inclusion; inspected 2026-08-26).
        monomorphisms = (
            _sets.Sets().morphism_category(1)(subset, base_set).Monomorphisms()
        )
        self.retain_datum(subset, monomorphisms(lambda datum: datum))
        return subset


class ChosenQuotientObject:
    """The local object role of ``Sets().ChosenQuotients()``: a set that retains its quotient map."""

    def quotient_map(self) -> SetMap:
        """The retained quotient epimorphism ``X -> X/~``."""
        return _sets.Sets().ChosenQuotients().retained_datum(self)

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

    ObjectType = ChosenQuotientObject

    class ElementType:
        """A generalized element of a chosen quotient."""

    class MorphismType:
        """A map between chosen quotients."""

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        super().__init__(ambient)

    def name(self) -> str:
        return "ChosenQuotients"

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.{self.name()}()"

    def __call__(
        self,
        base_set: SetObject,
        class_of: Callable[[Datum], Datum],
        membership_rule: MembershipRule,
    ) -> SetObject:
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        finite = sets.Finite()
        if finite.has_chosen_enumeration(base_set):
            classes = tuple(
                class_of(datum) for datum in finite.chosen_enumeration(base_set)
            )
            distinct = _distinct(classes)
            if distinct is not Unknown:
                quotient = finite(distinct)
                refine(quotient, self)
                return self._retain_quotient_map(base_set, quotient, class_of)
        quotient = sets.rule_valued(membership_rule, Unknown)
        refine(quotient, self)
        return self._retain_quotient_map(base_set, quotient, class_of)

    def _retain_quotient_map(
        self,
        base_set: SetObject,
        quotient: SetObject,
        class_of: Callable[[Datum], Datum],
    ) -> SetObject:
        epimorphisms = (
            _sets.Sets().morphism_category(1)(base_set, quotient).Epimorphisms()
        )
        self.retain_datum(quotient, epimorphisms(class_of))
        return quotient
