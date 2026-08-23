"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from itertools import combinations, count
from itertools import product as cartesian_product
from math import comb
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
    is_opposite_arrow,
    is_product_arrow,
    is_product_category,
)
from sage_categories.abstract_categories.functors import (
    DiscreteCategories,
    DiscreteDiagram,
    DiscreteHomCategory,
    DiscreteObject,
    Functor,
    InclusionFunctor,
    NaturalTransformation,
    StructuralFunctor,
    is_functor,
)
from sage_categories.abstract_categories.functors import (
    DiscreteCategory as DiscreteCategoryObject,
)
from sage_categories.abstract_categories.hom_categories import (
    Automorphism,
    AutomorphismCategoryFamily,
    EndCategoryFamily,
    Endomorphism,
    EndomorphismHomCategory,
    Epimorphism,
    EpimorphismCategoryFamily,
    EpimorphismHomCategory,
    HomCategory,
    HomCategoryFamily,
    Isomorphism,
    IsomorphismCategoryFamily,
    IsomorphismHomCategory,
    Monomorphism,
    MonomorphismCategoryFamily,
    MonomorphismHomCategory,
    is_restricted_hom_category,
)
from sage_categories.abstract_categories.products import (
    Cocone,
    CoconeObject,
    ColimitObject,
    ColimitsOfCategory,
    Cone,
    ConeObject,
    Coproduct,
    CoproductObject,
    CoproductPresentation,
    CoproductsOfCategory,
    LimitObject,
    LimitsOfCategory,
    Product,
    ProductObject,
    ProductPresentation,
    ProductsOfCategory,
)
from sage_categories.category import Category
from sage_categories.theories.cardinals import (
    Aleph0,
    Cardinal,
    Cardinals,
    UnknownCardinality,
    aleph,
    cardinal,
    is_cardinal_hom_category,
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
        PartiallyOrderedSetsCategory,
        PosetObject,
        SimplexOrderIndexing,
        TotallyOrderedSetsCategory,
    )

type SetElementFamily = Callable[[SetElement], SetElement]
type MembershipPredicate = Callable[[SetElement], Decision]
type SetIterator = Callable[[], Iterator[SetElement]]


type SetMorphismFamily = Callable[[DiscreteObject], SetMorphism]


class SetElement(MathematicalElement):
    """An element of one owned set."""

    def __init__(
        self,
        *,
        category: Category,
        ambient_object: SetObject,
    ) -> None:
        assert ambient_object in Sets()
        assert category is SetElements() or category.is_subcategory(SetElements())
        super().__init__(
            category=category,
            ambient_object=ambient_object,
        )

    def ambient_set(self) -> SetObject:
        ambient = self.ambient_object()
        assert Sets().contains_set(ambient)
        return ambient

    def value(self) -> MathematicalObject:
        return self


class SetElementsCategory(Category):
    """The total category of elements of owned sets."""

    ObjectType = SetElement

    def __init__(self) -> None:
        super().__init__()

    def contains_set_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SetElement]:
        return candidate in self

    def __repr__(self) -> str:
        return "Elements of sets"


_SET_ELEMENTS: SetElementsCategory | None = None


def SetElements() -> SetElementsCategory:
    global _SET_ELEMENTS

    if _SET_ELEMENTS is None:
        _SET_ELEMENTS = SetElementsCategory()
    return _SET_ELEMENTS


