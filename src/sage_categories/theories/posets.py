"""Partially and totally ordered sets over the owned ``Sets`` category.

The mathematical surface follows ``specs/ordered-sets.md`` and the mature
Sage finite-poset interface.  Ordered objects and arrows retain their set
implementations through explicit structural functors.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from itertools import count
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.category_constructions import (
    FullSubcategory,
)
from sage_categories.abstract_categories.functors import (
    Functor,
    NaturalIsomorphism,
    StructuralFunctor,
    compose_functors,
    is_functor,
    is_functor_category,
)
from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
    Isomorphism,
    is_isomorphism,
)
from sage_categories.abstract_categories.products import (
    Cone,
    ConeObject,
    Product,
    ProductObject,
    ProductPresentation,
    ProductsOfCategory,
)
from sage_categories.category import Category
from sage_categories.theories.sets import (
    EnumerationInjection,
    FiniteSet,
    FiniteSets,
    FiniteSetsCategory,
    NaturalNumbers,
    ProductElements,
    ProductsOfSetsCategory,
    SetElement,
    SetElements,
    SetMorphism,
    SetObject,
    SetProductObject,
    Sets,
    SetsCategory,
    is_products_of_sets_category,
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

if TYPE_CHECKING:
    from sage_categories.backends.sage.finite_posets import (
        SageFinitePosetObject,
    )
    from sage_categories.theories.cardinals import Cardinal

type OrderRelation = Callable[[PosetElement, PosetElement], Decision]


class PosetElement(MathematicalElement):
    """An element of one partially ordered set."""

    def __init__(
        self,
        *,
        ambient_object: PosetObject,
        set_element: SetElement,
    ) -> None:
        assert ambient_object in PartiallyOrderedSets()
        underlying_set = PartiallyOrderedSets().underlying_set(ambient_object)
        assert set_element.ambient_set() is underlying_set
        assert set_element in underlying_set
        self._set_element = set_element
        super().__init__(
            category=PosetElements(),
            ambient_object=ambient_object,
        )

    def _set_implementation(self) -> SetElement:
        return self._set_element

    def ambient_poset(self) -> PosetObject:
        ambient = self.ambient_object()
        assert PartiallyOrderedSets().contains_poset(ambient)
        return ambient

    def __le__(self, other: PosetElement) -> Decision:
        return self.ambient_poset()._is_lequal(self, other)

    def __lt__(self, other: PosetElement) -> Decision:
        comparison = self <= other
        if comparison is UNKNOWN:
            return UNKNOWN
        return comparison and self != other

    def __repr__(self) -> str:
        return repr(self._set_element)


class PosetElementsCategory(Category):
    """The total category of elements of partially ordered sets."""

    ObjectType = PosetElement

    def __init__(self) -> None:
        super().__init__(object_type=PosetElement)

    def contains_poset_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[PosetElement]:
        return candidate in self

    def __repr__(self) -> str:
        return "Elements of partially ordered sets"


_POSET_ELEMENTS: PosetElementsCategory | None = None


def PosetElements() -> PosetElementsCategory:
    global _POSET_ELEMENTS

    if _POSET_ELEMENTS is None:
        _POSET_ELEMENTS = PosetElementsCategory()
    return _POSET_ELEMENTS


class PosetObject(MathematicalObject):
    """A set equipped with one chosen partial order."""

    def __init__(
        self,
        *,
        category: (PartiallyOrderedSetsCategory | FinitePosetsCategory | ProductsOfPosetsCategory),
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> None:
        assert underlying_set in Sets()
        self._underlying_set = underlying_set
        self._relation = relation
        self._elements: dict[int, PosetElement] = {}
        self._thin_category: ThinCategory | None = None
        super().__init__(category=category)

    def _set_implementation(self) -> SetObject:
        return self._underlying_set

    def element(self, set_element: SetElement) -> PosetElement:
        assert set_element.ambient_set() is self._underlying_set
        assert set_element in self._underlying_set
        key = id(set_element)
        cached = self._elements.get(key)
        if cached is None:
            cached = PartiallyOrderedSets().ElementType(
                ambient_object=self,
                set_element=set_element,
            )
            self._elements[key] = cached
        return cached

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and PosetElements().contains_poset_element(value) and value.ambient_poset() is self

    def __iter__(self) -> Iterator[PosetElement]:
        return iter(self.element(member) for member in self._underlying_set)

    def _is_lequal(self, left: PosetElement, right: PosetElement) -> Decision:
        assert left in self
        assert right in self
        return self._relation(left, right)

    def thin_category(self) -> ThinCategory:
        if self._thin_category is None:
            self._thin_category = ThinCategory(self)
        return self._thin_category

    def __repr__(self) -> str:
        return f"Partially ordered {self._underlying_set}"


class ThinCategoryObjectElement(SetElement):
    """A poset element regarded as an object name in its thin category."""

    def __init__(
        self,
        *,
        ambient_object: ThinCategoryObjectSet,
        value: PosetElement,
    ) -> None:
        self._value = value
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def value(self) -> PosetElement:
        return self._value


class ThinCategoryObjectSet(SetObject):
    """The set of objects in the thin category of one poset."""

    def __init__(self, category: ThinCategory) -> None:
        self._thin_category = category
        self._elements: dict[int, ThinCategoryObjectElement] = {}
        underlying_set = PartiallyOrderedSets().underlying_set(category.poset())
        super().__init__(
            category=Sets(),
            cardinality=underlying_set.cardinality(),
        )

    def element(self, value: PosetElement) -> ThinCategoryObjectElement:
        assert self._thin_category.contains_object(value)
        key = id(value)
        cached = self._elements.get(key)
        if cached is None:
            cached = ThinCategoryObjectElement(
                ambient_object=self,
                value=value,
            )
            self._elements[key] = cached
        return cached

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def __iter__(self) -> Iterator[SetElement]:
        return iter(self.element(value) for value in self._thin_category.poset())


class ThinCategoryArrow(Arrow):
    """The unique arrow represented by one valid poset comparison."""

    def __repr__(self) -> str:
        return f"{self.domain()} <= {self.codomain()}"


class ThinCategoryHom(HomCategory):
    """The empty or singleton Hom category of one poset comparison."""

    ObjectType = ThinCategoryArrow
    ElementType = ThinCategoryArrow

    def __init__(
        self,
        *,
        domain: MathematicalObject,
        codomain: MathematicalObject,
        hom_category: HomCategoryFamily,
    ) -> None:
        self._unique_morphism: ThinCategoryArrow | None = None
        super().__init__(
            domain=domain,
            codomain=codomain,
            hom_category=hom_category,
        )
        _THIN_HOM_CATEGORIES[id(self)] = self

    def comparison(self) -> Decision:
        category = self.base_category()
        assert is_thin_category(category)
        domain = self.domain()
        codomain = self.codomain()
        assert category.contains_object(domain)
        assert category.contains_object(codomain)
        return domain <= codomain

    def unique_morphism(self) -> ThinCategoryArrow:
        assert self.comparison() is True
        if self._unique_morphism is None:
            self._unique_morphism = self.ObjectType(hom_category=self)
        return self._unique_morphism

    def __call__(self) -> ThinCategoryArrow:
        return self.unique_morphism()

    def objects(self) -> SetObject:
        comparison = self.comparison()
        assert comparison is not UNKNOWN
        if comparison is False:
            return FiniteSet(())
        return FiniteSet((self.unique_morphism(),))

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> ThinCategoryArrow:
        assert value is None
        assert self.domain() is self.codomain()
        return self.unique_morphism()

    def compose(self, second: Arrow, first: Arrow) -> ThinCategoryArrow:
        assert first in self.base_category().ArrowCategory()
        assert second in self.base_category().ArrowCategory()
        assert first.codomain() is second.domain()
        return self.unique_morphism()


_THIN_HOM_CATEGORIES: dict[int, ThinCategoryHom] = {}


def is_thin_category_hom(
    category: MathematicalObject,
) -> TypeIs[ThinCategoryHom]:
    return _THIN_HOM_CATEGORIES.get(id(category)) is category


class ThinCategoryArrowElement(SetElement):
    """A thin-category arrow regarded as a member of its arrow set."""

    def __init__(
        self,
        *,
        ambient_object: ThinCategoryArrowSet,
        value: ThinCategoryArrow,
    ) -> None:
        self._value = value
        super().__init__(
            category=SetElements(),
            ambient_object=ambient_object,
        )

    def value(self) -> ThinCategoryArrow:
        return self._value


class ThinCategoryArrowSet(SetObject):
    """The set of arrows in one thin category."""

    def __init__(self, category: ThinCategory) -> None:
        self._thin_category = category
        self._elements: dict[int, ThinCategoryArrowElement] = {}
        super().__init__(category=Sets())

    def element(self, value: ThinCategoryArrow) -> ThinCategoryArrowElement:
        assert value in self._thin_category.ArrowCategory()
        key = id(value)
        cached = self._elements.get(key)
        if cached is None:
            cached = ThinCategoryArrowElement(
                ambient_object=self,
                value=value,
            )
            self._elements[key] = cached
        return cached

    def membership(self, member: SetElement) -> Decision:
        return member.ambient_set() is self

    def __iter__(self) -> Iterator[SetElement]:
        poset = self._thin_category.poset()
        underlying_set = PartiallyOrderedSets().underlying_set(poset)
        assert underlying_set.is_finite() is True
        for source in poset:
            for target in poset:
                comparison = source <= target
                assert comparison is not UNKNOWN
                if comparison:
                    hom_category = self._thin_category.Hom(source, target)
                    yield self.element(hom_category())


class ThinCategory(Category):
    """The thin category associated to one partially ordered set."""

    ObjectType = PosetElement

    def __init__(self, poset: PosetObject) -> None:
        assert PartiallyOrderedSets().contains_poset(poset)
        self._poset = poset
        self._objects: ThinCategoryObjectSet | None = None
        self._arrows: ThinCategoryArrowSet | None = None
        super().__init__(object_type=PosetElement)
        _THIN_CATEGORIES[id(self)] = self

    def poset(self) -> PosetObject:
        return self._poset

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and self.contains_object(value)

    def contains_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[PosetElement]:
        return PosetElements().contains_poset_element(candidate) and candidate.ambient_poset() is self._poset

    def objects(self) -> ThinCategoryObjectSet:
        if self._objects is None:
            self._objects = ThinCategoryObjectSet(self)
        return self._objects

    def object_element(self, value: MathematicalObject) -> SetElement:
        assert PosetElements().contains_poset_element(value)
        return self.objects().element(value)

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> ThinCategoryHom:
        assert codomain is not None
        category = Category.Hom(self, domain, codomain)
        assert is_thin_category_hom(category)
        return category

    def arrows(self) -> ThinCategoryArrowSet:
        if self._arrows is None:
            self._arrows = ThinCategoryArrowSet(self)
        return self._arrows

    def _hom_category_type(self) -> type[HomCategory]:
        return ThinCategoryHom

    def __repr__(self) -> str:
        return f"Thin category of {self._poset}"


_THIN_CATEGORIES: dict[int, ThinCategory] = {}


def is_thin_category(category: Category) -> TypeIs[ThinCategory]:
    return _THIN_CATEGORIES.get(id(category)) is category


class PosetMorphism(Arrow):
    """An order-preserving map with its underlying set function."""

    def __init__(
        self,
        *,
        hom_category: PosetHomCategory,
        underlying_function: SetMorphism,
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

    def _set_implementation(self) -> SetMorphism:
        return self._underlying_function

    def __call__(self, member: PosetElement) -> PosetElement:
        source = self.domain()
        target = self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        assert category.contains_poset(source)
        assert category.contains_poset(target)
        assert member in source
        forgetful_functor = category.forgetful_functor()
        set_member = forgetful_functor.on_element(source, member)
        assert SetElements().contains_set_element(set_member)
        image = self._underlying_function(set_member)
        return target.element(image)

    def is_order_preserving(self) -> bool:
        return True

    def is_order_reflecting(self) -> Decision:
        source = self.domain()
        target = self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        assert category.contains_poset(source)
        assert category.contains_poset(target)
        underlying_set = category.underlying_set(source)
        if underlying_set.is_finite() is not True:
            return UNKNOWN
        answer: Decision = True
        for left in source:
            for right in source:
                image_comparison = self(left) <= self(right)
                source_comparison = left <= right
                if image_comparison is True and source_comparison is False:
                    return False
                if image_comparison is UNKNOWN or source_comparison is UNKNOWN:
                    answer = UNKNOWN
        return answer

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
        return hom_category.ObjectType(
            hom_category=hom_category,
            underlying_function=inverse,
        )


class PosetHomCategory(HomCategory):
    """The order-preserving maps between two posets."""

    ObjectType = PosetMorphism
    ElementType = PosetMorphism

    def __call__(
        self,
        action: Callable[[PosetElement], PosetElement] | Mapping[PosetElement, PosetElement] | PosetMorphism,
        *,
        injective: Decision = UNKNOWN,
        surjective: Decision = UNKNOWN,
    ) -> PosetMorphism:
        existing = registered_value(action)
        if existing is not None:
            assert self.contains_poset_morphism(existing)
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

        def underlying_action(member: SetElement) -> SetElement:
            source_member = source.element(member)
            if callable(action):
                image = action(source_member)
            else:
                image = action[source_member]
            assert PosetElements().contains_poset_element(image)
            assert image in target
            set_image = category.forgetful_functor().on_element(target, image)
            assert SetElements().contains_set_element(set_image)
            return set_image

        underlying = set_hom(
            underlying_action,
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
        assert Sets().contains_set_morphism(underlying)
        return self.ObjectType(
            hom_category=self,
            underlying_function=underlying,
        )

    def compose(self, second: Arrow, first: Arrow) -> PosetMorphism:
        second_hom = second.hom_category()
        first_hom = first.hom_category()
        assert is_poset_hom_category(second_hom)
        assert is_poset_hom_category(first_hom)
        assert second_hom.contains_poset_morphism(second)
        assert first_hom.contains_poset_morphism(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        category = self.base_category()
        assert is_partially_ordered_sets_category(category)
        forgetful_functor = category.forgetful_functor()
        underlying = Sets().compose(
            forgetful_functor.on_morphism(second),
            forgetful_functor.on_morphism(first),
        )
        assert Sets().contains_set_morphism(underlying)
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

    def __init__(
        self,
        posets: PartiallyOrderedSetsCategory | FinitePosetsCategory,
        sets: SetsCategory | FiniteSetsCategory,
    ) -> None:
        super().__init__(posets, sets)

    def _object_image(self, source: MathematicalObject) -> SetObject:
        assert PartiallyOrderedSets().contains_poset(source)
        image = source._set_implementation()
        assert image in self.codomain()
        return image

    def _morphism_image(self, morphism: Arrow) -> SetMorphism:
        hom_category = morphism.hom_category()
        assert is_poset_hom_category(hom_category)
        assert hom_category.contains_poset_morphism(morphism)
        return morphism._set_implementation()

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> SetElement:
        assert PartiallyOrderedSets().contains_poset(source)
        assert PosetElements().contains_poset_element(element)
        assert element in source
        return element._set_implementation()

    def is_faithful(self) -> bool:
        return True


class PosetProductObject(ProductObject, PosetObject):
    """A product whose additional order is componentwise."""

    def __init__(
        self,
        *,
        category: ProductsOfPosetsCategory,
        diagram: Functor,
    ) -> None:
        underlying_product = category.set_product(diagram)

        def componentwise(
            left: PosetElement,
            right: PosetElement,
        ) -> Decision:
            left_components = left._set_implementation()
            right_components = right._set_implementation()
            assert ProductElements().contains_product_element(left_components)
            assert ProductElements().contains_product_element(right_components)
            indices = underlying_product.index_set()
            if indices.is_finite() is not True:
                return UNKNOWN
            answer: Decision = True
            for index in indices:
                diagram_object = underlying_product.index_category().object(index)
                factor = diagram(diagram_object)
                assert PartiallyOrderedSets().contains_poset(factor)
                comparison = factor.element(left_components[index]) <= factor.element(
                    right_components[index],
                )
                if comparison is False:
                    return False
                if comparison is UNKNOWN:
                    answer = UNKNOWN
            return answer

        PosetObject.__init__(
            self,
            category=category,
            underlying_set=underlying_product,
            relation=componentwise,
        )
        self._preimage = diagram
        self._image = self
        self._set_product = underlying_product
        self._limit_presentation = self._product_presentation()

    def set_product(self) -> SetProductObject:
        return self._set_product

    def _product_presentation(self) -> ProductPresentation:
        diagram = self.diagram()

        def projection(index: MathematicalObject) -> Arrow:
            factor = diagram(index)
            assert PartiallyOrderedSets().contains_poset(factor)
            set_projection = self._set_product.projection(index)
            assert Sets().contains_set_morphism(set_projection)

            def project(member: PosetElement) -> PosetElement:
                set_member = (
                    PartiallyOrderedSets()
                    .forgetful_functor()
                    .on_element(
                        self,
                        member,
                    )
                )
                assert SetElements().contains_set_element(set_member)
                return factor.element(set_projection(set_member))

            return PartiallyOrderedSets().Hom(self, factor)(project)

        cone = Cone(diagram, self, projection)

        def mediate(other: ConeObject) -> Arrow:
            source = other.apex()
            assert PartiallyOrderedSets().contains_poset(source)

            def assemble(member: PosetElement) -> PosetElement:
                def component(index: SetElement) -> SetElement:
                    diagram_object = self._set_product.index_category().object(index)
                    component_arrow = other.structure_morphism(diagram_object)
                    component_hom = component_arrow.hom_category()
                    assert is_poset_hom_category(component_hom)
                    assert component_hom.contains_poset_morphism(component_arrow)
                    image = component_arrow(member)
                    set_image = PartiallyOrderedSets().forgetful_functor().on_element(component_arrow.codomain(), image)
                    assert SetElements().contains_set_element(set_image)
                    return set_image

                return self.element(self._set_product.element(component))

            return PartiallyOrderedSets().Hom(source, self)(assemble)

        return Product(cone, mediate)


class ForgetPosetProductFunctor(StructuralFunctor):
    """Forget componentwise order while retaining the chosen set product."""

    def __init__(self, products: ProductsOfPosetsCategory) -> None:
        self._products = products
        super().__init__(products, products.set_products())

    def _object_image(self, source: MathematicalObject) -> SetProductObject:
        assert self._products.contains_poset_product(source)
        return source.set_product()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._products.contains_image_arrow(morphism)
        underlying = morphism.underlying_arrow()
        underlying_hom = underlying.hom_category()
        assert is_poset_hom_category(underlying_hom)
        assert underlying_hom.contains_poset_morphism(underlying)
        set_morphism = (
            PartiallyOrderedSets()
            .forgetful_functor()
            .on_morphism(
                underlying,
            )
        )
        target = self._products.set_products()
        domain = self.on_object(morphism.domain())
        codomain = self.on_object(morphism.codomain())
        return target.Hom(domain, codomain)(set_morphism)

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> SetElement:
        assert self._products.contains_poset_product(source)
        assert PosetElements().contains_poset_element(element)
        image = (
            PartiallyOrderedSets()
            .forgetful_functor()
            .on_element(
                source,
                element,
            )
        )
        assert SetElements().contains_set_element(image)
        return image

    def is_faithful(self) -> bool:
        return True


class ProductsOfPosetsCategory(ProductsOfCategory):
    """Products of posets with componentwise order."""

    ObjectType: type[PosetProductObject] = PosetProductObject
    ElementType: type[PosetElement] = PosetElement

    def __init__(self, functor: Functor) -> None:
        domain = functor.domain()
        assert is_functor_category(domain)
        self._index_category = domain.domain()
        self._poset_products: dict[int, PosetProductObject] = {}
        self._set_products: ProductsOfSetsCategory | None = None
        self._forgetful_functor: ForgetPosetProductFunctor | None = None
        self._structural_coherence: Isomorphism | None = None
        super().__init__(
            functor,
            object_type=PosetProductObject,
            element_type=PosetElement,
        )

    def __call__(self, preimage: MathematicalObject) -> PosetProductObject:
        assert is_functor(preimage)
        return self.product_of(preimage)

    def limit_of(self, diagram: Functor) -> PosetProductObject:
        return self.product_of(diagram)

    def product_of(self, diagram: Functor) -> PosetProductObject:
        assert diagram in self.functor().domain()
        key = id(diagram)
        cached = self._poset_products.get(key)
        if cached is None:
            cached = self.ObjectType(category=self, diagram=diagram)
            self._poset_products[key] = cached
        return cached

    def set_diagram(self, diagram: Functor) -> Functor:
        assert diagram in self.functor().domain()
        image = PartiallyOrderedSets().forgetful_functor().postcomposition(diagram.domain())(diagram)
        assert is_functor(image)
        return image

    def set_products(self) -> ProductsOfSetsCategory:
        if self._set_products is None:
            category = Sets().Products(self._index_category)
            assert is_products_of_sets_category(category)
            self._set_products = category
        return self._set_products

    def set_product(self, diagram: Functor) -> SetProductObject:
        return self.set_products()(self.set_diagram(diagram))

    def forgetful_functor(self) -> ForgetPosetProductFunctor:
        if self._forgetful_functor is None:
            self._forgetful_functor = ForgetPosetProductFunctor(self)
        return self._forgetful_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return (*super().super_functors(), self.forgetful_functor())

    def structural_coherences(self) -> tuple[Isomorphism, ...]:
        if self._structural_coherence is None:
            inclusion = super().super_functors()[0]
            first = compose_functors(
                PartiallyOrderedSets().forgetful_functor(),
                inclusion,
            )
            second = compose_functors(
                self.set_products().inclusion(),
                self.forgetful_functor(),
            )

            def component(source: MathematicalObject) -> Arrow:
                image = first(source)
                assert image is second(source)
                return Sets().identity(image)

            coherence = NaturalIsomorphism(
                first,
                second,
                component,
                component,
            )
            assert is_isomorphism(coherence)
            self._structural_coherence = coherence
        return (self._structural_coherence,)

    def contains_poset_product(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[PosetProductObject]:
        return candidate in self


class FinitePosetObject(PosetObject):
    """A finite poset with finite order algorithms."""

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


class FinitePosetsCategory(FullSubcategory):
    """The full subcategory of finite partially ordered sets."""

    ObjectType: type[FinitePosetObject] = FinitePosetObject
    ElementType: type[PosetElement] = PosetElement

    def __init__(self, posets: PartiallyOrderedSetsCategory) -> None:
        self._forgetful_functor: ForgetPosetFunctor | None = None
        self._structural_coherence: Isomorphism | None = None
        super().__init__(
            posets,
            self._is_finite,
            name="Finite partially ordered sets",
            object_type=FinitePosetObject,
            element_type=PosetElement,
        )

    def __call__(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> FinitePosetObject:
        assert underlying_set in FiniteSets()
        value = self.ObjectType(
            category=self,
            underlying_set=underlying_set,
            relation=relation,
        )
        assert self.contains_finite_poset(value)
        return value

    def _is_finite(self, value: MathematicalObject) -> bool:
        assert PartiallyOrderedSets().contains_poset(value)
        return value._set_implementation() in FiniteSets()

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
                first,
                second,
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


class PartiallyOrderedSetsCategory(Category):
    """Sets equipped with a chosen partial order."""

    ObjectType = PosetObject
    ElementType = PosetElement

    def __init__(self) -> None:
        self._forgetful_functor: ForgetPosetFunctor | None = None
        self._finite_posets: FinitePosetsCategory | None = None
        super().__init__(
            object_type=PosetObject,
            element_type=PosetElement,
        )

    def __call__(
        self,
        underlying_set: SetObject,
        relation: OrderRelation,
    ) -> PosetObject:
        if underlying_set in FiniteSets():
            return self.Finite()(underlying_set, relation)
        return self.ObjectType(
            category=self,
            underlying_set=underlying_set,
            relation=relation,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return PosetHomCategory

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> PosetHomCategory:
        assert codomain is not None
        category = Category.Hom(self, domain, codomain)
        assert is_poset_hom_category(category)
        return category

    def forgetful_functor(self) -> ForgetPosetFunctor:
        if self._forgetful_functor is None:
            self._forgetful_functor = ForgetPosetFunctor(self, Sets())
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
            self._finite_posets = FinitePosetsCategory(self)
        return self._finite_posets

    def _products_of_category(self, functor: Functor) -> Category:
        return ProductsOfPosetsCategory(functor)

    def __repr__(self) -> str:
        return "Partially ordered sets"


type PosetEnumeration = Callable[[int], PosetElement]
type PosetPosition = Callable[[PosetElement], int]


class TotallyOrderedSetElement(MathematicalElement):
    """An element of one totally ordered set."""

    def __init__(
        self,
        *,
        ambient_object: TotallyOrderedSetObject,
        poset_element: PosetElement,
    ) -> None:
        assert ambient_object in TotallyOrderedSets()
        inclusion = TotallyOrderedSets().inclusion()
        assert poset_element.ambient_poset() is inclusion.on_object(ambient_object)
        self._poset_element = poset_element
        super().__init__(
            category=TotallyOrderedSetElements(),
            ambient_object=ambient_object,
        )

    def _poset_implementation(self) -> PosetElement:
        return self._poset_element

    def ambient_total_order(self) -> TotallyOrderedSetObject:
        ambient = self.ambient_object()
        assert TotallyOrderedSets().contains_total_order(ambient)
        return ambient

    def position(self) -> int:
        return self.ambient_total_order().position(self)

    def rank(self) -> int:
        return self.position()

    def __le__(self, other: TotallyOrderedSetElement) -> bool:
        inclusion = TotallyOrderedSets().inclusion()
        other_poset_element = inclusion.on_element(other.ambient_total_order(), other)
        assert PosetElements().contains_poset_element(other_poset_element)
        comparison = self._poset_element <= other_poset_element
        assert comparison is not UNKNOWN
        return comparison

    def __lt__(self, other: TotallyOrderedSetElement) -> bool:
        inclusion = TotallyOrderedSets().inclusion()
        other_poset_element = inclusion.on_element(other.ambient_total_order(), other)
        assert PosetElements().contains_poset_element(other_poset_element)
        comparison = self._poset_element < other_poset_element
        assert comparison is not UNKNOWN
        return comparison

    def __repr__(self) -> str:
        return repr(self._poset_element)


class TotallyOrderedSetElementsCategory(Category):
    """The total category of elements of totally ordered sets."""

    ObjectType = TotallyOrderedSetElement

    def __init__(self) -> None:
        super().__init__(object_type=TotallyOrderedSetElement)

    def contains_total_order_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[TotallyOrderedSetElement]:
        return candidate in self

    def __repr__(self) -> str:
        return "Elements of totally ordered sets"


_TOTALLY_ORDERED_SET_ELEMENTS: TotallyOrderedSetElementsCategory | None = None


def TotallyOrderedSetElements() -> TotallyOrderedSetElementsCategory:
    global _TOTALLY_ORDERED_SET_ELEMENTS

    if _TOTALLY_ORDERED_SET_ELEMENTS is None:
        _TOTALLY_ORDERED_SET_ELEMENTS = TotallyOrderedSetElementsCategory()
    return _TOTALLY_ORDERED_SET_ELEMENTS


class TotallyOrderedSetObject(MathematicalObject):
    """A poset with a chosen total-order enumeration."""

    def __init__(
        self,
        *,
        category: TotallyOrderedSetsCategory | FiniteTotallyOrderedSetsCategory,
        poset: PosetObject,
        element_at: PosetEnumeration,
        position_of: PosetPosition,
        finite_enumeration: tuple[PosetElement, ...] | None,
    ) -> None:
        self._poset = poset
        self._element_at = element_at
        self._position_of = position_of
        self._finite_enumeration = finite_enumeration
        self._elements: dict[int, TotallyOrderedSetElement] = {}
        super().__init__(category=category)

    def _poset_implementation(self) -> PosetObject:
        return self._poset

    def element(self, poset_element: PosetElement) -> TotallyOrderedSetElement:
        assert poset_element.ambient_poset() is self._poset
        key = id(poset_element)
        cached = self._elements.get(key)
        if cached is None:
            cached = TotallyOrderedSets().ElementType(
                ambient_object=self,
                poset_element=poset_element,
            )
            self._elements[key] = cached
        return cached

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and TotallyOrderedSetElements().contains_total_order_element(value) and value.ambient_total_order() is self

    def __iter__(self) -> Iterator[TotallyOrderedSetElement]:
        if self._finite_enumeration is not None:
            return iter(self.element(member) for member in self._finite_enumeration)
        size = PartiallyOrderedSets().underlying_set(self._poset).cardinality()
        if size.is_finite() is True:
            return iter(self[position] for position in range(size.finite_value()))
        return iter(self[position] for position in count())

    def __getitem__(self, position: int) -> TotallyOrderedSetElement:
        assert position >= 0
        member = self._element_at(position)
        assert member in self._poset
        return self.element(member)

    def position(self, member: TotallyOrderedSetElement) -> int:
        assert member in self
        poset_member = TotallyOrderedSets().inclusion().on_element(self, member)
        assert PosetElements().contains_poset_element(poset_member)
        position = self._position_of(poset_member)
        assert position >= 0
        assert self[position] == member
        return position

    def rank(self, member: TotallyOrderedSetElement) -> int:
        return self.position(member)

    def unrank(self, position: int) -> TotallyOrderedSetElement:
        return self[position]

    def enumeration_injection(self) -> Arrow:
        def position_of_set_element(member: SetElement) -> int:
            return self._position_of(self._poset.element(member))

        return EnumerationInjection(
            PartiallyOrderedSets().underlying_set(self._poset),
            position_of_set_element,
        )

    def __repr__(self) -> str:
        if self._finite_enumeration is None:
            return f"Totally ordered {PartiallyOrderedSets().underlying_set(self._poset)}"
        return "[" + ", ".join(map(repr, self._finite_enumeration)) + "]"


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

    def __call__(
        self,
        member: TotallyOrderedSetElement,
    ) -> TotallyOrderedSetElement:
        category = self.base_category()
        assert is_totally_ordered_sets_category(category)
        source = self.domain()
        target = self.codomain()
        assert category.contains_total_order(source)
        assert category.contains_total_order(target)
        assert member in source
        inclusion = category.inclusion()
        poset_member = inclusion.on_element(source, member)
        assert PosetElements().contains_poset_element(poset_member)
        image = self._poset_morphism(poset_member)
        return target.element(image)


class TotallyOrderedSetHomCategory(HomCategory):
    """The monotone maps between two totally ordered sets."""

    ObjectType = TotallyOrderedSetMorphism
    ElementType = TotallyOrderedSetMorphism

    def __call__(
        self,
        action: Callable[[TotallyOrderedSetElement], TotallyOrderedSetElement] | Mapping[TotallyOrderedSetElement, TotallyOrderedSetElement] | TotallyOrderedSetMorphism,
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

        existing = registered_value(action)
        if existing is not None:
            assert self.contains_total_order_morphism(existing)
            return existing

        def poset_action(member: PosetElement) -> PosetElement:
            source_member = domain.element(member)
            if callable(action):
                image = action(source_member)
            else:
                image = action[source_member]
            assert TotallyOrderedSetElements().contains_total_order_element(image)
            assert image in codomain
            poset_image = category.inclusion().on_element(codomain, image)
            assert PosetElements().contains_poset_element(poset_image)
            return poset_image

        underlying = poset_hom(
            poset_action,
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
        second_hom = second.hom_category()
        first_hom = first.hom_category()
        assert is_total_order_hom_category(second_hom)
        assert is_total_order_hom_category(first_hom)
        assert second_hom.contains_total_order_morphism(second)
        assert first_hom.contains_total_order_morphism(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        category = self.base_category()
        assert is_totally_ordered_sets_category(category)
        inclusion = category.inclusion()
        underlying = PartiallyOrderedSets().compose(
            inclusion.on_morphism(second),
            inclusion.on_morphism(first),
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

    def __init__(
        self,
        total_orders: TotallyOrderedSetsCategory | FiniteTotallyOrderedSetsCategory,
        posets: PartiallyOrderedSetsCategory | FinitePosetsCategory,
    ) -> None:
        super().__init__(total_orders, posets)

    def _object_image(self, source: MathematicalObject) -> PosetObject:
        assert TotallyOrderedSets().contains_total_order(source)
        image = source._poset_implementation()
        assert image in self.codomain()
        return image

    def _morphism_image(self, morphism: Arrow) -> PosetMorphism:
        hom_category = morphism.hom_category()
        assert is_total_order_hom_category(hom_category)
        assert hom_category.contains_total_order_morphism(morphism)
        return morphism._poset_implementation()

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> PosetElement:
        assert TotallyOrderedSets().contains_total_order(source)
        assert TotallyOrderedSetElements().contains_total_order_element(element)
        assert element in source
        return element._poset_implementation()

    def is_faithful(self) -> bool:
        return True


class FiniteTotallyOrderedSetObject(TotallyOrderedSetObject):
    """A finite totally ordered set."""


class FiniteTotallyOrderedSetsCategory(FullSubcategory):
    """The full subcategory of finite totally ordered sets."""

    ObjectType: type[FiniteTotallyOrderedSetObject] = FiniteTotallyOrderedSetObject
    ElementType: type[TotallyOrderedSetElement] = TotallyOrderedSetElement

    def __init__(self, total_orders: TotallyOrderedSetsCategory) -> None:
        self._finite_poset_functor: TotalOrderInclusionFunctor | None = None
        self._structural_coherence: Isomorphism | None = None
        super().__init__(
            total_orders,
            self._is_finite,
            name="Finite totally ordered sets",
            object_type=FiniteTotallyOrderedSetObject,
            element_type=TotallyOrderedSetElement,
        )

    def __call__(
        self,
        poset: PosetObject,
        element_at: PosetEnumeration,
        position_of: PosetPosition,
        *,
        finite_enumeration: tuple[PosetElement, ...] | None = None,
    ) -> FiniteTotallyOrderedSetObject:
        assert poset in FinitePosets()
        value = self.ObjectType(
            category=self,
            poset=poset,
            element_at=element_at,
            position_of=position_of,
            finite_enumeration=finite_enumeration,
        )
        assert self.contains_finite_total_order(value)
        return value

    def _is_finite(self, value: MathematicalObject) -> bool:
        assert TotallyOrderedSets().contains_total_order(value)
        return value._poset_implementation() in FinitePosets()

    def finite_poset_functor(self) -> TotalOrderInclusionFunctor:
        if self._finite_poset_functor is None:
            self._finite_poset_functor = TotalOrderInclusionFunctor(
                self,
                FinitePosets(),
            )
        return self._finite_poset_functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        return self.inclusion(), self.finite_poset_functor()

    def structural_coherences(self) -> tuple[Isomorphism, ...]:
        if self._structural_coherence is None:
            first = compose_functors(
                TotallyOrderedSets().inclusion(),
                self.inclusion(),
            )
            second = compose_functors(
                FinitePosets().inclusion(),
                self.finite_poset_functor(),
            )

            def component(source: MathematicalObject) -> Arrow:
                image = first(source)
                assert image is second(source)
                return PartiallyOrderedSets().identity(image)

            coherence = NaturalIsomorphism(
                first,
                second,
                component,
                component,
            )
            assert is_isomorphism(coherence)
            self._structural_coherence = coherence
        return (self._structural_coherence,)

    def contains_finite_total_order(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[FiniteTotallyOrderedSetObject]:
        return candidate in self

    def __repr__(self) -> str:
        return "Finite totally ordered sets"


class TotallyOrderedSetsCategory(Category):
    """Sets equipped with a chosen total order."""

    ObjectType = TotallyOrderedSetObject
    ElementType = TotallyOrderedSetElement

    def __init__(self) -> None:
        self._inclusion: TotalOrderInclusionFunctor | None = None
        self._finite_orders: FiniteTotallyOrderedSetsCategory | None = None
        super().__init__(
            object_type=TotallyOrderedSetObject,
            element_type=TotallyOrderedSetElement,
        )

    def __call__(
        self,
        poset: PosetObject,
        element_at: PosetEnumeration,
        position_of: PosetPosition,
        *,
        finite_enumeration: tuple[PosetElement, ...] | None = None,
    ) -> TotallyOrderedSetObject:
        if finite_enumeration is not None:
            assert len(finite_enumeration) == PartiallyOrderedSets().underlying_set(poset).cardinality()
        if poset in FinitePosets():
            return self.Finite()(
                poset,
                element_at,
                position_of,
                finite_enumeration=finite_enumeration,
            )
        return self.ObjectType(
            category=self,
            poset=poset,
            element_at=element_at,
            position_of=position_of,
            finite_enumeration=finite_enumeration,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return TotallyOrderedSetHomCategory

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject | None = None,
    ) -> TotallyOrderedSetHomCategory:
        assert codomain is not None
        category = Category.Hom(self, domain, codomain)
        assert is_total_order_hom_category(category)
        return category

    def inclusion(self) -> TotalOrderInclusionFunctor:
        if self._inclusion is None:
            self._inclusion = TotalOrderInclusionFunctor(
                self,
                PartiallyOrderedSets(),
            )
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
            self._finite_orders = FiniteTotallyOrderedSetsCategory(self)
        return self._finite_orders

    def __repr__(self) -> str:
        return "Totally ordered sets"


_PARTIALLY_ORDERED_SETS: PartiallyOrderedSetsCategory | None = None
_TOTALLY_ORDERED_SETS: TotallyOrderedSetsCategory | None = None
_ORDERED_FINITE_SETS: dict[
    tuple[SetElement, ...],
    FiniteTotallyOrderedSetObject,
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
    members_and_relation: tuple[
        Iterable[SetElement],
        Callable[[SetElement, SetElement], Decision],
    ],
) -> FinitePosetObject:
    """Construct the finite poset defined by ``(members, leq)``."""
    members, relation = members_and_relation
    values = tuple(dict.fromkeys(members))
    underlying_set = FiniteSet(values)

    def transported_relation(left: PosetElement, right: PosetElement) -> Decision:
        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
        left_element = forgetful_functor.on_element(left.ambient_poset(), left)
        right_element = forgetful_functor.on_element(right.ambient_poset(), right)
        assert SetElements().contains_set_element(left_element)
        assert SetElements().contains_set_element(right_element)
        left_value = left_element.value()
        right_value = right_element.value()
        assert SetElements().contains_set_element(left_value)
        assert SetElements().contains_set_element(right_value)
        return relation(left_value, right_value)

    poset = PartiallyOrderedSets()(underlying_set, transported_relation)
    assert FinitePosets().contains_finite_poset(poset)
    return poset


def ordered_set_owned_by(
    elements: Iterable[SetElement],
) -> FiniteTotallyOrderedSetObject:
    enumeration = tuple(dict.fromkeys(elements))
    cached = _ORDERED_FINITE_SETS.get(enumeration)
    if cached is None:
        underlying_set = FiniteSet(enumeration)
        owned_enumeration = tuple(underlying_set.element(element) for element in enumeration)
        positions: dict[SetElement, int] = {element: index for index, element in enumerate(owned_enumeration)}

        def ordered_relation(left: PosetElement, right: PosetElement) -> bool:
            forgetful_functor = PartiallyOrderedSets().forgetful_functor()
            left_element = forgetful_functor.on_element(left.ambient_poset(), left)
            right_element = forgetful_functor.on_element(right.ambient_poset(), right)
            assert SetElements().contains_set_element(left_element)
            assert SetElements().contains_set_element(right_element)
            return positions[left_element] <= positions[right_element]

        poset = PartiallyOrderedSets()(
            underlying_set,
            ordered_relation,
        )
        poset_enumeration = tuple(poset.element(element) for element in owned_enumeration)

        def position_of(member: PosetElement) -> int:
            forgetful_functor = PartiallyOrderedSets().forgetful_functor()
            set_member = forgetful_functor.on_element(member.ambient_poset(), member)
            assert SetElements().contains_set_element(set_member)
            return positions[set_member]

        total_order = TotallyOrderedSets()(
            poset,
            poset_enumeration.__getitem__,
            position_of,
            finite_enumeration=poset_enumeration,
        )
        assert FiniteTotallyOrderedSets().contains_finite_total_order(total_order)
        cached = total_order
        _ORDERED_FINITE_SETS[enumeration] = cached
    return cached


def finite_ordered_set(
    elements: Iterable[SetElement],
) -> FiniteTotallyOrderedSetObject:
    return ordered_set_owned_by(elements)


class SimplexOrderIndexing:
    """The canonical total orders ``Delta[n]`` and ``Delta[aleph0]``."""

    def __init__(self) -> None:
        self._countable_simplex: TotallyOrderedSetObject | None = None

    def __getitem__(self, index: int | Cardinal) -> MathematicalObject:
        from sage_categories.theories.cardinals import is_cardinal
        from sage_categories.theories.ordinals import Ordinals, ordinal

        if is_cardinal(index):
            if index.is_finite() is True:
                maximum = index.finite_value()
            else:
                assert index.is_countably_infinite()
                if self._countable_simplex is None:
                    naturals = NaturalNumbers()

                    def natural_order(
                        left: PosetElement,
                        right: PosetElement,
                    ) -> bool:
                        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
                        left_element = forgetful_functor.on_element(left.ambient_poset(), left)
                        right_element = forgetful_functor.on_element(right.ambient_poset(), right)
                        assert SetElements().contains_set_element(left_element)
                        assert SetElements().contains_set_element(right_element)
                        left_ordinal = left_element.value()
                        right_ordinal = right_element.value()
                        assert Ordinals().contains_ordinal(left_ordinal)
                        assert Ordinals().contains_ordinal(right_ordinal)
                        decision = Ordinals()._is_lequal(left_ordinal, right_ordinal)
                        assert decision is not UNKNOWN
                        return decision

                    poset = PartiallyOrderedSets()(naturals, natural_order)

                    def natural_element(position: int) -> PosetElement:
                        return poset.element(naturals[position])

                    def natural_position(member: PosetElement) -> int:
                        forgetful_functor = PartiallyOrderedSets().forgetful_functor()
                        set_member = forgetful_functor.on_element(member.ambient_poset(), member)
                        assert SetElements().contains_set_element(set_member)
                        return naturals.position(set_member)

                    self._countable_simplex = TotallyOrderedSets()(
                        poset,
                        natural_element,
                        natural_position,
                    )
                return self._countable_simplex
        else:
            maximum = index
        assert maximum >= -1
        naturals = NaturalNumbers()
        return finite_ordered_set(naturals.element(ordinal(position)) for position in range(maximum + 1))

    def __repr__(self) -> str:
        return "Delta"


_SIMPLEX_ORDERS = SimplexOrderIndexing()


def SimplexOrders() -> SimplexOrderIndexing:
    return _SIMPLEX_ORDERS


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
