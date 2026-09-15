"""Strict, full, and essential images of an owned functor."""

from __future__ import annotations

from abc import abstractmethod

from sympy import ask as sympy_ask

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition, register_handler
from sage_categories.cat.properties import PredicateSubcategory
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import MonoDict, cached_function, cached_method

__all__ = [
    "EssentialImageCategory",
    "FullImageCategory",
    "StrictImageCategory",
    "full_image",
    "register_full_image",
    "retain_morphism_image",
    "retain_object_image",
    "strict_image",
]


def _retained_object_image(
    defining_functor: Functor,
    candidate: CategoryOfCategories.ElementType,
) -> bool | None:
    """Whether ``candidate`` is already retained as an exact object image of ``defining_functor``."""
    return True if defining_functor._has_retained_object_image(candidate) else None


class ImageMorphismCategory[**MorphismData, **TwoMorphismData](MorphismCategory[MorphismData, TwoMorphismData]):
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


class ImageCategory[**MorphismData, **TwoMorphismData](Category[MorphismData, TwoMorphismData]):
    """The common retained-data boundary of strict and full images."""

    _image_name: str

    class ObjectType:
        """A literal object image in the target category."""

    class ElementType:
        """A generalized element inherited from the target category."""

    class MorphismType:
        """A target morphism admitted by this image construction."""

    def __init__(self, defining_functor: Functor) -> None:
        class _ImageObjectPredicate(Predicate):
            name = f"{self._image_name}_object"

        class _ImageMorphismPredicate(Predicate):
            name = f"{self._image_name}_morphism"

        self._defining_functor = defining_functor
        self._morphism_members: MonoDict = MonoDict()
        self._object_predicate: Predicate = _ImageObjectPredicate()
        self._morphism_predicate: Predicate = _ImageMorphismPredicate()
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
        return _retained_object_image(self._defining_functor, candidate)

    def _morphism_membership(
        self,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        if candidate in self._morphism_members or self._defining_functor._has_retained_morphism_image(candidate):
            return True
        return None

    def _retain_morphism(
        self,
        morphism: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        assert morphism in self.target().morphism_category(1), f"{morphism!r} is not a morphism of {self.target()!r}"
        self._morphism_members[morphism] = True
        return morphism

    def object_image(
        self,
        source: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return self._defining_functor.on_object(source)

    def morphism_image(
        self,
        source: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        self.object_image(source.domain())
        self.object_image(source.codomain())
        return self._retain_morphism(self._defining_functor.on_morphism(source))

    @cached_method
    def factor_functor(self) -> Functor:
        """The defining functor with its codomain restricted to this image."""
        return Fun(self._defining_functor.domain(), self)(self.object_image, self.morphism_image)

    @cached_method
    def inclusion_functor(self) -> Functor:
        return self._construct_inclusion()

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

    @cached_method(key=lambda self, member_object: identity_key(member_object))
    def _identity_morphism_(
        self,
        member_object: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        """Reuse the target identity without inventing image-category placement.

        Strict and full image inclusions are not generally isofibrations, so membership
        in either image does not give a placement relation to the target category.  The
        identity is nevertheless literally the target's identity on the retained object.
        Cache that shared value with Sage and retain its self-inverse fact locally; do not
        refine it into an image morphism property category.
        """
        identity = self.construct_identity(member_object)
        self._inverses[identity] = identity
        return identity

    def composite(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        assert first in self.morphism_category(1) and second in self.morphism_category(1)
        return self._retain_morphism(self.target().compose_morphisms(second, first))

    def __repr__(self) -> str:
        return f"{self.target()!r}.{type(self).__name__.removesuffix('Category')}({self._defining_functor!r})"


class StrictImageCategory[**MorphismData, **TwoMorphismData](ImageCategory[MorphismData, TwoMorphismData]):
    """The literal object and morphism image of ``F: C -> D``."""

    _image_name = "strict_image"

    class ObjectType:
        """A literal value ``F(X)``."""

    class ElementType:
        """A generalized element inherited from the target category."""

    class MorphismType:
        """A target morphism equal to a literal value ``F(f)``."""

    def _construct_inclusion(self) -> Functor:
        return Fun(self, self.target()).Monomorphisms()()


class FullImageCategory[**MorphismData, **TwoMorphismData](ImageCategory[MorphismData, TwoMorphismData]):
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
            self.membership_proposition(candidate.domain()) & self.membership_proposition(candidate.codomain()),
            assumptions,
        )

    def _construct_inclusion(self) -> Functor:
        return Fun(self, self.target()).FullyFaithful().Monomorphisms()()


class EssentialImageCategory[**MorphismData, **TwoMorphismData](PredicateSubcategory[MorphismData, TwoMorphismData]):
    """The full replete subcategory on objects isomorphic to some ``F(X)``.

    This is ``D.EssentialImage(F)``, the axiom ``Category`` declares, parameterized by the
    functor whose essential image it is (D168).  The declaration owns the name and the
    retention, one subcategory per target and defining functor.
    """

    _base_category_class_and_axiom = (Category, "EssentialImage")

    class ObjectType:
        """An object isomorphic in the target to a value ``F(X)``."""

    class ElementType:
        """A generalized element inherited from the target category."""

    class MorphismType:
        """Any target morphism between objects of the essential image."""

    def __init__(
        self,
        ambient: Category,
        name: str,
        full_subcategory_of: tuple[Category, ...],
        defining_functor: Functor,
    ) -> None:
        # The parameter fixes the ambient, which is what separates this axiom from an
        # inherited one.  ``D.Finite()`` for a declared subcategory ``D`` of ``A`` is the
        # inverse image of ``A.Finite()`` along ``D -> A``, because ``A`` states the same
        # predicate (D83, POL-CAT-084); ``A`` states no essential image of a functor that
        # lands in ``D``, so that derivation reaches here with the wrong ambient and stops.
        assert defining_functor.codomain() is ambient, f"{defining_functor!r} does not land in {ambient!r}, so {ambient!r} states no essential image of it"
        self._defining_functor = defining_functor
        super().__init__(ambient, name, full_subcategory_of)

    def defining_functor(self) -> Functor:
        return self._defining_functor

    def _predicate(
        self,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        return _retained_object_image(self._defining_functor, candidate)

    def object_image(
        self,
        source: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        image = self._defining_functor.on_object(source)
        refine(image, self)
        return image

    def morphism_image(
        self,
        source: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        image = self._defining_functor.on_morphism(source)
        refine(image, self.morphism_category(1))
        return image

    @cached_method
    def factor_functor(self) -> Functor:
        """The essentially-surjective factor from the source into this image."""
        return Fun(self._defining_functor.domain(), self).EssentiallySurjective()(
            self.object_image,
            self.morphism_image,
        )

    def inclusion_functor(self) -> Functor:
        """The fully-faithful inclusion into the original target."""
        inclusion = self.subcategory_monomorphism()
        refine(inclusion, Fun(self, self.ambient()).FullyFaithful())
        return inclusion

    def factorization(self) -> tuple[Functor, Functor]:
        return self.factor_functor(), self.inclusion_functor()

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.{self.name()}({self._defining_functor!r})"


def _has_essential_image(defining_functor: Functor) -> bool:
    """Whether ``D.EssentialImage(F)`` was already asked for; asking here constructs none.

    Every public object and morphism image passes through the two retentions below, so
    reading the axiom's own retention is what keeps a functor that nobody asked an
    essential image of from getting one (``Axiom.is_constructed``).
    """
    return Category.EssentialImage.is_constructed(defining_functor.codomain(), defining_functor)


def retain_object_image(
    defining_functor: Functor,
    image: CategoryOfCategories.ElementType,
) -> None:
    """Retain a completed public object image in each constructed image category."""
    target = defining_functor.codomain()
    if full_image.is_in_cache(target, defining_functor):
        retained_full_image = full_image(target, defining_functor)
        if not isinstance(retained_full_image, FullImageCategory):
            # A category that registered itself as the full image of its own defining
            # functor -- ``C.Limits(I)`` of its chosen limit functor, for one -- is a
            # declared subcategory of the target with its own placement monomorphism, and
            # placement follows that declaration.
            refine(image, retained_full_image)
    if _has_essential_image(defining_functor):
        refine(image, defining_functor.codomain().EssentialImage(defining_functor))


def retain_morphism_image(
    defining_functor: Functor,
    image: MorphismCategory.ObjectType,
) -> None:
    """Retain a completed public morphism image in each constructed image category."""
    target = defining_functor.codomain()
    if strict_image.is_in_cache(target, defining_functor):
        strict_image(target, defining_functor)._retain_morphism(image)
    if _has_essential_image(defining_functor):
        refine(image, defining_functor.codomain().EssentialImage(defining_functor).morphism_category(1))


@cached_function(key=identity_key)
def strict_image(target: Category, defining_functor: Functor) -> StrictImageCategory:
    """Return the retained strict image of ``defining_functor`` in its target."""
    assert defining_functor.codomain() is target
    return StrictImageCategory(defining_functor)


def register_full_image(defining_functor: Functor, image: Category) -> None:
    """Register the category that owns the full image of ``defining_functor``."""
    codomain = defining_functor.codomain()
    assert codomain is image or codomain is image.narrowing_base() or (image.has_ambient() and codomain is image.ambient()), (
        f"{defining_functor!r} does not land in {image!r}, its narrowing base, or its ambient"
    )
    if full_image.is_in_cache(codomain, defining_functor):
        assert full_image(codomain, defining_functor) is image
        return
    full_image.set_cache(image, codomain, defining_functor)


@cached_function(key=identity_key)
def full_image(target: Category, defining_functor: Functor) -> Category:
    """Return the retained full image of ``defining_functor`` in its target."""
    assert defining_functor.codomain() is target
    return FullImageCategory(defining_functor)