class SetObject(MathematicalObject):
    """The implementation shared by arbitrary owned sets."""

    def __init__(
        self,
        *,
        category: Category | None = None,
        cardinality: Cardinal | None = None,
    ) -> None:
        self._cardinality = UnknownCardinality() if cardinality is None else cardinality
        self._subset_poset: PosetObject | None = None
        owner = _category_for_cardinality(self._cardinality) if category is None else category
        super().__init__(category=owner)

    def membership(self, member: SetElement) -> Decision:
        """Return the represented membership decision for ``member``."""
        assert False, f"{self} has no represented membership predicate"

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
        return ExponentialOfSets(self, exponent)

    def __pow__(self, exponent: SetObject) -> SetHomCategory:
        return self.exponential(exponent)

    def powerset(self) -> SetHomCategory:
        return PowerSet(self)

    def subset_poset(self) -> PosetObject:
        if self._subset_poset is None:
            from sage_categories.theories.posets import (
                PartiallyOrderedSets,
                PosetElement,
            )

            powerset = self.powerset()
            subsets = SubsetsOfSet(self)

            def contained(left: PosetElement, right: PosetElement) -> Decision:
                forgetful_functor = PartiallyOrderedSets().forgetful_functor()
                left_subset = forgetful_functor.on_element(left.ambient_poset(), left)
                right_subset = forgetful_functor.on_element(right.ambient_poset(), right)
                assert subsets.contains_subset(left_subset)
                assert subsets.contains_subset(right_subset)
                return left_subset <= right_subset

            self._subset_poset = PartiallyOrderedSets()(powerset, contained)
        return self._subset_poset

    def subsets_of_size(self, size: int) -> SetObject:
        return SubsetsOfSize(self, size)

    def finite_subsets(self) -> SetObject:
        return FiniteSubsets(self)

    def subset_from(
        self,
        predicate: MembershipPredicate,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetSubset:
        return PowerSet(self).from_predicate(
            predicate,
            cardinality=cardinality,
        )

    def cartesian_product(self, *others: SetObject) -> SetProductObject:
        return CartesianProductOfSets((self, *others))

    def disjoint_union(self, *others: SetObject) -> SetCoproductObject:
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

    def value(self) -> MathematicalObject:
        return self._value

    def __repr__(self) -> str:
        return repr(self._value)


class FiniteSetObject(SetObject):
    """A set given by its complete finite member set."""

    def __init__(
        self,
        *,
        category: FiniteSetsCategory,
        values: frozenset[MathematicalObject],
    ) -> None:
        self._values = values
        super().__init__(category=category, cardinality=Cardinals()(len(values)))
        self._members = frozenset(category.ElementType(ambient_object=self, value=value) for value in values)

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def __iter__(self) -> Iterator[SetElement]:
        return iter(self._members)

    def members(self) -> frozenset[SetElement]:
        return self._members

    def element(self, value: MathematicalObject) -> FiniteSetElement:
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
        self._members: dict[int, NaturalNumberElement] = {}
        super().__init__(cardinality=Aleph0())

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


_NATURAL_NUMBERS: NaturalNumbersSet | None = None


def NaturalNumbers() -> NaturalNumbersSet:
    global _NATURAL_NUMBERS

    if _NATURAL_NUMBERS is None:
        _NATURAL_NUMBERS = NaturalNumbersSet()
    return _NATURAL_NUMBERS


def EnumerationInjection(
    source: SetObject,
    position: Callable[[SetElement], int],
) -> Arrow:
    from sage_categories.theories.ordinals import ordinal

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


class SubsetElement(SetElement):
    """An element of a represented set subobject."""

    def __init__(self, *, ambient_object: SubsetSetObject) -> None:
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def value(self) -> MathematicalObject:
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
        self._base_set = base_set
        self._predicate = predicate
        self._iterator = iterator
        self._elements: dict[int, SubsetElement] = {}
        self._base_elements: dict[int, SetElement] = {}
        super().__init__(cardinality=cardinality)

    def element(self, base_element: SetElement) -> SubsetElement:
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

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def __iter__(self) -> Iterator[SetElement]:
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

    def image(self, *, cardinality: Cardinal | None = None) -> SetSubset:
        return _image_subobject(self, cardinality=cardinality)

    def inverse(self) -> SetMorphism:
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
        base = self.domain()
        assert Sets().contains_set(base)
        return base

    def characteristic_morphism(self) -> SetMorphism:
        return self

    def inclusion(self) -> SetMonomorphism:
        return self._inclusion

    def members(self) -> frozenset[SetElement] | None:
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

    def __eq__(self, candidate: Any) -> bool:
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
        assert self.base_set() is other.base_set()
        if self._members is not None and other._members is not None:
            return PowerSet(self.base_set()).from_members(self._members | other._members)
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
        assert self.base_set() is other.base_set()
        if self._members is not None and other._members is not None:
            return PowerSet(self.base_set()).from_members(self._members - other._members)
        return PowerSet(self.base_set()).from_predicate(
            lambda member: _decision_and(
                self.membership(member),
                _decision_not(other.membership(member)),
            )
        )

    def __xor__(self, other: SetSubset) -> SetSubset:
        assert self.base_set() is other.base_set()
        if self._members is not None and other._members is not None:
            return PowerSet(self.base_set()).from_members(self._members ^ other._members)
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
        return PowerSet(self.base_set()).from_predicate(lambda member: _decision_not(self.membership(member)))

    def powerset(self) -> SetHomCategory:
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
        assert first in self and second in self
        members: frozenset[SetElement] | None = None
        cardinality: Cardinal | None = None
        first_members = first.members()
        second_members = second.members()
        if first_members is not None and second_members is not None:
            members = first_members & second_members
            cardinality = cardinal(len(members))
        subobjects = Sets().Subobjects(self._base_set)
        pullback = Sets().pullback(
            first.structure_morphism(),
            second.structure_morphism(),
            cardinality=cardinality,
        )
        apex = pullback.image()
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


class SetHomCategory(HomCategory, SetObject):
    """The set of all functions between two sets, as their hom category."""

    ObjectType = SetMorphism
    ElementType = SetMorphism

    def __init__(
        self,
        *,
        domain: SetObject,
        codomain: SetObject,
        hom_category: SetHomCategoryFamily,
    ) -> None:
        assert domain in Sets()
        assert codomain in Sets()
        self._evaluation: SetMorphism | None = None
        self._top_subset: SetSubset | None = None
        self._bottom_subset: SetSubset | None = None
        super().__init__(
            domain=domain,
            codomain=codomain,
            hom_category=hom_category,
        )

    def __call__(
        self,
        action: Callable[[SetElement], SetElement] | Mapping[SetElement, SetElement] | SetMorphism,
        *,
        injective: Decision = UNKNOWN,
        surjective: Decision = UNKNOWN,
    ) -> SetMorphism:
        existing = registered_value(action)
        if existing is not None:
            assert existing in self
            assert Sets().contains_set_morphism(existing)
            return existing
        set_action = self._set_action(action)
        return self.ObjectType(
            hom_category=self,
            action=set_action,
            injective=injective,
            surjective=surjective,
        )

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> SetHomCategory:
        assert codomain is None
        assert Sets().contains_set(domain)
        return Sets().Hom(self, domain)

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and value._belongs_to_hom(self)

    def _set_action(
        self,
        action: Callable[[SetElement], SetElement] | Mapping[SetElement, SetElement],
    ) -> Callable[[SetElement], SetElement]:
        if callable(action):
            return action
        domain = self.domain()
        codomain = self.codomain()
        assert Sets().contains_set(domain)
        assert Sets().contains_set(codomain)
        assert domain.is_finite() is True
        assert all(key in domain for key in action)
        assert all(member in action for member in domain)
        assert all(value in codomain for value in action.values())
        return action.__getitem__

    def membership(self, candidate: SetElement) -> Decision:
        return candidate in self

    def cardinality(self) -> Cardinal:
        domain = self.domain()
        codomain = self.codomain()
        assert Sets().contains_set(domain)
        assert Sets().contains_set(codomain)
        return Cardinals().power(codomain.cardinality(), domain.cardinality())

    def objects(self) -> SetObject:
        return self

    def _hom_category_type(self) -> type[HomCategory]:
        return DiscreteHomCategory

    def identity(self, value: MathematicalObject | None = None) -> SetMorphism:
        if value is not None:
            identity = Category.identity(self, value)
            assert Sets().contains_set_morphism(identity)
            return identity
        assert self.domain() is self.codomain()
        return self(
            lambda member: member,
            injective=True,
            surjective=True,
        )

    def compose(self, second: Arrow, first: Arrow) -> SetMorphism:
        second = second.forward()
        first = first.forward()
        assert Sets().contains_set_morphism(second)
        assert Sets().contains_set_morphism(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return self(
            lambda member: second(first(member)),
            injective=_decision_and(first.is_injective(), second.is_injective()),
            surjective=_decision_and(first.is_surjective(), second.is_surjective()),
        )

    def __iter__(self) -> Iterator[SetElement]:
        domain = self.domain()
        codomain = self.codomain()
        assert Sets().contains_set(domain)
        assert Sets().contains_set(codomain)
        assert domain.is_finite() is True and codomain.is_finite() is True
        domain_members = tuple(domain)
        if self.is_power_set():
            for choices in cartesian_product((False, True), repeat=len(domain_members)):
                yield self.from_members(
                    frozenset(
                        member
                        for member, selected in zip(
                            domain_members,
                            choices,
                            strict=True,
                        )
                        if selected
                    )
                )
            return
        codomain_members = tuple(codomain)
        for images in cartesian_product(codomain_members, repeat=len(domain_members)):
            table = tuple(zip(domain_members, images, strict=True))

            def action(
                member: SetElement,
                table: tuple[tuple[SetElement, SetElement], ...] = table,
            ) -> SetElement:
                return next(image for source, image in table if source == member)

            yield self(action)

    def exponent(self) -> SetObject:
        value = self.domain()
        assert Sets().contains_set(value)
        return value

    def base(self) -> SetObject:
        value = self.codomain()
        assert Sets().contains_set(value)
        return value

    def base_set(self) -> SetObject:
        assert self.is_power_set()
        return self.exponent()

    def is_power_set(self) -> bool:
        return self.codomain() is TruthValues()

    def from_predicate(
        self,
        predicate: MembershipPredicate,
        *,
        cardinality: Cardinal | None = None,
        iterator: SetIterator | None = None,
    ) -> SetSubset:
        assert self.is_power_set()
        size = UnknownCardinality() if cardinality is None else cardinality
        return SubsetsOfSet(self.exponent())(
            self,
            predicate=predicate,
            cardinality=size,
            iterator=iterator,
            members=None,
        )

    def from_members(self, members: frozenset[SetElement]) -> SetSubset:
        assert self.is_power_set()
        assert all(member in self.exponent() for member in members)
        return SubsetsOfSet(self.exponent())(
            self,
            lambda member: member in members,
            cardinality=cardinal(len(members)),
            iterator=lambda: iter(members),
            members=members,
        )

    def from_characteristic_morphism(self, characteristic: SetMorphism) -> SetSubset:
        assert self.is_power_set()
        assert characteristic in self
        value = registered_value(characteristic)
        assert value is not None
        subsets = SubsetsOfSet(self.base_set())
        if subsets.contains_subset(value):
            return value
        assert Sets().contains_set_morphism(value)

        def predicate(member: SetElement) -> Decision:
            from sage_categories.theories.ordinals import ordinal

            truth_value = value(member)
            assert truth_value in TruthValues()
            return truth_value is TruthValues().element(ordinal(1))

        return self.from_predicate(predicate)

    def top(self) -> SetSubset:
        assert self.is_power_set()
        if self._top_subset is None:
            self._top_subset = self.from_predicate(
                lambda member: self.exponent().membership(member),
                cardinality=self.exponent().cardinality(),
                iterator=lambda: iter(self.exponent()),
            )
        return self._top_subset

    def bottom(self) -> SetSubset:
        assert self.is_power_set()
        if self._bottom_subset is None:
            self._bottom_subset = self.from_members(frozenset())
        return self._bottom_subset

    def inverse_image_morphism(self, function: SetMorphism) -> SetMorphism:
        assert self.is_power_set()
        assert function.codomain() is self.base_set()
        source = function.domain()
        assert Sets().contains_set(source)
        target_power_set = PowerSet(source)

        def inverse_image(candidate: SetElement) -> SetSubset:
            subset = self._represented_subset(candidate)
            return target_power_set.from_predicate(lambda member: subset.membership(function(member)))

        return _set_morphism(
            self,
            target_power_set,
            inverse_image,
            injective=function.is_surjective(),
            surjective=function.is_injective(),
        )

    def direct_image_morphism(self, function: SetMorphism) -> SetMorphism:
        assert self.is_power_set()
        assert function.domain() is self.base_set()
        target = function.codomain()
        assert Sets().contains_set(target)
        target_power_set = PowerSet(target)

        def direct_image(candidate: SetElement) -> SetSubset:
            subset = self._represented_subset(candidate)
            members = subset.members()
            if members is not None:
                return target_power_set.from_members(
                    frozenset(function(member) for member in members),
                )
            inclusion = subset.inclusion().forward()
            assert Sets().contains_set_morphism(inclusion)
            restricted = Sets().compose(function, inclusion)
            assert Sets().contains_set_morphism(restricted)
            return restricted.image()

        return _set_morphism(
            self,
            target_power_set,
            direct_image,
            injective=function.is_injective(),
            surjective=function.is_surjective(),
        )

    def _represented_subset(self, candidate: MathematicalObject) -> SetSubset:
        value = registered_value(candidate)
        assert value is not None and value in self
        subsets = SubsetsOfSet(self.base_set())
        assert subsets.contains_subset(value)
        return value

    def evaluation(self) -> SetMorphism:
        if self._evaluation is None:
            sets = Sets()
            exponent = self.exponent()
            base = self.base()
            from sage_categories.theories.ordinals import ordinal

            labels = _finite_ordinal(2)
            index_category = DiscreteCategory(labels)
            function_index = index_category.object(labels.element(ordinal(0)))
            argument_index = index_category.object(labels.element(ordinal(1)))
            diagram = SetFamily(
                index_category,
                lambda index: self if index is function_index else exponent,
            )
            products = sets.Products(index_category)
            assert is_products_of_sets_category(products)
            product = products(
                diagram,
                cardinality=Cardinals().product(
                    self.cardinality(),
                    exponent.cardinality(),
                ),
            )
            function_projection = product.projection(function_index)
            argument_projection = product.projection(argument_index)
            assert sets.contains_set_morphism(function_projection)
            assert sets.contains_set_morphism(argument_projection)

            def evaluate(pair: SetElement) -> SetElement:
                function_value = registered_value(function_projection(pair))
                assert function_value is not None
                assert sets.contains_set_morphism(function_value)
                return function_value(argument_projection(pair))

            self._evaluation = _set_morphism(product, base, evaluate)
        return self._evaluation

    def __repr__(self) -> str:
        return f"{self.codomain()}^{self.domain()}"


def _underlying_set_function(arrow: Arrow) -> SetMorphism:
    underlying = arrow.forward()
    assert Sets().contains_set_morphism(underlying)
    return underlying


class SetEndomorphism(Endomorphism):
    """A callable endomorphism in ``Sets``."""

    def __call__(self, member: SetElement) -> SetElement:
        return _underlying_set_function(self)(member)


class SetMonomorphism(Monomorphism):
    """A callable declared injection in ``Sets``."""

    def __call__(self, member: SetElement) -> SetElement:
        return _underlying_set_function(self)(member)

    def is_injective(self) -> Decision:
        return True


class SetEpimorphism(Epimorphism):
    """A callable declared surjection in ``Sets``."""

    def __call__(self, member: SetElement) -> SetElement:
        return _underlying_set_function(self)(member)

    def is_surjective(self) -> Decision:
        return True


class SetIsomorphism(Isomorphism):
    """A callable declared bijection in ``Sets``."""

    def __call__(self, member: SetElement) -> SetElement:
        return _underlying_set_function(self)(member)

    def is_injective(self) -> Decision:
        return True

    def is_surjective(self) -> Decision:
        return True

    def is_bijective(self) -> Decision:
        return True


class SetAutomorphism(Automorphism):
    """A callable declared automorphism in ``Sets``."""

    def __call__(self, member: SetElement) -> SetElement:
        return _underlying_set_function(self)(member)

    def is_injective(self) -> Decision:
        return True

    def is_surjective(self) -> Decision:
        return True

    def is_bijective(self) -> Decision:
        return True


class SetEndomorphismHomCategory(EndomorphismHomCategory):
    ObjectType = SetEndomorphism
    ElementType = SetEndomorphism

    def __call__(self, underlying_arrow: Arrow) -> SetEndomorphism:
        assert Sets().contains_set_morphism(underlying_arrow)
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )


class SetMonomorphismHomCategory(MonomorphismHomCategory):
    ObjectType = SetMonomorphism
    ElementType = SetMonomorphism

    def __call__(self, underlying_arrow: Arrow) -> SetMonomorphism:
        assert Sets().contains_set_morphism(underlying_arrow)
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )


