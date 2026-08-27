"""Finite subsets, fixed-size subsets, and finitely supported functions (``specs/sets.md``, "Finite and fixed-cardinality subsets", "Finitely supported function sets").

``Sets().FiniteSubsets()(X)`` is the set of finite subsets of ``X``; its points select
finite chosen subobjects of ``X`` (``subset_at``), and each finite enumerated chosen
subset of ``X`` selects a point (``point_of``).  A point's private datum is the
frozen set of the member data, so two points are equal exactly when their subsets
have the same members.  ``Sets().SubsetsOfSize(k)`` is the narrowing of
``Sets().FiniteSubsets()`` on the sets of subsets of one size ``k``.

A chosen enumeration of ``X`` induces one on its subsets: Sage's
``sage.combinat.subset.Subsets`` is the private enumeration engine (``rank`` and
``unrank`` in its order; inspected 2026-08-27), so ``S[n]`` and ``S.index(A)`` exist
exactly when ``X`` has a chosen enumeration; countability alone selects none.

Cardinality is a computational case tree routed on the base set's cardinality
(POL-MATH-042), each case citing its theorem (all Mathlib, inspected 2026-08-27):

- all finite subsets of a finite ``X``: ``2 ** #X`` (``Finset.card_powerset``;
  ``Cardinal.mk_set``);
- all finite subsets of an infinite ``X``: ``#X`` (``Cardinal.mk_finset_of_infinite``);
- subsets of size ``k`` of a finite ``X``: the binomial coefficient
  (``Finset.card_powersetCard``, ``Fintype.card_finset_len``);
- subsets of size ``k >= 1`` of an infinite ``X``: ``#X``, since the subsets of
  size ``k`` embed in ``Finset X`` of cardinality ``#X``
  (``Cardinal.mk_subtype_le``, ``Cardinal.mk_finset_of_infinite``) and ``X`` less a
  fixed subset of size ``k - 1`` (``Cardinal.mk_compl_finset_of_infinite``) embeds
  in them by ``x |-> s ∪ {x}`` (``Cardinal.mk_le_of_injective``), so the two are
  equal (``Cardinal.le_antisymm``); of size ``0``: ``1``;
- otherwise ``Unknown``.

A subset of a countable set is countable and the finite subsets of a countable
set are countable (``Finset.countable``), so the sets are placed in
``Sets().Countable()`` when the base set is.

``Sets().FinitelySupportedFunctions()(S, x0)`` for a point ``x0`` of ``X`` is the
chosen subset ``X^(S)`` of the function set ``X ** S`` of the maps whose support
``{s : f(s) != x0}`` is finite, retaining its inclusion, with ``index_set()``,
``value_set()``, and ``basepoint()`` (Mathlib ``Finsupp``).  Its cardinality: for a
finite index set every function is finitely supported, so ``(#X) ** (#S)``
(``Cardinal.mk_finsupp_lift_of_fintype``); for an infinite index set and ``#X >= 2``,
``sup(#S, #X)`` (``Cardinal.mk_finsupp_of_infinite``); for ``#X = 1`` the one
constant function; otherwise ``Unknown``.  Membership of a name of a map decides
``True`` when the index set has a chosen enumeration (every support is then
finite) and is ``Unknown`` otherwise.
"""

from __future__ import annotations

from sage.arith.misc import binomial
from sage.combinat.subset import Subsets
from sage.structure.coerce_dict import MonoDict, TripleDict

import sage_categories.sets.category as _sets
from sage_categories.cat.category import Category
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass, decision_and
from sage_categories.kernel.predicates import ask
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ObjectOfCategory, Role
from sage_categories.sets.cardinals import Cardinal, CardinalObject
from sage_categories.sets.elements import Datum, SetPoint
from sage_categories.sets.exponentials import Function
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import SetObject

__all__ = [
    "FiniteSubsetsCategory",
    "FiniteSubsetsRole",
    "FinitelySupportedFunctionsCategory",
    "FinitelySupportedFunctionsRole",
    "SizedSubsetsCategory",
    "SizedSubsetsRole",
]


