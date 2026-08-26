"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.functors import (
    Functor,
    is_functor,
)
from sage_categories.abstract_categories.products import (
    LimitObject,
    LimitsOfCategory,
)
from sage_categories.category import Category
from sage_categories.theories.cardinals import (
    Cardinal,
    Cardinals,
)
from sage_categories.theories.set_category import (
    Sets,
)
from sage_categories.theories.set_elements import (
    SetElement,
    SetElementFamily,
)
from sage_categories.theories.set_objects import (
    SetObject,
)
from sage_categories.theories.set_products import (
    ProductElement,
    ProductElements,
    ProductSet,
    ProductSetElement,
    is_product_set_element,
)
from sage_categories.types import (
    Decision,
    MathematicalObject,
    Unknown,
    UnknownClass,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.set_subobjects import SetMorphism


class LimitSet(ProductSet):
    """The compatible families that form a limit in ``Sets``."""

    def __init__(
        self,
        diagram: Functor,
        *,
        category: Category,
        cardinality: Cardinal | UnknownClass,
    ) -> None:
        self._compatible_elements: set[int] = set()
        super().__init__(diagram, category=category, cardinality=cardinality)

    def _compatible_element(
        self,
        components: SetElementFamily,
    ) -> ProductSetElement:
        member = self.element(components)
        assert is_product_set_element(member)
        self._compatible_elements.add(id(member))
        return member

    def index_set(self) -> SetObject:
        from sage_categories.theories.set_colimits import index_objects

        return index_objects(self.diagram().domain())

    def factor(self, index: SetElement) -> SetObject:
        assert index in self.index_set()
        diagram_object = index.value()
        assert diagram_object in self.diagram().domain()
        value = self.diagram()(diagram_object)
        assert Sets().contains_set(value)
        return value

    def _limit_projection(self, index: MathematicalObject) -> SetMorphism:
        from sage_categories.theories.set_colimits import _object_set_element

        return self._projection(_object_set_element(self.diagram().domain(), index))

    def _cardinality_(self) -> Cardinal | UnknownClass:
        # A limit is the compatible part of its product. When that product is
        # finite the limit is finite too, and membership decides each candidate,
        # so counting supplies the cardinality no construction formula gives.
        declared = super()._cardinality_()
        if declared is not Unknown:
            return declared
        index_set = self.index_set()
        if index_set.is_finite() is not True:
            return Unknown
        if any(self.factor(index).is_finite() is not True for index in index_set):
            return Unknown
        return Cardinals()(sum(1 for _ in self))

    def _membership_(self, member: SetElement) -> Decision:
        from sage_categories.theories.set_colimits import (
            _object_set_element,
            index_arrows,
        )

        product_membership = super()._membership_(member)
        if product_membership is not True:
            return product_membership
        if id(member) in self._compatible_elements:
            return True
        arrows = index_arrows(self.diagram().domain())
        if arrows.is_finite() is not True:
            return Unknown
        value = registered_value(member)
        assert value is not None and is_product_set_element(value)
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

    def _set_iterator_(self) -> Iterator[SetElement]:
        for member in super()._set_iterator_():
            if self.membership(member) is True:
                yield member


class SetLimitObject(LimitObject):
    """A set limit with its cone and compatible families."""

    def __init__(
        self,
        *,
        category: LimitsOfSetsCategory,
        diagram: Functor,
        cardinality: Cardinal | UnknownClass,
    ) -> None:
        from sage_categories.theories.set_constructions import _limit_presentation

        limit_set = LimitSet(
            diagram,
            category=Sets(),
            cardinality=cardinality,
        )
        self._limit_set = limit_set
        super().__init__(
            category=category,
            diagram=diagram,
            presentation=_limit_presentation(diagram, limit_set),
        )

    def index_set(self) -> SetObject:
        return self._limit_set.index_set()

    def factor(self, index: SetElement) -> SetObject:
        return self._limit_set.factor(index)

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        if value is None or not ProductElements().contains_product_element(value):
            return False
        answer = self.membership(value)
        assert answer is not Unknown, f"membership in {self} is unknown"
        return answer


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
    ) -> SetLimitObject:
        assert is_functor(preimage)
        return self._limit(preimage, Unknown)

    def with_cardinality(
        self,
        diagram: Functor,
        cardinality: Cardinal,
    ) -> SetLimitObject:
        result = self._limit(diagram, cardinality)
        assert result.cardinality() == cardinality
        return result

    def limit_of(self, diagram: Functor) -> SetLimitObject:
        return self._limit(diagram, Unknown)

    def _limit(
        self,
        diagram: Functor,
        cardinality: Cardinal | UnknownClass,
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
