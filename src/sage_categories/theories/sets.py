"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from itertools import product as cartesian_product
from math import comb
from typing import Any, Protocol, TypeIs

from sage_categories.abstract_categories.functors import (
    DiscreteCategories,
    DiscreteDiagram,
    DiscreteHomCategory,
    DiscreteObject,
    Functor,
    InclusionFunctor,
    NaturalTransformation,
    StructuralFunctor,
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
    Cone,
    ConeObject,
    Coproduct,
    CoproductPresentation,
    Product,
    ProductPresentation,
    is_products_of_category,
)
from sage_categories.category import Category
from sage_categories.theories.cardinals import (
    UNKNOWN,
    Cardinal,
    Cardinals,
    Decision,
    UnknownCardinality,
    cardinal,
    is_cardinal_hom_category,
)
from sage_categories.values import (
    Arrow,
    MathematicalObject,
    MembershipInput,
    registered_value,
)

type SetElementInput = Any
type SetMapRule = Callable[[SetElementInput], SetElementInput]
type MembershipPredicate = Callable[[SetElementInput], Decision]
type SetIterator = Callable[[], Iterator[SetElementInput]]


class SymbolicSetRepresentation(Protocol):
    """The private symbolic operations required by an owned set."""

    def contains(self, member: SetElementInput) -> SetElementInput: ...

    def __iter__(self) -> Iterator[SetElementInput]: ...


type SetFunctionFamily = Callable[[DiscreteObject], SetFunction]


class SetObject(MathematicalObject):
    """The implementation shared by arbitrary owned sets."""

    def __init__(
        self,
        *,
        category: Category,
        cardinality: Cardinal | None = None,
    ) -> None:
        self._cardinality = UnknownCardinality() if cardinality is None else cardinality
        super().__init__(category=category)

    def contains(self, member: SetElementInput) -> Decision:
        """Return the represented membership decision for ``member``."""
        assert False, f"{self} has no represented membership predicate"

    def __contains__(self, member: SetElementInput) -> bool:
        answer = self.contains(member)
        assert answer is not UNKNOWN, f"membership in {self} is unknown"
        return answer

    def cardinality(self) -> Cardinal:
        return self._cardinality

    def is_finite(self) -> Decision:
        return self.cardinality().is_finite()

    def is_infinite(self) -> Decision:
        return self.cardinality().is_infinite()

    def is_countable(self) -> Decision:
        return self.cardinality().is_countable()

    def is_uncountable(self) -> Decision:
        return self.cardinality().is_uncountable()

    def __iter__(self) -> Iterator[SetElementInput]:
        assert False, f"{self} has no chosen enumeration"

    def exponential(self, exponent: SetObject) -> SetHomCategory:
        return ExponentialOfSets(self, exponent)

    def __pow__(self, exponent: SetObject) -> SetHomCategory:
        return self.exponential(exponent)

    def power_set(self) -> SetHomCategory:
        return PowerSet(self)

    def subsets_of_size(self, size: int) -> SetObject:
        return SubsetsOfSize(self, size)

    def finite_subsets(self) -> SetObject:
        return FiniteSubsets(self)

    def cartesian_product(self, *others: SetObject) -> SetObject:
        return CartesianProductOfSets((self, *others))

    def disjoint_union(self, *others: SetObject) -> SetObject:
        return DisjointUnionOfSets((self, *others))

    def __eq__(self, other: Any) -> bool:
        return other is self

    def __hash__(self) -> int:
        return id(self)


class FiniteSetObject(SetObject):
    """A set given by its complete finite member set."""

    def __init__(self, *, category: Category, members: frozenset[SetElementInput]) -> None:
        self._members = members
        super().__init__(category=category, cardinality=Cardinals()(len(members)))

    def contains(self, member: SetElementInput) -> Decision:
        return member in self._members

    def __iter__(self) -> Iterator[SetElementInput]:
        return iter(self._members)

    def members(self) -> frozenset[SetElementInput]:
        return self._members

    def __repr__(self) -> str:
        return "{" + ", ".join(map(repr, self._members)) + "}"


class PredicateSet(SetObject):
    """A set given by a membership predicate and optional enumeration."""

    def __init__(
        self,
        *,
        category: Category,
        predicate: MembershipPredicate,
        cardinality: Cardinal,
        iterator: SetIterator | None = None,
        representation: SymbolicSetRepresentation | None = None,
        name: str = "Predicate-defined set",
    ) -> None:
        self._predicate = predicate
        self._iterator = iterator
        self._representation = representation
        self._name = name
        super().__init__(category=category, cardinality=cardinality)

    def contains(self, member: SetElementInput) -> Decision:
        return self._predicate(member)

    def __iter__(self) -> Iterator[SetElementInput]:
        assert self._iterator is not None, f"{self} has no chosen enumeration"
        return self._iterator()

    def symbolic_representation(self) -> SymbolicSetRepresentation:
        assert self._representation is not None
        return self._representation

    def __repr__(self) -> str:
        return self._name


