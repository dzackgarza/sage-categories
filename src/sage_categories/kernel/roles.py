"""The shared ``Cat().ElementType`` root and role-specific kernel classes.

Every owned runtime value is an instance of exactly one of these bases
(architecture contract §2, §3):

- ``ObjectOfCategory``: the base of every ``C.ObjectType``;
- ``ElementOfObject``: the base of every ``C.ElementType`` (a generalized element
  ``t: T -> X``, represented by its defining morphism, POL-CAT-058);
- ``MorphismOfCategory``: the base of every ``C.MorphismType``.

``CategoryPointKernel`` is the stable end of the role MRO.  The module preallocates
the compiled ``Cat().ElementType`` class over it.  The object, ordinary-element, and
morphism kernel classes then refine that one class at their stated stages
(``specs/functor.md``, "Generalized elements").

A leaf's local role class subclasses only the kernel base of its role
(POL-CAT-053).  ``Cat().ObjectType`` and ``Cat().ElementType`` own the universal
operators.  Their compiled roles supply those operators to descendants.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, overload

from sage.structure.dynamic_class import dynamic_class

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.kernel.predicates import AppliedPredicate, Proposition

__all__ = [
    "CategoryPoint",
    "CategoryPointKernel",
    "ElementOfObject",
    "MorphismOfCategory",
    "ObjectOfCategory",
    "Role",
    "category_of",
    "cat_element_root",
    "kernel_base",
    "role_of",
]


class Role(Enum):
    OBJECT = "ObjectType"
    ELEMENT = "ElementType"
    MORPHISM = "MorphismType"


class CategoryPointKernel:
    """The stable Python end of the compiled ``Cat().ElementType`` role."""

    def __init__(self) -> None:
        from sage_categories.kernel.construction import active_construction_context

        context = active_construction_context(self)
        assert context is not None and context.canonical_image is self, (
            "a category point requires its active construction context"
        )
        self._cat_element_identity = context.cat_element_identity
        super().__init__()

    def defining_morphism(self) -> MorphismOfCategory:
        from sage_categories.kernel.construction import (
            ArrowStageIdentity,
            GeneralCategoryPointIdentity,
            ObjectStageIdentity,
        )

        match self._cat_element_identity:
            case GeneralCategoryPointIdentity(defining_morphism):
                return defining_morphism
            case ObjectStageIdentity(parent):
                return parent.point_functor(self)
            case ArrowStageIdentity(parent, _, _):
                return parent.arrow_functor(self)
        raise AssertionError(self._cat_element_identity)

    def stage(self) -> ObjectOfCategory:
        from sage_categories.cat.category import Cat
        from sage_categories.kernel.construction import (
            ArrowStageIdentity,
            GeneralCategoryPointIdentity,
            ObjectStageIdentity,
        )

        match self._cat_element_identity:
            case GeneralCategoryPointIdentity(defining_morphism):
                return defining_morphism.domain()
            case ObjectStageIdentity():
                return Cat().Terminal()
            case ArrowStageIdentity():
                return Cat().Simplex(1)
        raise AssertionError(self._cat_element_identity)

    def parent(self) -> ObjectOfCategory:
        from sage_categories.kernel.construction import (
            ArrowStageIdentity,
            GeneralCategoryPointIdentity,
            ObjectStageIdentity,
        )

        match self._cat_element_identity:
            case GeneralCategoryPointIdentity(defining_morphism):
                return defining_morphism.codomain()
            case ObjectStageIdentity(parent) | ArrowStageIdentity(parent, _, _):
                return parent
        raise AssertionError(self._cat_element_identity)

    def category(self) -> Category:
        """The slice category of an ordinary generalized element."""
        return self.parent().category().SliceOver(self.parent())

    def __eq__(self, candidate: Any) -> AppliedPredicate:
        return self.parent().category().equality()(self, candidate)

    def __ne__(self, candidate: Any) -> Proposition:
        return ~self.parent().category().equality()(self, candidate)

    def __hash__(self) -> int:
        return object.__hash__(self)


_CAT_ELEMENT_ROOT = dynamic_class("Cat.ElementType", (CategoryPointKernel,), cache=False)
CategoryPoint = _CAT_ELEMENT_ROOT


def cat_element_root() -> type[CategoryPoint]:
    """The preallocated compiled ``Cat().ElementType`` class."""
    return _CAT_ELEMENT_ROOT


class ObjectOfCategory(CategoryPoint):
    """An object of a category: a stage-``1`` point of it."""

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, category: Category) -> None: ...

    def __init__(self, category: Category | None = None) -> None:
        if category is None:
            from sage_categories.kernel.construction import active_object_context

            context = active_object_context()
            assert context is not None and context.canonical_image is self, "object identity requires its active construction context"
            category = context.identity.category
        self._category = category
        super().__init__()

    def category(self) -> Category:
        """The strongest category placement established for this object."""
        return self._category

    def identity(self) -> MorphismOfCategory:
        return self._category.identity_morphism(self)

    # The fibers over and under this object of the four morphism-property families,
    # constructed by the category's slice constructions (POL-FUN-029, POL-CAT-026).

    def subobjects(self) -> Category:
        """``C.Subobjects()(X)``: the monomorphisms into ``X`` as objects of ``C.SliceOver(X)``."""
        return self._category.Subobjects()(self)

    def superobjects(self) -> Category:
        """``C.Superobjects()(X)``: the monomorphisms out of ``X`` as objects of ``C.CosliceUnder(X)``."""
        return self._category.Superobjects()(self)

    def covering_objects(self) -> Category:
        """``C.CoveringObjects()(X)``: the pairs ``(Y, p: Y -> X)`` with ``p`` an epimorphism."""
        return self._category.CoveringObjects()(self)

    def covered_objects(self) -> Category:
        """``C.CoveredObjects()(X)``: the pairs ``(Y, p: X -> Y)`` with ``p`` an epimorphism."""
        return self._category.CoveredObjects()(self)

    def __eq__(self, candidate: Any) -> AppliedPredicate:
        return self._category.equality()(self, candidate)

    def __ne__(self, candidate: Any) -> Proposition:
        return ~self._category.equality()(self, candidate)

    def __hash__(self) -> int:
        return object.__hash__(self)


class ElementOfObject(CategoryPoint):
    """The role-specific kernel class of an ordinary generalized element."""


class MorphismOfCategory(CategoryPoint):
    """A morphism ``f: A -> B`` of ``C``: an object of ``Mor(C)``, a stage-``[1]`` point of ``C``."""

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, category: Category, domain: ObjectOfCategory, codomain: ObjectOfCategory) -> None: ...

    def __init__(
        self,
        category: Category | None = None,
        domain: ObjectOfCategory | None = None,
        codomain: ObjectOfCategory | None = None,
    ) -> None:
        if category is None and domain is None and codomain is None:
            from sage_categories.kernel.construction import active_morphism_context

            context = active_morphism_context()
            assert context is not None and context.canonical_image is self, "morphism identity requires its active construction context"
            identity = context.identity
            category, domain, codomain = identity.category, identity.domain, identity.codomain
        assert category is not None and domain is not None and codomain is not None, "supply all morphism identity fields or use the active construction context"
        # ``category`` is the placement, a subcategory of ``Mor(C)``; ``C`` is its base.
        self._category = category
        self._domain = domain
        self._codomain = codomain
        super().__init__()

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

    def __mul__(self, first: MorphismOfCategory) -> MorphismOfCategory:
        """``self * first`` is ``self`` after ``first``: composition owned by ``C``.

        ``*`` on a morphism is composition and nothing else: no operator carries two
        meanings on one role (POL-CAT-088).  The product of two morphisms is the
        product of two objects of ``Mor(C)`` and is constructed by naming that
        category: ``Mor(C).Products()((f, g))``.  It has no operator.
        """
        return self.base_category().compose_morphisms(self, first)

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


def role_of(candidate: Any) -> Role | None:
    """The implementation role of a candidate value, or ``None`` for an unowned candidate (POL-TYPE-004)."""
    match candidate:
        case ObjectOfCategory():
            return Role.OBJECT
        case MorphismOfCategory():
            return Role.MORPHISM
        case CategoryPoint():
            return Role.ELEMENT
    return None


def category_of(value: CategoryPoint, role: Role) -> Category:
    """The placement category of ``value`` in its role."""
    match role:
        case Role.OBJECT | Role.MORPHISM:
            return value.category()
        case Role.ELEMENT:
            return value.parent().category()
    raise AssertionError(role)
