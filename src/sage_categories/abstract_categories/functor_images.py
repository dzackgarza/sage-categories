"""Images of functors as categories over their codomains."""

from __future__ import annotations

from typing import TypeIs

from sage_categories.abstract_categories.functors import Functor, StructuralFunctor
from sage_categories.abstract_categories.hom_categories import HomCategory
from sage_categories.category import Category
from sage_categories.types import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
    TransportedElement,
)


class FunctorImageObject(MathematicalObject):
    """An output together with its chosen preimage."""

    def __init__(
        self,
        *,
        category: ImageOfFunctor,
        preimage: MathematicalObject,
        image: MathematicalObject,
    ) -> None:
        assert preimage in category.functor().domain()
        assert image in category.functor().codomain()
        self._preimage = preimage
        self._image = image
        super().__init__(category=category)

    # `_preimage` and `_image` record how this object was constructed. They stay
    # private: the construction data reaches users under the name its own
    # mathematics gives it, so a limit publishes `diagram()` and `apex()` and a
    # product its factors and projections. "Preimage of what?" has no answer at
    # a product. This module owns the field, and the inclusion functor and image
    # arrows below read it directly.

    def constructing_functor(self) -> Functor:
        category = self.category()
        assert is_functor_image_category(category)
        return category.functor()


class FunctorImageElement(TransportedElement):
    """An element of an object represented in a functor image."""


class FunctorImageArrow(Arrow):
    """A codomain arrow between represented image objects."""

    def __init__(self, *, hom_category: HomCategory, underlying_arrow: Arrow) -> None:
        image_category = hom_category.base_category()
        assert is_functor_image_category(image_category)
        domain = hom_category.domain()
        codomain = hom_category.codomain()
        assert image_category.contains_image(domain)
        assert image_category.contains_image(codomain)
        assert underlying_arrow in image_category.functor().codomain().Hom(
            domain._image,
            codomain._image,
        )
        self._underlying_arrow = underlying_arrow
        super().__init__(hom_category=hom_category)

    def underlying_arrow(self) -> Arrow:
        return self._underlying_arrow


class FunctorImageHomCategory(HomCategory):
    """Codomain arrows between two represented image objects."""

    ObjectType = FunctorImageArrow
    ElementType = FunctorImageArrow

    def __call__(self, underlying_arrow: Arrow) -> FunctorImageArrow:
        return self.ObjectType(
            hom_category=self,
            underlying_arrow=underlying_arrow,
        )

    def identity(
        self,
    ) -> FunctorImageArrow:
        assert self.domain() is self.codomain()
        image_category = self.base_category()
        assert is_functor_image_category(image_category)
        domain = self.domain()
        assert image_category.contains_image(domain)
        return self(image_category.functor().codomain().identity(domain._image))

    def compose(self, second: Arrow, first: Arrow) -> FunctorImageArrow:
        image_category = self.base_category()
        assert is_functor_image_category(image_category)
        assert image_category.contains_image_arrow(second)
        assert image_category.contains_image_arrow(first)
        assert first.domain() is self.domain()
        assert first.codomain() is second.domain()
        assert second.codomain() is self.codomain()
        return self(
            image_category.functor()
            .codomain()
            .compose(
                second.underlying_arrow(),
                first.underlying_arrow(),
            )
        )

    def contains_image_arrow(self, arrow: Arrow) -> TypeIs[FunctorImageArrow]:
        return arrow in self


class ImageInclusionFunctor(StructuralFunctor):
    """The inclusion of a represented functor image into its codomain."""

    def __init__(self, image_category: ImageOfFunctor) -> None:
        self._image = image_category
        super().__init__(image_category, image_category.functor().codomain())

    def _object_image(self, source: MathematicalObject) -> MathematicalObject:
        assert self._image.contains_image(source)
        return source._image

    def _morphism_image(self, morphism: Arrow) -> Arrow:
        assert self._image.contains_image_arrow(morphism)
        return morphism.underlying_arrow()

    def _element_image(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        assert element.ambient_object() is source
        image_element = element._ambient_implementation()
        assert image_element.ambient_object() is source._image
        return image_element

    def _element_preimage(
        self,
        source: MathematicalObject,
        element: MathematicalElement,
    ) -> MathematicalElement:
        assert self._image.contains_image(source)
        assert element.ambient_object() is source._image
        element_type = self._image.ElementType
        return element_type._transported_from_ambient(
            category=self._image,
            ambient_object=source,
            ambient_implementation=element,
        )

    def is_faithful(self) -> bool:
        return True

    def is_inclusion(self) -> bool:
        return True


class ImageOfFunctor(Category):
    """Outputs of one functor, each with a chosen preimage."""

    ObjectType: type[FunctorImageObject] = FunctorImageObject
    ElementType: type[MathematicalElement] = FunctorImageElement

    def __init__(
        self,
        functor: Functor,
    ) -> None:
        self._functor = functor
        self._inclusion: ImageInclusionFunctor | None = None
        super().__init__(
            object_type=self.ObjectType,
            element_type=self.ElementType,
            category=FunctorImageCategoryObjects(),
        )

    def functor(self) -> Functor:
        return self._functor

    def super_functors(self) -> tuple[StructuralFunctor, ...]:
        if self._inclusion is None:
            self._inclusion = ImageInclusionFunctor(self)
        return (self._inclusion,)

    def inclusion(self) -> ImageInclusionFunctor:
        if self._inclusion is None:
            self._inclusion = ImageInclusionFunctor(self)
        return self._inclusion

    def _hom_category_type(self) -> type[HomCategory]:
        return FunctorImageHomCategory

    def Hom(
        self,
        domain: MathematicalObject,
        codomain: MathematicalObject,
    ) -> FunctorImageHomCategory:
        category = Category.Hom(self, domain, codomain)
        assert is_functor_image_hom_category(category)
        return category

    def __call__(self, preimage: MathematicalObject) -> FunctorImageObject:
        image = self._functor(preimage)
        result = self.ObjectType(category=self, preimage=preimage, image=image)
        assert self.contains_image(result)
        return result

    def contains_image(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[FunctorImageObject]:
        return candidate in self

    def contains_image_arrow(
        self,
        candidate: Arrow,
    ) -> TypeIs[FunctorImageArrow]:
        return candidate in self.ArrowCategory()

    def __repr__(self) -> str:
        return f"Image({self._functor})"


class FunctorImageCategories(Category):
    """The category of represented functor-image categories."""

    def __init__(self) -> None:
        super().__init__(object_type=ImageOfFunctor)


_FUNCTOR_IMAGE_CATEGORIES = FunctorImageCategories()


def FunctorImageCategoryObjects() -> FunctorImageCategories:
    return _FUNCTOR_IMAGE_CATEGORIES


def is_functor_image_category(category: Category) -> TypeIs[ImageOfFunctor]:
    return category in _FUNCTOR_IMAGE_CATEGORIES


def is_functor_image_hom_category(
    category: HomCategory,
) -> TypeIs[FunctorImageHomCategory]:
    image_category = category.base_category()
    return is_functor_image_category(image_category) and category in image_category.HomCategory()
