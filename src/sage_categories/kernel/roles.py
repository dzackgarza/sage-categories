"""The kernel bases of the three implementation roles.

Every owned runtime value is an instance of exactly one of these bases
(architecture contract §2, §3):

- ``ObjectOfCategory``: the base of every ``C.ObjectType``;
- ``ElementOfObject``: the base of every ``C.ElementType`` (a generalized element
  ``t: T -> X``, represented by its defining morphism, D06);
- ``MorphismOfCategory``: the base of every ``C.MorphismType``.

All three refine ``CategoryPoint``, the role of ``Cat().ElementType``: a functor
``T -> C``.  An object is a stage-``1`` point of its category and a morphism a
stage-``[1]`` point (D06 role pin).

A leaf's local role class subclasses only the kernel base of its role
(POL-CAT-053).  The universal operations that every value receives from its
category live here and delegate to category-owned operations; the kernel never
decides mathematics.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.kernel.predicates import AppliedPredicate, Proposition

__all__ = [
    "CategoryPoint",
    "ElementOfObject",
    "MorphismOfCategory",
    "ObjectOfCategory",
    "Role",
    "category_of",
    "kernel_base",
    "role_of",
]


class Role(Enum):
    OBJECT = "ObjectType"
    ELEMENT = "ElementType"
    MORPHISM = "MorphismType"


class CategoryPoint:
    """A generalized element ``T -> C`` of a category; ``Cat().ElementType``'s base.

    Each role supplies ``stage()``, ``parent()``, and ``defining_morphism()``.
    """


class ObjectOfCategory(CategoryPoint):
    """An object of a category: a stage-``1`` point of it."""

    def __init__(self, category: Category) -> None:
        self._category = category

    def category(self) -> Category:
        """The strongest category placement established for this object."""
        return self._category

    def stage(self) -> ObjectOfCategory:
        return self._category.category().Terminal()

    def parent(self) -> Category:
        return self._category

    def defining_morphism(self) -> MorphismOfCategory:
        return self._category.point_functor(self)

    def identity(self) -> MorphismOfCategory:
        return self._category.identity_morphism(self)

    def __eq__(self, candidate: Any) -> AppliedPredicate:
        return self._category.equality()(self, candidate)

    def __ne__(self, candidate: Any) -> Proposition:
        return ~self._category.equality()(self, candidate)

    def __hash__(self) -> int:
        return object.__hash__(self)


class ElementOfObject(CategoryPoint):
    """A generalized element ``t: T -> X`` of ``X in C``, given by ``t``."""

    def __init__(self, defining_morphism: MorphismOfCategory) -> None:
        self._defining_morphism = defining_morphism

    def defining_morphism(self) -> MorphismOfCategory:
        return self._defining_morphism

    def stage(self) -> ObjectOfCategory:
        return self._defining_morphism.domain()

    def parent(self) -> ObjectOfCategory:
        return self._defining_morphism.codomain()

    def category(self) -> Category:
        """``C.SliceOver(X)``; constructed by the slice unit of the register (D06, step 7)."""
        return self.parent().category().SliceOver(self.parent())

    def __eq__(self, candidate: Any) -> AppliedPredicate:
        return self.parent().category().equality()(self, candidate)

    def __ne__(self, candidate: Any) -> Proposition:
        return ~self.parent().category().equality()(self, candidate)

    def __hash__(self) -> int:
        return object.__hash__(self)


class MorphismOfCategory(CategoryPoint):
    """A morphism ``f: A -> B`` of ``C``: an object of ``Mor(C)``, a stage-``[1]`` point of ``C``."""

    def __init__(self, category: Category, domain: ObjectOfCategory, codomain: ObjectOfCategory) -> None:
        # ``category`` is the placement, a subcategory of ``Mor(C)``; ``C`` is its base.
        self._category = category
        self._domain = domain
        self._codomain = codomain

    def category(self) -> Category:
        """The strongest placement established for this morphism as an object of ``Mor(C)``."""
        return self._category

    def base_category(self) -> Category:
        """The category ``C`` whose morphism this is."""
        return self._category.base_category()

    def domain(self) -> ObjectOfCategory:
        return self._domain

    def codomain(self) -> ObjectOfCategory:
        return self._codomain

    def stage(self) -> ObjectOfCategory:
        return self.base_category().category().Simplex(1)

    def parent(self) -> Category:
        return self.base_category()

    def defining_morphism(self) -> MorphismOfCategory:
        return self.base_category().arrow_functor(self)

    def __mul__(self, first: MorphismOfCategory) -> MorphismOfCategory:
        """``self * first`` is ``self`` after ``first``: composition owned by ``C``."""
        return self.base_category().composite(self, first)

    def is_monomorphism(self) -> AppliedPredicate:
        return self.base_category().morphism_category(1).Monomorphisms().predicate()(self)

    def is_epimorphism(self) -> AppliedPredicate:
        return self.base_category().morphism_category(1).Epimorphisms().predicate()(self)

    def is_isomorphism(self) -> AppliedPredicate:
        return self.base_category().morphism_category(1).Isomorphisms().predicate()(self)

    def is_endomorphism(self) -> AppliedPredicate:
        return self.base_category().morphism_category(1).Endomorphisms().predicate()(self)

    def __eq__(self, candidate: Any) -> AppliedPredicate:
        return self.base_category().equality()(self, candidate)

    def __ne__(self, candidate: Any) -> Proposition:
        return ~self.base_category().equality()(self, candidate)

    def __hash__(self) -> int:
        return object.__hash__(self)


_BASES: dict[Role, type[CategoryPoint]] = {
    Role.OBJECT: ObjectOfCategory,
    Role.ELEMENT: ElementOfObject,
    Role.MORPHISM: MorphismOfCategory,
}


def kernel_base(role: Role) -> type[CategoryPoint]:
    return _BASES[role]


def role_of(value: Any) -> Role | None:
    """The implementation role of a runtime value, or ``None`` for an unowned value."""
    match value:
        case ObjectOfCategory():
            return Role.OBJECT
        case ElementOfObject():
            return Role.ELEMENT
        case MorphismOfCategory():
            return Role.MORPHISM
    return None


def category_of(value: CategoryPoint, role: Role) -> Category:
    """The placement category of ``value`` in its role."""
    match role:
        case Role.OBJECT | Role.MORPHISM:
            return value.category()
        case Role.ELEMENT:
            return value.parent().category()
    raise AssertionError(role)
