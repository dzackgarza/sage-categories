"""Strict, full, and essential images of an owned functor."""

from __future__ import annotations

from abc import abstractmethod

from sage.structure.coerce_dict import MonoDict
from sympy import ask as sympy_ask

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor, identity_on_values
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition, predicate, register_handler
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.refinement import refine

__all__ = [
    "EssentialImageCategory",
    "FullImageCategory",
    "StrictImageCategory",
    "essential_image",
    "full_image",
    "register_full_image",
    "retain_morphism_image",
    "retain_object_image",
    "strict_image",
]


class ImageMorphismCategory[**MorphismData, **TwoMorphismData](
    MorphismCategory[MorphismData, TwoMorphismData]
):
    """The morphisms retained by a strict or full image."""

    class ObjectType:
        """A retained morphism of the target category."""

    class ElementType:
        """A generalized element of a retained target morphism."""

    class MorphismType:
        """A target 2-morphism between retained morphisms."""

    def membership_proposition(
        self,
        candidate: CategoryOfCategories.ElementType,
    ) -> Proposition:
        return self._base.morphism_membership_proposition(candidate)


class ImageCategory[**MorphismData, **TwoMorphismData](
    Category[MorphismData, TwoMorphismData]
):
    """The common retained-data boundary of strict and full images."""

    _image_name: str

    class ObjectType:
        """A literal object image in the target category."""

    class ElementType:
        """A generalized element inherited from the target category."""

    class MorphismType:
        """A target morphism admitted by this image construction."""

    def __init__(self, defining_functor: Functor) -> None:
        self._defining_functor = defining_functor
        self._object_members: MonoDict = MonoDict()
        self._morphism_members: MonoDict = MonoDict()
        self._object_predicate: Predicate = predicate(f"{self._image_name}_object")
        self._morphism_predicate: Predicate = predicate(f"{self._image_name}_morphism")
        self._inclusion: Functor | None = None
        self._factor: Functor | None = None
        register_handler(self._object_predicate, self._object_membership)
        register_handler(self._morphism_predicate, self._morphism_membership)
        super().__init__()

    def defining_functor(self) -> Functor:
        return self._defining_functor

    def target(self) -> Category:
        return self._defining_functor.codomain()

    def equality(self) -> Predicate:
        return self.target().equality()

    def morphism_category_type(
        self,
    ) -> type[ImageMorphismCategory[MorphismData, TwoMorphismData]]:
        return ImageMorphismCategory

    def membership_proposition(
        self,
        candidate: CategoryOfCategories.ElementType,
    ) -> Proposition:
        return self.target().membership_proposition(candidate) & self._object_predicate(candidate)

    def morphism_membership_proposition(
        self,
        candidate: CategoryOfCategories.ElementType,
    ) -> Proposition:
        return self.target().morphism_category(1).membership_proposition(candidate) & self._morphism_predicate(candidate)

    def _object_membership(
        self,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        return True if candidate in self._object_members else None

    def _morphism_membership(
        self,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        return True if candidate in self._morphism_members else None

    def _retain_object(
        self,
        member_object: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        assert member_object in self.target(), f"{member_object!r} is not an object of {self.target()!r}"
        self._object_members[member_object] = True
        return member_object

    def _retain_morphism(
        self,
        morphism: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        assert morphism in self.target().morphism_category(1), (
            f"{morphism!r} is not a morphism of {self.target()!r}"
        )
        self._morphism_members[morphism] = True
        return morphism

    def object_image(
        self,
        source: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return self._retain_object(self._defining_functor.on_object(source))

    def morphism_image(
        self,
        source: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        self.object_image(source.domain())
        self.object_image(source.codomain())
        return self._retain_morphism(self._defining_functor.on_morphism(source))

    def factor_functor(self) -> Functor:
        """The defining functor with its codomain restricted to this image."""
        if self._factor is None:
            self._factor = Fun(self._defining_functor.domain(), self)(self.object_image, self.morphism_image)
        return self._factor

    def inclusion_functor(self) -> Functor:
        if self._inclusion is None:
            self._inclusion = self._construct_inclusion()
        return self._inclusion

    def factorization(self) -> tuple[Functor, Functor]:
        """The retained factor followed by the identity-on-values inclusion."""
        return self.factor_functor(), self.inclusion_functor()

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.inclusion_functor(),)

    @abstractmethod
    def _construct_inclusion(self) -> Functor:
        """Construct the inclusion with the exact properties of this image."""

    def construct_identity(
        self,
        member_object: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        assert member_object in self, f"{member_object!r} is not an object of {self!r}"
        identity = self.target().morphism_category(1)(member_object, member_object).one()
        return self._retain_morphism(identity)

    def _identity_morphism_(
        self,
        member_object: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        if member_object not in self._identities:
            self._identities[member_object] = self.construct_identity(member_object)
        return self._identities[member_object]

    def composite(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        assert first in self.morphism_category(1) and second in self.morphism_category(1)
        return self._retain_morphism(self.target().compose_morphisms(second, first))

    def compose_morphisms(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        return self.composite(second, first)

    def __repr__(self) -> str:
        return f"{self.target()!r}.{type(self).__name__.removesuffix('Category')}({self._defining_functor!r})"


class StrictImageCategory[**MorphismData, **TwoMorphismData](
    ImageCategory[MorphismData, TwoMorphismData]
):
    """The literal object and morphism image of ``F: C -> D``."""

    _image_name = "strict_image"

    class ObjectType:
        """A literal value ``F(X)``."""

    class ElementType:
        """A generalized element inherited from the target category."""

    class MorphismType:
        """A target morphism equal to a literal value ``F(f)``."""

    def _construct_inclusion(self) -> Functor:
        return Fun(self, self.target()).Monomorphisms()(identity_on_values, identity_on_values)


class FullImageCategory[**MorphismData, **TwoMorphismData](
    ImageCategory[MorphismData, TwoMorphismData]
):
    """The full subcategory spanned by the literal object image of ``F``."""

    _image_name = "full_image"

    class ObjectType:
        """A literal value ``F(X)``."""

    class ElementType:
        """A generalized element inherited from the target category."""

    class MorphismType:
        """Any target morphism between literal object images."""

    def _morphism_membership(
        self,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        if not candidate._is_morphism():
            return False
        return sympy_ask(
            self.membership_proposition(candidate.domain())
            & self.membership_proposition(candidate.codomain()),
            assumptions,
        )

    def _construct_inclusion(self) -> Functor:
        return Fun(self, self.target()).FullyFaithful().Monomorphisms()(
            identity_on_values,
            identity_on_values,
        )


class EssentialImageCategory[**MorphismData, **TwoMorphismData](
    PropertySubcategory[MorphismData, TwoMorphismData]
):
    """The full replete subcategory on objects isomorphic to some ``F(X)``."""

    class ObjectType:
        """An object isomorphic in the target to a value ``F(X)``."""

    class ElementType:
        """A generalized element inherited from the target category."""

    class MorphismType:
        """Any target morphism between objects of the essential image."""

    def __init__(self, defining_functor: Functor) -> None:
        self._defining_functor = defining_functor
        self._factor: Functor | None = None
        super().__init__(defining_functor.codomain(), "EssentialImage", ())

    def defining_functor(self) -> Functor:
        return self._defining_functor

    def object_image(
        self,
        source: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return self(self._defining_functor.on_object(source))

    def morphism_image(
        self,
        source: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        image = self._defining_functor.on_morphism(source)
        refine(image, self.morphism_category(1))
        return image

    def factor_functor(self) -> Functor:
        """The essentially-surjective factor from the source into this image."""
        if self._factor is None:
            self._factor = Fun(self._defining_functor.domain(), self).EssentiallySurjective()(
                self.object_image,
                self.morphism_image,
            )
        return self._factor

    def inclusion_functor(self) -> Functor:
        """The fully-faithful inclusion into the original target."""
        inclusion = self.subcategory_monomorphism()
        refine(inclusion, Fun(self, self.ambient()).FullyFaithful())
        return inclusion

    def factorization(self) -> tuple[Functor, Functor]:
        return self.factor_functor(), self.inclusion_functor()

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.EssentialImage({self._defining_functor!r})"


_strict_images: MonoDict = MonoDict()
_full_images: MonoDict = MonoDict()
_essential_images: MonoDict = MonoDict()


def retain_object_image(
    defining_functor: Functor,
    image: CategoryOfCategories.ElementType,
) -> None:
    """Retain a completed public object image in each constructed image category."""
    if defining_functor in _strict_images:
        _strict_images[defining_functor]._retain_object(image)
    if defining_functor in _full_images:
        full_image = _full_images[defining_functor]
        if isinstance(full_image, FullImageCategory):
            full_image._retain_object(image)
        refine(image, full_image)
    if defining_functor in _essential_images:
        _essential_images[defining_functor](image)


def retain_morphism_image(
    defining_functor: Functor,
    image: MorphismCategory.ObjectType,
) -> None:
    """Retain a completed public morphism image in each constructed image category."""
    if defining_functor in _strict_images:
        _strict_images[defining_functor]._retain_morphism(image)
    if defining_functor in _essential_images:
        refine(image, _essential_images[defining_functor].morphism_category(1))


def strict_image(target: Category, defining_functor: Functor) -> StrictImageCategory:
    """Return the retained strict image of ``defining_functor`` in its target."""
    assert defining_functor.codomain() is target
    if defining_functor not in _strict_images:
        _strict_images[defining_functor] = StrictImageCategory(defining_functor)
    return _strict_images[defining_functor]


def register_full_image(defining_functor: Functor, image: Category) -> None:
    """Register the category that owns the full image of ``defining_functor``."""
    assert defining_functor.codomain() is image.narrowing_base()
    assert defining_functor not in _full_images or _full_images[defining_functor] is image
    _full_images[defining_functor] = image


def full_image(target: Category, defining_functor: Functor) -> Category:
    """Return the retained full image of ``defining_functor`` in its target."""
    assert defining_functor.codomain() is target
    if defining_functor not in _full_images:
        _full_images[defining_functor] = FullImageCategory(defining_functor)
    return _full_images[defining_functor]


def essential_image(target: Category, defining_functor: Functor) -> EssentialImageCategory:
    """Return the retained essential image of ``defining_functor`` in its target."""
    assert defining_functor.codomain() is target
    if defining_functor not in _essential_images:
        _essential_images[defining_functor] = EssentialImageCategory(defining_functor)
    return _essential_images[defining_functor]