def _position(position: CardinalObject | int) -> int:
    """A position in an enumeration lowered to the engine's integer at the private boundary."""
    if position in Cardinal():
        return position._finite_value_()
    return position


class FiniteSubsetsRole(ObjectOfCategory):
    """The local object role of ``Sets().FiniteSubsets()``: a set of finite subsets of a base set."""

    def base_set(self) -> SetObject:
        return _sets.Sets().FiniteSubsets().retained_base_set(self)

    def subset_at(self, point: SetPoint) -> SetObject:
        """The finite chosen subobject of the base set that a point selects, retained per point."""
        return _sets.Sets().FiniteSubsets().subset_at(self, point)

    def point_of(self, subset: SetObject) -> SetPoint:
        """The point selecting a finite enumerated chosen subset of the base set."""
        return _sets.Sets().FiniteSubsets().point_of(self, subset)

    def index(self, subset: SetObject) -> CardinalObject:
        """The position of a subset in the induced enumeration."""
        return _sets.Sets().FiniteSubsets().index(self, subset)

    def __getitem__(self, position: CardinalObject | int) -> SetObject:
        """``S[n]``: the subset at position ``n`` of the induced enumeration."""
        return _sets.Sets().FiniteSubsets().subset_at_position(self, position)


class SizedSubsetsRole(ObjectOfCategory):
    """The local object role of ``Sets().SubsetsOfSize(k)``: the common size of the subsets."""

    def subset_cardinality(self) -> CardinalObject:
        return _sets.Sets().FiniteSubsets().retained_size(self)


class SizedSubsetsCategory(PropertySubcategory[[Rule], []]):
    """``Sets().SubsetsOfSize(k)``: the sets of subsets of one size ``k``, a narrowing of ``Sets()``; ``(X)`` constructs the subsets of ``X`` of size ``k``."""

    def __init__(self, ambient: Category[[Rule], []], size: int) -> None:
        assert size >= 0
        self._size = size
        super().__init__(ambient, f"SubsetsOfSize({size})", {Role.OBJECT: SizedSubsetsRole}, ())

    def size(self) -> CardinalObject:
        return Cardinal()(self._size)

    def __call__(self, base_set: SetObject) -> SetObject:
        return self._ambient.FiniteSubsets().of_size(self._size, base_set)