class SetEpimorphismHomCategory(EpimorphismHomCategory):
    ObjectType = SetEpimorphism
    ElementType = SetEpimorphism

    def __call__(self, underlying_arrow: Arrow) -> SetEpimorphism:
        assert Sets().contains_set_morphism(underlying_arrow)
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )


class SetIsomorphismHomCategory(IsomorphismHomCategory):
    ObjectType = SetIsomorphism
    ElementType = SetIsomorphism

    def __call__(self, forward: Arrow, backward: Arrow) -> SetIsomorphism:
        assert Sets().contains_set_morphism(forward)
        assert Sets().contains_set_morphism(backward)
        return self.ObjectType(
            hom_category=self,
            forward=forward,
            backward=backward,
        )


class SetAutomorphismHomCategory(IsomorphismHomCategory):
    ObjectType = SetAutomorphism
    ElementType = SetAutomorphism

    def __call__(self, forward: Arrow, backward: Arrow) -> SetAutomorphism:
        assert Sets().contains_set_morphism(forward)
        assert Sets().contains_set_morphism(backward)
        return self.ObjectType(
            hom_category=self,
            forward=forward,
            backward=backward,
        )


class SetEndomorphismCategoryFamily(EndCategoryFamily):
    def __init__(self, base_category: Category) -> None:
        self._inclusion: StructuralFunctor | None = None
        HomCategoryFamily.__init__(
            self,
            base_category,
            hom_category_type=SetEndomorphismHomCategory,
        )


class SetMonomorphismCategoryFamily(MonomorphismCategoryFamily):
    def __init__(self, base_category: Category) -> None:
        self._inclusion: StructuralFunctor | None = None
        HomCategoryFamily.__init__(
            self,
            base_category,
            hom_category_type=SetMonomorphismHomCategory,
        )


class SetEpimorphismCategoryFamily(EpimorphismCategoryFamily):
    def __init__(self, base_category: Category) -> None:
        self._inclusion: StructuralFunctor | None = None
        HomCategoryFamily.__init__(
            self,
            base_category,
            hom_category_type=SetEpimorphismHomCategory,
        )


class SetIsomorphismCategoryFamily(IsomorphismCategoryFamily):
    def __init__(self, base_category: Category) -> None:
        self._inclusion: StructuralFunctor | None = None
        HomCategoryFamily.__init__(
            self,
            base_category,
            hom_category_type=SetIsomorphismHomCategory,
        )


class SetAutomorphismCategoryFamily(AutomorphismCategoryFamily):
    def __init__(self, base_category: Category) -> None:
        self._inclusion: StructuralFunctor | None = None
        HomCategoryFamily.__init__(
            self,
            base_category,
            hom_category_type=SetAutomorphismHomCategory,
        )


class SetHomCategoryFamily(HomCategoryFamily):
    """The family of function sets of ``Sets``."""

    ObjectType = SetHomCategory

    def __init__(
        self,
        base_category: Category,
        *,
        hom_category_type: type[HomCategory],
    ) -> None:
        self._sets_inclusion: InclusionFunctor | None = None
        super().__init__(base_category, hom_category_type=hom_category_type)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._sets_inclusion is None:
            self._sets_inclusion = InclusionFunctor(self, Sets())
        return (self._sets_inclusion,)


class CardinalityFunctor(Functor):
    """The cardinality functor from the core of ``Sets`` to ``Cardinals``."""

    def __init__(self, sets: SetsCategory) -> None:
        self._sets = sets
        super().__init__(sets.core(), Cardinals())

    def _object_image(self, source: MathematicalObject) -> Cardinal:
        assert source in self.domain()
        assert self._sets.contains_set(source)
        return source.cardinality()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert morphism in self.domain().ArrowCategory()
        source = morphism.domain()
        target = morphism.codomain()
        assert self._sets.contains_set(source)
        assert self._sets.contains_set(target)
        source_cardinality = source.cardinality()
        target_cardinality = target.cardinality()
        assert source_cardinality == target_cardinality
        hom_category = Cardinals().Hom(source_cardinality, target_cardinality)
        assert is_cardinal_hom_category(hom_category)
        return hom_category()


class ExponentialFunctor(Functor):
    """The internal-hom bifunctor ``Sets^op x Sets -> Sets``."""

    def __init__(self) -> None:
        super().__init__(Sets().OppositeCategory().ProductCategory(Sets()), Sets())

    def _object_image(self, source: MathematicalObject) -> SetHomCategory:
        domain = self.domain()
        assert is_product_category(domain)
        assert domain.contains_pair(source)
        exponent = source.first()
        base = source.second()
        assert Sets().contains_set(exponent)
        assert Sets().contains_set(base)
        return ExponentialOfSets(base, exponent)

    def _morphism_image(self, morphism: Arrow) -> SetMorphism:
        assert is_product_arrow(morphism)
        first = morphism.first()
        second = morphism.second()
        assert is_opposite_arrow(first)
        precompose = first.underlying_arrow()
        assert Sets().contains_set_morphism(precompose)
        assert Sets().contains_set_morphism(second)
        source = self(morphism.domain())
        target = self(morphism.codomain())
        assert is_set_hom_category(source)
        assert is_set_hom_category(target)

        def transport(candidate: SetElement) -> SetMorphism:
            assert Sets().contains_set_morphism(candidate)
            return target(lambda member: second(candidate(precompose(member))))

        return _set_morphism(source, target, transport)


class InverseImagePowerSetFunctor(Functor):
    """The contravariant power-set functor ``Sets^op -> Sets``."""

    def __init__(self) -> None:
        super().__init__(Sets().OppositeCategory(), Sets())

    def _object_image(self, source: MathematicalObject) -> SetHomCategory:
        assert Sets().contains_set(source)
        return PowerSet(source)

    def _morphism_image(self, morphism: Arrow) -> SetMorphism:
        assert is_opposite_arrow(morphism)
        underlying = morphism.underlying_arrow()
        assert Sets().contains_set_morphism(underlying)
        source = self(morphism.domain())
        assert is_set_hom_category(source)
        return source.inverse_image_morphism(underlying)


