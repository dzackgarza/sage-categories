"""Full subcategories and property subcategories (POL-CAT-054, POL-CAT-087, POL-FUN-024).

A full subcategory ``S`` of ``T`` shares ``T``'s object, element, and morphism
values; its morphism categories, identities, and composition are inherited
definitionally from ``T`` (Mathlib ``CategoryTheory.ObjectProperty.FullSubcategory``
and the functor ``ObjectProperty.ι`` it carries, full and faithful; inspected
2026-08-26).  Its one selected structural functor is the identity-on-values
monomorphism ``Fun(S, T).Monomorphisms().Isofibrations().Full()()``.

A property subcategory ``C.P()`` is the full subcategory on the objects satisfying
a predicate ``P``.  Its constructor is the trusted boundary of that property
(POL-CAT-038/069): calling it on a value of ``C`` refines the same value in place.
An implication ``P => Q`` is recorded as the subcategory monomorphism ``C.P() -> C.Q()``
(``specs/functor.md``, "Monomorphisms of ``Cat()`` and placement").  A descendant ``D`` with a selected
subcategory monomorphism into ``C`` derives ``D.P()`` as the narrowing of ``C.P()`` to ``D``
(POL-CAT-084): a full subcategory of both, with the same predicate.
"""

from __future__ import annotations

from types import ModuleType
from typing import TYPE_CHECKING

from sage_categories.cat.category import Category, member
from sage_categories.kernel.compiler import empty_local_role
from sage_categories.kernel.predicates import AppliedPredicate, PropertyPredicate, Proposition
from sage_categories.kernel.refinement import is_subcategory, refine
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, Role

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor, FunctorsCategory

__all__ = [
    "FixedEndpointProperty",
    "FullSubcategory",
    "IsomorphismRole",
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

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        return empty_local_role(self, role)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (_functors().full_subcategory_monomorphism(self, self._ambient),)

    def separating_family(self) -> tuple[CategoryPoint, ...]:
        """The separators of the ambient that are objects of this subcategory: a subcategory monomorphism supplies none of its own."""
        return tuple(separator for separator in self._ambient.separating_family() if separator in self)

    def element_from_defining_morphism(self, defining_morphism: MorphismOfCategory) -> CategoryPoint:
        """The elements of a full subcategory are those of its ambient on the shared values (POL-CAT-087)."""
        return self._ambient.element_from_defining_morphism(defining_morphism)


class PropertySubcategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):
    """``C.P()``: the full subcategory of ``C`` on the objects satisfying ``P``."""

    def __init__(
        self,
        ambient: Category[MorphismData, TwoMorphismData],
        name: str,
        roles: dict[Role, type[CategoryPoint]],
        implications: tuple[Category, ...],
    ) -> None:
        self._name = name
        self._roles = roles
        self._implications = implications
        self._predicate = PropertyPredicate(name, self)
        super().__init__(ambient)

    def name(self) -> str:
        return self._name

    def predicate(self) -> PropertyPredicate:
        return self._predicate

    def implications(self) -> tuple[Category, ...]:
        return self._implications

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        if role in self._roles:
            return self._roles[role]
        return empty_local_role(self, role)

    def structure_functors(self) -> tuple[Functor, ...]:
        """The monomorphism into the ambient, then one per recorded implication (POL-FUN-024)."""
        functors = _functors()
        return (
            functors.full_subcategory_monomorphism(self, self._ambient),
            *(functors.full_subcategory_monomorphism(self, implied) for implied in self._implications),
        )

    # Membership in a property subcategory is established placement (POL-CAT-043/044):
    # ``x in C.P()`` asks whether ``x`` already entered ``C.P()``; ``ask(x.is_P())`` computes.

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
        """Membership in the ambient together with established placement in every root."""
        proposition = self._ambient.membership_proposition(candidate)
        for root in self._roots:
            proposition = proposition & member(candidate, root)
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

    def identity(self) -> MorphismOfCategory:
        identity = self._ambient.identity()
        refine(identity, self)
        return identity


class IsomorphismRole(MorphismOfCategory):
    """The local object role of ``Mor(C).Isomorphisms()``: the isomorphism category owns inversion (POL-CAT-079)."""

    def inverse(self) -> MorphismOfCategory:
        """The inverse: the retained one when the construction supplied it, else the category-owned one."""
        return self.base_category().inverse_morphism(self)
