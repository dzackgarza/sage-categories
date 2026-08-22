"""Functors and natural transformations as arrows of ``Cat``.

The semantics are migrated from the research preamble's
``abstract_categories/functors.sage``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeIs, overload

from sage_categories.abstract_categories.hom_categories import (
    HomCategory,
    HomCategoryFamily,
)
from sage_categories.category import Category
from sage_categories.values import Arrow, MathematicalElement, MathematicalObject


class Functor(Arrow, ABC):
    """A functor, represented as an arrow in ``Cat``."""

    def __init__(
        self,
        domain: Category,
        codomain: Category,
        *,
        hom_category: HomCategory | None = None,
    ) -> None:
        from sage_categories.abstract_categories.cat import Cat

        self._image_category: Category | None = None
        self._functor_domain = domain
        self._functor_codomain = codomain
        functor_hom_category = (
            Cat().Hom(domain, codomain) if hom_category is None else hom_category
        )
        assert functor_hom_category.domain() is domain
        assert functor_hom_category.codomain() is codomain
        super().__init__(hom_category=functor_hom_category)

    def domain(self) -> Category:
        """Return the domain category."""
        return self._functor_domain

    def codomain(self) -> Category:
        """Return the codomain category."""
        return self._functor_codomain

    @abstractmethod
    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        """Construct the object image."""

    @abstractmethod
    def on_morphism(self, morphism: Arrow) -> Arrow:
        """Construct the arrow image."""

    def __call__(self, value: MathematicalObject) -> MathematicalObject:
        """Apply this functor to an object or arrow by categorical membership."""
        arrow_category = self.domain().ArrowCategory()
        if arrow_category.contains_arrow(value):
            arrow_image = self.on_morphism(value)
            assert arrow_image in self.codomain().ArrowCategory()
            return arrow_image
        assert value in self.domain()
        object_image = self.on_object(value)
        assert object_image in self.codomain()
        return object_image

    def is_faithful(self) -> bool:
        return False

    def factors(self) -> tuple[Functor, ...]:
        return (self,)

    def Image(self) -> Category:
        """Return outputs of this functor with their chosen preimages."""
        if self._image_category is None:
            from sage_categories.abstract_categories.functor_images import (
                ImageOfFunctor,
            )

            self._image_category = ImageOfFunctor(self)
        return self._image_category

    def then(self, following: Functor) -> Functor:
        """Return ``following`` after this functor."""
        return compose_functors(following, self)


class StructuralFunctor(Functor, ABC):
    """A functor selected to provide inherited object and element methods."""

    @abstractmethod
    def on_element(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        """Construct the element image."""


class IdentityFunctor(StructuralFunctor):
    """The identity functor of one category."""

    def __init__(
        self,
        category: Category,
        *,
        hom_category: HomCategory | None = None,
    ) -> None:
        super().__init__(category, category, hom_category=hom_category)

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        return source

    def on_morphism(self, morphism: Arrow) -> Arrow:
        return morphism

    def on_element(
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

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        assert source in self._included_domain
        assert source in self.codomain()
        return source

    def on_morphism(self, morphism: Arrow) -> Arrow:
        assert morphism in self._included_domain.ArrowCategory()
        assert morphism in self.codomain().ArrowCategory()
        return morphism

    def on_element(
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

    def on_object(self, source: MathematicalObject) -> HomCategory:
        assert self._domain_family.contains_hom_category(source)
        return self._codomain_family.Of(source.domain(), source.codomain())

    def on_morphism(self, morphism: Arrow) -> Arrow:
        assert morphism in self._domain_family.ArrowCategory()
        assert morphism in self._codomain_family.ArrowCategory()
        return morphism

    def on_element(
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
        for early, late in zip(factors, factors[1:], strict=False):
            assert early.codomain() is late.domain()
        self._factors = factors
        super().__init__(
            factors[0].domain(),
            factors[-1].codomain(),
            hom_category=hom_category,
        )

    def factors(self) -> tuple[Functor, ...]:
        return self._factors

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        value = source
        for factor in self._factors:
            value = factor(value)
        return value

    def on_morphism(self, morphism: Arrow) -> Arrow:
        value = morphism
        for factor in self._factors:
            image = factor(value)
            assert factor.codomain().ArrowCategory().contains_arrow(image)
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


class DomainFunctor(Functor):
    """The domain functor ``Ar(C) -> C``."""

    def __init__(self, category: Category) -> None:
        self._arrow_domain = category.ArrowCategory()
        super().__init__(self._arrow_domain, category)

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        assert self._arrow_domain.contains_arrow(source)
        return source.domain()

    def on_morphism(self, morphism: Arrow) -> Arrow:
        assert self._arrow_domain.contains_square(morphism)
        return morphism.left()


class CodomainFunctor(Functor):
    """The codomain functor ``Ar(C) -> C``."""

    def __init__(self, category: Category) -> None:
        self._arrow_domain = category.ArrowCategory()
        super().__init__(self._arrow_domain, category)

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        assert self._arrow_domain.contains_arrow(source)
        return source.codomain()

    def on_morphism(self, morphism: Arrow) -> Arrow:
        assert self._arrow_domain.contains_square(morphism)
        return morphism.right()


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

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        assert source in self.domain()
        return self._value

    def on_morphism(self, morphism: Arrow) -> Arrow:
        assert morphism in self.domain().ArrowCategory()
        return self.codomain().identity(self._value)


class DiagonalFunctor(Functor):
    """The functor sending each object to its constant diagram."""

    def __init__(self, category: Category, index_category: Category) -> None:
        self._index_category = index_category
        super().__init__(category, category.Diagram(index_category))

    def on_object(self, source: MathematicalObject) -> ConstantDiagram:
        return ConstantDiagram(self._index_category, self.domain(), source)

    def on_morphism(self, morphism: Arrow) -> Arrow:
        source = self.on_object(morphism.domain())
        target = self.on_object(morphism.codomain())
        return NaturalTransformation(source, target, lambda index: morphism)


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
        assert self.contains_transformation(second)
        assert self.contains_transformation(first)
        assert first.codomain() is second.domain()
        return self(
            lambda value: second.component(value) * first.component(value)
        )

    def contains_transformation(
        self,
        arrow: Arrow,
    ) -> TypeIs[_NaturalTransformation]:
        return arrow in self


class FunctorCategory(HomCategory):
    """The category ``Fun(C, D)`` of functors and natural transformations."""

    ObjectType = Functor
    ElementType = Functor

    def _hom_category_type(self) -> type[HomCategory]:
        return NaturalTransformationHomCategory

    def domain(self) -> Category:
        from sage_categories.abstract_categories.cat import Cat

        source = HomCategory.domain(self)
        assert Cat().contains_category(source)
        return source

    def codomain(self) -> Category:
        from sage_categories.abstract_categories.cat import Cat

        target = HomCategory.codomain(self)
        assert Cat().contains_category(target)
        return target

    @overload
    def identity(self) -> Functor: ...

    @overload
    def identity(self, value: MathematicalObject) -> Arrow: ...

    def identity(self, value: MathematicalObject | None = None) -> Arrow:
        if value is not None:
            return Category.identity(self, value)
        assert self.domain() is self.codomain()
        return IdentityFunctor(self.domain(), hom_category=self)

    def compose(self, second: Arrow, first: Arrow) -> Functor:
        assert self.contains_functor(second)
        assert self.contains_functor(first)
        assert first.codomain() is second.domain()
        return compose_functors(second, first, hom_category=self)

    def contains_functor(self, arrow: Arrow) -> TypeIs[Functor]:
        return arrow in self


def is_functor(candidate: MathematicalObject) -> TypeIs[Functor]:
    """Narrow an owned value by membership in ``Ar(Cat)``."""
    from sage_categories.abstract_categories.cat import Cat

    return candidate in Cat().ArrowCategory()


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
    from sage_categories.abstract_categories.cat import Cat

    base = category.base_category()
    return base in Cat().HomCategory() and category in base.HomCategory()