class SetsCategory(Category):
    """The category of arbitrary sets and arbitrary functions."""

    ObjectType = SetObject
    ElementType = SetElement

    def __init__(self) -> None:
        self.ℵ = Aleph
        self.א = Aleph
        self._finite_sets: FiniteSetsCategory | None = None
        self._infinite_sets: InfiniteSetsCategory | None = None
        self._countable_sets: CountableSetsCategory | None = None
        self._uncountable_sets: UncountableSetsCategory | None = None
        self._cardinality_functor: CardinalityFunctor | None = None
        self._exponential_functor: ExponentialFunctor | None = None
        self._inverse_image_power_set_functor: InverseImagePowerSetFunctor | None = None
        self._partially_ordered_sets: PartiallyOrderedSetsCategory | None = None
        self._totally_ordered_sets: TotallyOrderedSetsCategory | None = None
        super().__init__()

    def _hom_category_type(self) -> type[HomCategory]:
        return SetHomCategory

    def _hom_category_family_type(self) -> type[HomCategoryFamily]:
        return SetHomCategoryFamily

    def _end_category_family_type(self) -> type[HomCategoryFamily]:
        return SetEndomorphismCategoryFamily

    def _mono_category_family_type(self) -> type[HomCategoryFamily]:
        return SetMonomorphismCategoryFamily

    def _epi_category_family_type(self) -> type[HomCategoryFamily]:
        return SetEpimorphismCategoryFamily

    def _iso_category_family_type(self) -> type[HomCategoryFamily]:
        return SetIsomorphismCategoryFamily

    def _aut_category_family_type(self) -> type[HomCategoryFamily]:
        return SetAutomorphismCategoryFamily

    def __call__(self, source: MathematicalObject) -> SetObject:
        assert self.contains_set(source)
        return source

    def finite(self, members: frozenset[MathematicalObject]) -> FiniteSetObject:
        return self.Finite()(members)

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> SetHomCategory:
        category = Category.Hom(self, domain, codomain)
        assert codomain is not None
        assert is_set_hom_category(category)
        return category

    def Mono(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> SetMonomorphismHomCategory:
        assert codomain is not None
        category = Category.Mono(self, domain, codomain)
        assert is_set_monomorphism_hom_category(category)
        return category

    def contains_set(self, candidate: MathematicalObject) -> TypeIs[SetObject]:
        return candidate in self

    def contains_set_morphism(self, candidate: MathematicalObject) -> TypeIs[SetMorphism]:
        return candidate in self.ArrowCategory()

    def Finite(self) -> FiniteSetsCategory:
        if self._finite_sets is None:
            self._finite_sets = FiniteSetsCategory(self)
        return self._finite_sets

    def Infinite(self) -> InfiniteSetsCategory:
        if self._infinite_sets is None:
            self._infinite_sets = InfiniteSetsCategory(self)
        return self._infinite_sets

    def Countable(self) -> CountableSetsCategory:
        if self._countable_sets is None:
            self._countable_sets = CountableSetsCategory(self)
        return self._countable_sets

    def Uncountable(self) -> UncountableSetsCategory:
        if self._uncountable_sets is None:
            self._uncountable_sets = UncountableSetsCategory(self)
        return self._uncountable_sets

    def CardinalityFunctor(self) -> CardinalityFunctor:
        if self._cardinality_functor is None:
            self._cardinality_functor = CardinalityFunctor(self)
        return self._cardinality_functor

    def ExponentialFunctor(self) -> ExponentialFunctor:
        if self._exponential_functor is None:
            self._exponential_functor = ExponentialFunctor()
        return self._exponential_functor

    def InverseImagePowerSetFunctor(self) -> InverseImagePowerSetFunctor:
        if self._inverse_image_power_set_functor is None:
            self._inverse_image_power_set_functor = InverseImagePowerSetFunctor()
        return self._inverse_image_power_set_functor

    def PartiallyOrdered(self) -> PartiallyOrderedSetsCategory:
        if self._partially_ordered_sets is None:
            from sage_categories.theories.posets import PartiallyOrderedSets

            self._partially_ordered_sets = PartiallyOrderedSets()
        return self._partially_ordered_sets

    def TotallyOrdered(self) -> TotallyOrderedSetsCategory:
        if self._totally_ordered_sets is None:
            from sage_categories.theories.posets import TotallyOrderedSets

            self._totally_ordered_sets = TotallyOrderedSets()
        return self._totally_ordered_sets

    @property
    def Δ(self) -> SimplexOrderIndexing:
        from sage_categories.theories.posets import SimplexOrders

        return SimplexOrders()

    def chosen_limit(self, diagram: Functor) -> ProductPresentation:
        if diagram.domain() in DiscreteCategories():
            return ProductOfSets(diagram)
        return LimitOfSets(diagram)

    def chosen_colimit(self, diagram: Functor) -> CoproductPresentation:
        if diagram.domain() in DiscreteCategories():
            return _CoproductPresentationOfSets(diagram)
        return ColimitOfSets(diagram)

    def pullback(
        self,
        first: Arrow,
        second: Arrow,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetLimitObject:
        from sage_categories.abstract_categories.functors import InclusionFunctor
        from sage_categories.abstract_categories.products import DiagramCategory

        assert self.contains_set_morphism(first)
        assert self.contains_set_morphism(second)
        assert first.codomain() is second.codomain()
        index = DiagramCategory(
            self,
            (first.domain(), second.domain(), first.codomain()),
            (first, second),
        )
        diagram = InclusionFunctor(index, self)
        limits = self.Limits(index)
        assert is_limits_of_sets_category(limits)
        return limits(diagram, cardinality=cardinality)

    def _products_of_category(self, functor: Functor) -> Category:
        return ProductsOfSetsCategory(functor)

    def _coproducts_of_category(self, functor: Functor) -> Category:
        return CoproductsOfSetsCategory(functor)

    def _limits_of_category(self, functor: Functor) -> Category:
        return LimitsOfSetsCategory(functor)

    def _colimits_of_category(self, functor: Functor) -> Category:
        return ColimitsOfSetsCategory(functor)

    def __repr__(self) -> str:
        return "Sets"


class CountableSetsCategory(FullSubcategory):
    def __init__(self, sets: SetsCategory) -> None:
        self._sets = sets
        super().__init__(sets, self._is_countable, name="Countable sets")

    def _is_countable(self, value: MathematicalObject) -> bool:
        assert Sets().contains_set(value)
        finite = value.cardinality().is_finite()
        return finite is True or value.cardinality() == Cardinals().aleph()


class FiniteSetsCategory(FullSubcategory):
    ObjectType: type[FiniteSetObject] = FiniteSetObject
    ElementType: type[FiniteSetElement] = FiniteSetElement

    def __init__(self, sets: SetsCategory) -> None:
        self._sets = sets
        self._finite_sets_by_members: dict[
            frozenset[MathematicalObject],
            FiniteSetObject,
        ] = {}
        super().__init__(
            sets.Countable(),
            self._is_finite,
            name="Finite sets",
        )

    def __call__(self, members: frozenset[MathematicalObject]) -> FiniteSetObject:
        cached = self._finite_sets_by_members.get(members)
        if cached is None:
            cached = self.ObjectType(category=self, values=members)
            self._finite_sets_by_members[members] = cached
        return cached

    def _is_finite(self, value: MathematicalObject) -> bool:
        assert Sets().contains_set(value)
        return value.cardinality().is_finite() is True

    def contains_finite_set(self, candidate: MathematicalObject) -> TypeIs[SetObject]:
        return candidate in self


class InfiniteSetsCategory(FullSubcategory):
    def __init__(self, sets: SetsCategory) -> None:
        self._sets = sets
        super().__init__(sets, self._is_infinite, name="Infinite sets")

    def _is_infinite(self, value: MathematicalObject) -> bool:
        assert Sets().contains_set(value)
        return value.cardinality().is_infinite() is True


class UncountableSetsCategory(FullSubcategory):
    def __init__(self, sets: SetsCategory) -> None:
        self._sets = sets
        super().__init__(
            sets.Infinite(),
            self._is_uncountable,
            name="Uncountable sets",
        )

    def _is_uncountable(self, value: MathematicalObject) -> bool:
        assert Sets().contains_set(value)
        size = value.cardinality()
        return size.is_infinite() is True and size != Cardinals().aleph()


_SETS = SetsCategory()


def Sets() -> SetsCategory:
    return _SETS


def FiniteSets() -> FiniteSetsCategory:
    return Sets().Finite()


def InfiniteSets() -> InfiniteSetsCategory:
    return Sets().Infinite()


def CountableSets() -> CountableSetsCategory:
    return Sets().Countable()


def UncountableSets() -> UncountableSetsCategory:
    return Sets().Uncountable()


def _category_for_cardinality(size: Cardinal) -> Category:
    if size.is_finite() is True:
        return FiniteSets()
    if size.is_countable() is True:
        return CountableSets()
    if size.is_uncountable() is True:
        return UncountableSets()
    if size.is_infinite() is True:
        return InfiniteSets()
    return Sets()


def cardinality_functor() -> CardinalityFunctor:
    return Sets().CardinalityFunctor()


def is_set_hom_category(category: MathematicalObject) -> TypeIs[SetHomCategory]:
    return category in Sets().HomCategory()


def is_set_monomorphism_hom_category(
    category: MathematicalObject,
) -> TypeIs[SetMonomorphismHomCategory]:
    return category in Sets().MonoCategory()


def is_set_monomorphism(
    candidate: MathematicalObject,
) -> TypeIs[SetMonomorphism]:
    return candidate in Sets().MonomorphismArrowCategory()


def FiniteSet(members: Iterable[MathematicalObject]) -> FiniteSetObject:
    return Sets().finite(frozenset(members))


def Set(source: SetObject | Iterable[MathematicalObject]) -> SetObject:
    value = registered_value(source)
    if value is not None and Sets().contains_set(value):
        return value
    return FiniteSet(source)


def _set_morphism(
    domain: SetObject,
    codomain: SetObject,
    action: SetElementFamily,
    *,
    injective: Decision = UNKNOWN,
    surjective: Decision = UNKNOWN,
) -> SetMorphism:
    hom_category = Sets().Hom(domain, codomain)
    assert is_set_hom_category(hom_category)
    return hom_category(
        action,
        injective=injective,
        surjective=surjective,
    )


class DiscreteObjectSet(SetObject):
    """The object set of one discrete category."""

    def __init__(self, category: DiscreteCategoryObject, labels: SetObject) -> None:
        self._discrete_category = category
        self._labels = labels
        self._elements: dict[int, SetElement] = {}
        super().__init__(cardinality=labels.cardinality())

    def element(self, value: MathematicalObject) -> SetElement:
        assert value in self._discrete_category
        key = id(value)
        element = self._elements.get(key)
        if element is None:
            element = DiscreteObjectElement(
                ambient_object=self,
                discrete_object=value,
            )
            self._elements[key] = element
        return element

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def __iter__(self) -> Iterator[SetElement]:
        return iter(tuple(self.element(self._discrete_category.object(label)) for label in self._labels))


class DiscreteObjectElement(SetElement):
    """An object regarded as an element of a discrete category's object set."""

    def __init__(
        self,
        *,
        ambient_object: DiscreteObjectSet,
        discrete_object: MathematicalObject,
    ) -> None:
        self._discrete_object = discrete_object
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def value(self) -> MathematicalObject:
        return self._discrete_object


class DiscreteArrowSet(SetObject):
    """The identity arrows of one discrete category."""

    def __init__(self, category: DiscreteCategoryObject) -> None:
        self._discrete_category = category
        self._elements: dict[int, SetElement] = {}
        objects = category.objects()
        assert Sets().contains_set(objects)
        super().__init__(cardinality=objects.cardinality())

    def element(self, value: MathematicalObject) -> SetElement:
        assert self._discrete_category.contains_arrow(value)
        assert value.domain() is value.codomain()
        key = id(value)
        element = self._elements.get(key)
        if element is None:
            element = DiscreteArrowElement(
                ambient_object=self,
                discrete_arrow=value,
            )
            self._elements[key] = element
        return element

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def __iter__(self) -> Iterator[SetElement]:
        return iter(tuple(self.element(self._discrete_category.Hom(value, value).identity()) for value in self._discrete_category))


class DiscreteArrowElement(SetElement):
    """An identity arrow regarded as an element of an arrow set."""

    def __init__(
        self,
        *,
        ambient_object: DiscreteArrowSet,
        discrete_arrow: MathematicalObject,
    ) -> None:
        self._discrete_arrow = discrete_arrow
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def value(self) -> MathematicalObject:
        return self._discrete_arrow


class FiniteDiscreteCategoriesCategory(Category):
    """The property subcategory of finite discrete categories."""

    ObjectType = DiscreteCategoryObject

    def __init__(self) -> None:
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=DiscreteCategoryObject)

    def __call__(self, label_set: SetObject) -> DiscreteCategoryObject:
        assert label_set.is_finite() is True
        return self.ObjectType(category=self, label_set=label_set)

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        if value is None or not DiscreteCategories().contains_discrete_category(value):
            return False
        objects = value.objects()
        assert Sets().contains_set(objects)
        return objects.is_finite() is True

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, DiscreteCategories())
        return (self._inclusion,)

    def contains_finite_discrete_category(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[DiscreteCategoryObject]:
        return candidate in self


_FINITE_DISCRETE_CATEGORIES: FiniteDiscreteCategoriesCategory | None = None


def FiniteDiscreteCategories() -> FiniteDiscreteCategoriesCategory:
    global _FINITE_DISCRETE_CATEGORIES

    if _FINITE_DISCRETE_CATEGORIES is None:
        _FINITE_DISCRETE_CATEGORIES = FiniteDiscreteCategoriesCategory()
    return _FINITE_DISCRETE_CATEGORIES


def DiscreteCategory(label_set: SetObject) -> DiscreteCategoryObject:
    if label_set.is_finite() is True:
        return FiniteDiscreteCategories()(label_set)
    return DiscreteCategories()(label_set)


def SetFamily(
    index_category: DiscreteCategoryObject,
    values: Callable[[DiscreteObject], SetObject],
) -> DiscreteDiagram:
    return DiscreteDiagram(index_category, Sets(), values)


def ObjectSet(discrete_category: DiscreteCategoryObject) -> SetObject:
    objects = discrete_category.objects()
    assert Sets().contains_set(objects)
    return objects


class ProductElement(SetElement):
    """A point of a set-indexed cartesian product."""

    def __init__(self, product: ProductSet, components: SetElementFamily) -> None:
        self._product = product
        self._components = components
        super().__init__(
            category=ProductElements(),
            ambient_object=product,
        )

    def product(self) -> ProductSet:
        return self._product

    def component(self, index: SetElement) -> SetElement:
        assert index in self._product.index_set()
        value = self._components(index)
        assert value in self._product.factor(index)
        return value

    def __getitem__(self, index: SetElement) -> SetElement:
        return self.component(index)

    def components(self) -> SetElementFamily:
        return self._components

    def __iter__(self) -> Iterator[SetElement]:
        index_set = self._product.index_set()
        assert index_set.is_finite() is True
        return iter(self.component(index) for index in index_set)

    def __repr__(self) -> str:
        return f"Point of {self._product}"


class ProductElementsCategory(Category):
    def __init__(self) -> None:
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=ProductElement)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, SetElements())
        return (self._inclusion,)

    def contains_product_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[ProductElement]:
        return candidate in self


