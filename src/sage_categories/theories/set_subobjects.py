"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

import builtins
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.functors import (
    InclusionFunctor,
    StructuralFunctor,
)
from sage_categories.abstract_categories.hom_categories import (
    is_restricted_hom_category,
)
from sage_categories.category import Category
from sage_categories.theories.cardinals import (
    Cardinal,
    UnknownCardinality,
    cardinal,
)
from sage_categories.theories.set_elements import (
    MembershipPredicate,
    SetElement,
    SetElements,
    SetIterator,
)
from sage_categories.theories.set_objects import (
    SetObject,
)
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.set_homs import (
        SetHomCategory,
        SetMonomorphism,
    )


class SubsetElement(SetElement):
    """An element of a represented set subobject."""

    def __init__(self, *, ambient_object: SubsetSetObject) -> None:
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def value(self) -> MathematicalObject:
        from sage_categories.theories.set_category import Sets

        ambient = self.ambient_set()
        assert Sets().contains_set(ambient)
        assert ambient is self.ambient_object()
        return self


class SubsetSetObject(SetObject):
    """The domain set of one represented set subobject."""

    def __init__(
        self,
        *,
        base_set: SetObject,
        predicate: MembershipPredicate,
        cardinality: Cardinal,
        iterator: SetIterator | None,
    ) -> None:
        from sage_categories.theories.set_category import Sets

        self._base_set = base_set
        self._predicate = predicate
        self._iterator = iterator
        self._elements: dict[int, SubsetElement] = {}
        self._base_elements: dict[int, SetElement] = {}
        super().__init__(category=Sets(), cardinality=cardinality)

    def _element_(self, base_element: SetElement) -> SubsetElement:
        assert base_element.ambient_set() is self._base_set
        assert self._predicate(base_element) is True
        key = id(base_element)
        element = self._elements.get(key)
        if element is None:
            element = SubsetElement(ambient_object=self)
            self._elements[key] = element
            self._base_elements[id(element)] = base_element
        return element

    def base_element(self, member: SetElement) -> SetElement:
        assert member.ambient_set() is self
        base_element = self._base_elements.get(id(member))
        assert base_element is not None
        return base_element

    def _membership_(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def _set_iterator_(self) -> Iterator[SetElement]:
        assert self._iterator is not None, f"{self} has no chosen enumeration"
        return iter(self.element(member) for member in self._iterator())

    def __repr__(self) -> str:
        return f"Subset of {self._base_set}"


class SetMorphism(Arrow, SetElement):
    """An arbitrary morphism of sets."""

    def __init__(
        self,
        *,
        hom_category: SetHomCategory,
        action: Callable[[SetElement], SetElement],
        injective: Decision = UNKNOWN,
        surjective: Decision = UNKNOWN,
    ) -> None:

        self._action = action
        self._injective = injective
        self._surjective = surjective
        super().__init__(hom_category=hom_category)

    def __call__(self, member: SetElement) -> SetElement:
        from sage_categories.theories.set_category import Sets

        domain = self.domain()
        codomain = self.codomain()
        assert Sets().contains_set(domain)
        assert Sets().contains_set(codomain)
        assert member.ambient_object() in self.base_category()
        assert member.ambient_set() is domain
        assert domain.membership(member) is not False
        image = self._action(member)
        assert image.ambient_object() in self.base_category()
        assert image.ambient_set() is codomain
        assert codomain.membership(image) is not False
        return image

    def _belongs_to(self, category: Category) -> bool:
        return category is SetElements() or super()._belongs_to(category)

    def is_injective(self) -> Decision:
        return self._injective

    def is_surjective(self) -> Decision:
        return self._surjective

    def is_bijective(self) -> Decision:
        return _decision_and(self._injective, self._surjective)

    def image(self) -> SetSubset:
        from sage_categories.theories.finite_subset_sets import _image_subobject

        return _image_subobject(self)

    def inverse(self) -> SetMorphism:
        from sage_categories.theories.set_category import (
            Sets,
            is_set_hom_category,
        )

        assert self.is_bijective() is True
        domain = self.domain()
        codomain = self.codomain()
        assert Sets().contains_set(domain)
        assert Sets().contains_set(codomain)
        assert domain.is_finite() is True
        inverse_values = {self(member): member for member in domain}
        inverse_hom = Sets().Hom(codomain, domain)
        assert is_set_hom_category(inverse_hom)
        return inverse_hom(
            inverse_values,
            injective=True,
            surjective=True,
        )


class SetSubset(SetMorphism):
    """A subset, its characteristic function, and its inclusion arrow."""

    def __init__(
        self,
        *,
        category: SubsetsOfSetCategory,
        hom_category: SetHomCategory,
        predicate: MembershipPredicate,
        underlying_set: SetObject,
        inclusion: SetMonomorphism,
        members: frozenset[SetElement] | None,
    ) -> None:
        from sage_categories.theories.set_category import Sets
        from sage_categories.theories.set_constructions import TruthValues

        assert hom_category.codomain() is TruthValues()
        assert hom_category.domain() is category.base_set()
        assert inclusion in Sets().Mono(underlying_set, category.base_set())
        self._subset_category = category
        self._predicate = predicate
        self._underlying_set = underlying_set
        self._inclusion = inclusion
        self._members = members

        def characteristic_value(member: SetElement) -> SetElement:
            from sage_categories.theories.ordinals import ordinal
            from sage_categories.theories.set_constructions import TruthValues

            answer = predicate(member)
            assert answer is not UNKNOWN, f"membership of {member} in {underlying_set} is unknown"
            return TruthValues().element(ordinal(1 if answer else 0))

        super().__init__(
            hom_category=hom_category,
            action=characteristic_value,
        )

    def category(self) -> Category:
        return self._subset_category

    def _belongs_to(self, category: Category) -> bool:
        return category is SetElements() or self._subset_category is category or self._subset_category.is_subcategory(category)

    def object(self) -> SetObject:
        return self._underlying_set

    def underlying_set(self) -> SetObject:
        return self._underlying_set

    def fixed_object(self) -> SetObject:
        return self.base_set()

    def structure_morphism(self) -> SetMonomorphism:

        return self._inclusion

    def base_set(self) -> SetObject:
        from sage_categories.theories.set_category import Sets

        base = self.domain()
        assert Sets().contains_set(base)
        return base

    def characteristic_morphism(self) -> SetMorphism:
        return self

    def inclusion(self) -> SetMonomorphism:

        return self._inclusion

    def _represented_members(self) -> frozenset[SetElement] | None:
        return self._members

    def membership(self, member: SetElement) -> Decision:
        return self._predicate(member)

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        if value is None or not SetElements().contains_set_element(value):
            return False
        answer = self.membership(value)
        assert answer is not UNKNOWN
        return answer

    def __eq__(self, candidate: builtins.object) -> bool:
        value = registered_value(candidate)
        if value is None or not SubsetsOfSet(self.base_set()).contains_subset(value):
            return False
        other_subset = value
        if self is candidate:
            return True
        if self.base_set() is not other_subset.base_set():
            return False
        assert self._members is not None and other_subset._members is not None
        return self._members == other_subset._members

    def __hash__(self) -> int:
        if self._members is None:
            return id(self)
        return hash((id(self.base_set()), self._members))

    def __le__(self, other: SetSubset) -> Decision:
        assert self.base_set() is other.base_set()
        if self is other:
            return True
        if self._members is None:
            return UNKNOWN
        answer: Decision = True
        for member in self._members:
            contained = other.membership(member)
            if contained is False:
                return False
            if contained is UNKNOWN:
                answer = UNKNOWN
        return answer

    def __or__(self, other: SetSubset) -> SetSubset:
        from sage_categories.theories.set_constructions import PowerSet

        assert self.base_set() is other.base_set()
        if self._members is not None and other._members is not None:
            return PowerSet(self.base_set())._from_members(self._members | other._members)
        return PowerSet(self.base_set()).from_predicate(
            lambda member: _decision_or(
                self.membership(member),
                other.membership(member),
            )
        )

    def __and__(self, other: SetSubset) -> SetSubset:
        assert self.base_set() is other.base_set()
        return self._subset_category._intersection(self, other)

    def __sub__(self, other: SetSubset) -> SetSubset:
        from sage_categories.theories.set_constructions import PowerSet

        assert self.base_set() is other.base_set()
        if self._members is not None and other._members is not None:
            return PowerSet(self.base_set())._from_members(self._members - other._members)
        return PowerSet(self.base_set()).from_predicate(
            lambda member: _decision_and(
                self.membership(member),
                _decision_not(other.membership(member)),
            )
        )

    def __xor__(self, other: SetSubset) -> SetSubset:
        from sage_categories.theories.set_constructions import PowerSet

        assert self.base_set() is other.base_set()
        if self._members is not None and other._members is not None:
            return PowerSet(self.base_set())._from_members(self._members ^ other._members)
        return PowerSet(self.base_set()).from_predicate(
            lambda member: _decision_or(
                _decision_and(
                    self.membership(member),
                    _decision_not(other.membership(member)),
                ),
                _decision_and(
                    _decision_not(self.membership(member)),
                    other.membership(member),
                ),
            )
        )

    def __invert__(self) -> SetSubset:
        from sage_categories.theories.set_constructions import PowerSet

        return PowerSet(self.base_set()).from_predicate(lambda member: _decision_not(self.membership(member)))

    def powerset(self) -> SetHomCategory:
        from sage_categories.theories.set_constructions import PowerSet

        return PowerSet(self.underlying_set())

    def __repr__(self) -> str:
        return f"Subset of {self.base_set()}"


class SubsetsOfSetCategory(Category):
    """The subcategory of represented subobjects of one set."""

    ObjectType = SetSubset

    def __init__(self, base_set: SetObject) -> None:
        self._base_set = base_set
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=SetSubset)

    def base_set(self) -> SetObject:
        return self._base_set

    def __call__(
        self,
        hom_category: SetHomCategory,
        predicate: MembershipPredicate,
        *,
        cardinality: Cardinal,
        iterator: SetIterator | None,
        members: frozenset[SetElement] | None,
    ) -> SetSubset:
        from sage_categories.theories.set_category import (
            Sets,
            _set_morphism,
        )

        underlying_set = SubsetSetObject(
            base_set=self._base_set,
            predicate=predicate,
            cardinality=cardinality,
            iterator=iterator,
        )
        forward = _set_morphism(
            underlying_set,
            self._base_set,
            underlying_set.base_element,
            injective=True,
        )
        monomorphisms = Sets().Mono(underlying_set, self._base_set)
        assert is_restricted_hom_category(monomorphisms)
        inclusion = monomorphisms(forward)
        result = self.ObjectType(
            category=self,
            hom_category=hom_category,
            predicate=predicate,
            underlying_set=underlying_set,
            inclusion=inclusion,
            members=members,
        )
        assert self.contains_subset(result)
        return result

    def contains_subset(self, candidate: MathematicalObject) -> TypeIs[SetSubset]:
        return candidate in self

    def _intersection(
        self,
        first: SetSubset,
        second: SetSubset,
    ) -> SetSubset:
        from sage_categories.theories.set_category import (
            Sets,
            is_set_monomorphism,
        )
        from sage_categories.theories.set_constructions import PowerSet

        assert first in self and second in self
        members: frozenset[SetElement] | None = None
        cardinality = UnknownCardinality()
        first_members = first._represented_members()
        second_members = second._represented_members()
        if first_members is not None and second_members is not None:
            members = first_members & second_members
            cardinality = cardinal(len(members))
        subobjects = Sets().Subobjects(self._base_set)
        if cardinality is UnknownCardinality():
            pullback = Sets().pullback(
                first.structure_morphism(),
                second.structure_morphism(),
            )
        else:
            pullback = Sets().pullback_with_cardinality(
                first.structure_morphism(),
                second.structure_morphism(),
                cardinality,
            )
        apex = pullback.apex()
        assert Sets().contains_set(apex)
        projection = pullback.projection(first.object())
        structure_morphism = Sets().compose(
            first.structure_morphism(),
            projection,
        )
        monomorphisms = Sets().Mono(apex, self._base_set)
        assert is_restricted_hom_category(monomorphisms)
        intersection = subobjects(monomorphisms(structure_morphism))
        underlying_set = intersection.object()
        assert Sets().contains_set(underlying_set)
        inclusion = intersection.structure_morphism()
        assert is_set_monomorphism(inclusion)
        return self.ObjectType(
            category=self,
            hom_category=PowerSet(self._base_set),
            predicate=lambda member: _decision_and(
                first.membership(member),
                second.membership(member),
            ),
            underlying_set=underlying_set,
            inclusion=inclusion,
            members=members,
        )

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        from sage_categories.theories.set_category import Sets

        if self._inclusion is None:
            self._inclusion = InclusionFunctor(
                self,
                Sets().Subobjects(self._base_set),
            )
        return (self._inclusion,)


_SUBSET_CATEGORIES: dict[int, SubsetsOfSetCategory] = {}


def SubsetsOfSet(base_set: SetObject) -> SubsetsOfSetCategory:
    key = id(base_set)
    cached = _SUBSET_CATEGORIES.get(key)
    if cached is None:
        cached = SubsetsOfSetCategory(base_set)
        _SUBSET_CATEGORIES[key] = cached
    return cached


def _decision_and(left: Decision, right: Decision) -> Decision:
    if left is False or right is False:
        return False
    if left is UNKNOWN or right is UNKNOWN:
        return UNKNOWN
    return True


def _decision_or(left: Decision, right: Decision) -> Decision:
    if left is True or right is True:
        return True
    if left is UNKNOWN or right is UNKNOWN:
        return UNKNOWN
    return False


def _decision_not(value: Decision) -> Decision:
    if value is UNKNOWN:
        return UNKNOWN
    return not value
