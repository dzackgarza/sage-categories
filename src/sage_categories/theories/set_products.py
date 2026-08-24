"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Iterator
from itertools import product as cartesian_product
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.functor_images import (
    FunctorImageArrow,
    FunctorImageHomCategory,
    ImageInclusionFunctor,
)
from sage_categories.abstract_categories.functors import (
    DiscreteCategories,
    DiscreteDiagram,
    Functor,
    InclusionFunctor,
    StructuralFunctor,
    is_functor,
)
from sage_categories.abstract_categories.functors import (
    DiscreteCategory as DiscreteCategoryObject,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
)
from sage_categories.abstract_categories.products import (
    ConeObject,
    ProductObject,
    ProductsOfCategory,
)
from sage_categories.category import Category
from sage_categories.descriptors import ParameterRole
from sage_categories.theories.cardinals import (
    Cardinal,
    Cardinals,
)
from sage_categories.theories.set_category import (
    FiniteSets,
    Sets,
    _set_morphism,
)
from sage_categories.theories.set_elements import (
    SetElement,
    SetElementFamily,
    SetElements,
)
from sage_categories.theories.set_objects import (
    SetObject,
)
from sage_categories.values import (
    UNKNOWN,
    Decision,
    MathematicalElement,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.set_limits import SetLimitObject
    from sage_categories.theories.set_subobjects import SetMorphism


class ProductElement(MathematicalElement):
    """A point of a set-indexed cartesian product."""

    def __init__(
        self,
        product: ProductSet | SetProductObject | SetLimitObject,
        components: SetElementFamily,
    ) -> None:
        # The element surface arrives through the inclusion its category
        # declares into SetElements, not by inheriting the set element type.

        self._product = product
        self._components = components
        super().__init__(
            category=ProductElements(),
            ambient_object=product,
        )

    def product(self) -> ProductSet | SetProductObject | SetLimitObject:

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
    ObjectType: type[ProductElement] = ProductElement

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
        cardinality: Cardinal,
    ) -> None:
        self._diagram = diagram
        super().__init__(category=category, cardinality=cardinality)

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
        # The category owns the constructor: its compiled type carries the
        # element surface inherited along the declared inclusion.
        return ProductElements().ObjectType(self, components)

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


class SetProductObject(ProductObject):
    """A set product with its factors and universal arrows."""

    def __init__(
        self,
        *,
        category: ProductsOfSetsCategory,
        diagram: Functor,
        cardinality: Cardinal,
    ) -> None:
        from sage_categories.theories.set_constructions import _product_presentation

        set_product = ProductSet(
            diagram,
            category=Sets(),
            cardinality=cardinality,
        )
        self._set_product = set_product
        super().__init__(
            category=category,
            diagram=diagram,
            presentation=_product_presentation(diagram, set_product),
        )

    def index_category(self) -> DiscreteCategoryObject:
        return self._set_product.index_category()

    def index_set(self) -> SetObject:
        return self._set_product.index_set()

    def factor(self, index: SetElement) -> SetObject:
        return self._set_product.factor(index)

    def factor_cardinalities(self) -> Functor:
        return self._set_product.factor_cardinalities()

    def apex(self) -> ProductSet:
        return self._set_product

    def element(self, components: SetElementFamily) -> ProductElement:
        return ProductElements().ObjectType(self, components)

    def membership(self, member: SetElement) -> Decision:
        value = registered_value(member)
        return value is not None and ProductElements().contains_product_element(value) and value.product() is self

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
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

    def projection(self, index: MathematicalObject) -> SetMorphism:

        assert self.index_category().contains_object(index)
        return self._projection(index.label())

    def _projection(self, index: SetElement) -> SetMorphism:

        factor = self.factor(index)

        def project(member: SetElement) -> SetElement:
            value = registered_value(member)
            assert value is not None
            assert ProductElements().contains_product_element(value)
            assert value.product() is self
            return value.component(index)

        return _set_morphism(self, factor, project)

    def universal_morphism(self, cone: ConeObject) -> SetMorphism:
        from sage_categories.theories.set_constructions import _cone_component_value

        source = cone.apex()
        assert Sets().contains_set(source)
        return _set_morphism(
            source,
            self,
            lambda member: self.element(
                lambda index: _cone_component_value(
                    cone,
                    self.index_category().object(index),
                    member,
                )
            ),
        )

    def __repr__(self) -> str:
        return f"Product of {self.diagram()}"


class SetProductInclusionFunctor(ImageInclusionFunctor):
    """Include a refined set product and its elements into ``Sets()``."""

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> SetElement:
        category = self.domain()
        assert is_products_of_sets_category(category)
        assert category.contains_set_product(source)
        assert ProductElements().contains_product_element(element)
        image = source.apex()
        return image.element(element.components())


class SetProductHomCategory(FunctorImageHomCategory):
    """Maps between refined set products."""

    ObjectType = FunctorImageArrow
    ElementType = FunctorImageArrow


class ProductsOfSetsCategory(ProductsOfCategory):
    """Products in ``Sets()``, with each product equal to its apex set."""

    ObjectType: type[SetProductObject] = SetProductObject
    ElementType: type[ProductElement] = ProductElement

    def __init__(self, functor: Functor) -> None:
        self._set_inclusion: SetProductInclusionFunctor | None = None
        super().__init__(functor)
        _PRODUCTS_OF_SETS[id(self)] = self

    def _hom_category_type(self) -> type[HomCategory]:
        return SetProductHomCategory

    def inclusion(self) -> SetProductInclusionFunctor:
        if self._set_inclusion is None:
            self._set_inclusion = SetProductInclusionFunctor(self)
        return self._set_inclusion

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (self.inclusion(),)

    def __call__(
        self,
        preimage: MathematicalObject,
    ) -> SetProductObject:
        assert is_functor(preimage)
        return self._product(preimage)

    def limit_of(self, diagram: Functor) -> SetProductObject:
        return self._product(diagram)

    def product_of(self, diagram: Functor) -> SetProductObject:
        return self._product(diagram)

    def _product(
        self,
        diagram: Functor,
    ) -> SetProductObject:
        assert diagram in self.functor().domain()
        key = id(diagram)
        cached = self._limits.get(key)
        if cached is None:
            from sage_categories.theories.set_colimits import _indexed_product_cardinality

            cardinality = _indexed_product_cardinality(
                diagram.domain().label_set(),
                lambda index: diagram(diagram.domain().object(index)),
                factor_finiteness=(True if diagram.codomain().is_subcategory(FiniteSets()) else UNKNOWN),
            )
            candidate = self.ObjectType(
                category=self,
                diagram=diagram,
                cardinality=cardinality,
            )
            assert self.contains_set_product(candidate)
            cached = candidate
            self._limits[key] = cached
        assert self.contains_set_product(cached)
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
