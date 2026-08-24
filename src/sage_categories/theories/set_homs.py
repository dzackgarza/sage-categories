"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from itertools import product as cartesian_product
from typing import Any

from sage_categories.abstract_categories.functors import (
    DiscreteHomCategory,
    InclusionFunctor,
    StructuralFunctor,
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
)
from sage_categories.category import Category
from sage_categories.theories.cardinals import (
    Cardinal,
    Cardinals,
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
from sage_categories.theories.set_subobjects import (
    SetMorphism,
    SetSubset,
    SubsetsOfSet,
    _decision_and,
)
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalObject,
    registered_value,
)


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
        from sage_categories.theories.set_category import Sets

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
        morphism: SetMorphism,
    ) -> SetMorphism:
        from sage_categories.theories.set_category import Sets

        assert morphism in self
        assert Sets().contains_set_morphism(morphism)
        return morphism

    def from_callable_checked(
        self,
        action: Callable[[SetElement], SetElement],
    ) -> SetMorphism:
        domain = self.domain()
        codomain = self.codomain()
        assert domain.is_finite() is True
        for member in domain:
            image = action(member)
            assert image.ambient_set() is codomain
            assert codomain.membership(image) is True
        return self._construct(action, UNKNOWN, UNKNOWN)

    def _construct(
        self,
        action: Callable[[SetElement], SetElement],
        injective: Decision,
        surjective: Decision,
    ) -> SetMorphism:
        return self.ObjectType(
            hom_category=self,
            action=action,
            injective=injective,
            surjective=surjective,
        )

    def Hom(
        self,
        target: MathematicalObject,
    ) -> SetHomCategory:
        from sage_categories.theories.set_category import Sets

        assert Sets().contains_set(target)
        return Sets().Hom(self, target)

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and value._belongs_to_hom(self)

    def _membership_(self, candidate: SetElement) -> Decision:
        return candidate in self

    def _cardinality_(self) -> Cardinal:
        from sage_categories.theories.set_category import Sets

        domain = self.domain()
        codomain = self.codomain()
        assert Sets().contains_set(domain)
        assert Sets().contains_set(codomain)
        return Cardinals().power(codomain.cardinality(), domain.cardinality())

    def objects(self) -> SetObject:
        return self

    def _hom_category_type(self) -> type[HomCategory]:
        return DiscreteHomCategory

    def identity(self) -> SetMorphism:
        assert self.domain() is self.codomain()
        return self._construct(
            lambda member: member,
            injective=True,
            surjective=True,
        )

    def compose(self, second: Arrow, first: Arrow) -> SetMorphism:
        from sage_categories.theories.set_category import Sets

        second = second.forward()
        first = first.forward()
        assert Sets().contains_set_morphism(second)
        assert Sets().contains_set_morphism(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return self._construct(
            lambda member: second(first(member)),
            injective=_decision_and(first.is_injective(), second.is_injective()),
            surjective=_decision_and(first.is_surjective(), second.is_surjective()),
        )

    def _set_iterator_(self) -> Iterator[SetElement]:
        from sage_categories.theories.set_category import Sets

        domain = self.domain()
        codomain = self.codomain()
        assert Sets().contains_set(domain)
        assert Sets().contains_set(codomain)
        assert domain.is_finite() is True and codomain.is_finite() is True
        domain_members = tuple(domain)
        if self.is_power_set():
            for choices in cartesian_product((False, True), repeat=len(domain_members)):
                yield self._from_members(
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
        from sage_categories.theories.set_category import Sets

        value = self.domain()
        assert Sets().contains_set(value)
        return value

    def base(self) -> SetObject:
        from sage_categories.theories.set_category import Sets

        value = self.codomain()
        assert Sets().contains_set(value)
        return value

    def base_set(self) -> SetObject:
        assert self.is_power_set()
        return self.exponent()

    def is_power_set(self) -> bool:
        from sage_categories.theories.set_constructions import TruthValues

        return self.codomain() is TruthValues()

    def from_predicate(
        self,
        predicate: MembershipPredicate,
    ) -> SetSubset:
        return self._from_predicate(
            predicate,
            UnknownCardinality(),
            None,
        )

    def _from_predicate(
        self,
        predicate: MembershipPredicate,
        cardinality: Cardinal,
        iterator: SetIterator | None,
    ) -> SetSubset:
        assert self.is_power_set()
        return SubsetsOfSet(self.exponent())(
            self,
            predicate=predicate,
            cardinality=cardinality,
            iterator=iterator,
            members=None,
        )

    def from_predicate_with_cardinality(
        self,
        predicate: MembershipPredicate,
        cardinality: Cardinal,
    ) -> SetSubset:
        return self._from_predicate(predicate, cardinality, None)

    def from_finite_set(self, members: SetObject) -> SetSubset:
        assert members.is_finite() is True
        represented: set[SetElement] = set()
        for member in members:
            value = member.value()
            assert SetElements().contains_set_element(value)
            represented.add(value)
        return self._from_members(frozenset(represented))

    def from_enumerated_image(self, function: SetMorphism) -> SetSubset:
        assert self.is_power_set()
        assert function.codomain() is self.exponent()
        return self._from_members(
            frozenset(function(member) for member in function.domain()),
        )

    def _from_members(self, members: frozenset[SetElement]) -> SetSubset:
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
        from sage_categories.theories.set_category import Sets
        from sage_categories.theories.set_constructions import TruthValues

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
            self._top_subset = self._from_predicate(
                lambda member: self.exponent().membership(member),
                self.exponent().cardinality(),
                lambda: iter(self.exponent()),
            )
        return self._top_subset

    def bottom(self) -> SetSubset:
        assert self.is_power_set()
        if self._bottom_subset is None:
            self._bottom_subset = self._from_members(frozenset())
        return self._bottom_subset

    def inverse_image_morphism(self, function: SetMorphism) -> SetMorphism:
        from sage_categories.theories.set_category import (
            Sets,
            _set_morphism_with_properties,
        )
        from sage_categories.theories.set_constructions import PowerSet

        assert self.is_power_set()
        assert function.codomain() is self.base_set()
        source = function.domain()
        assert Sets().contains_set(source)
        target_power_set = PowerSet(source)

        def inverse_image(candidate: SetElement) -> SetSubset:
            subset = self._represented_subset(candidate)
            return target_power_set.from_predicate(lambda member: subset.membership(function(member)))

        return _set_morphism_with_properties(
            self,
            target_power_set,
            inverse_image,
            function.is_surjective(),
            function.is_injective(),
        )

    def direct_image_morphism(self, function: SetMorphism) -> SetMorphism:
        from sage_categories.theories.set_category import (
            Sets,
            _set_morphism_with_properties,
        )
        from sage_categories.theories.set_constructions import PowerSet

        assert self.is_power_set()
        assert function.domain() is self.base_set()
        target = function.codomain()
        assert Sets().contains_set(target)
        target_power_set = PowerSet(target)

        def direct_image(candidate: SetElement) -> SetSubset:
            from sage_categories.theories.set_category import Sets

            subset = self._represented_subset(candidate)
            members = subset._represented_members()
            if members is not None:
                return target_power_set._from_members(
                    frozenset(function(member) for member in members),
                )
            inclusion = subset.inclusion().forward()
            assert Sets().contains_set_morphism(inclusion)
            restricted = Sets().compose(function, inclusion)
            assert Sets().contains_set_morphism(restricted)
            return restricted.image()

        return _set_morphism_with_properties(
            self,
            target_power_set,
            direct_image,
            function.is_injective(),
            function.is_surjective(),
        )

    def _represented_subset(self, candidate: MathematicalObject) -> SetSubset:
        value = registered_value(candidate)
        assert value is not None and value in self
        subsets = SubsetsOfSet(self.base_set())
        assert subsets.contains_subset(value)
        return value

    def evaluation(self) -> SetMorphism:
        from sage_categories.theories.discrete_sets import (
            DiscreteCategory,
            SetFamily,
        )
        from sage_categories.theories.set_category import (
            Sets,
            _set_morphism,
        )
        from sage_categories.theories.set_constructions import _finite_ordinal
        from sage_categories.theories.set_products import is_products_of_sets_category

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
    from sage_categories.theories.set_category import Sets

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
        from sage_categories.theories.set_category import Sets

        assert Sets().contains_set_morphism(underlying_arrow)
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )


class SetMonomorphismHomCategory(MonomorphismHomCategory):
    ObjectType = SetMonomorphism
    ElementType = SetMonomorphism

    def __call__(self, underlying_arrow: Arrow) -> SetMonomorphism:
        from sage_categories.theories.set_category import Sets

        assert Sets().contains_set_morphism(underlying_arrow)
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )


class SetEpimorphismHomCategory(EpimorphismHomCategory):
    ObjectType = SetEpimorphism
    ElementType = SetEpimorphism

    def __call__(self, underlying_arrow: Arrow) -> SetEpimorphism:
        from sage_categories.theories.set_category import Sets

        assert Sets().contains_set_morphism(underlying_arrow)
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )


class SetIsomorphismHomCategory(IsomorphismHomCategory):
    ObjectType = SetIsomorphism
    ElementType = SetIsomorphism


class SetAutomorphismHomCategory(IsomorphismHomCategory):
    ObjectType = SetAutomorphism
    ElementType = SetAutomorphism


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
        from sage_categories.theories.set_category import Sets

        if self._sets_inclusion is None:
            self._sets_inclusion = InclusionFunctor(self, Sets())
        return (self._sets_inclusion,)
