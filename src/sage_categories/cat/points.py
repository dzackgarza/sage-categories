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

from sage_categories.cat.category import Category
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate, Proposition
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory

__all__ = ["PointCategory", "PointMorphismCategory"]


point_object = Predicate("point_object", 2, False)
point_identity = Predicate("point_identity", 2, False)


def _point_object_by_identity(candidate: CategoryPoint, category: Category) -> Decision:
    if not isinstance(category, PointCategory):
        return Unknown
    return candidate is category.member()


def _point_identity_by_identity(candidate: CategoryPoint, category: Category) -> Decision:
    if not isinstance(category, PointCategory):
        return Unknown
    return candidate is category.identity_morphism(category.member())


point_object.register_handler(_point_object_by_identity)
point_identity.register_handler(_point_identity_by_identity)


class PointMorphismCategory(MorphismCategory[[], []]):
    """The one-object category whose sole object is ``1_X``."""

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return point_identity(candidate, self._base)


class PointCategory(Category[[], []]):
    """The one-object category on one existing object ``X``."""

    class ObjectType(ObjectOfCategory):
        """The sole object ``X``: the value its established category already holds.

        The monomorphism into that category is identity on values, so ``{X}`` constructs
        no object.  It is where a declaration specific to ``X`` belongs (POL-CAT-083):
        ``{NN}`` owns what is true of the natural numbers and of no other set.
        """

    class ElementType(ElementOfObject):
        """A generalized element ``t: T -> X`` in ``{X}``: the identity, since ``1_X`` is the only morphism."""

    class MorphismType(MorphismOfCategory):
        """``1_X``, the sole morphism of ``{X}``: the identity ``X`` already has where it was placed."""

    def __init__(self, member: CategoryPoint, targets: tuple[Category, ...]) -> None:
        self._member = member
        self._targets = targets
        # The placement ``X`` already has: the monomorphism into it is what makes ``{X}`` a
        # subcategory, so refining ``X`` into ``{X}`` never weakens its placement
        # (POL-CAT-074).
        self._established = member.category()
        super().__init__()

    def member(self) -> CategoryPoint:
        """The sole object ``X``."""
        return self._member

    def targets(self) -> tuple[Category, ...]:
        """The categories this point category places ``X`` in through its point functors."""
        return self._targets

    def structure_functors(self) -> tuple[MorphismOfCategory, ...]:
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

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return point_object(candidate, self)

    def __call__(self) -> CategoryPoint:
        """Return the sole object ``X``."""
        return self._member

    def construct_morphism(self, domain: CategoryPoint, codomain: CategoryPoint) -> MorphismOfCategory:
        """Return ``1_X``, the sole morphism, for its unique endpoint pair."""
        assert domain is self._member and codomain is self._member
        return self.identity_morphism(self._member)

    def construct_identity(self, member_object: CategoryPoint) -> MorphismOfCategory:
        """``1_X`` is the identity ``X`` already has in the category it was placed in."""
        assert member_object is self._member
        return self._established.identity_morphism(member_object)

    def identity_morphism(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        """Return the existing identity of ``X``."""
        return self.construct_identity(member_object)

    def composite(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        identity = self.identity_morphism(self._member)
        assert first is identity and second is identity
        return identity

    def inverse_morphism(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        identity = self.identity_morphism(self._member)
        assert morphism is identity
        return identity

    def __repr__(self) -> str:
        return f"{{{self._member!r}}}"
