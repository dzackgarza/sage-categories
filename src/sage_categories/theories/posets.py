"""Partially and totally ordered sets over the owned ``Sets`` category.

The mathematical surface follows ``specs/ordered-sets.md`` and the mature
Sage finite-poset interface.  Ordered objects and arrows retain their set
implementations through explicit structural functors.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeIs

from sage_categories.abstract_categories.category_constructions import (
    PullbackCategory,
    PullbackObject,
)
from sage_categories.abstract_categories.functors import (
    StructuralFunctor,
    compose_functors,
)
from sage_categories.abstract_categories.hom_categories import HomCategory
from sage_categories.category import Category
from sage_categories.theories.sets import (
    FiniteSet,
    FiniteSets,
    SetElementInput,
    SetFunction,
    SetMapDefinition,
    SetObject,
    Sets,
    is_set_hom_category,
)
from sage_categories.values import (
    UNKNOWN,
    Arrow,
    Decision,
    MathematicalElement,
    MathematicalObject,
    registered_value,
)

type OrderRelation = Callable[[SetElementInput, SetElementInput], bool]
type PosetMapDefinition = SetMapDefinition | SetFunction


class PosetObject(MathematicalObject):
    """A set equipped with one chosen partial order."""

    def __init__(
        self,
        *,
        category: PartiallyOrderedSetsCategory,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> None:
        assert underlying_set in Sets()
        self._underlying_set = underlying_set
        self._relation = relation
        super().__init__(category=category)

    def _set_implementation(self) -> SetObject:
        return self._underlying_set

    def le(self, left: SetElementInput, right: SetElementInput) -> bool:
        assert self._underlying_set.contains(left) is True
        assert self._underlying_set.contains(right) is True
        return self._relation(left, right)

    def is_lequal(self, left: SetElementInput, right: SetElementInput) -> bool:
        return self.le(left, right)

    def is_less_than(self, left: SetElementInput, right: SetElementInput) -> bool:
        return self.le(left, right) and left != right

    def compare_elements(
        self,
        left: SetElementInput,
        right: SetElementInput,
    ) -> int | None:
        if self.le(left, right):
            return 0 if self.le(right, left) else -1
        if self.le(right, left):
            return 1
        return None

    def __repr__(self) -> str:
        return f"Partially ordered {self._underlying_set}"


class PosetMorphism(Arrow):
    """An order-preserving map with its underlying set function."""

    def __init__(
        self,
        *,
        hom_category: PosetHomCategory,
        underlying_function: SetFunction,
    ) -> None:
        source = hom_category.domain()
        target = hom_category.codomain()
        category = hom_category.base_category()
        assert is_partially_ordered_sets_category(category)
        assert category.contains_poset(source)
        assert category.contains_poset(target)
        assert underlying_function in Sets().Hom(
            category.underlying_set(source),
            category.underlying_set(target),
        )
        self._underlying_function = underlying_function
        super().__init__(hom_category=hom_category)

    def _set_implementation(self) -> SetFunction:
        return self._underlying_function

    def is_order_preserving(self) -> bool:
        return True

    def is_order_reflecting(self) -> Decision:
        source = self.domain()
        target = self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        assert category.contains_poset(source)
        assert category.contains_poset(target)
        members = category.underlying_set(source)
        if members.is_finite() is not True:
            return UNKNOWN
        for left in members:
            for right in members:
                if target.le(
                    self._underlying_function(left),
                    self._underlying_function(right),
                ) and not source.le(left, right):
                    return False
        return True

    def is_order_embedding(self) -> Decision:
        return self.is_order_reflecting()

    def is_order_isomorphism(self) -> Decision:
        bijective = self._underlying_function.is_bijective()
        reflecting = self.is_order_reflecting()
        if bijective is False or reflecting is False:
            return False
        if bijective is UNKNOWN or reflecting is UNKNOWN:
            return UNKNOWN
        return True

    def inverse(self) -> PosetMorphism:
        assert self.is_order_isomorphism() is True
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        inverse = self._underlying_function.inverse()
        hom_category = category.Hom(self.codomain(), self.domain())
        assert is_poset_hom_category(hom_category)
        return hom_category(inverse)


class PosetHomCategory(HomCategory):
    """The order-preserving maps between two posets."""

    ObjectType = PosetMorphism
    ElementType = PosetMorphism

    def __call__(
        self,
        definition: PosetMapDefinition,
        *,
        injective: Decision = UNKNOWN,
        surjective: Decision = UNKNOWN,
    ) -> PosetMorphism:
        existing = registered_value(definition)
        if existing is not None and self.contains_poset_morphism(existing):
            return existing
        source = self.domain()
        target = self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        assert category.contains_poset(source)
        assert category.contains_poset(target)
        set_hom = Sets().Hom(
            category.underlying_set(source),
            category.underlying_set(target),
        )
        assert is_set_hom_category(set_hom)
        if existing is not None:
            assert Sets().contains_function(existing)
            underlying = existing
        else:
            underlying = set_hom(
                definition,
                injective=injective,
                surjective=surjective,
            )
        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def identity(self, value: MathematicalObject | None = None) -> PosetMorphism:
        assert value is None
        assert self.domain() is self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        source = self.domain()
        assert category.contains_poset(source)
        underlying = Sets().identity(category.underlying_set(source))
        assert Sets().contains_function(underlying)
        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def compose(self, second: Arrow, first: Arrow) -> PosetMorphism:
        assert self.contains_poset_morphism(second)
        assert self.contains_poset_morphism(first)
        assert first.codomain() is second.domain()
        underlying = Sets().compose(
            second._set_implementation(),
            first._set_implementation(),
        )
        assert Sets().contains_function(underlying)
        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def contains_poset_morphism(
        self,
        arrow: MathematicalObject,
    ) -> TypeIs[PosetMorphism]:
        return arrow in self


class ForgetPosetFunctor(StructuralFunctor):
    """Forget the chosen order and retain the underlying set and function."""

    def __init__(self, posets: PartiallyOrderedSetsCategory) -> None:
        self._posets = posets
        super().__init__(posets, Sets())

    def on_object(self, source: MathematicalObject) -> SetObject:
        assert self._posets.contains_poset(source)
        return source._set_implementation()

    def on_morphism(self, morphism: Arrow) -> SetFunction:
        hom_category = morphism.hom_category()
        assert is_poset_hom_category(hom_category)
        assert hom_category.contains_poset_morphism(morphism)
        return morphism._set_implementation()

    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        assert self._posets.contains_poset(source)
        return element

    def is_faithful(self) -> bool:
        return True


class FinitePosetsCategory(PullbackCategory):
    """The pullback of posets and finite sets over sets."""

    def __repr__(self) -> str:
        return "Finite partially ordered sets"


class PartiallyOrderedSetsCategory(Category):
    """Sets equipped with a chosen partial order."""

    ObjectType = PosetObject

    def __init__(self) -> None:
        self._forgetful_functor: ForgetPosetFunctor | None = None
        self._finite_posets: FinitePosetsCategory | None = None
        super().__init__(object_type=PosetObject)

    def __call__(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> PosetObject:
        return self.ObjectType(
            category=self,
            underlying_set=underlying_set,
            relation=relation,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return PosetHomCategory

    def forgetful_functor(self) -> ForgetPosetFunctor:
        if self._forgetful_functor is None:
            self._forgetful_functor = ForgetPosetFunctor(self)
        return self._forgetful_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (self.forgetful_functor(),)

    def contains_poset(self, candidate: MathematicalObject) -> TypeIs[PosetObject]:
        return candidate in self

    def underlying_set(self, source: MathematicalObject) -> SetObject:
        assert source in self
        image = self.forgetful_functor()(source)
        assert Sets().contains_set(image)
        return image

    def Finite(self) -> FinitePosetsCategory:
        if self._finite_posets is None:
            finite_to_countable = FiniteSets().super_functors()[0]
            countable_to_sets = finite_to_countable.codomain().super_functors()[0]
            finite_to_sets = compose_functors(
                countable_to_sets,
                finite_to_countable,
            )
            self._finite_posets = FinitePosetsCategory(
                self.forgetful_functor(),
                finite_to_sets,
            )
        return self._finite_posets

    def __repr__(self) -> str:
        return "Partially ordered sets"


class TotallyOrderedSetObject(MathematicalObject):
    """A poset with a chosen finite total-order enumeration."""

    def __init__(
        self,
        *,
        category: TotallyOrderedSetsCategory,
        poset: PosetObject,
        enumeration: tuple[SetElementInput, ...],
    ) -> None:
        self._poset = poset
        self._enumeration = enumeration
        super().__init__(category=category)

    def _poset_implementation(self) -> PosetObject:
        return self._poset

    def __getitem__(self, position: int) -> SetElementInput:
        assert position >= 0
        return self._enumeration[position]

    def position(self, member: SetElementInput) -> int:
        assert self._poset._set_implementation().contains(member) is True
        return self._enumeration.index(member)

    def rank(self, member: SetElementInput) -> int:
        return self.position(member)

    def unrank(self, position: int) -> SetElementInput:
        return self[position]

    def __repr__(self) -> str:
        return "[" + ", ".join(map(repr, self._enumeration)) + "]"


class TotallyOrderedSetMorphism(Arrow):
    """A monotone map between two totally ordered sets."""

    def __init__(
        self,
        *,
        hom_category: TotallyOrderedSetHomCategory,
        poset_morphism: PosetMorphism,
    ) -> None:
        self._poset_morphism = poset_morphism
        super().__init__(hom_category=hom_category)

    def _poset_implementation(self) -> PosetMorphism:
        return self._poset_morphism


class TotallyOrderedSetHomCategory(HomCategory):
    """The monotone maps between two totally ordered sets."""

    ObjectType = TotallyOrderedSetMorphism
    ElementType = TotallyOrderedSetMorphism

    def __call__(
        self,
        definition: PosetMapDefinition,
        *,
        injective: Decision = UNKNOWN,
        surjective: Decision = UNKNOWN,
    ) -> TotallyOrderedSetMorphism:
        category = self.base_category()
        assert is_totally_ordered_sets_category(category)
        domain = self.domain()
        codomain = self.codomain()
        assert category.contains_total_order(domain)
        assert category.contains_total_order(codomain)
        source = category.underlying_poset(domain)
        target = category.underlying_poset(codomain)
        poset_hom = PartiallyOrderedSets().Hom(source, target)
        assert is_poset_hom_category(poset_hom)
        underlying = poset_hom(
            definition,
            injective=injective,
            surjective=surjective,
        )
        return self.ObjectType(
            hom_category=self,
            poset_morphism=underlying,
        )

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> TotallyOrderedSetMorphism:
        assert value is None
        assert self.domain() is self.codomain()
        category = self.base_category()
        assert is_totally_ordered_sets_category(category)
        domain = self.domain()
        assert category.contains_total_order(domain)
        source = category.underlying_poset(domain)
        underlying = PartiallyOrderedSets().identity(source)
        underlying_hom = underlying.hom_category()
        assert is_poset_hom_category(underlying_hom)
        assert underlying_hom.contains_poset_morphism(underlying)
        return self.ObjectType(
            hom_category=self,
            poset_morphism=underlying,
        )

    def compose(
        self,
        second: Arrow,
        first: Arrow,
    ) -> TotallyOrderedSetMorphism:
        assert self.contains_total_order_morphism(second)
        assert self.contains_total_order_morphism(first)
        underlying = PartiallyOrderedSets().compose(
            second._poset_implementation(),
            first._poset_implementation(),
        )
        underlying_hom = underlying.hom_category()
        assert is_poset_hom_category(underlying_hom)
        assert underlying_hom.contains_poset_morphism(underlying)
        return self.ObjectType(
            hom_category=self,
            poset_morphism=underlying,
        )

    def contains_total_order_morphism(
        self,
        arrow: MathematicalObject,
    ) -> TypeIs[TotallyOrderedSetMorphism]:
        return arrow in self


class TotalOrderInclusionFunctor(StructuralFunctor):
    """Regard a total order as its underlying partial order."""

    def __init__(self, total_orders: TotallyOrderedSetsCategory) -> None:
        self._total_orders = total_orders
        super().__init__(total_orders, PartiallyOrderedSets())

    def on_object(self, source: MathematicalObject) -> PosetObject:
        assert self._total_orders.contains_total_order(source)
        return source._poset_implementation()

    def on_morphism(self, morphism: Arrow) -> PosetMorphism:
        hom_category = morphism.hom_category()
        assert is_total_order_hom_category(hom_category)
        assert hom_category.contains_total_order_morphism(morphism)
        return morphism._poset_implementation()

    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        assert self._total_orders.contains_total_order(source)
        return element

    def is_faithful(self) -> bool:
        return True


class FiniteTotallyOrderedSetsCategory(PullbackCategory):
    """The pullback of total orders and finite sets over sets."""

    def __repr__(self) -> str:
        return "Finite totally ordered sets"


class TotallyOrderedSetsCategory(Category):
    """Sets equipped with a chosen total order."""

    ObjectType = TotallyOrderedSetObject

    def __init__(self) -> None:
        self._inclusion: TotalOrderInclusionFunctor | None = None
        self._finite_orders: FiniteTotallyOrderedSetsCategory | None = None
        super().__init__(object_type=TotallyOrderedSetObject)

    def __call__(
        self,
        poset: PosetObject,
        enumeration: tuple[SetElementInput, ...],
    ) -> TotallyOrderedSetObject:
        assert poset._set_implementation().is_finite() is True
        assert len(enumeration) == poset._set_implementation().cardinality()
        return self.ObjectType(
            category=self,
            poset=poset,
            enumeration=enumeration,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return TotallyOrderedSetHomCategory

    def inclusion(self) -> TotalOrderInclusionFunctor:
        if self._inclusion is None:
            self._inclusion = TotalOrderInclusionFunctor(self)
        return self._inclusion

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (self.inclusion(),)

    def contains_total_order(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[TotallyOrderedSetObject]:
        return candidate in self

    def underlying_poset(self, source: MathematicalObject) -> PosetObject:
        assert source in self
        image = self.inclusion()(source)
        assert PartiallyOrderedSets().contains_poset(image)
        return image

    def Finite(self) -> FiniteTotallyOrderedSetsCategory:
        if self._finite_orders is None:
            total_to_sets = compose_functors(
                PartiallyOrderedSets().forgetful_functor(),
                self.inclusion(),
            )
            finite_to_countable = FiniteSets().super_functors()[0]
            finite_to_sets = compose_functors(
                finite_to_countable.codomain().super_functors()[0],
                finite_to_countable,
            )
            self._finite_orders = FiniteTotallyOrderedSetsCategory(
                total_to_sets,
                finite_to_sets,
            )
        return self._finite_orders

    def __repr__(self) -> str:
        return "Totally ordered sets"


_PARTIALLY_ORDERED_SETS: PartiallyOrderedSetsCategory | None = None
_TOTALLY_ORDERED_SETS: TotallyOrderedSetsCategory | None = None
_ORDERED_FINITE_SETS: dict[
    tuple[SetElementInput, ...],
    PullbackObject,
] = {}


def PartiallyOrderedSets() -> PartiallyOrderedSetsCategory:
    global _PARTIALLY_ORDERED_SETS

    if _PARTIALLY_ORDERED_SETS is None:
        _PARTIALLY_ORDERED_SETS = PartiallyOrderedSetsCategory()
    return _PARTIALLY_ORDERED_SETS


def TotallyOrderedSets() -> TotallyOrderedSetsCategory:
    global _TOTALLY_ORDERED_SETS

    if _TOTALLY_ORDERED_SETS is None:
        _TOTALLY_ORDERED_SETS = TotallyOrderedSetsCategory()
    return _TOTALLY_ORDERED_SETS


def FinitePosets() -> FinitePosetsCategory:
    return PartiallyOrderedSets().Finite()


def FiniteTotallyOrderedSets() -> FiniteTotallyOrderedSetsCategory:
    return TotallyOrderedSets().Finite()


def Poset(
    data: tuple[Iterable[SetElementInput], OrderRelation],
) -> PullbackObject:
    """Construct the finite poset defined by ``(members, leq)``."""
    members, relation = data
    underlying_set = FiniteSet(tuple(dict.fromkeys(members)))
    poset = PartiallyOrderedSets()(underlying_set, relation)
    return FinitePosets()(poset, underlying_set)


def ordered_set_owned_by(
    elements: Iterable[SetElementInput],
) -> PullbackObject:
    enumeration = tuple(dict.fromkeys(elements))
    cached = _ORDERED_FINITE_SETS.get(enumeration)
    if cached is None:
        underlying_set = FiniteSet(enumeration)
        positions = {element: index for index, element in enumerate(enumeration)}
        poset = PartiallyOrderedSets()(
            underlying_set,
            lambda left, right: positions[left] <= positions[right],
        )
        total_order = TotallyOrderedSets()(poset, enumeration)
        cached = FiniteTotallyOrderedSets()(total_order, underlying_set)
        _ORDERED_FINITE_SETS[enumeration] = cached
    return cached


def finite_ordered_set(
    elements: Iterable[SetElementInput],
) -> PullbackObject:
    return ordered_set_owned_by(elements)


def is_partially_ordered_sets_category(
    category: Category,
) -> TypeIs[PartiallyOrderedSetsCategory]:
    return category is PartiallyOrderedSets()


def is_totally_ordered_sets_category(
    category: Category,
) -> TypeIs[TotallyOrderedSetsCategory]:
    return category is TotallyOrderedSets()


def is_poset_hom_category(
    category: HomCategory,
) -> TypeIs[PosetHomCategory]:
    return category.base_category() is PartiallyOrderedSets() and category in PartiallyOrderedSets().HomCategory()


def is_total_order_hom_category(
    category: HomCategory,
) -> TypeIs[TotallyOrderedSetHomCategory]:
    return category.base_category() is TotallyOrderedSets() and category in TotallyOrderedSets().HomCategory()
