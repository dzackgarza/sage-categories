"""The parameterized one-object categories ``Cat().Point(X)`` (POL-CAT-083).

``Cat().Point(X)`` has the existing object ``X`` as its sole object and the
existing identity ``1_X`` as its sole morphism.  It follows Mathlib's punctual
category ``Discrete PUnit`` and ``Functor.fromPUnit``; the repository names the
chosen object in the category itself instead of in a constant functor
(``Mathlib/CategoryTheory/PUnit``, inspected 2026-08-27).

The object and identity keep their established category placements.  Membership
in the punctual category is therefore the exact identity statement owned by this
construction.
"""

from __future__ import annotations

from sage_categories.cat.category import Category
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.compiler import empty_local_role
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate, Proposition
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, Role

__all__ = ["PointCategory", "PointMorphismCategory"]


point_object = Predicate("point_object", 2, False)
point_identity = Predicate("point_identity", 2, False)


def _point_object_by_identity(candidate: CategoryPoint, category: Category) -> Decision:
    if not isinstance(category, PointCategory):
        return Unknown
    return candidate is category.distinguished_object()


def _point_identity_by_identity(candidate: CategoryPoint, category: Category) -> Decision:
    if not isinstance(category, PointCategory):
        return Unknown
    return candidate is category.identity_morphism(category.distinguished_object())


point_object.register_handler(_point_object_by_identity)
point_identity.register_handler(_point_identity_by_identity)


class PointMorphismCategory(MorphismCategory[[], []]):
    """The one-object category whose sole object is ``1_X``."""

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return point_identity(candidate, self._base)


class PointCategory(Category[[], []]):
    """The one-object category on one existing object ``X``."""

    def __init__(self, distinguished_object: CategoryPoint) -> None:
        self._distinguished_object = distinguished_object
        super().__init__()

    def distinguished_object(self) -> CategoryPoint:
        """The sole object ``X``."""
        return self._distinguished_object

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        return empty_local_role(self, role)

    def morphism_category_type(self) -> type[PointMorphismCategory]:
        return PointMorphismCategory

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return point_object(candidate, self)

    def __call__(self) -> CategoryPoint:
        """Return the sole object ``X``."""
        return self._distinguished_object

    def construct_morphism(self, domain: CategoryPoint, codomain: CategoryPoint) -> MorphismOfCategory:
        """Return ``1_X``, the sole morphism, for its unique endpoint pair."""
        assert domain is self._distinguished_object and codomain is self._distinguished_object
        return self.identity_morphism(self._distinguished_object)

    def construct_identity(self, member_object: CategoryPoint) -> MorphismOfCategory:
        assert member_object is self._distinguished_object
        return member_object.category().identity_morphism(member_object)

    def identity_morphism(self, member_object: CategoryPoint) -> MorphismOfCategory:
        """Return the existing identity of ``X``."""
        return self.construct_identity(member_object)

    def composite(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        identity = self.identity_morphism(self._distinguished_object)
        assert first is identity and second is identity
        return identity

    def inverse_morphism(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        identity = self.identity_morphism(self._distinguished_object)
        assert morphism is identity
        return identity

    def __repr__(self) -> str:
        return f"{{{self._distinguished_object!r}}}"
