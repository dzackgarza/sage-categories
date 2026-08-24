"""Finite posets."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
)
from sage_categories.abstract_categories.functors import (
    InclusionFunctor,
    NaturalIsomorphism,
    StructuralFunctor,
    compose_functors,
)
from sage_categories.abstract_categories.hom_categories import (
    Isomorphism,
    is_isomorphism,
)
from sage_categories.theories.sets import (
    FiniteSets,
    SetElement,
    SetObject,
    Sets,
)
from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
)

if TYPE_CHECKING:
    from sage_categories.backends.sage.finite_posets import (
        SageFinitePosetObject,
    )

from sage_categories.theories.poset_core import (
    ForgetPosetFunctor,
    OrderRelation,
    PartiallyOrderedSets,
    PartiallyOrderedSetsCategory,
    PosetElement,
    PosetMorphism,
    PosetObject,
    is_poset_element,
    is_poset_hom_category,
)


class FinitePosetElement(MathematicalElement):
    """An element of one finite poset."""

    def __init__(
        self,
        *,
        ambient_object: FinitePosetObject,
        set_element: SetElement,
    ) -> None:
        self._set_element = set_element
        super().__init__(
            category=ambient_object.category(),
            ambient_object=ambient_object,
        )

    def _set_implementation(self) -> SetElement:
        return self._set_element


class FinitePosetObject(MathematicalObject):
    """A finite poset with finite order algorithms."""

    def __init__(
        self,
        *,
        category: FinitePosetsCategory,
        poset: PosetObject,
    ) -> None:
        assert poset in PartiallyOrderedSets()
        assert PartiallyOrderedSets().underlying_set(poset) in FiniteSets()
        self._poset = poset
        super().__init__(category=category)

    def _poset_implementation(self) -> PosetObject:
        return self._poset

    def _set_implementation(self) -> SetObject:
        return PartiallyOrderedSets().underlying_set(self._poset)

    def _is_lequal(self, left: PosetElement, right: PosetElement) -> Decision:
        poset_left = self._poset.element(left._set_implementation())
        poset_right = self._poset.element(right._set_implementation())
        return self._poset._is_lequal(poset_left, poset_right)

    def _realization(self) -> SageFinitePosetObject:
        from sage_categories.backends.sage.finite_posets import (
            realize_finite_poset,
        )

        return realize_finite_poset(self)

    def covers(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> bool:
        return self._realization().covers(lower, upper)

    def lower_covers(self, member: PosetElement) -> Iterator[PosetElement]:
        return self._realization().lower_covers(member)

    def upper_covers(self, member: PosetElement) -> Iterator[PosetElement]:
        return self._realization().upper_covers(member)

    def common_lower_covers(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return self._realization().common_lower_covers(members)

    def common_upper_covers(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return self._realization().common_upper_covers(members)

    def open_interval(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> Iterator[PosetElement]:
        return self._realization().open_interval(lower, upper)

    def closed_interval(
        self,
        lower: PosetElement,
        upper: PosetElement,
    ) -> Iterator[PosetElement]:
        return self._realization().closed_interval(lower, upper)

    def principal_order_ideal(
        self,
        member: PosetElement,
    ) -> Iterator[PosetElement]:
        return self._realization().principal_order_ideal(member)

    def principal_order_filter(
        self,
        member: PosetElement,
    ) -> Iterator[PosetElement]:
        return self._realization().principal_order_filter(member)

    def order_ideal(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return self._realization().order_ideal(members)

    def order_filter(
        self,
        members: Iterable[PosetElement],
    ) -> Iterator[PosetElement]:
        return self._realization().order_filter(members)

    def minimal_elements(self) -> Iterator[PosetElement]:
        return self._realization().minimal_elements()

    def maximal_elements(self) -> Iterator[PosetElement]:
        return self._realization().maximal_elements()

    def has_bottom(self) -> bool:
        return self._realization().has_bottom()

    def bottom(self) -> PosetElement:
        return self._realization().bottom()

    def has_top(self) -> bool:
        return self._realization().has_top()

    def top(self) -> PosetElement:
        return self._realization().top()

    def is_bounded(self) -> bool:
        return self._realization().is_bounded()

    def height(self) -> int:
        return self._realization().height()

    def width(self) -> int:
        return self._realization().width()

    def rank(self, member: PosetElement | None = None) -> int:
        return self._realization().rank(member)

    def level_sets(self) -> Iterator[Iterator[PosetElement]]:
        return self._realization().level_sets()

    def is_ranked(self) -> bool:
        return self._realization().is_ranked()

    def is_graded(self) -> bool:
        return self._realization().is_graded()

    def is_chain(self) -> bool:
        return self._realization().is_chain()

    def is_chain_of_poset(self, members: Iterable[PosetElement]) -> bool:
        return self._realization().is_chain_of_poset(members)

    def is_antichain_of_poset(self, members: Iterable[PosetElement]) -> bool:
        return self._realization().is_antichain_of_poset(members)

    def linear_extension(self) -> Iterator[PosetElement]:
        return self._realization().linear_extension()


class FinitePosetInclusionFunctor(InclusionFunctor):
    """Include finite posets in all partially ordered sets."""

    def __init__(self, finite_posets: FinitePosetsCategory) -> None:
        self._finite_posets = finite_posets
        super().__init__(finite_posets, PartiallyOrderedSets())

    def _object_image(self, source: MathematicalObject) -> PosetObject:
        assert self._finite_posets.contains_finite_poset(source)
        return source._poset_implementation()

    def _morphism_image(self, morphism: Arrow) -> PosetMorphism:
        hom_category = morphism.hom_category()
        assert is_poset_hom_category(hom_category)
        assert hom_category.contains_poset_morphism(morphism)
        domain = self.on_object(morphism.domain())
        codomain = self.on_object(morphism.codomain())
        target_hom = PartiallyOrderedSets().Hom(domain, codomain)
        return target_hom.ObjectType(
            hom_category=target_hom,
            underlying_function=morphism._set_implementation(),
        )

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> PosetElement:
        assert self._finite_posets.contains_finite_poset(source)
        assert is_poset_element(element)
        target = self.on_object(source)
        assert PartiallyOrderedSets().contains_poset(target)
        return target.element(element._set_implementation())

    def _element_preimage(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> FinitePosetElement:
        assert self._finite_posets.contains_finite_poset(source)
        assert is_poset_element(element)
        return self._finite_posets.ElementType(
            ambient_object=source,
            set_element=element._set_implementation(),
        )


class FinitePosetsCategory(FullSubcategory):
    """The full subcategory of finite partially ordered sets."""

    ObjectType: type[FinitePosetObject] = FinitePosetObject
    ElementType: type[FinitePosetElement] = FinitePosetElement

    def __init__(self, posets: PartiallyOrderedSetsCategory) -> None:
        self._forgetful_functor: ForgetPosetFunctor | None = None
        self._poset_inclusion: FinitePosetInclusionFunctor | None = None
        self._structural_coherence: Isomorphism | None = None
        super().__init__(
            posets,
            self._is_finite,
            name="Finite partially ordered sets",
        )

    def __call__(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> FinitePosetObject:
        assert underlying_set in FiniteSets()
        poset = PartiallyOrderedSets().ObjectType(
            category=PartiallyOrderedSets(),
            underlying_set=underlying_set,
            relation=relation,
        )
        value = self.ObjectType(
            category=self,
            poset=poset,
        )
        assert self.contains_finite_poset(value)
        return value

    def _is_finite(self, value: MathematicalObject) -> bool:
        assert PartiallyOrderedSets().contains_poset(value)
        return PartiallyOrderedSets().underlying_set(value) in FiniteSets()

    def inclusion(self) -> FinitePosetInclusionFunctor:
        if self._poset_inclusion is None:
            self._poset_inclusion = FinitePosetInclusionFunctor(self)
        return self._poset_inclusion

    def forgetful_functor(self) -> ForgetPosetFunctor:
        if self._forgetful_functor is None:
            self._forgetful_functor = ForgetPosetFunctor(self, FiniteSets())
        return self._forgetful_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return self.inclusion(), self.forgetful_functor()

    def structural_coherences(self) -> tuple[Isomorphism, ...]:
        if self._structural_coherence is None:
            first = compose_functors(
                PartiallyOrderedSets().forgetful_functor(),
                self.inclusion(),
            )
            finite_to_countable = FiniteSets().super_functors()[0]
            countable_to_sets = finite_to_countable.codomain().super_functors()[0]
            second = compose_functors(
                countable_to_sets,
                compose_functors(
                    finite_to_countable,
                    self.forgetful_functor(),
                ),
            )

            def component(source: MathematicalObject) -> Arrow:
                image = first(source)
                assert image is second(source)
                return Sets().identity(image)

            coherence = NaturalIsomorphism(
                second,
                first,
                component,
                component,
            )
            assert is_isomorphism(coherence)
            self._structural_coherence = coherence
        return (self._structural_coherence,)

    def contains_finite_poset(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[FinitePosetObject]:
        return candidate in self

    def __repr__(self) -> str:
        return "Finite partially ordered sets"
