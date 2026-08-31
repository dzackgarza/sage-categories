"""The parameterized one-object categories ``Cat().Point(X)`` (POL-CAT-083).

``Cat().Point(X)``, written ``{X}``, has the existing object ``X`` as its sole object
and the existing identity ``1_X`` as its sole morphism.  It follows Mathlib's punctual
category ``Discrete PUnit`` and ``Functor.fromPUnit``; the repository names the chosen
object in the category itself instead of in a constant functor
(``Mathlib/CategoryTheory/PUnit``, inspected 2026-08-27).

``{X}`` selects the monomorphism into the category ``X`` was already placed in, then one
**point functor** per target: the subcategory monomorphism ``{X} -> D`` stating one
further placement of ``X`` as an object of ``D`` (``specs/functor.md``, "Point categories
and point functors").  ``{X}`` has one hom category, so every functor out of it is
faithful.

The member and its identity keep the placements they already have; membership in the
punctual category is the exact identity statement owned by this construction.
"""

from __future__ import annotations

from reprlib import recursive_repr
from typing import TYPE_CHECKING

from sage_categories.cat.category import Category
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Decision, Unknown
from sage_categories.cat.predicates import Predicate, Proposition, predicate, register_handler

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = ["PointCategory", "PointMorphismCategory"]


point_object = predicate("point_object")
point_identity = predicate("point_identity")


def _point_object_by_identity(candidate: CategoryOfCategories.ElementType, category: Category) -> Decision:
    if not isinstance(category, PointCategory):
        return Unknown
    return candidate is category.member()


def _point_identity_by_identity(candidate: CategoryOfCategories.ElementType, category: Category) -> Decision:
    if not isinstance(category, PointCategory):
        return Unknown
    member = category.member()
    return candidate is category.morphism_category(1)(member, member).one()


register_handler(point_object, _point_object_by_identity)
register_handler(point_identity, _point_identity_by_identity)


class PointMorphismCategory(MorphismCategory[[], []]):
    """The one-object category whose sole object is ``1_X``."""

    # ``Mor({X})`` has one object, ``1_X``, and one morphism, its identity 2-morphism.
    class ObjectType:
        """The identity ``1_X``: the one morphism of ``{X}``."""

    class ElementType:
        """A generalized element of ``1_X``: its identity 2-morphism."""

    class MorphismType:
        """The identity 2-morphism of ``1_X``: the one morphism of ``Mor({X})``."""

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return point_identity(candidate, self._base)


class PointCategory(Category[[], []]):
    """The one-object category on one existing object ``X``."""

    class ObjectType:
        """The sole object ``X``: the value its established category already holds.

        The monomorphism into that category is identity on values, so ``{X}`` constructs
        no object.  It is where a declaration specific to ``X`` belongs (POL-CAT-083):
        ``{NN}`` owns what is true of the natural numbers and of no other set.
        """

    class ElementType:
        """A generalized element ``t: T -> X`` in ``{X}``: the identity, since ``1_X`` is the only morphism."""

    class MorphismType:
        """``1_X``, the sole morphism of ``{X}``: the identity ``X`` already has where it was placed."""

    def __init__(self, member: CategoryOfCategories.ElementType, targets: tuple[Category, ...]) -> None:
        self._member = member
        self._targets = targets
        # The placement ``X`` already has: the monomorphism into it is what makes ``{X}`` a
        # subcategory, so refining ``X`` into ``{X}`` never weakens its placement
        # (POL-CAT-074).
        self._established = member.category()
        super().__init__()

    def member(self) -> CategoryOfCategories.ElementType:
        """The sole object ``X``."""
        return self._member

    def targets(self) -> tuple[Category, ...]:
        """The categories this point category places ``X`` in through its point functors."""
        return self._targets

    def structure_functors(self) -> tuple[CategoryOfCategories.MorphismType, ...]:
        """The monomorphism into ``X``'s established category, then one point functor per target.

        Each is constructed through ``Fun``'s table of subcategory monomorphisms, so ``Fun({X}, D)`` and
        ``{X}.structure_functors()`` name one functor (POL-FUN-027).  ``{X}`` is not yet
        an object of ``Cat()`` while its own declaration runs, which is why the table is
        addressed directly rather than through ``Fun({X}, D).Monomorphisms().Isofibrations()()``.
        """
        functors = self.universe().morphism_category(1)
        return (
            functors.subcategory_monomorphism(self, self._established),
            *(functors.subcategory_monomorphism(self, target) for target in self._targets),
        )

    def morphism_category_type(self) -> type[PointMorphismCategory]:
        return PointMorphismCategory

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return point_object(candidate, self)

    def __call__(self) -> CategoryOfCategories.ElementType:
        """Return the sole object ``X``."""
        return self._member

    def construct_morphism(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        """Return ``1_X``, the sole morphism, for its unique endpoint pair."""
        assert domain is self._member and codomain is self._member
        return self._identity_morphism_(self._member)

    def construct_identity(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        """``1_X`` is the identity ``X`` already has in the category it was placed in."""
        assert member_object is self._member
        return self._established.morphism_category(1)(member_object, member_object).one()

    def _identity_morphism_(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        """``{X}`` places nothing: the unit of ``End_{X}(X)`` is the identity ``X`` already has."""
        return self.construct_identity(member_object)

    def composite(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        identity = self._identity_morphism_(self._member)
        assert first is identity and second is identity
        return identity

    def inverse_morphism(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        identity = self._identity_morphism_(self._member)
        assert morphism is identity
        return identity

    @recursive_repr("{...}")
    def __repr__(self) -> str:
        """``{X}``: the member between braces.

        ``Cat().Point(X)`` refines ``X`` into this category, so ``X`` presents itself
        through the placement it now has, and a member that names its placement names
        this category back.  The two presentations are each correct and the pair is
        cyclic, which is what ``reprlib.recursive_repr`` is for: CPython uses it wherever
        a value can contain itself (``reprlib``, and ``dataclasses`` and
        ``collections.OrderedDict`` on their own ``__repr__``; inspected 2026-08-29).
        Presentation only: no identity, equality, or order reads it (``AGENTS.md``).
        """
        return f"{{{self._member!r}}}"
