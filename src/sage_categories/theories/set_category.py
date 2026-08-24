"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
)
from sage_categories.abstract_categories.functors import (
    DiscreteCategories,
    Functor,
    InclusionFunctor,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.abstract_categories.products import (
    CoproductPresentation,
    ProductPresentation,
)
from sage_categories.category import Category
from sage_categories.theories.cardinals import (
    Cardinal,
    Cardinals,
    UnknownCardinality,
)
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.posets import (
        PartiallyOrderedSetsCategory,
        SimplexOrderIndexing,
        TotallyOrderedSetsCategory,
    )


from sage_categories.theories.set_elements import (
    SetElement,
    SetElementFamily,
)
from sage_categories.theories.set_functors import (
    CardinalityFunctor,
    ExponentialFunctor,
    InverseImagePowerSetFunctor,
)
from sage_categories.theories.set_homs import (
    SetAutomorphismCategoryFamily,
    SetEndomorphismCategoryFamily,
    SetEpimorphismCategoryFamily,
    SetHomCategory,
    SetHomCategoryFamily,
    SetIsomorphismCategoryFamily,
    SetMonomorphism,
    SetMonomorphismCategoryFamily,
    SetMonomorphismHomCategory,
)
from sage_categories.theories.set_objects import (
    Aleph,
    FiniteSetElement,
    FiniteSetObject,
    SetObject,
)
from sage_categories.theories.set_subobjects import (
    SetMorphism,
    SetSubset,
)

if TYPE_CHECKING:
    from sage_categories.theories.set_colimits import (
        SetColimitObject,
    )
    from sage_categories.theories.set_limits import (
        SetLimitObject,
    )


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
        from sage_categories.abstract_categories.cat import Cat

        self.Limits(Cat())
        self.Colimits(Cat())

    def _hom_category_type(self) -> type[HomCategory]:
        return SetHomCategory

    def relation(
        self,
        base_set: SetObject,
        relation: SetSubset,
    ) -> SetSubset:
        """Return an owned subobject of ``base_set`` squared as a relation."""
        from sage_categories.theories.set_constructions import CartesianProductOfSets

        assert base_set in self
        product = CartesianProductOfSets((base_set, base_set))
        assert relation.base_set() is product
        return relation

    def binary_predicate(
        self,
        base_set: SetObject,
        rule: Callable[[SetElement, SetElement], Decision],
    ) -> SetSubset:
        """Construct an owned predicate subobject of ``base_set`` squared."""
        from sage_categories.theories.set_constructions import CartesianProductOfSets
        from sage_categories.theories.set_products import ProductElements

        product = CartesianProductOfSets((base_set, base_set))
        indices = tuple(product.index_set())
        assert len(indices) == 2

        def contains_pair(pair: SetElement) -> Decision:
            assert ProductElements().contains_product_element(pair)
            return rule(
                pair.component(indices[0]),
                pair.component(indices[1]),
            )

        return product.subset_from(contains_pair)

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
        codomain: MathematicalObject,
    ) -> SetHomCategory:
        category = Category.Hom(self, domain, codomain)
        assert is_set_hom_category(category)
        return category

    def Mono(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> SetMonomorphismHomCategory:
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
        from sage_categories.theories.set_constructions import (
            LimitOfSets,
            ProductOfSets,
        )

        if diagram.domain() in DiscreteCategories():
            return ProductOfSets(diagram)
        return LimitOfSets(diagram)

    def chosen_colimit(self, diagram: Functor) -> CoproductPresentation:
        from sage_categories.theories.set_constructions import (
            ColimitOfSets,
            _CoproductPresentationOfSets,
        )

        if diagram.domain() in DiscreteCategories():
            return _CoproductPresentationOfSets(diagram)
        return ColimitOfSets(diagram)

    def equalizer(self, first: Arrow, second: Arrow) -> SetLimitObject:
        # The generic construction already builds it; in Sets its apex is a set.
        from sage_categories.theories.set_limits import (
            is_limits_of_sets_category,
        )

        result = super().equalizer(first, second)
        limits = result.category()
        assert is_limits_of_sets_category(limits)
        assert limits.contains_set_limit(result)
        return result

    def coequalizer(self, first: Arrow, second: Arrow) -> SetColimitObject:
        # The generic construction already builds it; in Sets its apex is a set.
        from sage_categories.theories.set_colimits import (
            is_colimits_of_sets_category,
        )

        result = super().coequalizer(first, second)
        colimits = result.category()
        assert is_colimits_of_sets_category(colimits)
        assert colimits.contains_set_colimit(result)
        return result

    def pullback(
        self,
        first: Arrow,
        second: Arrow,
    ) -> SetLimitObject:
        return self._pullback(first, second, UnknownCardinality())

    def pullback_with_cardinality(
        self,
        first: Arrow,
        second: Arrow,
        cardinality: Cardinal,
    ) -> SetLimitObject:
        return self._pullback(first, second, cardinality)

    def _pullback(
        self,
        first: Arrow,
        second: Arrow,
        cardinality: Cardinal,
    ) -> SetLimitObject:
        from sage_categories.abstract_categories.products import DiagramCategory
        from sage_categories.theories.set_limits import (
            is_limits_of_sets_category,
        )

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
        if cardinality is UnknownCardinality():
            return limits(diagram)
        return limits.with_cardinality(diagram, cardinality)

    def _products_of_category(self, functor: Functor) -> Category:
        from sage_categories.theories.set_products import ProductsOfSetsCategory

        return ProductsOfSetsCategory(functor)

    def _coproducts_of_category(self, functor: Functor) -> Category:
        from sage_categories.theories.set_coproducts import CoproductsOfSetsCategory

        return CoproductsOfSetsCategory(functor)

    def _limits_of_category(self, functor: Functor) -> Category:
        from sage_categories.theories.set_limits import LimitsOfSetsCategory

        return LimitsOfSetsCategory(functor)

    def _colimits_of_category(self, functor: Functor) -> Category:
        from sage_categories.theories.set_colimits import ColimitsOfSetsCategory

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
        return finite is True or value.cardinality() == Cardinals().aleph(0)


class FiniteSetsCategory(FullSubcategory):
    def __init__(self, sets: SetsCategory) -> None:
        self._sets = sets
        self._finite_sets_by_members: dict[
            frozenset[MathematicalObject],
            MathematicalObject,
        ] = {}
        super().__init__(
            sets.Countable(),
            self._is_finite,
            name="Finite sets",
        )

    def __call__(self, members: frozenset[MathematicalObject]) -> MathematicalObject:
        cached = self._finite_sets_by_members.get(members)
        if cached is None:
            ambient = FiniteSetObject(category=Sets(), values=members)
            countable = CountableSets()._refine_object(ambient)
            cached = self._refine_object(countable)
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
        return size.is_infinite() is True and size != Cardinals().aleph(0)


_SETS: SetsCategory | None = None


def Sets() -> SetsCategory:
    global _SETS

    if _SETS is None:
        _SETS = SetsCategory()
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


def FiniteSet(members: Iterable[MathematicalObject]) -> MathematicalObject:
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
