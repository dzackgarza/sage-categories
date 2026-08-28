"""Full subcategories and property subcategories (POL-CAT-054, POL-CAT-087, POL-FUN-024).

A full subcategory ``S`` of ``T`` shares ``T``'s object, element, and morphism
values; its morphism categories, identities, and composition are inherited
definitionally from ``T`` (Mathlib ``CategoryTheory.ObjectProperty.FullSubcategory``
and the functor ``ObjectProperty.ι`` it carries, full and faithful; inspected
2026-08-26).  Its one selected structural functor is the identity-on-values
monomorphism ``Fun(S, T).Monomorphisms().Isofibrations().Full()()``.

A property subcategory ``C.P()`` is the full subcategory on the objects satisfying
a predicate ``P``.  ``C`` declares it once, as an ``Axiom`` in the body of its class,
and a separate class implements the generated subcategory by naming the declaring
category class and the axiom (POL-LEAF-059).  Its constructor is the trusted boundary of that property
(POL-CAT-038/069): calling it on a value of ``C`` refines the same value in place.
``C.P()`` is a full subcategory of ``C.Q()`` whenever the mathematics says so, and that
containment is the statement: it is recorded as the subcategory monomorphism
``C.P() -> C.Q()``, and nothing induces it from a relation between the two predicates
(D83).  ``Mor(C).Isomorphisms()`` is a full subcategory of ``Mor(C).Monomorphisms()`` and
of ``Mor(C).Epimorphisms()`` at once
(``specs/functor.md``, "Monomorphisms of ``Cat()`` and placement").  A descendant ``D`` with a selected
subcategory monomorphism into ``C`` derives ``D.P()`` as the narrowing of ``C.P()`` to ``D``
(POL-CAT-084): a full subcategory of both, with the same predicate.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from types import ModuleType
from typing import TYPE_CHECKING, ClassVar

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category
from sage_categories.kernel.predicates import AppliedPredicate, PropertyPredicate, Proposition
from sage_categories.kernel.refinement import is_subcategory, refine
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor, FunctorsCategory

__all__ = [
    "Axiom",
    "FixedEndpointProperty",
    "FullSubcategory",
    "NarrowedProperty",
    "PropertySubcategory",
]


def _functors() -> FunctorsCategory:
    from sage_categories.cat.functors import Fun

    return Fun


def _morphisms() -> ModuleType:
    from sage_categories.cat import morphisms

    return morphisms


class FullSubcategory[**MorphismData, **TwoMorphismData](Category[MorphismData, TwoMorphismData]):
    """A full subcategory of an ambient category, declared by its monomorphism into the ambient.

    Its morphisms, identities, and composites are those of the ambient between its
    objects; ``Category`` supplies them from the ambient (POL-CAT-087).

    Every full subcategory of ``C`` is a root of the narrowings of ``C``: two of
    them, a property subcategory and a construction family (a chosen subset that
    is a chosen limit; a finite set that is a chosen product), meet in the
    narrowing of ``C`` by both (POL-CAT-084, POL-KERNEL-013).  Membership in a
    construction family is placement by construction; only a property
    subcategory owns a predicate.
    """

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData]) -> None:
        self._ambient = ambient
        super().__init__()

    def has_ambient(self) -> bool:
        return True

    def ambient(self) -> Category[MorphismData, TwoMorphismData]:
        """The ambient is construction data: this category declares exactly one subcategory monomorphism."""
        return self._ambient

    def narrowing_base(self) -> Category:
        return self._ambient.narrowing_base()

    def narrowing_roots(self) -> tuple[Category, ...]:
        return (*self._ambient.narrowing_roots(), self)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (_functors().full_subcategory_monomorphism(self, self._ambient),)

    def separating_family(self) -> tuple[CategoryPoint, ...]:
        """The separators of the ambient that are objects of this subcategory: a subcategory monomorphism supplies none of its own."""
        return tuple(separator for separator in self._ambient.separating_family() if separator in self)

    def element_from_defining_morphism(self, defining_morphism: MorphismOfCategory) -> CategoryPoint:
        """The elements of a full subcategory are those of its ambient on the shared values (POL-CAT-087)."""
        return self._ambient.element_from_defining_morphism(defining_morphism)


class Axiom:
    """A property axiom, declared once in the body of a category class (D77.4, POL-LEAF-059).

    ``Finite = Axiom()`` in the body of ``SetsCategory`` gives every value of that class
    the accessor ``Finite()``, whose value is the property subcategory ``Sets().Finite()``.
    A category ``D`` declared as a subcategory of ``C`` derives ``D.Finite()`` from that
    one declaration, as the narrowing of ``D`` by ``C.Finite()``; it states no class,
    predicate, constructor, or transport of its own (POL-CAT-084).

    ``full_subcategory_of`` lists the categories ``C.P()`` is a full subcategory of beyond
    its ambient, by their axioms; each is recorded on the constructed subcategory as the
    monomorphism ``C.P() -> C.Q()`` (D83).

    A separate class implements the generated subcategory by naming the declaring
    category class and the axiom in ``_base_category_class_and_axiom``, exactly as Sage
    links ``FiniteSets`` back to ``(Sets, 'Finite')``
    (``sage/categories/category_with_axiom.py`` lines 213-242 and 1886-1953, inspected
    2026-08-29).  In Sage the implementation then *is* the attribute on the base category
    class, ``Groups.Finite``; here that attribute is this declaration, so the declaration
    holds the link and no table records it.

    Sage also deduces the link from the class name when the class sits in the standard
    module location (``base_category_class_and_axiom``, same file, line 1717).  This
    kernel does not: ``specs/undecidable-properties.md`` requires the property class to
    state its mathematics and forbids inferring it from the strings ``"Finite"`` or
    ``"is_finite"`` by name matching, so the link is always the field.
    """

    def __init__(self, full_subcategory_of: tuple[Axiom, ...] = ()) -> None:
        self._full_subcategory_of = full_subcategory_of
        self._implementation: type[PropertySubcategory] = PropertySubcategory
        self._constructed: MonoDict = MonoDict()

    def __set_name__(self, declaring_class: type[Category], name: str) -> None:
        self._declaring_class = declaring_class
        self._name = name

    def __get__(self, category: Category | None, owner: type[Category]) -> Axiom | Callable[[], Category]:
        """``C.P`` on a category value is its accessor; on the class it is the declaration."""
        if category is None:
            return self
        return partial(self.subcategory, category)

    def name(self) -> str:
        return self._name

    def implemented_by(self, implementation: type[PropertySubcategory]) -> None:
        """Record the class that implements this axiom's subcategory; one axiom has one."""
        assert self._implementation is PropertySubcategory or self._implementation is implementation, (
            f"{self!r} is already implemented by {self._implementation.__name__}, not {implementation.__name__}"
        )
        self._implementation = implementation

    def subcategory(self, category: Category) -> Category:
        """``category.P()``: one property subcategory per category value."""
        if category not in self._constructed:
            self._constructed[category] = self._construct(category)
        return self._constructed[category]

    def _construct(self, category: Category) -> Category:
        """The narrowing of a declared subcategory, else the implementation of this axiom."""
        if category.has_ambient():
            return category.property_subcategory(self._declared_on(category.ambient()))
        containing = tuple(axiom._declared_on(category) for axiom in self._full_subcategory_of)
        return self._implementation(category, self._name, containing)

    def _declared_on(self, category: Category) -> Category:
        """``category.P()``, through the accessor that category declares for this axiom.

        A category can build the subcategory itself -- ``Fun`` builds its property
        categories eagerly, before any of them can be constructed on demand -- and that
        declaration is then the one owner of ``C.P()``.  The axiom name is the name the
        category writes, exactly as a role is (``Category.local_role_class``,
        POL-KERNEL-028), so this reads the declaration rather than probing for it.
        """
        return getattr(category, self._name)()

    def __repr__(self) -> str:
        return f"{self._declaring_class.__name__}.{self._name}"


class PropertySubcategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):
    """``C.P()``: the full subcategory of ``C`` on the objects satisfying ``P``.

    A subclass implements one generated property subcategory by naming the declaring
    category class and the axiom in ``_base_category_class_and_axiom``, and declares its
    own ``ObjectType``, ``ElementType``, and ``MorphismType`` like any other category
    (``Axiom``, POL-LEAF-059).  The kernel reads those declarations through the ordinary
    ``Category.local_role_class``, which is the class of this value.
    """

    _base_category_class_and_axiom: ClassVar[tuple[type[Category], str]]

    def __init_subclass__(cls) -> None:
        """Record this class on the axiom it names: the declaration is the one place the link lives."""
        super().__init_subclass__()
        connection = cls.__dict__.get("_base_category_class_and_axiom")
        if connection is None:
            return
        declaring_class, name = connection
        axiom = getattr(declaring_class, name, None)
        assert isinstance(axiom, Axiom), f"{declaring_class.__name__}.{name} is not an axiom, so {cls.__name__} cannot implement it"
        axiom.implemented_by(cls)

    def __init__(
        self,
        ambient: Category[MorphismData, TwoMorphismData],
        name: str,
        full_subcategory_of: tuple[Category, ...],
    ) -> None:
        self._name = name
        self._full_subcategory_of = full_subcategory_of
        self._predicate = PropertyPredicate(name, self)
        super().__init__(ambient)

    def name(self) -> str:
        return self._name

    def predicate(self) -> PropertyPredicate:
        return self._predicate

    def full_subcategory_of(self) -> tuple[Category, ...]:
        """The categories this one is a full subcategory of, beyond its ambient (D83)."""
        return self._full_subcategory_of

    def structure_functors(self) -> tuple[Functor, ...]:
        """The monomorphism into the ambient, then one per further recorded containment (POL-FUN-024)."""
        functors = _functors()
        return (
            functors.full_subcategory_monomorphism(self, self._ambient),
            *(functors.full_subcategory_monomorphism(self, containing) for containing in self._full_subcategory_of),
        )

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        """Membership in the ambient and the property's own predicate.

        ``x in C.P()`` and ``ask(x.is_P())`` are one question asked twice
        (``specs/property-refinement.md``, "Category membership is proposition-backed
        Boolean admission").  Placement is a positive evaluation case inside that one
        question -- a value that entered through the constructor already satisfies the
        predicate, so ``ask`` answers ``True`` from placement without recomputing -- and
        it is never the definition of membership.  A value that never entered still gets
        the defining predicate evaluated, and an undecided answer fails loudly at
        ``__contains__`` rather than being reported as non-membership.
        """
        return self._ambient.membership_proposition(candidate) & self._predicate(candidate)

    def __call__(self, *arguments: CategoryPoint) -> CategoryPoint:
        """The trusted constructor: refine a value of the ambient; or dispatch endpoints ``P(A, B)``."""
        match arguments:
            case (value,):
                assert value in self._ambient, f"{value!r} is not an object of {self._ambient!r}"
                refine(value, self)
                return value
            case (domain, codomain):
                return self._ambient(domain, codomain).property_subcategory(self)
        raise TypeError(f"{self!r} takes one value to refine or two endpoints")

    def __repr__(self) -> str:
        return f"{self._ambient!r}.{self._name}()"