_PRODUCT_ELEMENTS = ProductElementsCategory()


def ProductElements() -> ProductElementsCategory:
    return _PRODUCT_ELEMENTS


class ProductSet(SetObject):
    """The cartesian product of a set-indexed family of sets."""

    def __init__(
        self,
        diagram: Functor,
        *,
        category: Category,
        cardinality: Cardinal | None = None,
    ) -> None:
        self._diagram = diagram
        size = cardinality
        if size is None:
            size = _indexed_product_cardinality(
                self.index_set(),
                self.factor,
                factor_finiteness=(
                    True
                    if diagram.codomain().is_subcategory(FiniteSets())
                    else UNKNOWN
                ),
            )
        super().__init__(category=category, cardinality=size)

    def diagram(self) -> Functor:
        return self._diagram

    def index_category(self) -> DiscreteCategoryObject:
        value = self._diagram.domain()
        assert DiscreteCategories().contains_discrete_category(value)
        return value

    def index_set(self) -> SetObject:
        index_category = self.index_category()
        value = index_category.label_set()
        assert Sets().contains_set(value)
        return value

    def factor(self, index: SetElement) -> SetObject:
        assert index in self.index_set()
        value = self._diagram(self.index_category().object(index))
        assert Sets().contains_set(value)
        return value

    def factor_cardinalities(self) -> Functor:
        return DiscreteDiagram(
            self.index_category(),
            Cardinals(),
            lambda index: self.factor(index.label()).cardinality(),
        )

    def element(self, components: SetElementFamily) -> ProductElement:
        return ProductElement(self, components)

    def membership(self, member: SetElement) -> Decision:
        value = registered_value(member)
        return value is not None and ProductElements().contains_product_element(value) and value.product() is self

    def __iter__(self) -> Iterator[SetElement]:
        assert self.index_set().is_finite() is True
        indices = tuple(self.index_set())
        factors = tuple(self.factor(index) for index in indices)
        assert all(factor.is_finite() is True for factor in factors)
        for values in cartesian_product(*(tuple(factor) for factor in factors)):
            table = tuple(zip(indices, values, strict=True))

            def component(
                index: SetElement,
                table: tuple[tuple[SetElement, SetElement], ...] = table,
            ) -> SetElement:
                return next(value for key, value in table if key is index)

            yield self.element(component)

    def _projection(self, index: SetElement) -> SetMorphism:
        factor = self.factor(index)

        def project(member: SetElement) -> SetElement:
            assert ProductElements().contains_product_element(member)
            assert member.product() is self
            return member.component(index)

        return _set_morphism(self, factor, project)

    def __repr__(self) -> str:
        return f"Product of {self._diagram}"


class SetProductObject(ProductObject, ProductSet):
    """A product presentation whose apex is the same owned set object."""

    def __init__(
        self,
        *,
        category: ProductsOfSetsCategory,
        diagram: Functor,
        cardinality: Cardinal | None = None,
    ) -> None:
        ProductSet.__init__(
            self,
            diagram,
            category=category,
            cardinality=cardinality,
        )
        self._preimage = diagram
        self._image = self
        self._limit_presentation = _product_presentation(diagram, self)


class ProductsOfSetsCategory(ProductsOfCategory):
    """Products in ``Sets()``, with each product equal to its apex set."""

    ObjectType: type[SetProductObject] = SetProductObject
    ElementType: type[ProductElement] = ProductElement

    def __init__(self, functor: Functor) -> None:
        super().__init__(functor)
        _PRODUCTS_OF_SETS[id(self)] = self

    def __call__(
        self,
        preimage: MathematicalObject,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetProductObject:
        assert is_functor(preimage)
        return self._product(preimage, cardinality=cardinality)

    def limit_of(self, diagram: Functor) -> SetProductObject:
        return self._product(diagram)

    def product_of(self, diagram: Functor) -> SetProductObject:
        return self._product(diagram)

    def _product(
        self,
        diagram: Functor,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetProductObject:
        assert diagram in self.functor().domain()
        key = id(diagram)
        cached = self._limits.get(key)
        if cached is None:
            candidate = self.ObjectType(
                category=self,
                diagram=diagram,
                cardinality=cardinality,
            )
            assert self.contains_set_product(candidate)
            cached = candidate
            self._limits[key] = cached
        assert self.contains_set_product(cached)
        if cardinality is not None:
            assert cached.cardinality() == cardinality
        return cached

    def contains_set_product(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SetProductObject]:
        return candidate in self


_PRODUCTS_OF_SETS: dict[int, ProductsOfSetsCategory] = {}


def is_products_of_sets_category(
    category: Category,
) -> TypeIs[ProductsOfSetsCategory]:
    return _PRODUCTS_OF_SETS.get(id(category)) is category


class CoproductElement(SetElement):
    """A tagged element of a set-indexed disjoint union."""

    def __init__(
        self,
        coproduct: CoproductSet,
        index: SetElement,
        value: SetElement,
    ) -> None:
        assert index in coproduct.index_set()
        assert value in coproduct.cofactor(index)
        self._coproduct = coproduct
        self._index = index
        self._value = value
        super().__init__(
            category=CoproductElements(),
            ambient_object=coproduct,
        )

    def coproduct(self) -> CoproductSet:
        return self._coproduct

    def index(self) -> SetElement:
        return self._index

    def value(self) -> SetElement:
        return self._value


class CoproductElementsCategory(Category):
    def __init__(self) -> None:
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=CoproductElement)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, SetElements())
        return (self._inclusion,)

    def contains_coproduct_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[CoproductElement]:
        return candidate in self


_COPRODUCT_ELEMENTS = CoproductElementsCategory()


def CoproductElements() -> CoproductElementsCategory:
    return _COPRODUCT_ELEMENTS


