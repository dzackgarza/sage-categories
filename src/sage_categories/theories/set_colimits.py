"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.functors import (
    Functor,
    InclusionFunctor,
    StructuralFunctor,
    is_functor,
)
from sage_categories.abstract_categories.products import (
    CoconeObject,
    ColimitObject,
    ColimitsOfCategory,
)
from sage_categories.category import Category
from sage_categories.descriptors import ParameterRole
from sage_categories.theories.cardinals import (
    Cardinal,
    Cardinals,
)
from sage_categories.theories.discrete_sets import (
    DiscreteCategory,
    SetFamily,
)
from sage_categories.theories.set_category import (
    FiniteSets,
    Sets,
    _set_morphism,
)
from sage_categories.theories.set_coproducts import (
    CoproductElement,
    CoproductElements,
    CoproductSet,
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


class ColimitElement(MathematicalElement):
    """An element of a Set colimit, represented by one coproduct term."""

    def __init__(
        self,
        colimit: ColimitSet | SetColimitObject,
        representative: CoproductElement,
    ) -> None:
        assert representative.coproduct() is colimit.coproduct()
        self._colimit = colimit
        self._representative = representative
        super().__init__(
            category=ColimitElements(),
            ambient_object=colimit,
        )

    def colimit(self) -> ColimitSet | SetColimitObject:
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
    ObjectType: type[ColimitElement] = ColimitElement

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
        return ColimitElements().ObjectType(self, self._coproduct.element(index, value))

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
        # Beyond a single arrow the relation is the equivalence relation the
        # diagram generates, so the question becomes whether the two terms share
        # a connected component. Generating one enumerates every term.
        if not self._has_finitely_many_terms():
            return UNKNOWN
        component = self._component_of(arrows, left_representative)
        return any(_same_coproduct_term(right_representative, term) for term in component)

    def _has_finitely_many_terms(self) -> bool:
        indices = self._coproduct.index_set()
        if indices.is_finite() is not True:
            return False
        return all(self._coproduct.cofactor(index).is_finite() is True for index in indices)

    def _component_of(
        self,
        arrows: SetObject,
        start: CoproductElement,
    ) -> tuple[CoproductElement, ...]:
        representatives: tuple[CoproductElement, ...] = ()
        for representative in self._coproduct:
            value = registered_value(representative)
            assert value is not None
            assert CoproductElements().contains_coproduct_element(value)
            representatives = (*representatives, value)
        reached: tuple[CoproductElement, ...] = (start,)
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
                return reached
            reached = (*reached, *enlarged)

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


class SetColimitObject(ColimitObject):
    """A set colimit with its cocone and quotient presentation."""

    def __init__(
        self,
        *,
        category: ColimitsOfSetsCategory,
        diagram: Functor,
        cardinality: Cardinal | None = None,
    ) -> None:
        from sage_categories.theories.set_constructions import _colimit_presentation

        colimit_set = ColimitSet(
            diagram,
            category=Sets(),
            cardinality=cardinality,
        )
        self._coproduct = colimit_set.coproduct()
        super().__init__(
            category=category,
            diagram=diagram,
            presentation=_colimit_presentation(diagram, colimit_set),
        )

    def coproduct(self) -> CoproductSet:
        return self._coproduct

    def element(self, index: SetElement, value: SetElement) -> ColimitElement:
        return ColimitElements().ObjectType(
            self,
            self._coproduct.element(index, value),
        )

    def membership(self, member: SetElement) -> Decision:
        value = registered_value(member)
        return value is not None and ColimitElements().contains_colimit_element(value) and value.colimit() is self

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
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
        arrows = index_arrows(self.diagram().domain())
        if arrows.is_finite() is not True:
            return UNKNOWN
        if _colimit_terms_are_related(
            self.diagram(),
            arrows,
            left_representative,
            right_representative,
        ):
            return True
        if not self._has_finitely_many_terms():
            return UNKNOWN
        component = self._component_of(arrows, left_representative)
        return any(_same_coproduct_term(right_representative, term) for term in component)

    def _has_finitely_many_terms(self) -> bool:
        indices = self._coproduct.index_set()
        if indices.is_finite() is not True:
            return False
        return all(self._coproduct.cofactor(index).is_finite() is True for index in indices)

    def _component_of(
        self,
        arrows: SetObject,
        start: CoproductElement,
    ) -> tuple[CoproductElement, ...]:
        representatives: tuple[CoproductElement, ...] = ()
        for representative in self._coproduct:
            value = registered_value(representative)
            assert value is not None
            assert CoproductElements().contains_coproduct_element(value)
            representatives = (*representatives, value)
        reached: tuple[CoproductElement, ...] = (start,)
        while True:
            enlarged = tuple(
                candidate
                for candidate in representatives
                if not any(_same_coproduct_term(candidate, known) for known in reached)
                and any(
                    _colimit_terms_are_related(
                        self.diagram(),
                        arrows,
                        candidate,
                        known,
                    )
                    for known in reached
                )
            )
            if not enlarged:
                return reached
            reached = (*reached, *enlarged)

    def __iter__(self) -> Iterator[SetElement]:
        chosen: tuple[ColimitElement, ...] = ()
        for representative in self._coproduct:
            value = registered_value(representative)
            assert value is not None and CoproductElements().contains_coproduct_element(value)
            candidate = ColimitElements().ObjectType(self, value)
            if any(self.equivalent(candidate, known) is True for known in chosen):
                continue
            chosen = (*chosen, candidate)
            yield candidate

    def injection(self, index: MathematicalObject) -> SetMorphism:

        return self._injection(_object_set_element(self.diagram().domain(), index))

    def _injection(self, index: SetElement) -> SetMorphism:

        return _set_morphism(
            self._coproduct.cofactor(index),
            self,
            lambda value: self.element(index, value),
        )

    def apex(self) -> SetObject:
        return self

    def universal_morphism(self, cocone: CoconeObject) -> SetMorphism:

        target = cocone.apex()
        assert Sets().contains_set(target)

        def induced(member: SetElement) -> SetElement:
            assert ColimitElements().contains_colimit_element(member)
            representative = member.representative()
            component = cocone.costructure_morphism(representative.index().value())
            assert Sets().contains_set_morphism(component)
            return component(representative.value())

        return _set_morphism(self, target, induced)


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
        finiteness=(True if factor_finiteness is True and indices in FiniteSets() else UNKNOWN),
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
        finiteness=(True if summand_finiteness is True and indices in FiniteSets() else UNKNOWN),
    )
