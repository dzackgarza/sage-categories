"""Define the private kernel bases for objects, elements, and morphisms."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from enum import Enum
from typing import TYPE_CHECKING, Generic

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.cat.functors import Functor
    from sage_categories.kernel.functor_cache import FunctorImageCache

__all__ = [
    "CategoryPoint",
    "ElementOfObject",
    "MorphismOfCategory",
    "ObjectOfCategory",
    "Role",
    "RoleCandidate",
    "building_role_classes",
    "category_of",
    "install_cat_element_root",
    "kernel_base",
    "prepare_category_subclass",
    "role_of",
]


class Role(Enum):
    OBJECT = "ObjectType"
    ELEMENT = "ElementType"
    MORPHISM = "MorphismType"


_building_role_class = False
_category_declaration_root: type[CategoryPoint] | None = None
_category_universal_class: type[CategoryPoint] | None = None


@contextmanager
def building_role_classes() -> Iterator[None]:
    """Mark a class as kernel-built while Sage constructs one role class.

    A compiled role class derives from the category declaration that supplies its
    methods.  Python therefore calls that declaration's ``__init_subclass__`` even
    though the compiled class states no new category and declares no roles.
    """
    global _building_role_class
    previous, _building_role_class = _building_role_class, True
    try:
        yield
    finally:
        _building_role_class = previous


class CategoryPoint:
    """The stable Python end of the compiled ``Cat().ElementType`` role."""

    def _is_element(self) -> bool:
        return role_of(self) is Role.ELEMENT

    def _is_morphism(self) -> bool:
        return role_of(self) is Role.MORPHISM

    def _is_object(self) -> bool:
        return role_of(self) is Role.OBJECT

    def _initialize_identity(self) -> None:
        """Read the point identity from the active construction context; the kernel calls this first."""
        from sage_categories.kernel.construction import active_construction_context

        context = active_construction_context(self)
        assert context is not None and context.canonical_image is self, (
            "a category point requires its active construction context"
        )
        self._cat_element_identity = context.cat_element_identity

    def __hash__(self) -> int:
        return object.__hash__(self)


def _install_category_initializer(category_class: type[CategoryPoint]) -> None:
    """Run a category class's own initializer, then the kernel's, with no base call.

    A category class stores its parameters and nothing else (``POL-LEAF-063``); the
    initialization that follows is the kernel's to run, so the class calls no base
    initializer (D13, D110).  A class that writes no initializer reaches the root
    initializer directly and needs no wrapper.

    A chained declaration in ``Cat`` stores its own parameters before it delegates, so
    the root initializer runs once, for the class the value actually names; an inner
    wrapper reached through that chain leaves it to the outer one.
    """
    written = vars(category_class).get("__init__")
    if written is None or getattr(written, "_runs_the_kernel_initializer", False):
        return

    def kernel_initializer(self: CategoryPoint, *arguments: object, **keywords: object) -> None:
        written(self, *arguments, **keywords)
        if type(self).__init__ is kernel_initializer:
            from sage_categories.kernel.compiler import construct_category_value

            construct_category_value(self)

    kernel_initializer._runs_the_kernel_initializer = True
    category_class.__init__ = kernel_initializer


def prepare_category_subclass(cls: type[CategoryPoint]) -> None:
    """Install the kernel's initializer on a newly written category class.

    A declaration calls no base initializer and no base hook (D110), so the theory's
    ``__init_subclass__`` names this instead of reaching a base through ``super()``.
    The compiler copies a written hook onto the class it compiles, so a class written
    over the declaration and one written over its compiled class both arrive here.
    """
    if _building_role_class:
        return
    _install_category_initializer(cls)


class ObjectOfCategory(CategoryPoint):
    """An object of a category: a point ``* -> C`` of it."""

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if (
            not _building_role_class
            and _category_declaration_root is not None
            and issubclass(cls, _category_declaration_root)
        ):
            _require_declarations(cls, _category_universal_class)

    def _compile_category(self: Category, functors: tuple[Functor, ...]) -> None:
        from sage_categories.kernel.compiler import compile_category

        compile_category(self, functors)

    def _recompile_category(self: Category, functors: tuple[Functor, ...]) -> None:
        from sage_categories.kernel.compiler import recompile_category

        recompile_category(self, functors)

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        """Return the declaration written for one role of this category."""
        return vars(_written_class(type(self)))[role.value]

    def role_class(self, role: Role) -> type[CategoryPoint]:
        """Return the compiled class installed for one role of this category."""
        return getattr(self, role.value)

    def role_source(self: Category, role: Role) -> tuple[Category, Role]:
        """Return the category and role that own this role node."""
        return self, role

    def _object_role_source(self: Category) -> tuple[Category, bool]:
        source, role = self.role_source(Role.OBJECT)
        return source, role is Role.MORPHISM

    def _initialize_placement(self) -> None:
        """Read the object construction context, which is the one an object is built in.

        Each role reads its own context and no other, so an object never sees a morphism
        input and a morphism never sees an object input.
        """
        from sage_categories.kernel.construction import active_object_context

        context = active_object_context()
        assert context is not None and context.canonical_image is self, "object identity requires its active construction context"
        self._category = context.identity.category


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

    _image_cache: FunctorImageCache

    def _initialize_functor_image_cache(self) -> None:
        from sage_categories.kernel.functor_cache import FunctorImageCache

        self._image_cache = FunctorImageCache()

    def _cached_object_image(
        self,
        source: ObjectOfCategory,
        construct: Callable[[ObjectOfCategory], ObjectOfCategory],
    ) -> ObjectOfCategory:
        return self._image_cache.object_image(source, construct)

    def _cached_morphism_image(
        self,
        source: MorphismOfCategory,
        on_object: Callable[[ObjectOfCategory], ObjectOfCategory],
        construct: Callable[[MorphismOfCategory], MorphismOfCategory],
    ) -> MorphismOfCategory:
        return self._image_cache.morphism_image(source, on_object, construct)

    def _initialize_placement(self) -> None:
        from sage_categories.kernel.construction import active_morphism_context

        context = active_morphism_context()
        assert context is not None and context.canonical_image is self, "morphism identity requires its active construction context"
        identity = context.identity
        # ``category`` is the placement, a subcategory of ``Mor(C)``; ``C`` is its base.
        self._category = identity.category
        self._domain = identity.domain
        self._codomain = identity.codomain


_BASES: dict[Role, type[CategoryPoint]] = {
    Role.OBJECT: ObjectOfCategory,
    Role.ELEMENT: ElementOfObject,
    Role.MORPHISM: MorphismOfCategory,
}

# A declaration can stand on one kernel role base or directly on ``object``.  Any
# other base carries another category's written mathematics onto this role node.
_DECLARATION_BASES = frozenset({*_BASES.values(), CategoryPoint, Generic, object})

# One category owns a declaration at one role.  The same declaration can also name
# the level identity ``Mor(K).ObjectType = K.MorphismType`` at a different role.
_declaration_owners: dict[type[CategoryPoint], tuple[type[CategoryPoint], Role]] = {}


def _written_class(runtime_class: type[CategoryPoint]) -> type[CategoryPoint]:
    """Return the category class that writes all three local role declarations."""
    return next(
        found
        for found in runtime_class.__mro__
        if all(role.value in vars(found) for role in Role)
    )


def _borrowed_declaration(local: type[CategoryPoint]) -> type[CategoryPoint] | None:
    """Return the category declaration inherited by ``local``, if one exists."""
    for base in local.__mro__[1:]:
        if base in _DECLARATION_BASES:
            return None
        return base
    return None


def _require_declarations(
    category_class: type[CategoryPoint],
    universal_class: type[CategoryPoint] | None,
) -> None:
    """Require one local declaration for each category role (POL-CAT-053/057).

    A category must state all three roles in its own class body.  An inherited
    declaration, ``Cat()``'s universal declaration, or another category's
    declaration states no local mathematics.  An empty local class is the exact
    declaration when the category adds no operation at that role.

    This check uses class and role identity.  A renamed declaration remains the
    same declaration, while a namesake elsewhere remains distinct.  The role stays
    part of the key because one class can state the categorical level identity
    ``Mor(K).ObjectType = K.MorphismType``.
    """
    missing = [role.value for role in Role if role.value not in vars(category_class)]
    assert not missing, (
        f"{category_class.__name__} writes no {' or '.join(missing)} declaration.  Every category class writes all three "
        "in its own body, and where it adds no new mathematics the class it writes has an empty body "
        "(POL-CAT-057)"
    )
    for role in Role:
        declared = vars(category_class)[role.value]
        inherited = next(
            (base for base in category_class.__mro__[1:] if vars(base).get(role.value) is declared),
            None,
        )
        assert inherited is None, (
            f"{category_class.__name__}.{role.value} names {inherited.__name__}'s {role.value} declaration, which this class "
            f"inherits and which therefore states nothing about this category.  Write this category's own class; "
            "where it adds no new mathematics its body is empty (POL-CAT-057)"
        )
        universal = None if universal_class is None or category_class is universal_class else vars(universal_class)[role.value]
        assert declared is not universal, (
            f"{category_class.__name__}.{role.value} names ``Cat()``'s {role.value} declaration, which every category class "
            "inherits and which therefore states nothing about this one.  Write this category's own class; where "
            "it adds no new mathematics its body is empty (POL-CAT-057)"
        )
        owner = _declaration_owners.get(declared)
        assert owner is None or owner[1] is not role, (
            f"{category_class.__name__}.{role.value} names the {role.value} declaration of {owner[0].__name__}, whose "
            f"mathematics it would state instead of its own.  Write this category's own class; where it adds no "
            "new mathematics its body is empty (POL-CAT-053, POL-CAT-057)"
        )
        borrowed = _borrowed_declaration(declared)
        assert borrowed is None, (
            f"{category_class.__name__}.{role.value} derives from {borrowed.__qualname__}, so it carries that category's "
            "body onto this one.  A declaration stands on its role's kernel class alone; the implementation "
            "bases come from the selected structure functors (POL-CAT-053, POL-CAT-057)"
        )
    for role in Role:
        declared = vars(category_class)[role.value]
        if declared not in _BASES.values() and declared is not CategoryPoint:
            _declaration_owners.setdefault(declared, (category_class, role))


def install_category_declaration_root(
    declaration_root: type[CategoryPoint],
    universal_class: type[CategoryPoint],
) -> None:
    """Install the written ``Cat().ObjectType`` as the root of category declarations."""
    global _category_declaration_root, _category_universal_class
    assert _category_declaration_root is None or _category_declaration_root is declaration_root
    assert _category_universal_class is None or _category_universal_class is universal_class
    _category_declaration_root = declaration_root
    _category_universal_class = universal_class
    _require_declarations(universal_class, universal_class)


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


type RoleCandidate = CategoryPoint | int


def role_of(candidate: RoleCandidate) -> Role | None:
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
