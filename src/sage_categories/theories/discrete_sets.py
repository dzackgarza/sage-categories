"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, TypeIs

from sage_categories.abstract_categories.functors import (
    DiscreteCategories,
    DiscreteDiagram,
    DiscreteObject,
    InclusionFunctor,
    StructuralFunctor,
)
from sage_categories.abstract_categories.functors import (
    DiscreteCategory as DiscreteCategoryObject,
)
from sage_categories.category import Category
from sage_categories.theories.set_category import (
    Sets,
)
from sage_categories.theories.set_elements import (
    SetElement,
    SetElements,
)
from sage_categories.theories.set_objects import (
    SetObject,
)
from sage_categories.values import (
    Decision,
    MathematicalObject,
    registered_value,
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
        return iter(
            tuple(
                self.element(self._discrete_category.object(label))
                for label in self._labels
            )
        )


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
        return iter(
            tuple(
                self.element(self._discrete_category.Hom(value, value).identity())
                for value in self._discrete_category
            )
        )


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
