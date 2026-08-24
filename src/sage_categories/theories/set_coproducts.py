"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Iterator
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
    CoconeObject,
    CoproductObject,
    CoproductsOfCategory,
)
from sage_categories.category import Category
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
    from sage_categories.theories.set_subobjects import SetMorphism


class CoproductElement(MathematicalElement):
    """A tagged element of a set-indexed disjoint union."""

    def __init__(
        self,
        coproduct: CoproductSet | SetCoproductObject,
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

    @classmethod
    def _refined_element_from_ambient(
        cls,
        *,
        category: Category,
        ambient_object: MathematicalObject,
        ambient_implementation: MathematicalElement,
    ) -> CoproductElement:
        assert is_coproducts_of_sets_category(category)
        assert category.contains_set_coproduct(ambient_object)
        assert CoproductElements().contains_coproduct_element(ambient_implementation)
        return cls(
            ambient_object,
            ambient_implementation.index(),
            ambient_implementation.value(),
        )

    def coproduct(self) -> CoproductSet | SetCoproductObject:
        return self._coproduct

    def index(self) -> SetElement:
        return self._index

    def _value_(self) -> SetElement:
        return self._value


class CoproductElementsCategory(Category):
    ObjectType: type[CoproductElement] = CoproductElement

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
    ) -> None:
        from sage_categories.theories.set_colimits import _indexed_sum_cardinality

        self._diagram = diagram
        size = _indexed_sum_cardinality(
            self.index_set(),
            self.cofactor,
            summand_finiteness=(True if diagram.codomain().is_subcategory(FiniteSets()) else UNKNOWN),
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

    def _element_(self, index: SetElement, value: SetElement) -> CoproductElement:
        return CoproductElements().ObjectType(self, index, value)

    def _membership_(self, member: SetElement) -> Decision:
        value = registered_value(member)
        return value is not None and CoproductElements().contains_coproduct_element(value) and value.coproduct() is self

    def _set_iterator_(self) -> Iterator[SetElement]:
        assert self.index_set().is_finite() is True
        for index in self.index_set():
            cofactor = self.cofactor(index)
            for value in cofactor:
                yield self._element_(index, value)

    def _injection(self, index: SetElement) -> SetMorphism:

        from sage_categories.theories.set_category import _set_morphism_with_properties

        return _set_morphism_with_properties(
            self.cofactor(index),
            self,
            lambda value: self._element_(index, value),
            True,
            UNKNOWN,
        )

    def __repr__(self) -> str:
        return f"Coproduct of {self._diagram}"


class SetCoproductObject(CoproductObject):
    """A set coproduct with its summands and universal arrows."""

    def __init__(
        self,
        *,
        category: CoproductsOfSetsCategory,
        diagram: Functor,
    ) -> None:
        from sage_categories.theories.set_constructions import _coproduct_presentation

        set_coproduct = CoproductSet(
            diagram,
            category=Sets(),
        )
        self._set_coproduct = set_coproduct
        super().__init__(
            category=category,
            diagram=diagram,
            presentation=_coproduct_presentation(diagram, set_coproduct),
        )

    def index_category(self) -> DiscreteCategoryObject:
        return self._set_coproduct.index_category()

    def index_set(self) -> SetObject:
        return self._set_coproduct.index_set()

    def cofactor(self, index: SetElement) -> SetObject:
        return self._set_coproduct.cofactor(index)

    def cofactor_cardinalities(self) -> Functor:
        return self._set_coproduct.cofactor_cardinalities()

    def apex(self) -> CoproductSet:
        return self._set_coproduct

    def element(self, index: SetElement, value: SetElement) -> CoproductElement:
        return CoproductElements().ObjectType(self, index, value)

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and CoproductElements().contains_coproduct_element(value) and value.coproduct() is self

    def injection(self, index: MathematicalObject) -> SetMorphism:

        assert self.index_category().contains_object(index)
        return self._injection(index.label())

    def _injection(self, index: SetElement) -> SetMorphism:

        from sage_categories.theories.set_category import _set_morphism_with_properties

        return _set_morphism_with_properties(
            self.cofactor(index),
            self,
            lambda value: self.element(index, value),
            True,
            UNKNOWN,
        )

    def universal_morphism(self, cocone: CoconeObject) -> SetMorphism:

        target = cocone.apex()
        assert Sets().contains_set(target)

        def induced(member: SetElement) -> SetElement:
            assert CoproductElements().contains_coproduct_element(member)
            component = cocone.costructure_morphism(
                self.index_category().object(member.index()),
            )
            assert Sets().contains_set_morphism(component)
            return component(member.value())

        return _set_morphism(self, target, induced)

    def __repr__(self) -> str:
        return f"Coproduct of {self.diagram()}"


class SetCoproductInclusionFunctor(ImageInclusionFunctor):
    """Include a refined set coproduct and its elements into ``Sets()``."""

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> SetElement:
        category = self.domain()
        assert is_coproducts_of_sets_category(category)
        assert category.contains_set_coproduct(source)
        assert CoproductElements().contains_coproduct_element(element)
        return source.apex()._element_(element.index(), element.value())


class SetCoproductHomCategory(FunctorImageHomCategory):
    """Maps between refined set coproducts."""

    ObjectType = FunctorImageArrow
    ElementType = FunctorImageArrow


class CoproductsOfSetsCategory(CoproductsOfCategory):
    """Coproducts in ``Sets()``, with each coproduct equal to its apex set."""

    ObjectType: type[SetCoproductObject] = SetCoproductObject
    ElementType: type[CoproductElement] = CoproductElement

    def __init__(self, functor: Functor) -> None:
        self._set_inclusion: SetCoproductInclusionFunctor | None = None
        super().__init__(functor)
        _COPRODUCTS_OF_SETS[id(self)] = self

    def _hom_category_type(self) -> type[HomCategory]:
        return SetCoproductHomCategory

    def inclusion(self) -> SetCoproductInclusionFunctor:
        if self._set_inclusion is None:
            self._set_inclusion = SetCoproductInclusionFunctor(self)
        return self._set_inclusion

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (self.inclusion(),)

    def __call__(
        self,
        preimage: MathematicalObject,
    ) -> SetCoproductObject:
        assert is_functor(preimage)
        return self._coproduct(preimage)

    def colimit_of(self, diagram: Functor) -> SetCoproductObject:
        return self._coproduct(diagram)

    def coproduct_of(self, diagram: Functor) -> SetCoproductObject:
        return self._coproduct(diagram)

    def _coproduct(
        self,
        diagram: Functor,
    ) -> SetCoproductObject:
        assert diagram in self.functor().domain()
        key = id(diagram)
        cached = self._colimits.get(key)
        if cached is None:
            candidate = self.ObjectType(
                category=self,
                diagram=diagram,
            )
            assert self.contains_set_coproduct(candidate)
            cached = candidate
            self._colimits[key] = cached
        assert self.contains_set_coproduct(cached)
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
