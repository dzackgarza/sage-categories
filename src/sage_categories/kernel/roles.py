"""The kernel bases of the three implementation roles.

Every owned runtime value is an instance of exactly one of these bases
(architecture contract §2, §3):

- ``ObjectOfCategory``: the base of every ``C.ObjectType``;
- ``ElementOfObject``: the base of every ``C.ElementType`` (a generalized element
  ``t: T -> X``, represented by its defining morphism, POL-CAT-058);
- ``MorphismOfCategory``: the base of every ``C.MorphismType``.

All three refine ``CategoryPoint``, the role of ``Cat().ElementType``: a functor
``T -> C``.  An object is a stage-``1`` point of its category and a morphism a
stage-``[1]`` point (``specs/functor.md``, "Generalized elements").

A leaf's local role class subclasses only the kernel base of its role
(POL-CAT-053).  ``Cat().ObjectType`` and ``Cat().ElementType`` own the universal
operators.  Their compiled roles supply those operators to descendants.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, overload

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
    """A generalized element ``t: T -> X`` of ``X in C``, given by ``t``."""

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, defining_morphism: MorphismOfCategory) -> None: ...

    def __init__(self, defining_morphism: MorphismOfCategory | None = None) -> None:
        if defining_morphism is None:
            from sage_categories.kernel.construction import active_element_context

            context = active_element_context()
            assert context is not None and context.canonical_image is self, "element identity requires its active construction context"
            defining_morphism = context.identity.defining_morphism
        self._defining_morphism = defining_morphism

    def defining_morphism(self) -> MorphismOfCategory:
        return self._defining_morphism

    def stage(self) -> ObjectOfCategory:
        return self._defining_morphism.domain()

    def parent(self) -> ObjectOfCategory:
        return self._defining_morphism.codomain()

    def category(self) -> Category:
        """``C.SliceOver(X)``, the pullback of ``ev_1`` along ``X: 1 -> C`` (POL-CAT-058); the slice construction is not yet owned."""
        return self.parent().category().SliceOver(self.parent())

    def __eq__(self, candidate: Any) -> AppliedPredicate:
        return self.parent().category().equality()(self, candidate)

    def __ne__(self, candidate: Any) -> Proposition:
        return ~self.parent().category().equality()(self, candidate)

    def __hash__(self) -> int:
        return object.__hash__(self)


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