class CoproductSet(SetObject):
    """The disjoint union of a set-indexed family of sets."""

    def __init__(
        self,
        diagram: Functor,
        *,
        category: Category,
        cardinality: Cardinal | None = None,
    ) -> None:
        self._diagram = diagram
        size = cardinality
        if size is None:
            size = _indexed_sum_cardinality(
                self.index_set(),
                self.cofactor,
                summand_finiteness=(
                    True
                    if diagram.codomain().is_subcategory(FiniteSets())
                    else UNKNOWN
                ),
            )
        super().__init__(category=category, cardinality=size)

    def diagram(self) -> Functor:
        return self._diagram

    def index_category(self) -> DiscreteCategoryObject:
        value = self._diagram.domain()
        assert DiscreteCategories().contains_discrete_category(value)
        return value

    def index_set(self) -> SetObject:
        index_category = self.index_category()
        value = index_category.label_set()
        assert Sets().contains_set(value)
        return value

    def cofactor(self, index: SetElement) -> SetObject:
        assert index in self.index_set()
        value = self._diagram(self.index_category().object(index))
        assert Sets().contains_set(value)
        return value

    def cofactor_cardinalities(self) -> Functor:
        return DiscreteDiagram(
            self.index_category(),
            Cardinals(),
            lambda index: self.cofactor(index.label()).cardinality(),
        )

    def element(self, index: SetElement, value: SetElement) -> CoproductElement:
        return CoproductElement(self, index, value)

    def membership(self, member: SetElement) -> Decision:
        value = registered_value(member)
        return value is not None and CoproductElements().contains_coproduct_element(value) and value.coproduct() is self

    def __iter__(self) -> Iterator[SetElement]:
        assert self.index_set().is_finite() is True
        for index in self.index_set():
            cofactor = self.cofactor(index)
            for value in cofactor:
                yield self.element(index, value)

    def _injection(self, index: SetElement) -> SetMorphism:
        return _set_morphism(
            self.cofactor(index),
            self,
            lambda value: self.element(index, value),
            injective=True,
        )

    def __repr__(self) -> str:
        return f"Coproduct of {self._diagram}"


class SetCoproductObject(CoproductObject, CoproductSet):
    """A coproduct presentation whose apex is the same owned set object."""

    def __init__(
        self,
        *,
        category: CoproductsOfSetsCategory,
        diagram: Functor,
        cardinality: Cardinal | None = None,
    ) -> None:
        CoproductSet.__init__(
            self,
            diagram,
            category=category,
            cardinality=cardinality,
        )
        self._preimage = diagram
        self._image = self
        self._colimit_presentation = _coproduct_presentation(diagram, self)