class FiniteSubsetsCategory(PropertySubcategory[[Rule], []]):
    """``Sets().FiniteSubsets()``: the sets of finite subsets of a set, a narrowing of ``Sets()``; owns their construction and enumeration engines."""

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        self._objects: MonoDict = MonoDict()
        self._sized_objects: TripleDict = TripleDict(weak_values=False)
        self._base_sets: MonoDict = MonoDict()
        self._engines: MonoDict = MonoDict()
        self._sizes: MonoDict = MonoDict()
        self._subsets: MonoDict = MonoDict()
        super().__init__(ambient, "FiniteSubsets", {Role.OBJECT: FiniteSubsetsRole}, ())

    # -- construction -----------------------------------------------------------------

    def __call__(self, base_set: SetObject) -> SetObject:
        """The set of finite subsets of ``X``, retained per ``X``."""
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        if base_set not in self._objects:
            self._objects[base_set] = self._construct(base_set, Unknown)
        return self._objects[base_set]

    def of_size(self, size: int, base_set: SetObject) -> SetObject:
        """``Sets().SubsetsOfSize(k)(X)``: the set of subsets of ``X`` of size ``k``, retained per pair."""
        sets = _sets.Sets()
        assert base_set in sets, f"{base_set!r} is not an object of {sets!r}"
        sized = sets.SubsetsOfSize(size)
        key = (sized, base_set, self)
        if key not in self._sized_objects:
            subsets = self._construct(base_set, size)
            self._sizes[subsets] = sized.size()
            refine(subsets, sized)
            self._sized_objects[key] = subsets
        return self._sized_objects[key]

    def _construct(self, base_set: SetObject, size: int | UnknownClass) -> SetObject:
        sets = _sets.Sets()
        finite = sets.Finite()
        if finite.has_chosen_enumeration(base_set):
            enumeration = list(finite.chosen_enumeration(base_set))
            engine = Subsets(enumeration) if size is Unknown else Subsets(enumeration, size)
            subsets = finite(tuple(frozenset(members) for members in engine))
            self._engines[subsets] = engine
        else:
            base_rule = base_set._set_object_data.membership_rule

            def membership_rule(datum: Datum) -> Decision:
                match datum:
                    case frozenset() if size is Unknown or len(datum) == size:
                        return decision_and(*(base_rule(member) for member in datum))
                    case _:
                        return False

            cardinality = self._cardinality(base_set.cardinality(), size)
            subsets = sets(membership_rule) if cardinality is Unknown else sets.with_cardinality(membership_rule, cardinality)
            if base_set in sets.Countable():
                # Mathlib ``Finset.countable``: the finite subsets of a countable type are countable.
                sets.Countable()(subsets)
        refine(subsets, self)
        self._base_sets[subsets] = base_set
        return subsets

    def _cardinality(self, base_cardinality: CardinalObject | UnknownClass, size: int | UnknownClass) -> CardinalObject | UnknownClass:
        """The case tree of the module docstring, for a base set without a chosen enumeration."""
        cardinals = Cardinal()
        if base_cardinality is Unknown:
            return Unknown
        if ask(base_cardinality.is_finite()) is True:
            if size is Unknown:
                # Finset.card_powerset, Cardinal.mk_set.
                return cardinals(2) ** base_cardinality
            # Finset.card_powersetCard, Fintype.card_finset_len; the engine's integer is lowered to
            # the Python integer that keys every finite cardinal.
            return cardinals(int(binomial(base_cardinality._finite_value_(), size)))
        if size is Unknown:
            # Cardinal.mk_finset_of_infinite.
            return base_cardinality
        if size == 0:
            return cardinals(1)
        # The subsets of size k >= 1 of an infinite set: the sandwich of the docstring.
        return base_cardinality

    # -- the retained data ------------------------------------------------------------

    def retained_base_set(self, subsets: SetObject) -> SetObject:
        assert subsets in self._base_sets, f"{subsets!r} retains no base set"
        return self._base_sets[subsets]

    def retained_size(self, subsets: SetObject) -> CardinalObject:
        assert subsets in self._sizes, f"{subsets!r} retains no subset size"
        return self._sizes[subsets]

    def subset_at(self, subsets: SetObject, point: SetPoint) -> SetObject:
        assert point in subsets, f"{point!r} is not a point of {subsets!r}"
        if point not in self._subsets:
            sets = _sets.Sets()
            base_set, members = self.retained_base_set(subsets), point._set_element_data.datum
            if sets.Finite().has_chosen_enumeration(base_set):
                # The induced enumeration lists the members in the order of the base set's.
                members = frozenset(datum for datum in sets.Finite().chosen_enumeration(base_set) if datum in members)
            self._subsets[point] = sets.ChosenSubsets().from_enumeration(base_set, tuple(members))
        return self._subsets[point]

    def point_of(self, subsets: SetObject, subset: SetObject) -> SetPoint:
        sets = _sets.Sets()
        base_set = self.retained_base_set(subsets)
        assert subset in sets.ChosenSubsets() and subset.underlying_set() is base_set, f"{subset!r} is not a chosen subset of {base_set!r}"
        assert sets.Finite().has_chosen_enumeration(subset), f"{subset!r} has no chosen enumeration"
        return subsets.point(frozenset(sets.Finite().chosen_enumeration(subset)))

    def index(self, subsets: SetObject, subset: SetObject) -> CardinalObject:
        assert subsets in self._engines, f"{self.retained_base_set(subsets)!r} has no chosen enumeration, so {subsets!r} has no induced enumeration"
        return Cardinal()(self._engines[subsets].rank(self.point_of(subsets, subset)._set_element_data.datum))

    def subset_at_position(self, subsets: SetObject, position: CardinalObject | int) -> SetObject:
        assert subsets in self._engines, f"{self.retained_base_set(subsets)!r} has no chosen enumeration, so {subsets!r} has no induced enumeration"
        return self.subset_at(subsets, subsets.point(frozenset(self._engines[subsets].unrank(_position(position)))))