class NarrowedProperty[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):
    """``D.P().Q()...``: the objects of ``D`` in each of the root subcategories.

    It is a full subcategory of ``D``, of each root, of the narrowing of ``D`` by
    every subset of its roots (a narrowing by ``{P, Q}`` is a full subcategory of
    the narrowing by ``{P}``), and of the same narrowing of ``D``'s ambient when
    ``D`` is itself a full subcategory (POL-CAT-084).
    """

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData], roots: tuple[FullSubcategory, ...]) -> None:
        self._roots = roots
        super().__init__(ambient)

    def narrowing_roots(self) -> tuple[Category, ...]:
        return self._roots

    def predicate(self) -> PropertyPredicate:
        """The predicate of the one root property this narrowing restricts (``D.P()``)."""
        (root,) = self._roots
        return root.predicate()

    def structure_functors(self) -> tuple[Functor, ...]:
        """The monomorphisms into the base, into each root, into each narrowing by the roots not below one root, and into the same narrowing of the base's ambient, each once."""
        targets: list[Category] = [self._ambient, *self._roots]
        for omitted in self._roots:
            kept = tuple(root for root in self._roots if not is_subcategory(root, omitted))
            if kept:
                targets.append(self._ambient.intersection(kept))
        if self._ambient.has_ambient():
            targets.append(self._ambient.ambient().intersection(self._roots))
        distinct: list[Category] = []
        for target in targets:
            if target is not self and not any(target is known for known in distinct):
                distinct.append(target)
        return tuple(_functors().full_subcategory_monomorphism(self, target) for target in distinct)

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        """Membership in the ambient together with membership in every root.

        Each root states its own membership: a property subcategory asks its predicate,
        and a construction family asks established placement, which is what membership in
        it means (``FullSubcategory``).
        """
        proposition = self._ambient.membership_proposition(candidate)
        for root in self._roots:
            proposition = proposition & root.membership_proposition(candidate)
        return proposition

    def __call__(self, value: CategoryPoint) -> CategoryPoint:
        assert value in self._ambient, f"{value!r} is not an object of {self._ambient!r}"
        refine(value, self)
        return value

    def __repr__(self) -> str:
        return f"{self._ambient!r}." + ".".join(f"{root.name()}()" for root in self._roots)


class FixedEndpointProperty[**MorphismData, **TwoMorphismData](NarrowedProperty[TwoMorphismData, []]):
    """``Mor(C)(A, B).P()``: constructs a morphism ``A -> B`` with property ``P``, or refines one."""

    def domain(self) -> CategoryPoint:
        return self._ambient.domain()

    def codomain(self) -> CategoryPoint:
        return self._ambient.codomain()

    def is_inhabited(self) -> AppliedPredicate:
        """The proposition that some morphism ``A -> B`` with the property exists (POL-CAT-086)."""
        return _morphisms().inhabited(self)

    def is_empty(self) -> Proposition:
        """The negation of ``is_inhabited()``."""
        return ~_morphisms().inhabited(self)

    def __call__(self, *args: MorphismData.args, **kwargs: MorphismData.kwargs) -> MorphismOfCategory:
        if len(args) == 1 and not kwargs and args[0] in self._ambient:
            refine(args[0], self)
            return args[0]
        morphism = self._ambient(*args, **kwargs)
        refine(morphism, self)
        return morphism

    def multiplicative_identity(self) -> MorphismOfCategory:
        """``1_X`` with this property: the unit of ``End_C(X)`` refined into the narrowing (D86)."""
        identity = self._ambient.multiplicative_identity()
        refine(identity, self)
        return identity
