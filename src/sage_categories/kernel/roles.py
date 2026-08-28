"""The shared ``Cat().ElementType`` root and role-specific kernel classes.

Every owned runtime value has one role-specific path through these classes
(architecture contract §2, §3):

- ``ObjectOfCategory``: the base of every ``C.ObjectType``;
- ``ElementOfObject``: the base of every ordinary ``C.ElementType`` (a point
  ``1_C -> X``, represented by its defining morphism, POL-CAT-058);
- ``MorphismOfCategory``: the base of every ``C.MorphismType``.

``CategoryPoint`` is the stable end of the role MRO.  Each of the three kernel classes
stands on the class ``Cat()`` writes for its own element role, which
``install_cat_element_root`` fills in when ``Cat()`` compiles.  An object of ``C`` and a
morphism of ``C`` are both points ``* -> K`` of a category, at ``K = C`` and
``K = Mor(C)``; a ``C.ElementType`` value is a point of an object (``specs/functor.md``,
"Compiled implementation classes").

A leaf's local role class subclasses only the kernel base of its role
(POL-CAT-053).  ``Cat().ObjectType`` and ``Cat().ElementType`` own the universal
operators.  Their compiled roles supply those operators to descendants.
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
    "install_cat_element_root",
    "kernel_base",
    "role_of",
]


class Role(Enum):
    OBJECT = "ObjectType"
    ELEMENT = "ElementType"
    MORPHISM = "MorphismType"


class CategoryPoint:
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
        from sage_categories.kernel.construction import CategoryPointIdentity, ElementRoleIdentity

        match self._cat_element_identity:
            case ElementRoleIdentity(defining_morphism):
                return defining_morphism
            case CategoryPointIdentity(parent):
                return parent.point_functor(self)
        raise AssertionError(self._cat_element_identity)

    def parent(self) -> ObjectOfCategory:
        from sage_categories.kernel.construction import CategoryPointIdentity, ElementRoleIdentity

        match self._cat_element_identity:
            case ElementRoleIdentity(defining_morphism):
                return defining_morphism.codomain()
            case CategoryPointIdentity(parent):
                return parent
        raise AssertionError(self._cat_element_identity)

    def category(self) -> Category:
        """The slice category of a point ``1_C -> X`` of an object."""
        return self.parent().category().SliceOver(self.parent())

    def __eq__(self, candidate: Any) -> AppliedPredicate:
        return self.parent().category().equality()(self, candidate)

    def __ne__(self, candidate: Any) -> Proposition:
        return ~self.parent().category().equality()(self, candidate)

    def __hash__(self) -> int:
        return object.__hash__(self)


class ObjectOfCategory(CategoryPoint):
    """An object of a category: a point ``* -> C`` of it."""

    def __init__(self) -> None:
        self._initialize_placement()
        super().__init__()

    def _initialize_placement(self) -> None:
        """Read the object construction context, which is the one an object is built in.

        Each role reads its own context and no other, so an object never sees a morphism
        input and a morphism never sees an object input.
        """
        from sage_categories.kernel.construction import active_object_context

        context = active_object_context()
        assert context is not None and context.canonical_image is self, "object identity requires its active construction context"
        self._category = context.identity.category

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
    """The role-specific kernel class of a point ``1_C -> X`` of an object."""


class MorphismOfCategory(ObjectOfCategory):
    """A morphism ``f: A -> B`` of ``C``: an object of ``Mor(C)``, and so a point ``* -> Mor(C)``.

    ``Mor(n, C).ObjectType`` *is* ``Mor(n-1, C).MorphismType`` (``specs/functor.md``, "The
    ``Mor(n, C)`` tower"), so a morphism is an object and this class states that: the
    object surface applies to it at its own placement, ``Mor(C)``.  Its construction
    context is the morphism one, which carries the two endpoints the object context does
    not.
    """

    def _initialize_placement(self) -> None:
        from sage_categories.kernel.construction import active_morphism_context

        context = active_morphism_context()
        assert context is not None and context.canonical_image is self, "morphism identity requires its active construction context"
        identity = context.identity
        # ``category`` is the placement, a subcategory of ``Mor(C)``; ``C`` is its base.
        self._category = identity.category
        self._domain = identity.domain
        self._codomain = identity.codomain

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


def install_cat_element_root(root: type[CategoryPoint]) -> None:
    """Put the class ``Cat()`` writes for its element role below every role's kernel class.

    A leaf writes its own declaration over one of these three classes, so they are
    statements here and exist before any category does.  ``Cat().ElementType`` is the
    class ``Cat()`` writes and the first class the compiler compiles: this fills in the
    one link that makes every owned value a point ``* -> K`` of a category.

    ``MorphismOfCategory`` stands on ``ObjectOfCategory`` and reaches the root through it,
    so only the classes standing directly on ``CategoryPoint`` are rebased.
    """
    for base in _BASES.values():
        if base.__bases__ == (CategoryPoint,):
            base.__bases__ = (root,)


def role_of(candidate: Any) -> Role | None:
    """The implementation role of a candidate value, or ``None`` for an unowned candidate (POL-TYPE-004)."""
    match candidate:
        case MorphismOfCategory():
            return Role.MORPHISM
        case ObjectOfCategory():
            return Role.OBJECT
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
