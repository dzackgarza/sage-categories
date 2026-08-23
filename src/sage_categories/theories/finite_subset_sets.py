"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Iterator
from itertools import combinations
from math import comb

from sage_categories.theories.cardinals import (
    Cardinal,
    Cardinals,
    cardinal,
)
from sage_categories.theories.set_category import (
    Sets,
    _set_morphism,
)
from sage_categories.theories.set_constructions import (
    PowerSet,
)
from sage_categories.theories.set_elements import (
    SetElement,
    SetElementFamily,
)
from sage_categories.theories.set_homs import (
    SetHomCategory,
)
from sage_categories.theories.set_objects import (
    SetObject,
)
from sage_categories.theories.set_subobjects import (
    SetMorphism,
    SetSubset,
    SubsetsOfSet,
)
from sage_categories.values import (
    UNKNOWN,
    Decision,
    registered_value,
)


class FixedCardinalitySubsetSet(SetObject):
    """The set of subsets with one fixed finite cardinality."""

    def __init__(self, source: SetObject, subset_cardinality: int) -> None:
        assert subset_cardinality >= 0
        self._source = source
        self._subset_cardinality = subset_cardinality
        size: Cardinal | None = None
        if subset_cardinality == 0:
            size = cardinal(1)
        elif source.is_finite() is True:
            size = cardinal(comb(int(source.cardinality()), subset_cardinality))
        elif source.is_infinite() is True:
            size = source.cardinality()
        super().__init__(cardinality=size)

    def source(self) -> SetObject:
        return self._source

    def powerset(self) -> SetHomCategory:
        return PowerSet(self._source)

    def subset_cardinality(self) -> int:
        return self._subset_cardinality

    def membership(self, candidate: SetElement) -> Decision:
        if not SubsetsOfSet(self._source).contains_subset(candidate):
            return False
        return candidate.underlying_set().cardinality() == self._subset_cardinality

    def __iter__(self) -> Iterator[SetElement]:
        size = self._subset_cardinality
        if size == 0:
            yield self.powerset().bottom()
            return
        preceding: list[SetElement] = []
        for maximum in self._source:
            if len(preceding) >= size - 1:
                for initial in combinations(preceding, size - 1):
                    yield self.powerset().from_members(frozenset((*initial, maximum)))
            preceding.append(maximum)

    def __getitem__(self, position: int) -> SetSubset:
        assert position >= 0
        for index, candidate in enumerate(self):
            if index == position:
                value = registered_value(candidate)
                assert value is not None
                assert SubsetsOfSet(self._source).contains_subset(value)
                return value
        assert False, f"{position} is outside {self}"

    def __repr__(self) -> str:
        return f"Subsets of {self._source} of cardinality {self._subset_cardinality}"


class FiniteSubsetSet(SetObject):
    """The set of finite subsets of one set."""

    def __init__(self, source: SetObject) -> None:
        self._source = source
        size: Cardinal | None = None
        if source.is_finite() is True:
            size = cardinal(2) ** source.cardinality()
        elif source.is_infinite() is True:
            size = source.cardinality()
        super().__init__(cardinality=size)

    def source(self) -> SetObject:
        return self._source

    def powerset(self) -> SetHomCategory:
        return PowerSet(self._source)

    def membership(self, candidate: SetElement) -> Decision:
        if not SubsetsOfSet(self._source).contains_subset(candidate):
            return False
        return candidate.underlying_set().cardinality().is_finite()

    def __iter__(self) -> Iterator[SetElement]:
        powerset = self.powerset()
        yield powerset.bottom()
        preceding: list[SetElement] = []
        for maximum in self._source:
            for size in range(len(preceding) + 1):
                for initial in combinations(preceding, size):
                    yield powerset.from_members(frozenset((*initial, maximum)))
            preceding.append(maximum)

    def position(self, subset: SetSubset) -> int:
        assert subset in self
        for position, candidate in enumerate(self):
            value = registered_value(candidate)
            assert value is not None
            assert SubsetsOfSet(self._source).contains_subset(value)
            if value == subset:
                return position
        assert False, f"{subset} has no position in the chosen enumeration"

    def __getitem__(self, position: int) -> SetSubset:
        assert position >= 0
        for index, candidate in enumerate(self):
            if index == position:
                value = registered_value(candidate)
                assert value is not None
                assert SubsetsOfSet(self._source).contains_subset(value)
                return value
        assert False, f"{position} is outside {self}"

    def __repr__(self) -> str:
        return f"Finite subsets of {self._source}"


_FIXED_CARDINALITY_SUBSETS: dict[tuple[int, int], FixedCardinalitySubsetSet] = {}
_FINITE_SUBSETS: dict[int, FiniteSubsetSet] = {}


