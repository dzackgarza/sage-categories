"""Full subcategories and property subcategories (POL-CAT-054, POL-CAT-087, POL-FUN-024).

A full subcategory ``S`` of ``T`` shares ``T``'s object, element, and morphism
values; its morphism categories, identities, and composition are inherited
definitionally from ``T`` (Mathlib ``CategoryTheory.ObjectProperty.FullSubcategory``
and its inclusion ``ObjectProperty.ι``, full and faithful; inspected 2026-08-26).
Its one selected structural functor is the identity-on-value inclusion
``Fun(S, T).FullyFaithful().inclusion()``.

A property subcategory ``C.P()`` is the full subcategory on the objects satisfying
a predicate ``P``.  Its constructor is the trusted boundary of that property
(POL-CAT-038/069): calling it on a value of ``C`` refines the same value in place.
An implication ``P => Q`` is recorded as the inclusion ``C.P() -> C.Q()``
(``specs/functor.md``, "Inclusion functors").  A descendant ``D`` with a selected
inclusion into ``C`` derives ``D.P()`` as the narrowing of ``C.P()`` to ``D``
(POL-CAT-084): a full subcategory of both, with the same predicate.
"""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from sage_categories.cat.category import Category, member
from sage_categories.kernel.compiler import empty_local_role
from sage_categories.kernel.predicates import PropertyPredicate, Proposition
from sage_categories.kernel.refinement import refine
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


class FullSubcategory[**MorphismData, **TwoMorphismData](Category[MorphismData, TwoMorphismData]):
    """A full subcategory of an ambient category, declared by its inclusion.

    Its morphisms, identities, and composites are those of the ambient between its
    objects; ``Category`` supplies them from the ambient (POL-CAT-087).
    """

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData]) -> None:
        self._ambient = ambient
        super().__init__()

    def has_ambient(self) -> bool:
        return True

    def ambient(self) -> Category[MorphismData, TwoMorphismData]:
        """The ambient is construction data: this category declares exactly one inclusion."""
        return self._ambient

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        return empty_local_role(self, role)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (_functors().full_inclusion(self, self._ambient),)


_ordinals = itertools.count()


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
        self._ordinal = next(_ordinals)
        super().__init__(ambient)

    def name(self) -> str:
        return self._name

    def predicate(self) -> PropertyPredicate:
        return self._predicate

    def ordinal(self) -> int:
        """The declaration order of this root property, used to canonicalize narrowings."""
        return self._ordinal

    def narrowing_base(self) -> Category:
        return self._ambient

    def narrowing_roots(self) -> tuple[Category, ...]:
        return (self,)

    def implications(self) -> tuple[Category, ...]:
        return self._implications

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        if role in self._roles:
            return self._roles[role]
        return empty_local_role(self, role)

    def structure_functors(self) -> tuple[Functor, ...]:
        """The inclusion into the ambient, then one inclusion per recorded implication (POL-FUN-024)."""
        functors = _functors()
        return (
            functors.full_inclusion(self, self._ambient),
            *(functors.full_inclusion(self, implied) for implied in self._implications),
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
    """``D.P().Q()...``: the objects of ``D`` satisfying each of the root properties.

    It is a full subcategory of ``D``, of each root, and of the same narrowing of
    ``D``'s ambient when ``D`` is itself a full subcategory (POL-CAT-084).
    """

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData], roots: tuple[PropertySubcategory, ...]) -> None:
        self._roots = roots
        super().__init__(ambient)

    def narrowing_base(self) -> Category:
        return self._ambient

    def narrowing_roots(self) -> tuple[Category, ...]:
        return self._roots

    def predicate(self) -> PropertyPredicate:
        """The predicate of the one root property this narrowing restricts (``D.P()``)."""
        (root,) = self._roots
        return root.predicate()

    def structure_functors(self) -> tuple[Functor, ...]:
        """The inclusions into the ambient, into each root, and into the same narrowing of the ambient's ambient, each once."""
        targets: list[Category] = [self._ambient, *self._roots]
        if self._ambient.has_ambient():
            narrowing = self._ambient.ambient().intersection(self._roots)
            if not any(narrowing is target for target in targets):
                targets.append(narrowing)
        return tuple(_functors().full_inclusion(self, target) for target in targets)

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
