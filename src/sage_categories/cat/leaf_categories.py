"""Generic Cat-owned assembly for leaves whose morphisms carry local data.

The classes here are deliberately small.  A production leaf states its object and
morphism data and, when appropriate, its immediate inheritance-carrying structure
functor.  Cat remains the owner of the categorical operation: endpoints, identities,
composition, construction of the compiled morphism role, and retained factor data are
not reimplemented by the leaf.
"""

from __future__ import annotations

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Proposition

__all__ = [
    "ContravariantFaithfulStructureCategory",
    "FaithfulStructureCategory",
    "LeafCategory",
    "MorphismDataCategory",
    "ParameterizedThinCategory",
]


class LeafCategory(Category):
    """Cat-owned role assembly surface for production mathematical leaves."""

    def assemble_object(self, data: object) -> CategoryOfCategories.ElementType:
        """Construct the compiled object role carrying one leaf-local datum."""
        return self.ObjectType(data)

    def assemble_morphism(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        """Construct a data-free compiled morphism role through Cat's default owner."""
        return Category.construct_morphism(self, domain, codomain)


class MorphismDataCategory(LeafCategory):
    """A category whose leaf supplies only the local datum of each morphism.

    ``_identity_data`` and ``_composite_data`` are operations of that local datum, not
    category-runtime operations.  This base turns the data into owned morphisms.  It is
    useful when a morphism has genuinely local structure in addition to anything carried
    by an immediate structure functor (for example an inverse-image functor on opens).
    """

    def _morphism_from_data(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
        data: object,
    ) -> MorphismCategory.ObjectType:
        return self.MorphismType(domain=domain, codomain=codomain, data=data)

    def _identity_data(self, member_object: CategoryOfCategories.ElementType) -> object:
        raise AssertionError(f"{self!r} declares no local identity datum")

    def _composite_data(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> object:
        raise AssertionError(f"{self!r} declares no local composition datum")

    def construct_identity(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        return self._morphism_from_data(member_object, member_object, self._identity_data(member_object))

    def composite(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        assert first.codomain() is second.domain()
        return self._morphism_from_data(first.domain(), second.codomain(), self._composite_data(second, first))


class FaithfulStructureCategory(MorphismDataCategory):
    """A structure category whose morphism datum is its first inherited image.

    The leaf declares an immediate faithful isofibration in ``structure_functors`` and
    accepts one morphism of its target as the local datum of ``construct_morphism``.
    Cat then obtains identity and composition from that target.  The declaration order
    already chooses among multiple inheritance paths (D165/D167), so no leaf-specific
    identity or composition wiring is needed.
    """

    def _morphism_data_functor(self) -> Functor:
        for functor in self.selected_functors():
            if functor.domain() is self and functor.codomain() is not self and Fun.declares_inheritance(functor):
                return functor
        raise AssertionError(f"{self!r} declares no inheritance-carrying structure functor for its morphism data")

    def _identity_data(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        functor = self._morphism_data_functor()
        image = functor.on_object(member_object)
        return functor.codomain().morphism_category(1)(image, image).one()

    def _composite_data(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        functor = self._morphism_data_functor()
        return functor.on_morphism(second) * functor.on_morphism(first)

    def _morphism_equality(
        self,
        first: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
    ) -> bool | None:
        """Reflect morphism equality through the declared faithful structure functor."""
        if first.domain() is not second.domain() or first.codomain() is not second.codomain():
            return False
        from sage_categories.cat.predicates import ask

        functor = self._morphism_data_functor()
        return ask(functor.on_morphism(first) == functor.on_morphism(second))


class ContravariantFaithfulStructureCategory(FaithfulStructureCategory):
    """Faithful structure whose stored local datum is the original of an opposite map."""

    def _identity_data(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        from sage_categories.cat.opposites import opposite_morphism

        return opposite_morphism(super()._identity_data(member_object))

    def _composite_data(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        from sage_categories.cat.opposites import opposite_morphism

        functor = self._morphism_data_functor()
        return opposite_morphism(functor.on_morphism(second) * functor.on_morphism(first))


class ParameterizedThinCategory(MorphismDataCategory):
    """A thin leaf category parameterized by mathematical owner data.

    The leaf supplies only ``_admits_morphism``. Cat owns parameter retention and the
    unique identity/composite morphism assembly.
    """

    def __init__(self, *parameters: object) -> None:
        self._leaf_parameters = parameters
        super().__init__()

    def parameter(self, position: int) -> object:
        return self._leaf_parameters[position]

    def _admits_morphism(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
    ) -> bool:
        raise AssertionError(f"{self!r} declares no thin morphism predicate")

    def construct_morphism(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
        *args: object,
        **kwargs: object,
    ) -> MorphismCategory.ObjectType:
        assert not args and not kwargs
        assert self._admits_morphism(domain, codomain)
        return self._morphism_from_data(domain, codomain, None)

    def _identity_data(self, member_object: CategoryOfCategories.ElementType) -> None:
        return None

    def _composite_data(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> None:
        return None