def SubsetsOfSize(
    base_set: SetObject,
    size: int,
) -> FixedCardinalitySubsetSet:
    key = id(base_set), size
    cached = _FIXED_CARDINALITY_SUBSETS.get(key)
    if cached is None:
        cached = FixedCardinalitySubsetSet(base_set, size)
        _FIXED_CARDINALITY_SUBSETS[key] = cached
    return cached


def FiniteSubsets(base_set: SetObject) -> FiniteSubsetSet:
    key = id(base_set)
    cached = _FINITE_SUBSETS.get(key)
    if cached is None:
        cached = FiniteSubsetSet(base_set)
        _FINITE_SUBSETS[key] = cached
    return cached


_FUNCTION_SUPPORTS: dict[int, SetSubset] = {}


class FinitelySupportedFunctionSet(SetObject):
    """Functions from an index set into a pointed set with finite support."""

    def __init__(
        self,
        index_set: SetObject,
        value_set: SetObject,
        basepoint: SetElement,
    ) -> None:
        assert basepoint in value_set
        self._index_set = index_set
        self._value_set = value_set
        self._basepoint = basepoint
        super().__init__(
            cardinality=self._construction_cardinality(),
        )

    def index_set(self) -> SetObject:
        return self._index_set

    def value_set(self) -> SetObject:
        return self._value_set

    def basepoint(self) -> SetElement:
        return self._basepoint

    def _construction_cardinality(self) -> Cardinal | None:
        value_cardinality = self._value_set.cardinality()
        index_cardinality = self._index_set.cardinality()
        if value_cardinality == 1 or index_cardinality == 0:
            return cardinal(1)
        if index_cardinality.is_finite() is True:
            return Cardinals().power(value_cardinality, index_cardinality)
        if index_cardinality.is_infinite() is True:
            return Cardinals().supremum(value_cardinality, index_cardinality)
        return None

    def __call__(
        self,
        action: SetElementFamily,
        *,
        support: SetSubset,
    ) -> SetMorphism:
        assert support in FiniteSubsets(self._index_set)

        def finitely_supported_action(index: SetElement) -> SetElement:
            supported = support.membership(index)
            assert supported is not UNKNOWN
            if supported:
                value = action(index)
                assert value != self._basepoint
                return value
            return self._basepoint

        function = _set_morphism(
            self._index_set,
            self._value_set,
            finitely_supported_action,
        )
        _FUNCTION_SUPPORTS[id(function)] = support
        assert function in self
        return function

    def support(self, function: SetMorphism) -> SetSubset:
        assert function in self
        support = _FUNCTION_SUPPORTS.get(id(function))
        assert support is not None
        return support

    def membership(self, candidate: SetElement) -> Decision:
        if candidate not in Sets().Hom(self._index_set, self._value_set):
            return False
        support = _FUNCTION_SUPPORTS.get(id(candidate))
        if support is None:
            return UNKNOWN
        return support in FiniteSubsets(self._index_set)

    def __repr__(self) -> str:
        return f"Finitely supported functions {self._index_set} -> {self._value_set}"


_FINITELY_SUPPORTED_FUNCTION_SETS: dict[
    tuple[int, int, int],
    FinitelySupportedFunctionSet,
] = {}


def FinitelySupportedFunctions(
    index_set: SetObject,
    value_set: SetObject,
    basepoint: SetElement,
) -> FinitelySupportedFunctionSet:
    key = id(index_set), id(value_set), id(basepoint)
    cached = _FINITELY_SUPPORTED_FUNCTION_SETS.get(key)
    if cached is None:
        cached = FinitelySupportedFunctionSet(index_set, value_set, basepoint)
        _FINITELY_SUPPORTED_FUNCTION_SETS[key] = cached
    return cached


def _image_subobject(
    function: SetMorphism,
    *,
    cardinality: Cardinal | None = None,
) -> SetSubset:
    domain = function.domain()
    codomain = function.codomain()
    assert Sets().contains_set(domain)
    assert Sets().contains_set(codomain)
    if function.is_surjective() is True:
        return PowerSet(codomain).top()
    if domain.cardinality() == 0:
        return PowerSet(codomain).bottom()
    size = cardinality
    if size is None and function.is_injective() is True:
        size = domain.cardinality()
    return PowerSet(codomain).from_predicate(
        lambda member: _imagemembership(function, member),
        cardinality=size,
    )


def _imagemembership(
    function: SetMorphism,
    member: SetElement,
) -> Decision:
    codomain = function.codomain()
    assert Sets().contains_set(codomain)
    if codomain.membership(member) is False:
        return False
    return UNKNOWN
