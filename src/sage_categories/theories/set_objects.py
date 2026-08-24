"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from itertools import count
from typing import TYPE_CHECKING, Annotated, Any

from sage_categories.abstract_categories.hom_categories import (
    is_restricted_hom_category,
)
from sage_categories.category import Category
from sage_categories.descriptors import ParameterRole
from sage_categories.theories.cardinals import (
    Aleph0,
    Cardinal,
    Cardinals,
    UnknownCardinality,
    aleph,
)
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalElement,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.posets import (
        PosetObject,
    )


from sage_categories.theories.set_elements import (
    MembershipPredicate,
    SetElement,
    SetElements,
)

if TYPE_CHECKING:
    from sage_categories.theories.set_category import (
        FiniteSetsCategory,
    )
    from sage_categories.theories.set_coproducts import SetCoproductObject
    from sage_categories.theories.set_homs import SetHomCategory
    from sage_categories.theories.set_products import SetProductObject
    from sage_categories.theories.set_subobjects import (
        SetSubset,
    )


class SetObject(MathematicalObject):
    """The implementation shared by arbitrary owned sets."""

    def __init__(
        self,
        *,
        category: Category | None = None,
        cardinality: Cardinal | None = None,
    ) -> None:
        from sage_categories.theories.set_category import _category_for_cardinality

        self._cardinality = UnknownCardinality() if cardinality is None else cardinality
        self._subset_poset: PosetObject | None = None
        owner = _category_for_cardinality(self._cardinality) if category is None else category
        super().__init__(category=owner)

    def membership(self, member: SetElement) -> Decision:
        """Return the represented membership decision for ``member``."""
        assert False, f"{self} has no represented membership predicate"

    def element(
        self,
        value: Annotated[MathematicalObject, ParameterRole.VALUE],
    ) -> SetElement:
        """Return the represented element with semantic value ``value``."""
        assert False, f"{self} has no represented element constructor for {value}"

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        if value is None or not SetElements().contains_set_element(value):
            return False
        answer = self.membership(value)
        assert answer is not UNKNOWN, f"membership in {self} is unknown"
        return answer

    def cardinality(self) -> Cardinal:
        return self._cardinality

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> SetHomCategory:
        from sage_categories.theories.set_category import Sets

        assert codomain is None
        assert Sets().contains_set(domain)
        return Sets().Hom(self, domain)

    def is_finite(self) -> Decision:
        return self.cardinality().is_finite()

    def is_infinite(self) -> Decision:
        return self.cardinality().is_infinite()

    def is_countable(self) -> Decision:
        return self.cardinality().is_countable()

    def is_uncountable(self) -> Decision:
        return self.cardinality().is_uncountable()

    def __iter__(self) -> Iterator[SetElement]:
        assert False, f"{self} has no chosen enumeration"

    def exponential(self, exponent: SetObject) -> SetHomCategory:
        from sage_categories.theories.set_constructions import ExponentialOfSets

        return ExponentialOfSets(self, exponent)

    def __pow__(self, exponent: SetObject) -> SetHomCategory:

        return self.exponential(exponent)

    def powerset(self) -> SetHomCategory:
        from sage_categories.theories.set_constructions import PowerSet

        return PowerSet(self)

    def subset_poset(self) -> PosetObject:
        from sage_categories.theories.set_subobjects import SubsetsOfSet

        if self._subset_poset is None:
            from sage_categories.theories.posets import PartiallyOrderedSets

            powerset = self.powerset()
            subsets = SubsetsOfSet(self)

            def contained(left: SetElement, right: SetElement) -> Decision:
                assert subsets.contains_subset(left)
                assert subsets.contains_subset(right)
                return left <= right

            self._subset_poset = PartiallyOrderedSets().from_theorem(
                powerset,
                Sets().relation(
                    powerset,
                    Sets().binary_predicate(powerset, contained),
                ),
                self,
            )
        return self._subset_poset

    def subsets_of_size(self, size: int) -> SetObject:
        from sage_categories.theories.finite_subset_sets import SubsetsOfSize

        return SubsetsOfSize(self, size)

    def finite_subsets(self) -> SetObject:
        from sage_categories.theories.finite_subset_sets import FiniteSubsets

        return FiniteSubsets(self)

    def subset_from(
        self,
        predicate: MembershipPredicate,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetSubset:
        from sage_categories.theories.set_constructions import PowerSet

        return PowerSet(self).from_predicate(
            predicate,
            cardinality=cardinality,
        )

    def cartesian_product(self, *others: SetObject) -> SetProductObject:
        from sage_categories.theories.set_constructions import CartesianProductOfSets

        return CartesianProductOfSets((self, *others))

    def disjoint_union(self, *others: SetObject) -> SetCoproductObject:
        from sage_categories.theories.set_constructions import DisjointUnionOfSets

        return DisjointUnionOfSets((self, *others))

    def __eq__(self, candidate: Any) -> bool:
        return candidate is self

    def __hash__(self) -> int:
        return id(self)


class FiniteSetElement(SetElement):
    """An element of a finite set."""

    def __init__(
        self,
        *,
        ambient_object: FiniteSetObject,
        value: MathematicalObject,
    ) -> None:
        self._value = value
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def value(self) -> Annotated[MathematicalObject, ParameterRole.VALUE]:
        return self._value

    def __repr__(self) -> str:
        return repr(self._value)


class FiniteSetObject(SetObject):
    """A set given by its complete finite member set."""

    def __init__(
        self,
        *,
        category: Category,
        values: frozenset[MathematicalObject],
    ) -> None:

        self._values = values
        super().__init__(
            category=category,
            cardinality=Cardinals()(len(values)),
        )
        self._members = frozenset(
            FiniteSetElement(ambient_object=self, value=value)
            for value in values
        )

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def __iter__(self) -> Iterator[SetElement]:
        return iter(self._members)

    def _represented_members(self) -> frozenset[SetElement]:
        return self._members

    def element(
        self,
        value: Annotated[MathematicalObject, ParameterRole.VALUE],
    ) -> FiniteSetElement:
        assert value in self._values
        return next(member for member in self._members if member.value() == value)

    def __getitem__(self, position: int) -> SetElement:
        assert position >= 0
        return tuple(self._members)[position]

    def position(self, member: SetElement) -> int:
        assert member in self
        return tuple(self._members).index(member)

    def enumeration_injection(self) -> Arrow:
        return EnumerationInjection(self, self.position)

    def __repr__(self) -> str:
        return "{" + ", ".join(map(repr, self._values)) + "}"


class NaturalNumberElement(SetElement):
    """A finite ordinal as an element of the natural numbers."""

    def __init__(
        self,
        *,
        ambient_object: NaturalNumbersSet,
        ordinal_value: MathematicalObject,
    ) -> None:
        self._ordinal = ordinal_value
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def value(self) -> MathematicalObject:
        return self._ordinal

    def __repr__(self) -> str:
        return repr(self._ordinal)


class NaturalNumbersSet(SetObject):
    """The set of finite ordinals."""

    def __init__(self) -> None:
        from sage_categories.theories.set_category import Sets

        self._members: dict[int, NaturalNumberElement] = {}
        super().__init__(category=Sets(), cardinality=Aleph0())

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def element(self, ordinal_value: MathematicalObject) -> NaturalNumberElement:
        from sage_categories.theories.ordinals import OrdinalKind, Ordinals

        assert Ordinals().contains_ordinal(ordinal_value)
        assert ordinal_value.kind() is OrdinalKind.FINITE
        position = ordinal_value.finite_value()
        member = self._members.get(position)
        if member is None:
            member = NaturalNumberElement(
                ambient_object=self,
                ordinal_value=ordinal_value,
            )
            self._members[position] = member
        return member

    def __iter__(self) -> Iterator[SetElement]:
        from sage_categories.theories.ordinals import ordinal

        return iter(self.element(ordinal(index)) for index in count())

    def __getitem__(self, position: int) -> SetElement:
        from sage_categories.theories.ordinals import ordinal

        assert position >= 0
        return self.element(ordinal(position))

    def position(self, member: SetElement) -> int:
        assert member in self
        return next(position for position, candidate in self._members.items() if candidate is member)

    def __repr__(self) -> str:
        return "Natural numbers"


_NATURAL_NUMBERS: MathematicalObject | None = None


def NaturalNumbers() -> MathematicalObject:
    global _NATURAL_NUMBERS

    if _NATURAL_NUMBERS is None:
        from sage_categories.theories.set_category import CountableSets

        _NATURAL_NUMBERS = CountableSets().refine_from_theorem(
            NaturalNumbersSet(),
            Sets(),
        )
    return _NATURAL_NUMBERS


def EnumerationInjection(
    source: SetObject,
    position: Callable[[SetElement], int],
) -> Arrow:
    from sage_categories.theories.ordinals import ordinal
    from sage_categories.theories.set_category import (
        Sets,
        _set_morphism,
    )

    function = _set_morphism(
        source,
        NaturalNumbers(),
        lambda member: NaturalNumbers().element(ordinal(position(member))),
        injective=True,
    )
    monomorphisms = Sets().Mono(source, NaturalNumbers())
    assert is_restricted_hom_category(monomorphisms)
    return monomorphisms(function)


class AlephIndexing:
    """The aleph cardinals at finite ordinal indices."""

    def __getitem__(self, index: int) -> Cardinal:
        assert index >= 0
        return aleph(index)

    def __repr__(self) -> str:
        return "ℵ"


Aleph = AlephIndexing()
