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
    Cardinals,
)
from sage_categories.theories.set_category import (
    Sets,
    _set_morphism,
)
from sage_categories.theories.set_elements import (
    SetElement,
    SetElements,
)
from sage_categories.theories.set_objects import (
    SetObject,
    _known_cardinality,
)
from sage_categories.types import (
    Decision,
    MathematicalObject,
    TransportedElement,
    Unknown,
    registered_element,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.set_subobjects import SetMorphism


class CoproductSetElement(SetElement):
    """The private set representation of a coproduct element."""

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
            category=SetElements(),
            ambient_object=coproduct,
        )

    def coproduct(self) -> CoproductSet:
        return self._coproduct

    def index(self) -> SetElement:
        return self._index

    def _value_(self) -> SetElement:
        return self._value


class CoproductElement(TransportedElement):
    """A tagged element of a set-indexed disjoint union."""

    def _set_implementation(self) -> CoproductSetElement:
        value = self._ambient_implementation()
        assert is_coproduct_set_element(value)
        return value

    def coproduct(self) -> SetCoproductObject:
        coproduct = self.ambient_object()
        assert is_set_coproduct_object(coproduct)
        return coproduct

    def index(self) -> SetElement:
        return self._set_implementation().index()

    def _value_(self) -> SetElement:
        return self._set_implementation().value()


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

    def __contains__(self, candidate: Any) -> bool:
        element = registered_element(candidate)
        return (
            element is not None
            and is_set_coproduct_object(element.ambient_object())
        )


_COPRODUCT_ELEMENTS = CoproductElementsCategory()

_COPRODUCT_SET_ELEMENTS: dict[int, CoproductSetElement] = {}


def CoproductElements() -> CoproductElementsCategory:
    return _COPRODUCT_ELEMENTS


def is_coproduct_set_element(
    candidate: MathematicalObject,
) -> TypeIs[CoproductSetElement]:
    return _COPRODUCT_SET_ELEMENTS.get(id(candidate)) is candidate


def is_set_coproduct_object(
    candidate: MathematicalObject,
) -> TypeIs[SetCoproductObject]:
    category = candidate.category()
    return (
        is_coproducts_of_sets_category(category)
        and category.contains_set_coproduct(candidate)
    )


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
        size = _indexed_sum_cardinality(self.index_set(), self.cofactor)
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
            lambda index: _known_cardinality(self.cofactor(index.label())),
        )

    def _element_(self, index: SetElement, value: SetElement) -> CoproductSetElement:
        element = CoproductSetElement(self, index, value)
        _COPRODUCT_SET_ELEMENTS[id(element)] = element
        return element

    def _membership_(self, member: SetElement) -> Decision:
        value = registered_value(member)
        return value is not None and is_coproduct_set_element(value) and value.coproduct() is self

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
            Unknown,
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
        ambient = self.apex()._element_(index, value)
        category = self.category()
        assert is_coproducts_of_sets_category(category)
        element = category.inclusion().preimage_element(self, ambient)
        assert CoproductElements().contains_coproduct_element(element)
        return element

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
            Unknown,
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


class SetCoproductHomCategory(FunctorImageHomCategory):
    """Maps between refined set coproducts."""

    ObjectType = FunctorImageArrow
    ElementType = FunctorImageArrow


class CoproductsOfSetsCategory(CoproductsOfCategory):
    """Coproducts in ``Sets()``, with each coproduct equal to its apex set."""

    ObjectType: type[SetCoproductObject] = SetCoproductObject
    ElementType: type[CoproductElement] = CoproductElement

    def __init__(self, functor: Functor) -> None:
        super().__init__(functor)
        _COPRODUCTS_OF_SETS[id(self)] = self

    def _hom_category_type(self) -> type[HomCategory]:
        return SetCoproductHomCategory

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