class CoproductsOfSetsCategory(CoproductsOfCategory):
    """Coproducts in ``Sets()``, with each coproduct equal to its apex set."""

    ObjectType: type[SetCoproductObject] = SetCoproductObject
    ElementType: type[CoproductElement] = CoproductElement

    def __init__(self, functor: Functor) -> None:
        super().__init__(functor)
        _COPRODUCTS_OF_SETS[id(self)] = self

    def __call__(
        self,
        preimage: MathematicalObject,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetCoproductObject:
        assert is_functor(preimage)
        return self._coproduct(preimage, cardinality=cardinality)

    def colimit_of(self, diagram: Functor) -> SetCoproductObject:
        return self._coproduct(diagram)

    def coproduct_of(self, diagram: Functor) -> SetCoproductObject:
        return self._coproduct(diagram)

    def _coproduct(
        self,
        diagram: Functor,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetCoproductObject:
        assert diagram in self.functor().domain()
        key = id(diagram)
        cached = self._colimits.get(key)
        if cached is None:
            candidate = self.ObjectType(
                category=self,
                diagram=diagram,
                cardinality=cardinality,
            )
            assert self.contains_set_coproduct(candidate)
            cached = candidate
            self._colimits[key] = cached
        assert self.contains_set_coproduct(cached)
        if cardinality is not None:
            assert cached.cardinality() == cardinality
        return cached

    def contains_set_coproduct(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SetCoproductObject]:
        return candidate in self


_COPRODUCTS_OF_SETS: dict[int, CoproductsOfSetsCategory] = {}


def is_coproducts_of_sets_category(
    category: Category,
) -> TypeIs[CoproductsOfSetsCategory]:
    return _COPRODUCTS_OF_SETS.get(id(category)) is category


class LimitSet(ProductSet):
    """The compatible families that form a limit in ``Sets``."""

    def __init__(
        self,
        diagram: Functor,
        *,
        category: Category,
        cardinality: Cardinal | None = None,
    ) -> None:
        self._compatible_elements: set[int] = set()
        size = UnknownCardinality() if cardinality is None else cardinality
        super().__init__(diagram, category=category, cardinality=size)

    def _compatible_element(
        self,
        components: SetElementFamily,
    ) -> ProductElement:
        member = self.element(components)
        self._compatible_elements.add(id(member))
        return member

    def index_set(self) -> SetObject:
        return index_objects(self.diagram().domain())

    def factor(self, index: SetElement) -> SetObject:
        assert index in self.index_set()
        diagram_object = index.value()
        assert diagram_object in self.diagram().domain()
        value = self.diagram()(diagram_object)
        assert Sets().contains_set(value)
        return value

    def _limit_projection(self, index: MathematicalObject) -> SetMorphism:
        return self._projection(_object_set_element(self.diagram().domain(), index))

    def membership(self, member: SetElement) -> Decision:
        product_membership = super().membership(member)
        if product_membership is not True:
            return product_membership
        if id(member) in self._compatible_elements:
            return True
        arrows = index_arrows(self.diagram().domain())
        if arrows.is_finite() is not True:
            return UNKNOWN
        value = registered_value(member)
        assert value is not None and ProductElements().contains_product_element(value)
        for candidate in arrows:
            arrow = candidate.value()
            assert self.diagram().domain().contains_arrow(arrow)
            image = self.diagram()(arrow)
            assert Sets().contains_set_morphism(image)
            source_index = _object_set_element(self.diagram().domain(), arrow.domain())
            target_index = _object_set_element(self.diagram().domain(), arrow.codomain())
            if image(value.component(source_index)) != value.component(target_index):
                return False
        return True

    def __iter__(self) -> Iterator[SetElement]:
        for member in super().__iter__():
            if self.membership(member) is True:
                yield member


class SetLimitObject(LimitObject, LimitSet):
    """A limit presentation whose apex is the same owned set object."""

    def __init__(
        self,
        *,
        category: LimitsOfSetsCategory,
        diagram: Functor,
        cardinality: Cardinal | None = None,
    ) -> None:
        LimitSet.__init__(
            self,
            diagram,
            category=category,
            cardinality=cardinality,
        )
        self._preimage = diagram
        self._image = self
        self._limit_presentation = _limit_presentation(diagram, self)

    def universal_morphism(self, cone: ConeObject) -> SetMorphism:
        morphism = LimitObject.universal_morphism(self, cone)
        assert Sets().contains_set_morphism(morphism)
        return morphism


class LimitsOfSetsCategory(LimitsOfCategory):
    """Limits in ``Sets()``, with each limit equal to its apex set."""

    ObjectType: type[SetLimitObject] = SetLimitObject
    ElementType: type[ProductElement] = ProductElement

    def __init__(self, functor: Functor) -> None:
        super().__init__(functor)
        _LIMITS_OF_SETS[id(self)] = self

    def __call__(
        self,
        preimage: MathematicalObject,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetLimitObject:
        assert is_functor(preimage)
        return self._limit(preimage, cardinality=cardinality)

    def limit_of(self, diagram: Functor) -> SetLimitObject:
        return self._limit(diagram)

    def _limit(
        self,
        diagram: Functor,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetLimitObject:
        assert diagram in self.functor().domain()
        key = id(diagram)
        cached = self._limits.get(key)
        if cached is None:
            candidate = self.ObjectType(
                category=self,
                diagram=diagram,
                cardinality=cardinality,
            )
            assert self.contains_set_limit(candidate)
            cached = candidate
            self._limits[key] = cached
        assert self.contains_set_limit(cached)
        if cardinality is not None:
            assert cached.cardinality() == cardinality
        return cached

    def contains_set_limit(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SetLimitObject]:
        return candidate in self


_LIMITS_OF_SETS: dict[int, LimitsOfSetsCategory] = {}


def is_limits_of_sets_category(
    category: Category,
) -> TypeIs[LimitsOfSetsCategory]:
    return _LIMITS_OF_SETS.get(id(category)) is category


class ColimitElement(SetElement):
    """An element of a Set colimit, represented by one coproduct term."""

    def __init__(self, colimit: ColimitSet, representative: CoproductElement) -> None:
        assert representative.coproduct() is colimit.coproduct()
        self._colimit = colimit
        self._representative = representative
        super().__init__(
            category=ColimitElements(),
            ambient_object=colimit,
        )

    def colimit(self) -> ColimitSet:
        return self._colimit

    def representative(self) -> CoproductElement:
        return self._representative

    def __eq__(self, candidate: Any) -> bool:
        if candidate is self:
            return True
        value = registered_value(candidate)
        if value is None or not ColimitElements().contains_colimit_element(value):
            return False
        if value.colimit() is not self._colimit:
            return False
        answer = self._colimit.equivalent(self, value)
        assert answer is not UNKNOWN, "equality in this colimit is not decidable from its presentation"
        return answer

    def __hash__(self) -> int:
        return hash(id(self._colimit))


class ColimitElementsCategory(Category):
    def __init__(self) -> None:
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=ColimitElement)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, SetElements())
        return (self._inclusion,)

    def contains_colimit_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[ColimitElement]:
        return candidate in self


_COLIMIT_ELEMENTS = ColimitElementsCategory()


def ColimitElements() -> ColimitElementsCategory:
    return _COLIMIT_ELEMENTS


class ColimitSet(SetObject):
    """The quotient presentation of a small Set diagram's coproduct."""

    def __init__(
        self,
        diagram: Functor,
        *,
        category: Category,
        cardinality: Cardinal | None = None,
    ) -> None:
        self._diagram = diagram
        objects = index_objects(diagram.domain())
        discrete_objects = DiscreteCategory(objects)
        object_diagram = SetFamily(
            discrete_objects,
            lambda index: self._object_image(index.label()),
        )
        self._coproduct = CoproductSet(
            object_diagram,
            category=Sets(),
        )
        super().__init__(category=category, cardinality=cardinality)

    def _object_image(self, index: SetElement) -> SetObject:
        value = self._diagram(index.value())
        assert Sets().contains_set(value)
        return value

    def diagram(self) -> Functor:
        return self._diagram

    def coproduct(self) -> CoproductSet:
        return self._coproduct

    def element(self, index: SetElement, value: SetElement) -> ColimitElement:
        return ColimitElement(self, self._coproduct.element(index, value))

    def membership(self, member: SetElement) -> Decision:
        value = registered_value(member)
        return value is not None and ColimitElements().contains_colimit_element(value) and value.colimit() is self

    def equivalent(
        self,
        left: ColimitElement,
        right: ColimitElement,
    ) -> Decision:
        assert left.colimit() is self and right.colimit() is self
        left_representative = left.representative()
        right_representative = right.representative()
        if _same_coproduct_term(left_representative, right_representative):
            return True
        arrows = index_arrows(self._diagram.domain())
        if arrows.is_finite() is not True:
            return UNKNOWN
        if _colimit_terms_are_related(
            self._diagram,
            arrows,
            left_representative,
            right_representative,
        ):
            return True
        indices = self._coproduct.index_set()
        if indices.is_finite() is not True:
            return UNKNOWN
        for index in indices:
            if self._coproduct.cofactor(index).is_finite() is not True:
                return UNKNOWN
        representatives: tuple[CoproductElement, ...] = ()
        for representative in self._coproduct:
            value = registered_value(representative)
            assert value is not None
            assert CoproductElements().contains_coproduct_element(value)
            representatives = (*representatives, value)
        reached: tuple[CoproductElement, ...] = (left_representative,)
        while True:
            enlarged = tuple(
                candidate
                for candidate in representatives
                if not any(_same_coproduct_term(candidate, known) for known in reached)
                and any(
                    _colimit_terms_are_related(
                        self._diagram,
                        arrows,
                        candidate,
                        known,
                    )
                    for known in reached
                )
            )
            if not enlarged:
                return False
            reached = (*reached, *enlarged)
            if any(_same_coproduct_term(right_representative, known) for known in reached):
                return True

    def __iter__(self) -> Iterator[SetElement]:
        chosen: tuple[ColimitElement, ...] = ()
        for representative in self._coproduct:
            value = registered_value(representative)
            assert value is not None and CoproductElements().contains_coproduct_element(value)
            candidate = ColimitElement(self, value)
            if any(self.equivalent(candidate, known) is True for known in chosen):
                continue
            chosen = (*chosen, candidate)
            yield candidate

    def _injection(self, index: SetElement) -> SetMorphism:
        return _set_morphism(
            self._coproduct.cofactor(index),
            self,
            lambda value: self.element(index, value),
        )


class SetColimitObject(ColimitObject, ColimitSet):
    """A colimit presentation whose apex is the same owned set object."""

    def __init__(
        self,
        *,
        category: ColimitsOfSetsCategory,
        diagram: Functor,
        cardinality: Cardinal | None = None,
    ) -> None:
        ColimitSet.__init__(
            self,
            diagram,
            category=category,
            cardinality=cardinality,
        )
        self._preimage = diagram
        self._image = self
        self._colimit_presentation = _colimit_presentation(diagram, self)

    def universal_morphism(self, cocone: CoconeObject) -> SetMorphism:
        morphism = ColimitObject.universal_morphism(self, cocone)
        assert Sets().contains_set_morphism(morphism)
        return morphism


class ColimitsOfSetsCategory(ColimitsOfCategory):
    """Colimits in ``Sets()``, with each colimit equal to its apex set."""

    ObjectType: type[SetColimitObject] = SetColimitObject
    ElementType: type[ColimitElement] = ColimitElement

    def __init__(self, functor: Functor) -> None:
        super().__init__(functor)
        _COLIMITS_OF_SETS[id(self)] = self

    def __call__(
        self,
        preimage: MathematicalObject,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetColimitObject:
        assert is_functor(preimage)
        return self._colimit(preimage, cardinality=cardinality)

    def colimit_of(self, diagram: Functor) -> SetColimitObject:
        return self._colimit(diagram)

    def _colimit(
        self,
        diagram: Functor,
        *,
        cardinality: Cardinal | None = None,
    ) -> SetColimitObject:
        assert diagram in self.functor().domain()
        key = id(diagram)
        cached = self._colimits.get(key)
        if cached is None:
            candidate = self.ObjectType(
                category=self,
                diagram=diagram,
                cardinality=cardinality,
            )
            assert self.contains_set_colimit(candidate)
            cached = candidate
            self._colimits[key] = cached
        assert self.contains_set_colimit(cached)
        if cardinality is not None:
            assert cached.cardinality() == cardinality
        return cached

    def contains_set_colimit(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SetColimitObject]:
        return candidate in self


_COLIMITS_OF_SETS: dict[int, ColimitsOfSetsCategory] = {}


def is_colimits_of_sets_category(
    category: Category,
) -> TypeIs[ColimitsOfSetsCategory]:
    return _COLIMITS_OF_SETS.get(id(category)) is category


def _same_coproduct_term(
    left: CoproductElement,
    right: CoproductElement,
) -> bool:
    return left.index() is right.index() and left.value() == right.value()


def _colimit_terms_are_related(
    diagram: Functor,
    arrows: SetObject,
    left: CoproductElement,
    right: CoproductElement,
) -> bool:
    for candidate in arrows:
        arrow = candidate.value()
        assert diagram.domain().contains_arrow(arrow)
        image = diagram(arrow)
        assert Sets().contains_set_morphism(image)
        if left.index().value() is arrow.domain() and right.index().value() is arrow.codomain() and image(left.value()) == right.value():
            return True
        if right.index().value() is arrow.domain() and left.index().value() is arrow.codomain() and image(right.value()) == left.value():
            return True
    return False


def _object_set_element(
    index_category: Category,
    value: MathematicalObject,
) -> SetElement:
    assert value in index_category
    element = index_category.object_element(value)
    assert SetElements().contains_set_element(element)
    assert element.ambient_set() is index_objects(index_category)
    return element


def index_objects(index_category: Category) -> SetObject:
    represented = index_category.objects()
    assert Sets().contains_set(represented)
    return represented


def index_arrows(index_category: Category) -> SetObject:
    represented = index_category.arrows()
    assert Sets().contains_set(represented)
    return represented


def _indexed_product_cardinality(
    indices: SetObject,
    factors: Callable[[SetElement], SetObject],
    *,
    factor_finiteness: Decision = UNKNOWN,
) -> Cardinal:
    return Cardinals().indexed_product(
        indices,
        lambda index: factors(index).cardinality(),
        finiteness=(
            True
            if factor_finiteness is True and indices in FiniteSets()
            else UNKNOWN
        ),
    )


def _indexed_sum_cardinality(
    indices: SetObject,
    summands: Callable[[SetElement], SetObject],
    *,
    summand_finiteness: Decision = UNKNOWN,
) -> Cardinal:
    return Cardinals().indexed_sum(
        indices,
        lambda index: summands(index).cardinality(),
        finiteness=(
            True
            if summand_finiteness is True and indices in FiniteSets()
            else UNKNOWN
        ),
    )


def ProductOfSets(
    diagram: Functor,
    *,
    cardinality: Cardinal | None = None,
) -> ProductPresentation:
    assert diagram.codomain() is Sets()
    apex = ProductSet(
        diagram,
        category=Sets(),
        cardinality=cardinality,
    )
    return _product_presentation(diagram, apex)


def _product_presentation(
    diagram: Functor,
    apex: ProductSet,
) -> ProductPresentation:
    assert apex.diagram() is diagram

    def projection(index: MathematicalObject) -> Arrow:
        index_category = diagram.domain()
        assert DiscreteCategories().contains_discrete_category(index_category)
        assert index_category.contains_object(index)
        return apex._projection(index.label())

    cone = Cone(diagram, apex, projection)

    def mediate(other: ConeObject) -> Arrow:
        source = other.apex()
        assert Sets().contains_set(source)
        return _set_morphism(
            source,
            apex,
            lambda member: apex.element(
                lambda index: _cone_component_value(
                    other,
                    apex.index_category().object(index),
                    member,
                )
            ),
        )

    return Product(cone, mediate)


def _cone_component_value(
    cone: ConeObject,
    index: MathematicalObject,
    member: SetElement,
) -> SetElement:
    component = cone.structure_morphism(index)
    assert Sets().contains_set_morphism(component)
    return component(member)


def _CoproductPresentationOfSets(
    diagram: Functor,
    *,
    cardinality: Cardinal | None = None,
) -> CoproductPresentation:
    assert diagram.codomain() is Sets()
    apex = CoproductSet(
        diagram,
        category=Sets(),
        cardinality=cardinality,
    )
    return _coproduct_presentation(diagram, apex)


def _coproduct_presentation(
    diagram: Functor,
    apex: CoproductSet,
) -> CoproductPresentation:
    assert apex.diagram() is diagram

    def injection(index: MathematicalObject) -> Arrow:
        index_category = diagram.domain()
        assert DiscreteCategories().contains_discrete_category(index_category)
        assert index_category.contains_object(index)
        return apex._injection(index.label())

    cocone = Cocone(diagram, apex, injection)

    def mediate(other: CoconeObject) -> Arrow:
        target = other.apex()
        assert Sets().contains_set(target)

        def induced(member: SetElement) -> SetElement:
            assert CoproductElements().contains_coproduct_element(member)
            component = other.costructure_morphism(apex.index_category().object(member.index()))
            assert Sets().contains_set_morphism(component)
            return component(member.value())

        return _set_morphism(apex, target, induced)

    return Coproduct(cocone, mediate)


def LimitOfSets(
    diagram: Functor,
    *,
    cardinality: Cardinal | None = None,
) -> ProductPresentation:
    assert diagram.codomain() is Sets()
    apex = LimitSet(
        diagram,
        category=Sets(),
        cardinality=cardinality,
    )
    return _limit_presentation(diagram, apex)


def _limit_presentation(
    diagram: Functor,
    apex: LimitSet,
) -> ProductPresentation:
    assert apex.diagram() is diagram
    cone = Cone(
        diagram,
        apex,
        lambda index: apex._limit_projection(index),
    )

    def mediate(other: ConeObject) -> Arrow:
        source = other.apex()
        assert Sets().contains_set(source)
        return _set_morphism(
            source,
            apex,
            lambda member: apex._compatible_element(
                lambda index: _cone_component_value(
                    other,
                    index.value(),
                    member,
                )
            ),
        )

    return Product(cone, mediate)


def ColimitOfSets(
    diagram: Functor,
    *,
    cardinality: Cardinal | None = None,
) -> CoproductPresentation:
    assert diagram.codomain() is Sets()
    apex = ColimitSet(
        diagram,
        category=Sets(),
        cardinality=cardinality,
    )
    return _colimit_presentation(diagram, apex)


def _colimit_presentation(
    diagram: Functor,
    apex: ColimitSet,
) -> CoproductPresentation:
    assert apex.diagram() is diagram

    def injection(index: MathematicalObject) -> Arrow:
        return apex._injection(_object_set_element(diagram.domain(), index))

    cocone = Cocone(diagram, apex, injection)

    def mediate(other: CoconeObject) -> Arrow:
        target = other.apex()
        assert Sets().contains_set(target)

        def induced(member: SetElement) -> SetElement:
            assert ColimitElements().contains_colimit_element(member)
            representative = member.representative()
            component = other.costructure_morphism(representative.index().value())
            assert Sets().contains_set_morphism(component)
            return component(representative.value())

        return _set_morphism(apex, target, induced)

    return Coproduct(cocone, mediate)


def CartesianProductOfSets(
    factors: tuple[SetObject, ...],
) -> SetProductObject:
    labels = _finite_ordinal(len(factors))
    index = DiscreteCategory(labels)

    def factor(value: DiscreteObject) -> SetObject:
        from sage_categories.theories.ordinals import Ordinals

        label = value.label()
        ordinal_index = label.value()
        assert Ordinals().contains_ordinal(ordinal_index)
        return factors[ordinal_index.finite_value()]

    diagram = SetFamily(index, factor)
    size = Cardinals().product(*(factor.cardinality() for factor in factors))
    products = Sets().Products(index)
    assert is_products_of_sets_category(products)
    image = products(
        diagram,
        cardinality=size,
    )
    return image


def CartesianProductOfFamily(
    index_set: SetObject,
    factors: Callable[[SetElement], SetObject],
    *,
    cardinality: Cardinal | None = None,
) -> SetProductObject:
    index_category = DiscreteCategory(index_set)
    diagram = SetFamily(
        index_category,
        lambda index: factors(index.label()),
    )
    products = Sets().Products(index_category)
    assert is_products_of_sets_category(products)
    image = products(diagram, cardinality=cardinality)
    return image


def CartesianProductMorphismOfFamily(
    index_category: DiscreteCategoryObject,
    functions: SetMorphismFamily,
    *,
    domain_cardinality: Cardinal | None = None,
    codomain_cardinality: Cardinal | None = None,
) -> SetMorphism:
    def function(index: DiscreteObject) -> SetMorphism:
        value = functions(index)
        assert Sets().contains_set_morphism(value)
        return value

    def domain(index: DiscreteObject) -> SetObject:
        value = function(index).domain()
        assert Sets().contains_set(value)
        return value

    def codomain(index: DiscreteObject) -> SetObject:
        value = function(index).codomain()
        assert Sets().contains_set(value)
        return value

    source = SetFamily(index_category, domain)
    target = SetFamily(index_category, codomain)

    def component(index: MathematicalObject) -> Arrow:
        assert index_category.contains_object(index)
        return function(index)

    transformation = NaturalTransformation(
        source,
        target,
        component,
    )
    products = Sets().Products(index_category)
    assert is_products_of_sets_category(products)
    products(source, cardinality=domain_cardinality)
    products(target, cardinality=codomain_cardinality)
    image = Sets().ProductFunctor(index_category)(transformation)
    assert Sets().contains_set_morphism(image)
    return image


def _domain_cardinality(morphism: SetMorphism) -> Cardinal:
    domain = morphism.domain()
    assert Sets().contains_set(domain)
    return domain.cardinality()


def _codomain_cardinality(morphism: SetMorphism) -> Cardinal:
    codomain = morphism.codomain()
    assert Sets().contains_set(codomain)
    return codomain.cardinality()


def cartesian_product_morphism(*functions: SetMorphism) -> SetMorphism:
    labels = _finite_ordinal(len(functions))
    index_category = DiscreteCategory(labels)

    def function(index: DiscreteObject) -> SetMorphism:
        from sage_categories.theories.ordinals import Ordinals

        label = index.label()
        ordinal_index = label.value()
        assert Ordinals().contains_ordinal(ordinal_index)
        value = functions[ordinal_index.finite_value()]
        assert Sets().contains_set_morphism(value)
        return value

    return CartesianProductMorphismOfFamily(
        index_category,
        function,
        domain_cardinality=Cardinals().product(*(_domain_cardinality(morphism) for morphism in functions)),
        codomain_cardinality=Cardinals().product(*(_codomain_cardinality(morphism) for morphism in functions)),
    )


def DisjointUnionOfSets(
    cofactors: tuple[SetObject, ...],
) -> SetCoproductObject:
    labels = _finite_ordinal(len(cofactors))
    index = DiscreteCategory(labels)

    def cofactor(value: DiscreteObject) -> SetObject:
        from sage_categories.theories.ordinals import Ordinals

        label = value.label()
        ordinal_index = label.value()
        assert Ordinals().contains_ordinal(ordinal_index)
        return cofactors[ordinal_index.finite_value()]

    diagram = SetFamily(index, cofactor)
    coproducts = Sets().Coproducts(index)
    assert is_coproducts_of_sets_category(coproducts)
    image = coproducts(
        diagram,
        cardinality=Cardinals().sum(*(cofactor.cardinality() for cofactor in cofactors)),
    )
    return image


def CoproductOfSets(
    cofactors: tuple[SetObject, ...],
) -> SetCoproductObject:
    return DisjointUnionOfSets(cofactors)


def CoproductOfFamily(
    index_set: SetObject,
    cofactors: Callable[[SetElement], SetObject],
    *,
    cardinality: Cardinal | None = None,
) -> SetCoproductObject:
    index_category = DiscreteCategory(index_set)
    diagram = SetFamily(
        index_category,
        lambda index: cofactors(index.label()),
    )
    coproducts = Sets().Coproducts(index_category)
    assert is_coproducts_of_sets_category(coproducts)
    image = coproducts(diagram, cardinality=cardinality)
    return image


def CoproductMorphismOfFamily(
    index_category: DiscreteCategoryObject,
    functions: SetMorphismFamily,
    *,
    domain_cardinality: Cardinal | None = None,
    codomain_cardinality: Cardinal | None = None,
) -> SetMorphism:
    def function(index: DiscreteObject) -> SetMorphism:
        value = functions(index)
        assert Sets().contains_set_morphism(value)
        return value

    def domain(index: DiscreteObject) -> SetObject:
        value = function(index).domain()
        assert Sets().contains_set(value)
        return value

    def codomain(index: DiscreteObject) -> SetObject:
        value = function(index).codomain()
        assert Sets().contains_set(value)
        return value

    source = SetFamily(index_category, domain)
    target = SetFamily(index_category, codomain)

    def component(index: MathematicalObject) -> Arrow:
        assert index_category.contains_object(index)
        return function(index)

    transformation = NaturalTransformation(
        source,
        target,
        component,
    )
    coproducts = Sets().Coproducts(index_category)
    assert is_coproducts_of_sets_category(coproducts)
    coproducts(source, cardinality=domain_cardinality)
    coproducts(target, cardinality=codomain_cardinality)
    image = Sets().CoproductFunctor(index_category)(transformation)
    assert Sets().contains_set_morphism(image)
    return image


def coproduct_morphism(*functions: SetMorphism) -> SetMorphism:
    labels = _finite_ordinal(len(functions))
    index_category = DiscreteCategory(labels)

    def function(index: DiscreteObject) -> SetMorphism:
        from sage_categories.theories.ordinals import Ordinals

        label = index.label()
        ordinal_index = label.value()
        assert Ordinals().contains_ordinal(ordinal_index)
        value = functions[ordinal_index.finite_value()]
        assert Sets().contains_set_morphism(value)
        return value

    return CoproductMorphismOfFamily(
        index_category,
        function,
        domain_cardinality=Cardinals().sum(*(_domain_cardinality(morphism) for morphism in functions)),
        codomain_cardinality=Cardinals().sum(*(_codomain_cardinality(morphism) for morphism in functions)),
    )


def ExponentialOfSets(codomain: SetObject, exponent: SetObject) -> SetHomCategory:
    category = Sets().Hom(exponent, codomain)
    assert is_set_hom_category(category)
    return category


def _finite_ordinal(number_of_members: int) -> FiniteSetObject:
    from sage_categories.theories.ordinals import ordinal

    assert number_of_members >= 0
    return FiniteSet(ordinal(index) for index in range(number_of_members))


def TruthValues() -> FiniteSetObject:
    return _finite_ordinal(2)


def PowerSet(base_set: SetObject) -> SetHomCategory:
    return ExponentialOfSets(TruthValues(), base_set)


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