class FinitelySupportedFunctionsRole(ObjectOfCategory):
    """The local object role of ``Sets().FinitelySupportedFunctions()``: the retained index set, value set, and basepoint."""

    def index_set(self) -> SetObject:
        return _sets.Sets().FinitelySupportedFunctions().retained_index_set(self)

    def value_set(self) -> SetObject:
        return _sets.Sets().FinitelySupportedFunctions().retained_basepoint(self).parent()

    def basepoint(self) -> SetPoint:
        return _sets.Sets().FinitelySupportedFunctions().retained_basepoint(self)


class FinitelySupportedFunctionsCategory(PropertySubcategory[[Rule], []]):
    """``Sets().FinitelySupportedFunctions()``: the sets ``X^(S)`` of finitely supported maps, a narrowing of ``Sets()``; owns their construction."""

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        self._objects: TripleDict = TripleDict(weak_values=False)
        self._index_sets: MonoDict = MonoDict()
        self._basepoints: MonoDict = MonoDict()
        super().__init__(ambient, "FinitelySupportedFunctions", {Role.OBJECT: FinitelySupportedFunctionsRole}, ())

    def __call__(self, index_set: SetObject, basepoint: SetPoint) -> SetObject:
        """``X^(S)`` for the pointed set ``(X, x0)`` with ``x0`` a point of ``X``, retained per pair."""
        sets = _sets.Sets()
        assert index_set in sets, f"{index_set!r} is not an object of {sets!r}"
        value_set = basepoint.parent()
        assert basepoint in value_set, f"{basepoint!r} is not a point of {value_set!r}"
        key = (index_set, basepoint, self)
        if key not in self._objects:
            function_set = value_set ** index_set
            enumerated = sets.Finite().has_chosen_enumeration(index_set)

            def finitely_supported(datum: Datum) -> Decision:
                match datum:
                    case Function():
                        return True if enumerated else Unknown
                    case _:
                        return False

            cardinality = self._cardinality(index_set.cardinality(), value_set.cardinality())
            chosen = sets.ChosenSubsets()
            functions = chosen(function_set, finitely_supported) if cardinality is Unknown else chosen.with_cardinality(function_set, finitely_supported, cardinality)
            refine(functions, self)
            self._index_sets[functions] = index_set
            self._basepoints[functions] = basepoint
            self._objects[key] = functions
        return self._objects[key]

    def _cardinality(self, index_cardinality: CardinalObject | UnknownClass, value_cardinality: CardinalObject | UnknownClass) -> CardinalObject | UnknownClass:
        """The case tree of the module docstring."""
        if index_cardinality is Unknown or value_cardinality is Unknown:
            return Unknown
        if ask(index_cardinality.is_finite()) is True:
            # Cardinal.mk_finsupp_lift_of_fintype: every function on a finite index set is finitely supported.
            return value_cardinality**index_cardinality
        if ask(value_cardinality == 1) is True:
            return Cardinal()(1)
        if ask(value_cardinality >= 2) is True:
            # Cardinal.mk_finsupp_of_infinite: #(S →₀ X) = max(#S, #X) for infinite S and nontrivial X.
            return Cardinal().supremum(index_cardinality, value_cardinality)
        return Unknown

    def retained_index_set(self, functions: SetObject) -> SetObject:
        assert functions in self._index_sets, f"{functions!r} retains no index set"
        return self._index_sets[functions]

    def retained_basepoint(self, functions: SetObject) -> SetPoint:
        assert functions in self._basepoints, f"{functions!r} retains no basepoint"
        return self._basepoints[functions]