class SympySetObject(SetObject):
    """An owned set with a private SymPy set representation."""

    def __init__(
        self,
        *,
        representation: SymbolicSetRepresentation,
        cardinality: Cardinal | None = None,
        name: str = "Symbolic set",
    ) -> None:
        self._representation = representation
        self._name = name
        super().__init__(category=Sets(), cardinality=cardinality)

    def symbolic_representation(self) -> SymbolicSetRepresentation:
        return self._representation

    def membership_proposition(self, member: SetElementInput) -> SetElementInput:
        return self._representation.contains(member)

    def contains(self, member: SetElementInput) -> Decision:
        proposition = self.membership_proposition(member)
        if proposition in (True,):
            return True
        if proposition in (False,):
            return False
        return UNKNOWN

    def __iter__(self) -> Iterator[SetElementInput]:
        return iter(self._representation)

    def __repr__(self) -> str:
        return self._name


class SetFunction(Arrow):
    """An arbitrary function with declared domain, codomain, and rule."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        rule: SetMapRule,
        injective: Decision = UNKNOWN,
        surjective: Decision = UNKNOWN,
    ) -> None:
        self._rule = rule
        self._injective = injective
        self._surjective = surjective
        super().__init__(hom_category=hom_category)

    def __call__(self, member: SetElementInput) -> SetElementInput:
        domain = self.domain()
        codomain = self.codomain()
        assert Sets().contains_set(domain)
        assert Sets().contains_set(codomain)
        assert domain.contains(member) is not False
        image = self._rule(member)
        assert codomain.contains(image) is not False
        return image

    def rule(self) -> SetMapRule:
        return self._rule

    def is_injective(self) -> Decision:
        return self._injective

    def is_surjective(self) -> Decision:
        return self._surjective

    def is_bijective(self) -> Decision:
        return _decision_and(self._injective, self._surjective)


class SetSubset(SetFunction):
    """A subset, its characteristic function, and its inclusion arrow."""

    def __init__(
        self,
        *,
        category: SubsetsOfSetCategory,
        hom_category: SetHomCategory,
        predicate: MembershipPredicate,
        underlying_set: SetObject,
        inclusion: Arrow,
        members: frozenset[SetElementInput] | None,
    ) -> None:
        assert hom_category.codomain() is TruthValues()
        assert hom_category.domain() is category.base_set()
        assert inclusion in Sets().Mono(underlying_set, category.base_set())
        self._subset_category = category
        self._predicate = predicate
        self._underlying_set = underlying_set
        self._inclusion = inclusion
        self._members = members
        super().__init__(
            hom_category=hom_category,
            rule=lambda member: predicate(member) is True,
        )

    def category(self) -> Category:
        return self._subset_category

    def _belongs_to(self, category: Category) -> bool:
        return self._subset_category is category or self._subset_category.is_subcategory(category)

    def object(self) -> SetObject:
        return self._underlying_set

    def underlying_set(self) -> SetObject:
        return self._underlying_set

    def fixed_object(self) -> SetObject:
        return self.base_set()

    def structure_morphism(self) -> Arrow:
        return self._inclusion

    def base_set(self) -> SetObject:
        base = self.domain()
        assert Sets().contains_set(base)
        return base

    def characteristic_morphism(self) -> SetFunction:
        return self

    def inclusion(self) -> Arrow:
        return self._inclusion

    def members(self) -> frozenset[SetElementInput] | None:
        return self._members

    def equals(self, other: SetSubset) -> Decision:
        if self is other:
            return True
        if self.base_set() is not other.base_set():
            return False
        if self._members is not None and other._members is not None:
            return self._members == other._members
        return UNKNOWN

    def is_subset_of(self, other: SetSubset) -> Decision:
        assert self.base_set() is other.base_set()
        if self._members is None:
            return UNKNOWN
        answer: Decision = True
        for member in self._members:
            contained = other.underlying_set().contains(member)
            if contained is False:
                return False
            if contained is UNKNOWN:
                answer = UNKNOWN
        return answer

    def __le__(self, other: SetSubset) -> Decision:
        return self.is_subset_of(other)

    def union(self, other: SetSubset) -> SetSubset:
        assert self.base_set() is other.base_set()
        if self._members is not None and other._members is not None:
            return self.power_set().from_members(self._members | other._members)
        return self.power_set().from_predicate(
            lambda member: _decision_or(
                self.underlying_set().contains(member),
                other.underlying_set().contains(member),
            )
        )

    def intersection(self, other: SetSubset) -> SetSubset:
        assert self.base_set() is other.base_set()
        if self._members is not None and other._members is not None:
            return self.power_set().from_members(self._members & other._members)
        return self.power_set().from_predicate(
            lambda member: _decision_and(
                self.underlying_set().contains(member),
                other.underlying_set().contains(member),
            )
        )

    def difference(self, other: SetSubset) -> SetSubset:
        assert self.base_set() is other.base_set()
        if self._members is not None and other._members is not None:
            return self.power_set().from_members(self._members - other._members)
        return self.power_set().from_predicate(
            lambda member: _decision_and(
                self.underlying_set().contains(member),
                _decision_not(other.underlying_set().contains(member)),
            )
        )

    def symmetric_difference(self, other: SetSubset) -> SetSubset:
        assert self.base_set() is other.base_set()
        if self._members is not None and other._members is not None:
            return self.power_set().from_members(self._members ^ other._members)
        return self.union(other).difference(self.intersection(other))

    def complement(self) -> SetSubset:
        return self.power_set().from_predicate(lambda member: _decision_not(self.underlying_set().contains(member)))

    def __or__(self, other: SetSubset) -> SetSubset:
        return self.union(other)

    def power_set(self) -> SetHomCategory:
        return PowerSet(self.base_set())

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
        members: frozenset[SetElementInput] | None,
    ) -> SetSubset:
        def membership(member: SetElementInput) -> Decision:
            return _decision_and(self._base_set.contains(member), predicate(member))

        underlying_set = PredicateSet(
            category=Sets(),
            predicate=membership,
            cardinality=cardinality,
            iterator=iterator,
            name=f"Subset of {self._base_set}",
        )
        forward = SetMap(
            underlying_set,
            self._base_set,
            lambda member: member,
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

    ObjectType = SetFunction
    ElementType = SetFunction

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: HomCategoryFamily,
    ) -> None:
        self._evaluation: SetFunction | None = None
        super().__init__(
            domain=domain,
            codomain=codomain,
            hom_category=hom_category,
        )

    def __call__(
        self,
        rule: SetMapRule,
        *,
        injective: Decision = UNKNOWN,
        surjective: Decision = UNKNOWN,
    ) -> SetFunction:
        return self.ObjectType(
            hom_category=self,
            rule=rule,
            injective=injective,
            surjective=surjective,
        )

    def contains(self, candidate: SetElementInput) -> Decision:
        value = registered_value(candidate)
        return value is not None and value in self

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

    def identity(self, value: MathematicalObject | None = None) -> SetFunction:
        if value is not None:
            identity = Category.identity(self, value)
            assert Sets().contains_function(identity)
            return identity
        assert self.domain() is self.codomain()
        return self(
            lambda member: member,
            injective=True,
            surjective=True,
        )

    def compose(self, second: Arrow, first: Arrow) -> SetFunction:
        second = second.forward()
        first = first.forward()
        assert Sets().contains_function(second)
        assert Sets().contains_function(first)
        assert first.codomain() is second.domain()
        return self(
            lambda member: second(first(member)),
            injective=_decision_and(first.is_injective(), second.is_injective()),
            surjective=_decision_and(first.is_surjective(), second.is_surjective()),
        )

    def __iter__(self) -> Iterator[SetElementInput]:
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

            def rule(
                member: SetElementInput,
                table: tuple[tuple[SetElementInput, SetElementInput], ...] = table,
            ) -> SetElementInput:
                return next(image for source, image in table if source == member)

            yield self(rule)

    def exponent(self) -> SetObject:
        value = self.domain()
        assert Sets().contains_set(value)
        return value

    def base(self) -> SetObject:
        value = self.codomain()
        assert Sets().contains_set(value)
        return value

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

    def from_members(self, members: frozenset[SetElementInput]) -> SetSubset:
        assert self.is_power_set()
        assert all(self.exponent().contains(member) is True for member in members)
        return SubsetsOfSet(self.exponent())(
            self,
            lambda member: member in members,
            cardinality=cardinal(len(members)),
            iterator=lambda: iter(members),
            members=members,
        )

    def top(self) -> SetSubset:
        assert self.is_power_set()
        return self.from_predicate(
            lambda member: self.exponent().contains(member),
            cardinality=self.exponent().cardinality(),
            iterator=lambda: iter(self.exponent()),
        )

    def bottom(self) -> SetSubset:
        assert self.is_power_set()
        return self.from_members(frozenset())

    def evaluation(self) -> SetFunction:
        if self._evaluation is None:
            sets = Sets()
            exponent = self.exponent()
            base = self.base()
            labels = FiniteSet(frozenset({0, 1}))
            index_category = DiscreteCategory(labels)
            function_index = index_category.object(0)
            argument_index = index_category.object(1)
            diagram = SetFamily(
                index_category,
                lambda index: self if index is function_index else exponent,
            )
            product_functor = sets.ProductFunctor(index_category)
            products = product_functor.Image()
            assert is_products_of_category(products)
            product_object = products.product_of(diagram)
            product = product_object.image()
            assert sets.contains_set(product)
            function_projection = product_object.projection(function_index)
            argument_projection = product_object.projection(argument_index)
            assert sets.contains_function(function_projection)
            assert sets.contains_function(argument_projection)

            def evaluate(pair: SetElementInput) -> SetElementInput:
                function_value = registered_value(function_projection(pair))
                assert function_value is not None
                assert sets.contains_function(function_value)
                return function_value(argument_projection(pair))

            self._evaluation = SetMap(product, base, evaluate)
        return self._evaluation

    def __repr__(self) -> str:
        return f"{self.codomain()}^{self.domain()}"


def _underlying_set_function(arrow: Arrow) -> SetFunction:
    underlying = arrow.forward()
    assert Sets().contains_function(underlying)
    return underlying


class SetEndomorphism(Endomorphism):
    """A callable endomorphism in ``Sets``."""

    def __call__(self, member: SetElementInput) -> SetElementInput:
        return _underlying_set_function(self)(member)


class SetMonomorphism(Monomorphism):
    """A callable declared injection in ``Sets``."""

    def __call__(self, member: SetElementInput) -> SetElementInput:
        return _underlying_set_function(self)(member)

    def is_injective(self) -> Decision:
        return True


class SetEpimorphism(Epimorphism):
    """A callable declared surjection in ``Sets``."""

    def __call__(self, member: SetElementInput) -> SetElementInput:
        return _underlying_set_function(self)(member)

    def is_surjective(self) -> Decision:
        return True


class SetIsomorphism(Isomorphism):
    """A callable declared bijection in ``Sets``."""

    def __call__(self, member: SetElementInput) -> SetElementInput:
        return _underlying_set_function(self)(member)

    def is_injective(self) -> Decision:
        return True

    def is_surjective(self) -> Decision:
        return True

    def is_bijective(self) -> Decision:
        return True


class SetAutomorphism(Automorphism):
    """A callable declared automorphism in ``Sets``."""

    def __call__(self, member: SetElementInput) -> SetElementInput:
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
        assert Sets().contains_function(underlying_arrow)
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )


class SetMonomorphismHomCategory(MonomorphismHomCategory):
    ObjectType = SetMonomorphism
    ElementType = SetMonomorphism

    def __call__(self, underlying_arrow: Arrow) -> SetMonomorphism:
        assert Sets().contains_function(underlying_arrow)
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )


class SetEpimorphismHomCategory(EpimorphismHomCategory):
    ObjectType = SetEpimorphism
    ElementType = SetEpimorphism

    def __call__(self, underlying_arrow: Arrow) -> SetEpimorphism:
        assert Sets().contains_function(underlying_arrow)
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )


class SetIsomorphismHomCategory(IsomorphismHomCategory):
    ObjectType = SetIsomorphism
    ElementType = SetIsomorphism

    def __call__(self, forward: Arrow, backward: Arrow) -> SetIsomorphism:
        assert Sets().contains_function(forward)
        assert Sets().contains_function(backward)
        return self.ObjectType(
            hom_category=self,
            forward=forward,
            backward=backward,
        )


class SetAutomorphismHomCategory(IsomorphismHomCategory):
    ObjectType = SetAutomorphism
    ElementType = SetAutomorphism

    def __call__(self, forward: Arrow, backward: Arrow) -> SetAutomorphism:
        assert Sets().contains_function(forward)
        assert Sets().contains_function(backward)
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

    def on_object(self, source: MathematicalObject) -> Cardinal:
        assert source in self.domain()
        assert self._sets.contains_set(source)
        return source.cardinality()

    def on_morphism(self, morphism: Arrow) -> Arrow:
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


class SetsCategory(Category):
    """The category of arbitrary sets and arbitrary functions."""

    ObjectType = SetObject

    def __init__(self) -> None:
        self._finite_sets_by_members: dict[
            frozenset[SetElementInput],
            FiniteSetObject,
        ] = {}
        self._finite_sets: FiniteSetsCategory | None = None
        self._infinite_sets: InfiniteSetsCategory | None = None
        self._countable_sets: CountableSetsCategory | None = None
        self._uncountable_sets: UncountableSetsCategory | None = None
        self._cardinality_functor: CardinalityFunctor | None = None
        super().__init__(object_type=SetObject)

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

    def finite(self, members: frozenset[SetElementInput]) -> FiniteSetObject:
        cached = self._finite_sets_by_members.get(members)
        if cached is None:
            cached = FiniteSetObject(category=self, members=members)
            self._finite_sets_by_members[members] = cached
        return cached

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> HomCategory:
        category = Category.Hom(self, domain, codomain)
        if codomain is None:
            return category
        assert is_set_hom_category(category)
        return category

    def contains_set(self, candidate: MathematicalObject) -> TypeIs[SetObject]:
        return candidate in self

    def contains_function(self, candidate: MathematicalObject) -> TypeIs[SetFunction]:
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

    def chosen_limit(self, diagram: Functor) -> ProductPresentation:
        if diagram.domain() in DiscreteCategories():
            return ProductOfSets(diagram)
        return LimitOfSets(diagram)

    def chosen_colimit(self, diagram: Functor) -> CoproductPresentation:
        if diagram.domain() in DiscreteCategories():
            return CoproductOfSets(diagram)
        return ColimitOfSets(diagram)

    def __repr__(self) -> str:
        return "Sets"


class SetPropertyCategory(Category):
    """A property subcategory of ``Sets`` determined by cardinality."""

    def __init__(self, sets: SetsCategory) -> None:
        self._sets = sets
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=sets.ObjectType)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = InclusionFunctor(self, self._sets)
        return (self._inclusion,)


class CountableSetsCategory(SetPropertyCategory):
    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        if value is None or not Sets().contains_set(value):
            return False
        finite = value.cardinality().is_finite()
        return finite is True or value.cardinality() == Cardinals().aleph()


class FiniteSetsCategory(SetPropertyCategory):
    def __init__(self, sets: SetsCategory) -> None:
        self._countable_inclusion: InclusionFunctor | None = None
        super().__init__(sets)

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        return value is not None and Sets().contains_set(value) and value.cardinality().is_finite() is True

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._countable_inclusion is None:
            self._countable_inclusion = InclusionFunctor(self, self._sets.Countable())
        return (self._countable_inclusion,)

    def contains_finite_set(self, candidate: MathematicalObject) -> TypeIs[SetObject]:
        return candidate in self


class InfiniteSetsCategory(SetPropertyCategory):
    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        return value is not None and Sets().contains_set(value) and value.cardinality().is_infinite() is True


class UncountableSetsCategory(SetPropertyCategory):
    def __init__(self, sets: SetsCategory) -> None:
        self._infinite_inclusion: InclusionFunctor | None = None
        super().__init__(sets)

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        if value is None or not Sets().contains_set(value):
            return False
        size = value.cardinality()
        return size.is_infinite() is True and size != Cardinals().aleph()

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._infinite_inclusion is None:
            self._infinite_inclusion = InclusionFunctor(self, self._sets.Infinite())
        return (self._infinite_inclusion,)


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


def is_set_hom_category(category: HomCategory) -> TypeIs[SetHomCategory]:
    return category in Sets().HomCategory()


def FiniteSet(members: frozenset[SetElementInput]) -> FiniteSetObject:
    return Sets().finite(members)


def Set(members: frozenset[SetElementInput]) -> FiniteSetObject:
    return FiniteSet(members)


def ConditionSet(
    predicate: MembershipPredicate,
    *,
    cardinality: Cardinal | None = None,
    iterator: SetIterator | None = None,
    representation: SymbolicSetRepresentation | None = None,
    name: str = "Predicate-defined set",
) -> PredicateSet:
    size = UnknownCardinality() if cardinality is None else cardinality
    return PredicateSet(
        category=Sets(),
        predicate=predicate,
        cardinality=size,
        iterator=iterator,
        representation=representation,
        name=name,
    )


def SetFromSympy(
    representation: SymbolicSetRepresentation,
    *,
    cardinality: Cardinal | None = None,
    name: str = "Symbolic set",
) -> SympySetObject:
    return SympySetObject(
        representation=representation,
        cardinality=cardinality,
        name=name,
    )


def SetMap(
    domain: SetObject,
    codomain: SetObject,
    rule: SetMapRule,
    *,
    injective: Decision = UNKNOWN,
    surjective: Decision = UNKNOWN,
) -> SetFunction:
    hom_category = Sets().Hom(domain, codomain)
    assert is_set_hom_category(hom_category)
    return hom_category(
        rule,
        injective=injective,
        surjective=surjective,
    )


def SetMapFromMapping(
    domain: SetObject,
    codomain: SetObject,
    mapping: Mapping[SetElementInput, SetElementInput],
    *,
    injective: Decision = UNKNOWN,
    surjective: Decision = UNKNOWN,
) -> SetFunction:
    return SetMap(
        domain,
        codomain,
        mapping.__getitem__,
        injective=injective,
        surjective=surjective,
    )


class DiscreteObjectSet(SetObject):
    """The object set of one discrete category."""

    def __init__(self, category: DiscreteCategoryObject, labels: SetObject) -> None:
        self._discrete_category = category
        self._labels = labels
        super().__init__(category=Sets(), cardinality=labels.cardinality())

    def contains(self, member: SetElementInput) -> Decision:
        value = registered_value(member)
        return value is not None and value in self._discrete_category

    def __iter__(self) -> Iterator[SetElementInput]:
        return iter(tuple(self._discrete_category.object(label) for label in self._labels))


class DiscreteArrowSet(SetObject):
    """The identity arrows of one discrete category."""

    def __init__(self, category: DiscreteCategoryObject) -> None:
        self._discrete_category = category
        objects = category.objects()
        assert Sets().contains_set(objects)
        super().__init__(category=Sets(), cardinality=objects.cardinality())

    def contains(self, member: SetElementInput) -> Decision:
        value = registered_value(member)
        if value is None or not self._discrete_category.contains_arrow(value):
            return False
        return value.domain() is value.codomain()

    def __iter__(self) -> Iterator[SetElementInput]:
        return iter(tuple(self._discrete_category.Hom(value, value).identity() for value in self._discrete_category))


class FiniteDiscreteCategoriesCategory(Category):
    """The property subcategory of finite discrete categories."""

    ObjectType = DiscreteCategoryObject

    def __init__(self) -> None:
        self._inclusion: InclusionFunctor | None = None
        super().__init__(object_type=DiscreteCategoryObject)

    def __call__(self, label_set: SetObject) -> DiscreteCategoryObject:
        assert label_set.is_finite() is True
        return self.ObjectType(category=self, label_set=label_set)

    def __contains__(self, candidate: MembershipInput) -> bool:
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


class ProductElement(MathematicalObject):
    """A point of a set-indexed cartesian product."""

    def __init__(self, product: ProductSet, components: SetMapRule) -> None:
        self._product = product
        self._components = components
        super().__init__(category=ProductElements())

    def product(self) -> ProductSet:
        return self._product

    def component(self, index: SetElementInput) -> SetElementInput:
        assert self._product.index_set().contains(index) is True
        value = self._components(index)
        assert self._product.factor(index).contains(value) is True
        return value

    def __getitem__(self, index: SetElementInput) -> SetElementInput:
        return self.component(index)

    def components(self) -> SetMapRule:
        return self._components

    def __repr__(self) -> str:
        return f"Point of {self._product}"


class ProductElementsCategory(Category):
    def __init__(self) -> None:
        super().__init__(object_type=ProductElement)

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

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        indices = index_objects(diagram.domain())
        size = _indexed_product_cardinality(indices, self.factor)
        super().__init__(category=Sets(), cardinality=size)

    def diagram(self) -> Functor:
        return self._diagram

    def index_category(self) -> DiscreteCategoryObject:
        value = self._diagram.domain()
        assert DiscreteCategories().contains_discrete_category(value)
        return value

    def index_set(self) -> SetObject:
        return index_objects(self._diagram.domain())

    def factor(self, index: SetElementInput) -> SetObject:
        assert self.index_set().contains(index) is True
        value = self._diagram(index)
        assert Sets().contains_set(value)
        return value

    def factor_cardinalities(self) -> Functor:
        return DiscreteDiagram(
            self.index_category(),
            Cardinals(),
            lambda index: self.factor(index).cardinality(),
        )

    def element(self, components: SetMapRule) -> ProductElement:
        return ProductElement(self, components)

    def contains(self, member: SetElementInput) -> Decision:
        value = registered_value(member)
        return value is not None and ProductElements().contains_product_element(value) and value.product() is self

    def __iter__(self) -> Iterator[SetElementInput]:
        assert self.index_set().is_finite() is True
        indices = tuple(self.index_set())
        factors = tuple(self.factor(index) for index in indices)
        assert all(factor.is_finite() is True for factor in factors)
        for values in cartesian_product(*(tuple(factor) for factor in factors)):
            table = tuple(zip(indices, values, strict=True))

            def component(
                index: SetElementInput,
                table: tuple[tuple[SetElementInput, SetElementInput], ...] = table,
            ) -> SetElementInput:
                return next(value for key, value in table if key is index)

            yield self.element(component)

    def projection(self, index: SetElementInput) -> SetFunction:
        factor = self.factor(index)

        def project(member: SetElementInput) -> SetElementInput:
            value = registered_value(member)
            assert value is not None and ProductElements().contains_product_element(value)
            assert value.product() is self
            return value.component(index)

        return SetMap(self, factor, project)

    def __repr__(self) -> str:
        return f"Product of {self._diagram}"


class CoproductElement(MathematicalObject):
    """A tagged element of a set-indexed disjoint union."""

    def __init__(
        self,
        coproduct: CoproductSet,
        index: SetElementInput,
        value: SetElementInput,
    ) -> None:
        assert coproduct.index_set().contains(index) is True
        assert coproduct.cofactor(index).contains(value) is True
        self._coproduct = coproduct
        self._index = index
        self._value = value
        super().__init__(category=CoproductElements())

    def coproduct(self) -> CoproductSet:
        return self._coproduct

    def index(self) -> SetElementInput:
        return self._index

    def value(self) -> SetElementInput:
        return self._value


class CoproductElementsCategory(Category):
    def __init__(self) -> None:
        super().__init__(object_type=CoproductElement)

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

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        indices = index_objects(diagram.domain())
        size = _indexed_sum_cardinality(indices, self.cofactor)
        super().__init__(category=Sets(), cardinality=size)

    def diagram(self) -> Functor:
        return self._diagram

    def index_category(self) -> DiscreteCategoryObject:
        value = self._diagram.domain()
        assert DiscreteCategories().contains_discrete_category(value)
        return value

    def index_set(self) -> SetObject:
        return index_objects(self._diagram.domain())

    def cofactor(self, index: SetElementInput) -> SetObject:
        assert self.index_set().contains(index) is True
        value = self._diagram(index)
        assert Sets().contains_set(value)
        return value

    def cofactor_cardinalities(self) -> Functor:
        return DiscreteDiagram(
            self.index_category(),
            Cardinals(),
            lambda index: self.cofactor(index).cardinality(),
        )

    def element(self, index: SetElementInput, value: SetElementInput) -> CoproductElement:
        return CoproductElement(self, index, value)

    def contains(self, member: SetElementInput) -> Decision:
        value = registered_value(member)
        return value is not None and CoproductElements().contains_coproduct_element(value) and value.coproduct() is self

    def __iter__(self) -> Iterator[SetElementInput]:
        assert self.index_set().is_finite() is True
        for index in self.index_set():
            cofactor = self.cofactor(index)
            for value in cofactor:
                yield self.element(index, value)

    def injection(self, index: SetElementInput) -> SetFunction:
        return SetMap(
            self.cofactor(index),
            self,
            lambda value: self.element(index, value),
            injective=True,
        )

    def __repr__(self) -> str:
        return f"Coproduct of {self._diagram}"


class LimitSet(ProductSet):
    """The compatible families that form a limit in ``Sets``."""

    def __init__(
        self,
        diagram: Functor,
        *,
        cardinality: Cardinal | None = None,
    ) -> None:
        super().__init__(diagram)
        self._cardinality = UnknownCardinality() if cardinality is None else cardinality

    def contains(self, member: SetElementInput) -> Decision:
        product_membership = super().contains(member)
        if product_membership is not True:
            return product_membership
        arrows = index_arrows(self.diagram().domain())
        if arrows.is_finite() is not True:
            return UNKNOWN
        value = registered_value(member)
        assert value is not None and ProductElements().contains_product_element(value)
        for candidate in arrows:
            arrow = registered_value(candidate)
            assert arrow is not None and self.diagram().domain().contains_arrow(arrow)
            image = self.diagram()(arrow)
            assert Sets().contains_function(image)
            if image(value.component(arrow.domain())) != value.component(arrow.codomain()):
                return False
        return True

    def __iter__(self) -> Iterator[SetElementInput]:
        for member in super().__iter__():
            if self.contains(member) is True:
                yield member


class ColimitElement(MathematicalObject):
    """An element of a Set colimit, represented by one coproduct term."""

    def __init__(self, colimit: ColimitSet, representative: CoproductElement) -> None:
        assert representative.coproduct() is colimit.coproduct()
        self._colimit = colimit
        self._representative = representative
        super().__init__(category=ColimitElements())

    def colimit(self) -> ColimitSet:
        return self._colimit

    def representative(self) -> CoproductElement:
        return self._representative

    def __eq__(self, other: Any) -> bool:
        if other is self:
            return True
        value = registered_value(other)
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
        super().__init__(object_type=ColimitElement)

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
        cardinality: Cardinal | None = None,
    ) -> None:
        self._diagram = diagram
        self._coproduct = CoproductSet(diagram)
        super().__init__(category=Sets(), cardinality=cardinality)

    def diagram(self) -> Functor:
        return self._diagram

    def coproduct(self) -> CoproductSet:
        return self._coproduct

    def element(self, index: SetElementInput, value: SetElementInput) -> ColimitElement:
        return ColimitElement(self, self._coproduct.element(index, value))

    def contains(self, member: SetElementInput) -> Decision:
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
        if self._coproduct.is_finite() is not True:
            return UNKNOWN
        representatives = tuple(self._coproduct)
        reached = (left_representative,)
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

    def __iter__(self) -> Iterator[SetElementInput]:
        assert self._coproduct.is_finite() is True
        chosen: tuple[ColimitElement, ...] = ()
        for representative in self._coproduct:
            value = registered_value(representative)
            assert value is not None and CoproductElements().contains_coproduct_element(value)
            candidate = ColimitElement(self, value)
            if any(self.equivalent(candidate, known) is True for known in chosen):
                continue
            chosen = (*chosen, candidate)
            yield candidate

    def injection(self, index: SetElementInput) -> SetFunction:
        return SetMap(
            self._coproduct.cofactor(index),
            self,
            lambda value: self.element(index, value),
        )


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
        arrow = registered_value(candidate)
        assert arrow is not None and diagram.domain().contains_arrow(arrow)
        image = diagram(arrow)
        assert Sets().contains_function(image)
        if left.index() is arrow.domain() and right.index() is arrow.codomain() and image(left.value()) == right.value():
            return True
        if right.index() is arrow.domain() and left.index() is arrow.codomain() and image(right.value()) == left.value():
            return True
    return False


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
    factors: Callable[[SetElementInput], SetObject],
) -> Cardinal:
    if indices.is_finite() is True:
        return Cardinals().product(*(factors(index).cardinality() for index in indices))
    return Cardinals().indexed_product(
        indices,
        lambda index: factors(index).cardinality(),
    )


def _indexed_sum_cardinality(
    indices: SetObject,
    summands: Callable[[SetElementInput], SetObject],
) -> Cardinal:
    if indices.is_finite() is True:
        return Cardinals().sum(*(summands(index).cardinality() for index in indices))
    return Cardinals().indexed_sum(
        indices,
        lambda index: summands(index).cardinality(),
    )


def ProductOfSets(diagram: Functor) -> ProductPresentation:
    assert diagram.codomain() is Sets()
    apex = ProductSet(diagram)

    def projection(index: MathematicalObject) -> Arrow:
        return apex.projection(index)

    cone = Cone(diagram, apex, projection)

    def mediate(other: ConeObject) -> Arrow:
        source = other.apex()
        assert Sets().contains_set(source)
        return SetMap(
            source,
            apex,
            lambda member: apex.element(lambda index: _cone_component_value(other, index, member)),
        )

    return Product(cone, mediate)


def _cone_component_value(
    cone: ConeObject,
    index: SetElementInput,
    member: SetElementInput,
) -> SetElementInput:
    component = cone.structure_morphism(index)
    assert Sets().contains_function(component)
    return component(member)


def CoproductOfSets(diagram: Functor) -> CoproductPresentation:
    assert diagram.codomain() is Sets()
    apex = CoproductSet(diagram)

    def injection(index: MathematicalObject) -> Arrow:
        return apex.injection(index)

    cocone = Cocone(diagram, apex, injection)

    def mediate(other: CoconeObject) -> Arrow:
        target = other.apex()
        assert Sets().contains_set(target)

        def induced(member: SetElementInput) -> SetElementInput:
            value = registered_value(member)
            assert value is not None and CoproductElements().contains_coproduct_element(value)
            component = other.costructure_morphism(value.index())
            assert Sets().contains_function(component)
            return component(value.value())

        return SetMap(apex, target, induced)

    return Coproduct(cocone, mediate)


def LimitOfSets(
    diagram: Functor,
    *,
    cardinality: Cardinal | None = None,
) -> ProductPresentation:
    assert diagram.codomain() is Sets()
    apex = LimitSet(diagram, cardinality=cardinality)
    cone = Cone(diagram, apex, apex.projection)

    def mediate(other: ConeObject) -> Arrow:
        source = other.apex()
        assert Sets().contains_set(source)
        return SetMap(
            source,
            apex,
            lambda member: apex.element(lambda index: _cone_component_value(other, index, member)),
        )

    return Product(cone, mediate)


def ColimitOfSets(
    diagram: Functor,
    *,
    cardinality: Cardinal | None = None,
) -> CoproductPresentation:
    assert diagram.codomain() is Sets()
    apex = ColimitSet(diagram, cardinality=cardinality)
    cocone = Cocone(diagram, apex, apex.injection)

    def mediate(other: CoconeObject) -> Arrow:
        target = other.apex()
        assert Sets().contains_set(target)

        def induced(member: SetElementInput) -> SetElementInput:
            value = registered_value(member)
            assert value is not None and ColimitElements().contains_colimit_element(value)
            representative = value.representative()
            component = other.costructure_morphism(representative.index())
            assert Sets().contains_function(component)
            return component(representative.value())

        return SetMap(apex, target, induced)

    return Coproduct(cocone, mediate)


def CartesianProductOfSets(factors: tuple[SetObject, ...]) -> SetObject:
    labels = FiniteSet(frozenset(range(len(factors))))
    index = DiscreteCategory(labels)
    diagram = SetFamily(index, lambda value: factors[value.label()])
    image = Sets().ProductFunctor(index)(diagram)
    assert Sets().contains_set(image)
    return image


def CartesianProductMorphismOfFamily(
    index_category: DiscreteCategoryObject,
    functions: SetFunctionFamily,
) -> SetFunction:
    def function(index: DiscreteObject) -> SetFunction:
        value = functions(index)
        assert Sets().contains_function(value)
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
    image = Sets().ProductFunctor(index_category)(transformation)
    assert Sets().contains_function(image)
    return image


def cartesian_product_morphism(*functions: SetFunction) -> SetFunction:
    labels = FiniteSet(frozenset(range(len(functions))))
    index_category = DiscreteCategory(labels)

    def function(index: DiscreteObject) -> SetFunction:
        value = functions[index.label()]
        assert Sets().contains_function(value)
        return value

    return CartesianProductMorphismOfFamily(index_category, function)


def DisjointUnionOfSets(cofactors: tuple[SetObject, ...]) -> SetObject:
    labels = FiniteSet(frozenset(range(len(cofactors))))
    index = DiscreteCategory(labels)
    diagram = SetFamily(index, lambda value: cofactors[value.label()])
    image = Sets().CoproductFunctor(index)(diagram)
    assert Sets().contains_set(image)
    return image


def CoproductMorphismOfFamily(
    index_category: DiscreteCategoryObject,
    functions: SetFunctionFamily,
) -> SetFunction:
    def function(index: DiscreteObject) -> SetFunction:
        value = functions(index)
        assert Sets().contains_function(value)
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
    image = Sets().CoproductFunctor(index_category)(transformation)
    assert Sets().contains_function(image)
    return image


def coproduct_morphism(*functions: SetFunction) -> SetFunction:
    labels = FiniteSet(frozenset(range(len(functions))))
    index_category = DiscreteCategory(labels)

    def function(index: DiscreteObject) -> SetFunction:
        value = functions[index.label()]
        assert Sets().contains_function(value)
        return value

    return CoproductMorphismOfFamily(index_category, function)


def ExponentialOfSets(codomain: SetObject, exponent: SetObject) -> SetHomCategory:
    category = Sets().Hom(exponent, codomain)
    assert is_set_hom_category(category)
    return category


_TRUTH_VALUES = FiniteSet(frozenset({False, True}))


def TruthValues() -> FiniteSetObject:
    return _TRUTH_VALUES


def PowerSet(base_set: SetObject) -> SetHomCategory:
    return ExponentialOfSets(TruthValues(), base_set)


def SubsetsOfSize(base_set: SetObject, size: int) -> SetObject:
    assert size >= 0
    power_set = PowerSet(base_set)
    cardinality = UnknownCardinality()
    if base_set.is_finite() is True:
        cardinality = Cardinals()(comb(int(base_set.cardinality()), size))
    return PredicateSet(
        category=Sets(),
        predicate=lambda candidate: _has_subset_cardinality(power_set, candidate, size),
        cardinality=cardinality,
        name=f"Subsets of {base_set} with cardinality {size}",
    )


def _has_subset_cardinality(
    power_set: SetHomCategory,
    candidate: SetElementInput,
    size: int,
) -> Decision:
    value = registered_value(candidate)
    if value is None or not Sets().contains_set(value):
        return False
    if value not in power_set:
        return False
    return value.cardinality() == size


def FiniteSubsets(base_set: SetObject) -> SetObject:
    power_set = PowerSet(base_set)
    return PredicateSet(
        category=Sets(),
        predicate=lambda candidate: _is_finite_subset(power_set, candidate),
        cardinality=UnknownCardinality(),
        name=f"Finite subsets of {base_set}",
    )


def _is_finite_subset(
    power_set: SetHomCategory,
    candidate: SetElementInput,
) -> Decision:
    value = registered_value(candidate)
    if value is None or not Sets().contains_set(value):
        return False
    if value not in power_set:
        return False
    return value.is_finite()


def ImageSet(function: SetFunction) -> SetObject:
    domain = function.domain()
    assert Sets().contains_set(domain)
    if domain.is_finite() is True:
        return FiniteSet(frozenset(function(member) for member in domain))
    return PredicateSet(
        category=Sets(),
        predicate=lambda member: UNKNOWN,
        cardinality=UnknownCardinality(),
        name=f"Image of {function}",
    )
