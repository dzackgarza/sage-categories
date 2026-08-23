"""Functors and natural transformations as arrows of ``Cat``.

The semantics are migrated from the research preamble's
``abstract_categories/functors.sage``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from itertools import pairwise
from typing import TYPE_CHECKING, Any, TypeIs

from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.category import Category
from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.sets import DiscreteObjectSet, SetElement


class Functor(Arrow, ABC):
    """A functor, represented as an arrow in ``Cat``."""

    def __init__(
        self,
        domain: Category,
        codomain: Category,
        *,
        hom_category: HomCategory | None = None,
        object_map: Callable[[MathematicalObject], MathematicalObject] | None = None,
        morphism_map: Callable[[Arrow], Arrow] | None = None,
    ) -> None:
        assert (object_map is None) is (morphism_map is None)
        from sage_categories.abstract_categories.cat import category_universe

        self._cached_image_category: Category | None = None
        self._functor_domain = domain
        self._functor_codomain = codomain
        self._object_map = object_map
        self._morphism_map = morphism_map
        self._object_images: dict[int, MathematicalObject] = {}
        self._morphism_images: dict[int, Arrow] = {}
        self._postcomposition_functors: dict[int, PostcompositionFunctor] = {}
        functor_hom_category = category_universe(domain, codomain).Hom(domain, codomain) if hom_category is None else hom_category
        assert functor_hom_category.domain() is domain
        assert functor_hom_category.codomain() is codomain
        super().__init__(hom_category=functor_hom_category)

    def domain(self) -> Category:
        """Return the domain category."""
        return self._functor_domain

    def codomain(self) -> Category:
        """Return the codomain category."""
        return self._functor_codomain

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        """Construct the object image."""
        assert self._object_map is not None
        return self._object_map(source)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        """Construct the arrow image."""
        assert self._morphism_map is not None
        return self._morphism_map(morphism)

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        """Return the canonical image of one object."""
        assert source in self.domain()
        key = id(source)
        image = self._object_images.get(key)
        if image is None:
            image = self._object_image(source)
            assert image in self.codomain()
            self._object_images[key] = image
        return image

    def on_morphism(self, morphism: Arrow) -> Arrow:
        """Return the canonical image of one arrow."""
        assert self.domain().contains_arrow(morphism)
        key = id(morphism)
        image = self._morphism_images.get(key)
        if image is None:
            domain = self.on_object(morphism.domain())
            codomain = self.on_object(morphism.codomain())
            image = self._morphism_image(morphism)
            assert self.codomain().contains_arrow(image)
            assert image.domain() is domain
            assert image.codomain() is codomain
            self._morphism_images[key] = image
        return image

    def __call__(self, value: MathematicalObject) -> MathematicalObject:
        """Apply this functor to an object or arrow by categorical membership."""
        from sage_categories.compiler import category_compiler

        arrow_category = self.domain().ArrowCategory()
        if arrow_category.contains_object(value):
            source_arrow = value
            source_category = source_arrow.base_category()
            if source_category is not self.domain() and source_category.is_subcategory(self.domain()):
                route = category_compiler().implementation_route(
                    source_category,
                    self.domain(),
                )
                source_arrow = source_arrow._morphism_image_along(route)
            arrow_image = self.on_morphism(source_arrow)
            assert arrow_image in self.codomain().ArrowCategory()
            return arrow_image
        assert value in self.domain()
        source_object = value
        source_category = source_object.category()
        if source_category is not self.domain() and source_category.is_subcategory(self.domain()):
            route = category_compiler().implementation_route(
                source_category,
                self.domain(),
            )
            source_object = source_object._object_image_along(route)
        object_image = self.on_object(source_object)
        assert object_image in self.codomain()
        return object_image

    def is_faithful(self) -> bool:
        return False

    def factors(self) -> tuple[Functor, ...]:
        return (self,)

    def Image(self) -> Category:
        """Return outputs of this functor with their chosen preimages."""
        if self._cached_image_category is None:
            self._cached_image_category = self._construct_image_category()
        return self._cached_image_category

    def _construct_image_category(self) -> Category:
        from sage_categories.abstract_categories.functor_images import (
            ImageOfFunctor,
        )

        return ImageOfFunctor(self)

    def then(self, following: Functor) -> Functor:
        """Return ``following`` after this functor."""
        return compose_functors(following, self)

    def postcomposition(self, index_category: Category) -> PostcompositionFunctor:
        """Postcompose diagrams of shape ``index_category`` with this functor."""
        key = id(index_category)
        cached = self._postcomposition_functors.get(key)
        if cached is None:
            cached = PostcompositionFunctor(index_category, self)
            self._postcomposition_functors[key] = cached
        return cached


class StructuralFunctor(Functor, ABC):
    """A functor selected to provide inherited object and element methods."""

    def __init__(
        self,
        domain: Category,
        codomain: Category,
        *,
        hom_category: HomCategory | None = None,
    ) -> None:
        self._element_images: dict[int, MathematicalElement] = {}
        super().__init__(domain, codomain, hom_category=hom_category)
        _STRUCTURAL_FUNCTORS[id(self)] = self

    @abstractmethod
    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        """Construct the element image."""

    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        """Return the canonical image of an element of ``source``."""
        assert source in self.domain()
        assert element.ambient_object() is source
        target = self.on_object(source)
        key = id(element)
        image = self._element_images.get(key)
        if image is None:
            image = self._element_image(source, element)
            assert image.ambient_object() is target
            self._element_images[key] = image
        return image


_STRUCTURAL_FUNCTORS: dict[int, StructuralFunctor] = {}


def is_structural_functor(
    candidate: MathematicalObject,
) -> TypeIs[StructuralFunctor]:
    """Return whether ``candidate`` is a selected structural functor."""
    return _STRUCTURAL_FUNCTORS.get(id(candidate)) is candidate


class IdentityFunctor(StructuralFunctor):
    """The identity functor of one category."""

    def __init__(
        self,
        category: Category,
        *,
        hom_category: HomCategory | None = None,
    ) -> None:
        super().__init__(category, category, hom_category=hom_category)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        return source

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        return morphism

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element

    def is_faithful(self) -> bool:
        return True

    def factors(self) -> tuple[Functor, ...]:
        return ()

    def __repr__(self) -> str:
        return f"Id({self.domain()})"


class InclusionFunctor(StructuralFunctor):
    """The identity-on-values inclusion of a subcategory."""

    def __init__(self, domain: Category, codomain: Category) -> None:
        self._included_domain = domain
        super().__init__(domain, codomain)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert source in self._included_domain
        assert source in self.codomain()
        return source

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert morphism in self._included_domain.ArrowCategory()
        assert morphism in self.codomain().ArrowCategory()
        return morphism

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element

    def is_faithful(self) -> bool:
        return True


class HomCategoryFamilyInclusionFunctor(StructuralFunctor):
    """Map each restricted hom category to its ambient hom category."""

    def __init__(
        self,
        domain: HomCategoryFamily,
        codomain: HomCategoryFamily,
    ) -> None:
        self._domain_family = domain
        self._codomain_family = codomain
        super().__init__(domain, codomain)

    def _object_image(self, source: MathematicalObject) -> HomCategory:
        assert self._domain_family.contains_hom_category(source)
        return self._codomain_family.Of(source.domain(), source.codomain())

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert morphism in self._domain_family.ArrowCategory()
        assert morphism in self._codomain_family.ArrowCategory()
        return morphism

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element

    def is_faithful(self) -> bool:
        return True


class ComposedFunctor(Functor):
    """A flattened nonempty composite of functors."""

    def __init__(
        self,
        factors: tuple[Functor, ...],
        *,
        hom_category: HomCategory | None = None,
    ) -> None:
        assert factors
        for early, late in pairwise(factors):
            assert early.codomain() is late.domain()
        self._factors = factors
        super().__init__(
            factors[0].domain(),
            factors[-1].codomain(),
            hom_category=hom_category,
        )

    def factors(self) -> tuple[Functor, ...]:
        return self._factors

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        value = source
        for factor in self._factors:
            value = factor(value)
        return value

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        value = morphism
        for factor in self._factors:
            image = factor(value)
            assert factor.codomain().ArrowCategory().contains_object(image)
            value = image
        return value

    def is_faithful(self) -> bool:
        return all(factor.is_faithful() for factor in self._factors)


def compose_functors(
    second: Functor,
    first: Functor,
    *,
    hom_category: HomCategory | None = None,
) -> Functor:
    """Return the flattened composite ``second`` after ``first``."""
    assert first.codomain() is second.domain()
    factors = first.factors() + second.factors()
    if not factors:
        return IdentityFunctor(first.domain(), hom_category=hom_category)
    if len(factors) == 1:
        return factors[0]
    return ComposedFunctor(factors, hom_category=hom_category)


class PostcompositionFunctor(Functor):
    """Postcompose diagrams and right-whisker natural transformations."""

    # This is Mathlib's ``Functor.whiskeringRight`` specialized at one functor:
    # https://github.com/leanprover-community/mathlib4/blob/master/Mathlib/CategoryTheory/Whiskering.lean
    def __init__(self, index_category: Category, functor: Functor) -> None:
        self._index_category = index_category
        self._functor = functor
        super().__init__(
            functor.domain().Diagram(index_category),
            functor.codomain().Diagram(index_category),
        )

    def index_category(self) -> Category:
        return self._index_category

    def functor(self) -> Functor:
        return self._functor

    def _object_image(self, source: MathematicalObject) -> Functor:
        assert is_functor(source)
        return compose_functors(self._functor, source)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        hom_category = morphism.hom_category()
        assert is_natural_transformation_hom_category(hom_category)
        assert hom_category.contains_transformation(morphism)
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        assert is_functor(source)
        assert is_functor(target)
        return NaturalTransformation(
            source,
            target,
            lambda index: self._functor.on_morphism(morphism.component(index)),
        )


class DomainFunctor(Functor):
    """The domain functor ``Ar(C) -> C``."""

    def __init__(self, category: Category) -> None:
        self._arrow_domain = category.ArrowCategory()
        super().__init__(self._arrow_domain, category)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._arrow_domain.contains_object(source)
        return source.domain()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._arrow_domain.contains_square(morphism)
        return morphism.left()


class CodomainFunctor(Functor):
    """The codomain functor ``Ar(C) -> C``."""

    def __init__(self, category: Category) -> None:
        self._arrow_domain = category.ArrowCategory()
        super().__init__(self._arrow_domain, category)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._arrow_domain.contains_object(source)
        return source.codomain()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._arrow_domain.contains_square(morphism)
        return morphism.right()


class DiscreteObject(MathematicalObject):
    """One object of a represented discrete category."""

    def __init__(
        self,
        *,
        category: DiscreteCategory,
        label: SetElement,
    ) -> None:
        self._label = label
        super().__init__(category=category)

    def label(self) -> SetElement:
        return self._label

    def __repr__(self) -> str:
        return repr(self._label)


class DiscreteIdentity(Arrow):
    """The unique arrow at one object of a discrete category."""


class DiscreteHomCategory(HomCategory):
    """A singleton hom category when both endpoints are equal."""

    ObjectType = DiscreteIdentity
    ElementType = DiscreteIdentity

    def __call__(self) -> DiscreteIdentity:
        return self.identity()

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> DiscreteIdentity:
        assert value is None
        assert self.domain() is self.codomain()
        return self.ObjectType(hom_category=self)

    def compose(self, second: Arrow, first: Arrow) -> DiscreteIdentity:
        assert first in self and second in self
        return self.identity()

    def objects(self) -> MathematicalObject:
        from sage_categories.theories.sets import FiniteSet

        if self.domain() is self.codomain():
            return FiniteSet(frozenset({self.identity()}))
        return FiniteSet(frozenset())


class DiscreteCategory(Category):
    """The discrete category on one owned set."""

    ObjectType = DiscreteObject

    def __init__(
        self,
        *,
        category: Category,
        label_set: MathematicalObject,
    ) -> None:
        from sage_categories.theories.sets import Sets

        assert label_set in Sets()
        self._label_set = label_set
        self._objects_by_label: list[tuple[SetElement, DiscreteObject]] = []
        self._object_set: DiscreteObjectSet | None = None
        self._arrow_set: MathematicalObject | None = None
        super().__init__(object_type=DiscreteObject, category=category)

    def label_set(self) -> MathematicalObject:
        return self._label_set

    def object(self, label: SetElement) -> DiscreteObject:
        from sage_categories.theories.sets import Sets

        assert Sets().contains_set(self._label_set)
        assert label in self._label_set
        for saved_label, value in self._objects_by_label:
            if saved_label == label:
                return value
        value = self.ObjectType(category=self, label=label)
        assert self.contains_object(value)
        self._objects_by_label.append((label, value))
        return value

    def objects(self) -> DiscreteObjectSet:
        from sage_categories.theories.sets import DiscreteObjectSet, Sets

        if self._object_set is None:
            assert Sets().contains_set(self._label_set)
            self._object_set = DiscreteObjectSet(self, self._label_set)
        return self._object_set

    def object_element(self, value: MathematicalObject) -> SetElement:
        return self.objects().element(value)

    def arrows(self) -> MathematicalObject:
        from sage_categories.theories.sets import DiscreteArrowSet

        if self._arrow_set is None:
            self._arrow_set = DiscreteArrowSet(self)
        return self._arrow_set

    def __iter__(self) -> Iterator[DiscreteObject]:
        from sage_categories.theories.sets import Sets

        assert Sets().contains_set(self._label_set)
        return iter(tuple(self.object(label) for label in self._label_set))

    def __contains__(self, candidate: Any) -> bool:
        value = registered_value(candidate)
        return value is not None and value.category() is self

    def contains_object(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[DiscreteObject]:
        return candidate in self

    def _hom_category_type(self) -> type[HomCategory]:
        return DiscreteHomCategory

    def __repr__(self) -> str:
        return f"Discrete({self._label_set})"


class ObjectSetFunctor(StructuralFunctor):
    """Send a discrete category to its object set."""

    def __init__(self, domain: DiscreteCategoriesCategory) -> None:
        from sage_categories.theories.sets import Sets

        self._discrete_categories = domain
        super().__init__(domain, Sets())

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._discrete_categories.contains_discrete_category(source)
        return source.objects()

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        from sage_categories.theories.sets import Sets, is_set_hom_category

        assert is_functor(morphism)
        source = morphism.domain()
        target = morphism.codomain()
        assert self._discrete_categories.contains_discrete_category(source)
        assert self._discrete_categories.contains_discrete_category(target)
        source_objects = source.objects()
        target_objects = target.objects()
        assert Sets().contains_set(source_objects)
        assert Sets().contains_set(target_objects)

        def map_object(value: SetElement) -> SetElement:
            represented = value.value()
            assert source.contains_object(represented)
            image = morphism(represented)
            assert target.contains_object(image)
            return target_objects.element(image)

        hom_category = Sets().Hom(source_objects, target_objects)
        assert is_set_hom_category(hom_category)
        return hom_category(map_object)

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        return element


class DiscreteCategoriesCategory(Category):
    """The category of arbitrary discrete categories."""

    ObjectType = DiscreteCategory

    def __init__(self) -> None:
        self._object_set_functor: ObjectSetFunctor | None = None
        super().__init__(object_type=DiscreteCategory)

    def __call__(self, label_set: MathematicalObject) -> DiscreteCategory:
        return self.ObjectType(category=self, label_set=label_set)

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._object_set_functor is None:
            self._object_set_functor = ObjectSetFunctor(self)
        return (self._object_set_functor,)

    def contains_discrete_category(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[DiscreteCategory]:
        return candidate in self


_DISCRETE_CATEGORIES: DiscreteCategoriesCategory | None = None


def DiscreteCategories() -> DiscreteCategoriesCategory:
    global _DISCRETE_CATEGORIES

    if _DISCRETE_CATEGORIES is None:
        _DISCRETE_CATEGORIES = DiscreteCategoriesCategory()
    return _DISCRETE_CATEGORIES


class DiscreteDiagram(Functor):
    """A functor from a discrete category, given on objects."""

    def __init__(
        self,
        domain: DiscreteCategory,
        codomain: Category,
        values: Callable[[DiscreteObject], MathematicalObject],
    ) -> None:
        self._index_category = domain
        self._values = values
        super().__init__(domain, codomain)

    def domain(self) -> DiscreteCategory:
        return self._index_category

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self.domain().contains_object(source)
        image = self._values(source)
        assert image in self.codomain()
        return image

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        return self.codomain().identity(self.on_object(morphism.domain()))


class ConstantDiagram(Functor):
    """The constant diagram at one object."""

    def __init__(
        self,
        index_category: Category,
        codomain: Category,
        value: MathematicalObject,
    ) -> None:
        assert value in codomain
        self._value = value
        super().__init__(index_category, codomain)

    def constant_value(self) -> MathematicalObject:
        return self._value

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert source in self.domain()
        return self._value

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert morphism in self.domain().ArrowCategory()
        return self.codomain().identity(self._value)


class DiagonalFunctor(Functor):
    """The functor sending each object to its constant diagram."""

    def __init__(self, category: Category, index_category: Category) -> None:
        self._index_category = index_category
        super().__init__(category, category.Diagram(index_category))

    def _object_image(self, source: MathematicalObject) -> ConstantDiagram:
        return ConstantDiagram(self._index_category, self.domain(), source)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        assert is_functor(source)
        assert is_functor(target)
        return NaturalTransformation(source, target, lambda index: morphism)


class LimitFunctor(Functor):
    """A chosen limit functor on diagrams of one fixed shape."""

    def __init__(self, codomain: Category, index_category: Category) -> None:
        self._index_category = index_category
        super().__init__(codomain.Diagram(index_category), codomain)

    def index_category(self) -> Category:
        return self._index_category

    def _construct_image_category(self) -> Category:
        return self.codomain()._limits_of_category(self)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert is_functor(source)
        assert source in self.domain()
        from sage_categories.abstract_categories.products import (
            is_limits_of_category,
        )

        image = self.Image()
        assert is_limits_of_category(image)
        return image.limit_of(source)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        hom_category = morphism.hom_category()
        assert is_natural_transformation_hom_category(hom_category)
        assert hom_category.contains_transformation(morphism)
        source = morphism.domain()
        target = morphism.codomain()
        assert is_functor(source)
        assert is_functor(target)
        from sage_categories.abstract_categories.products import (
            Cone,
            is_limits_of_category,
        )

        image = self.Image()
        assert is_limits_of_category(image)
        source_limit = image.limit_of(source)
        target_limit = image.limit_of(target)
        source_cone = source_limit.limit_cone()
        cone = Cone(
            target,
            source_limit.image(),
            lambda index: self.codomain().compose(
                morphism.component(index),
                source_cone.structure_morphism(index),
            ),
        )
        return target_limit.universal_morphism(cone)


class ColimitFunctor(Functor):
    """A chosen colimit functor on diagrams of one fixed shape."""

    def __init__(self, codomain: Category, index_category: Category) -> None:
        self._index_category = index_category
        super().__init__(codomain.Diagram(index_category), codomain)

    def index_category(self) -> Category:
        return self._index_category

    def _construct_image_category(self) -> Category:
        return self.codomain()._colimits_of_category(self)

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert is_functor(source)
        assert source in self.domain()
        from sage_categories.abstract_categories.products import (
            is_colimits_of_category,
        )

        image = self.Image()
        assert is_colimits_of_category(image)
        return image.colimit_of(source)

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        hom_category = morphism.hom_category()
        assert is_natural_transformation_hom_category(hom_category)
        assert hom_category.contains_transformation(morphism)
        source = morphism.domain()
        target = morphism.codomain()
        assert is_functor(source)
        assert is_functor(target)
        from sage_categories.abstract_categories.products import (
            Cocone,
            is_colimits_of_category,
        )

        image = self.Image()
        assert is_colimits_of_category(image)
        source_colimit = image.colimit_of(source)
        target_colimit = image.colimit_of(target)
        target_cocone = target_colimit.colimit_cocone()
        cocone = Cocone(
            source,
            target_colimit.image(),
            lambda index: self.codomain().compose(
                target_cocone.costructure_morphism(index),
                morphism.component(index),
            ),
        )
        return source_colimit.universal_morphism(cocone)


class ProductFunctor(LimitFunctor):
    """The chosen limit functor on diagrams with discrete domain."""

    def __init__(self, codomain: Category, index_category: Category) -> None:
        assert index_category in DiscreteCategories()
        super().__init__(codomain, index_category)

    def _construct_image_category(self) -> Category:
        return self.codomain()._products_of_category(self)


class CoproductFunctor(ColimitFunctor):
    """The chosen colimit functor on diagrams with discrete domain."""

    def __init__(self, codomain: Category, index_category: Category) -> None:
        assert index_category in DiscreteCategories()
        super().__init__(codomain, index_category)

    def _construct_image_category(self) -> Category:
        return self.codomain()._coproducts_of_category(self)


class _NaturalTransformation(Arrow):
    """A natural transformation represented by its object components."""

    def __init__(
        self,
        *,
        hom_category: HomCategory,
        components: Callable[[MathematicalObject], Arrow],
    ) -> None:
        self._components = components
        super().__init__(hom_category=hom_category)

    def component(self, value: MathematicalObject) -> Arrow:
        """Return the component at ``value``."""
        source = self.domain()
        target = self.codomain()
        assert is_functor(source)
        assert is_functor(target)
        assert value in source.domain()
        component = self._components(value)
        assert component in source.codomain().Hom(source(value), target(value))
        return component


class NaturalTransformationHomCategory(HomCategory):
    """Natural transformations between two parallel functors."""

    ObjectType = _NaturalTransformation
    ElementType = _NaturalTransformation

    def __call__(
        self,
        components: Callable[[MathematicalObject], Arrow],
    ) -> _NaturalTransformation:
        return self.ObjectType(hom_category=self, components=components)

    def identity(
        self,
        value: MathematicalObject | None = None,
    ) -> _NaturalTransformation:
        assert value is None
        source = self.domain()
        assert source is self.codomain()
        assert is_functor(source)
        return self(lambda value: source.codomain().identity(source(value)))

    def compose(self, second: Arrow, first: Arrow) -> _NaturalTransformation:
        second_hom = second.hom_category()
        first_hom = first.hom_category()
        assert is_natural_transformation_hom_category(second_hom)
        assert is_natural_transformation_hom_category(first_hom)
        assert second_hom.contains_transformation(second)
        assert first_hom.contains_transformation(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return self(lambda value: second.component(value) * first.component(value))

    def contains_transformation(
        self,
        arrow: Arrow,
    ) -> TypeIs[_NaturalTransformation]:
        return arrow in self


class FunctorCategory(HomCategory):
    """The category ``Fun(C, D)`` of functors and natural transformations."""

    ObjectType = Functor
    ElementType = Functor

    def __call__(
        self,
        object_map: Callable[[MathematicalObject], MathematicalObject],
        morphism_map: Callable[[Arrow], Arrow],
    ) -> Functor:
        return self.ObjectType(
            self.domain(),
            self.codomain(),
            hom_category=self,
            object_map=object_map,
            morphism_map=morphism_map,
        )

    def _hom_category_type(self) -> type[HomCategory]:
        return NaturalTransformationHomCategory

    def domain(self) -> Category:
        from sage_categories.abstract_categories.cat import is_category_of_categories

        source = HomCategory.domain(self)
        universe = self.base_category()
        assert is_category_of_categories(universe)
        assert universe.contains_category(source)
        return source

    def codomain(self) -> Category:
        from sage_categories.abstract_categories.cat import is_category_of_categories

        target = HomCategory.codomain(self)
        universe = self.base_category()
        assert is_category_of_categories(universe)
        assert universe.contains_category(target)
        return target

    def identity(self, value: MathematicalObject | None = None) -> Arrow:
        if value is not None:
            return Category.identity(self, value)
        assert self.domain() is self.codomain()
        return IdentityFunctor(self.domain(), hom_category=self)

    def compose(self, second: Arrow, first: Arrow) -> Functor:
        assert is_functor(second)
        assert is_functor(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return compose_functors(second, first, hom_category=self)

    def contains_functor(self, arrow: Arrow) -> TypeIs[Functor]:
        return arrow in self


def is_functor_category(category: Category) -> TypeIs[FunctorCategory]:
    """Return whether ``category`` is a functor category."""
    from sage_categories.abstract_categories.cat import category_universes

    return any(category in universe.HomCategory() for universe in category_universes())


def is_functor(candidate: MathematicalObject) -> TypeIs[Functor]:
    """Narrow an owned value by membership in ``Ar(Cat)``."""
    from sage_categories.abstract_categories.cat import category_universes

    return any(candidate in universe.ArrowCategory() for universe in category_universes())


def NaturalTransformations(
    source: Functor,
    target: Functor,
) -> NaturalTransformationHomCategory:
    """Return the natural transformations from source to target."""
    assert source.hom_category() is target.hom_category()
    category = source.hom_category().Hom(source, target)
    assert is_natural_transformation_hom_category(category)
    return category


def NaturalTransformation(
    source: Functor,
    target: Functor,
    components: Callable[[MathematicalObject], Arrow],
) -> Arrow:
    """Construct a natural transformation from its components."""
    return NaturalTransformations(source, target)(components)


def NaturalIsomorphism(
    source: Functor,
    target: Functor,
    components: Callable[[MathematicalObject], Arrow],
    inverse_components: Callable[[MathematicalObject], Arrow],
) -> Arrow:
    """Construct a natural isomorphism from inverse component families."""
    from sage_categories.abstract_categories.arrow_categories import (
        declare_isomorphism,
    )

    forward = NaturalTransformation(source, target, components)
    backward = NaturalTransformation(target, source, inverse_components)
    return declare_isomorphism(forward, backward)


def is_natural_transformation_hom_category(
    category: HomCategory,
) -> TypeIs[NaturalTransformationHomCategory]:
    """Return whether ``category`` contains natural transformations."""
    from sage_categories.abstract_categories.cat import category_universes

    base = category.base_category()
    return any(base in universe.HomCategory() for universe in category_universes()) and category in base.HomCategory()
