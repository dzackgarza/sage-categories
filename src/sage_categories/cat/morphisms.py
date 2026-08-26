"""The ``Mor(n, C)`` tower and fixed endpoints (D03, D04).

For every category ``C`` and ``n >= 0``, ``Mor(n, C)`` is the category whose
objects are the ``n``-morphisms of ``C`` and whose morphisms are the
``(n+1)``-morphisms: ``Mor(0, C) = C``, ``Mor(C) = Mor(1, C)``,
``Mor(n+1, C) = Mor(Mor(n, C))``.  ``Mor(C).ObjectType`` *is* ``C.MorphismType``:
one implementation type, one value, two placements.  For a 1-category every
2-morphism is an identity, so ``Mor(C)`` is discrete; ``Cat()`` supplies natural
transformations instead (``cat/functors.py``).

``Mor(C)(A, B)`` is the full subcategory of ``Mor(C)`` on the morphisms with
domain ``A`` and codomain ``B``, one cached object per pair (POL-CAT-022/089).
Calling it with construction data constructs a morphism ``A -> B`` through the
category-owned constructor ``C.construct_morphism`` (POL-API-009/010).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from sage.structure.coerce_dict import TripleDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.properties import FullSubcategory, PropertySubcategory
from sage_categories.kernel.decisions import Decision, decision_and
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role

if TYPE_CHECKING:
    from sage_categories.cat.properties import FixedEndpointProperty

__all__ = ["FixedEndpointCategory", "IdentityTwoCell", "Mor", "MorphismCategory"]


@overload
def Mor[**M, **T](category: Category[M, T]) -> MorphismCategory[M, T]: ...


@overload
def Mor[**M, **T](level: Literal[0], category: Category[M, T]) -> Category[M, T]: ...


@overload
def Mor[**M, **T](level: Literal[1], category: Category[M, T]) -> MorphismCategory[M, T]: ...


@overload
def Mor[**M, **T](level: Literal[2], category: Category[M, T]) -> MorphismCategory[T, []]: ...


@overload
def Mor(level: int, category: Category) -> MorphismCategory[[], []]: ...


def Mor(*arguments: int | Category) -> Category:
    """``Mor(C)`` is ``Mor(1, C)``; ``Mor(n, C)`` is the ``n``-th morphism category of ``C``."""
    match arguments:
        case (Category() as category,):
            return category.morphism_category(1)
        case (int() as level, Category() as category):
            return category.morphism_category(level)
    raise TypeError("Mor takes a category or a level and a category")


class IdentityTwoCell(MorphismOfCategory):
    """The identity 2-morphism of a morphism of a 1-category: the only morphisms of ``Mor(C)``."""

    def __init__(self, category: Category, morphism: MorphismOfCategory) -> None:
        super().__init__(category, morphism, morphism)

    def __repr__(self) -> str:
        return f"identity of {self.domain()!r}"


# ``endpoints(f, A, B)``: the domain of ``f`` is ``A`` and its codomain is ``B``,
# decided through the equality predicate of the base category (identity first).
endpoints = Predicate("endpoints", 3, False)


def _endpoints_by_equality(morphism: MorphismOfCategory, domain: ObjectOfCategory, codomain: ObjectOfCategory) -> Decision:
    return decision_and(ask(morphism.domain() == domain), ask(morphism.codomain() == codomain))


endpoints.register_handler(_endpoints_by_equality)

# ``endomorphism(f)``: the domain of ``f`` is its codomain.


def _endomorphism_by_equality(morphism: MorphismOfCategory) -> Decision:
    return ask(morphism.domain() == morphism.codomain())


# ``endpoints_in(f, D)``: the domain and codomain of ``f`` are objects of ``D``.  A full
# subcategory ``D`` of ``C`` has exactly the morphisms of ``C`` between its objects
# (Mathlib ``InducedCategory.Hom``; inspected 2026-08-26).
endpoints_in = Predicate("endpoints_in", 2, False)


def _endpoints_in_by_membership(morphism: MorphismOfCategory, subcategory: Category) -> Decision:
    return decision_and(
        ask(subcategory.membership_proposition(morphism.domain())),
        ask(subcategory.membership_proposition(morphism.codomain())),
    )


endpoints_in.register_handler(_endpoints_in_by_membership)


class MorphismCategory[**MorphismData, **TwoMorphismData](Category[TwoMorphismData, []]):
    """``Mor(C)``: objects are the morphisms of ``C``, morphisms its 2-morphisms."""

    def __init__(self, base: Category[MorphismData, TwoMorphismData]) -> None:
        self._base = base
        self._fixed_endpoints: TripleDict = TripleDict(weak_values=False)
        # Each morphism category owns its element role (POL-CAT-058): a generalized
        # element of a morphism of ``C``, with no local operation.
        self._element_role = type(f"Mor({base!r}).ElementType", (ElementOfObject,), {})
        super().__init__()

    def base_category(self) -> Category[MorphismData, TwoMorphismData]:
        return self._base

    def role_source(self, role: Role) -> tuple[Category, Role]:
        if role is Role.OBJECT:
            return self._base, Role.MORPHISM
        return self, role

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        match role:
            case Role.ELEMENT:
                return self._element_role
            case Role.MORPHISM:
                return self._base.two_morphism_type()
        raise AssertionError(f"the objects of {self!r} are the morphisms of {self._base!r}")

    def equality(self) -> Predicate:
        return self._base.equality()

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        if self._base.has_ambient():
            return self._base.ambient().morphism_category(1).membership_proposition(candidate) & endpoints_in(candidate, self._base)
        return member(candidate, self)

    # -- fixed endpoints ---------------------------------------------------------

    def __call__(self, domain: ObjectOfCategory, codomain: ObjectOfCategory) -> FixedEndpointCategory[MorphismData, TwoMorphismData]:
        """``Mor(C)(A, B)``: the full subcategory on morphisms ``A -> B``, one object per pair."""
        assert domain in self._base and codomain in self._base
        key = (domain, codomain, self)
        if key not in self._fixed_endpoints:
            self._fixed_endpoints[key] = self.fixed_endpoint_type()(self, domain, codomain)
        return self._fixed_endpoints[key]

    def fixed_endpoint_type(self) -> type[FixedEndpointCategory[MorphismData, TwoMorphismData]]:
        return FixedEndpointCategory

    # -- 2-morphisms ------------------------------------------------------------

    def construct_identity(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        return self._base.identity_two_morphism(morphism)

    def composite(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        return self._base.compose_two_morphisms(second, first)

    def construct_morphism(
        self,
        source: MorphismOfCategory,
        target: MorphismOfCategory,
        *args: TwoMorphismData.args,
        **kwargs: TwoMorphismData.kwargs,
    ) -> MorphismOfCategory:
        return self._base.construct_two_morphism(source, target, *args, **kwargs)

    # -- property subcategories, defined once for every ``C`` (D09) -------------

    # ``D`` included in ``C`` derives ``Mor(D).P()`` as the narrowing of ``Mor(C).P()`` (POL-CAT-084).

    def _root_property(self, name: str, roles: dict[Role, type], implications: tuple[Category, ...]) -> PropertySubcategory:
        if name not in self._properties:
            self._properties[name] = PropertySubcategory(self, name, roles, implications)
        return self._properties[name]

    def Monomorphisms(self) -> Category:
        if self._base.has_ambient():
            return self.property_subcategory(self._base.ambient().morphism_category(1).Monomorphisms())
        return self._root_property("Monomorphisms", {}, ())

    def Epimorphisms(self) -> Category:
        if self._base.has_ambient():
            return self.property_subcategory(self._base.ambient().morphism_category(1).Epimorphisms())
        return self._root_property("Epimorphisms", {}, ())

    def Isomorphisms(self) -> Category:
        from sage_categories.cat.properties import IsomorphismRole

        if self._base.has_ambient():
            return self.property_subcategory(self._base.ambient().morphism_category(1).Isomorphisms())
        # An isomorphism is monic and epic (``specs/undecidable-properties.md``,
        # "How ask() works": Isomorphism implies Monomorphism and Epimorphism).
        return self._root_property("Isomorphisms", {Role.OBJECT: IsomorphismRole}, (self.Monomorphisms(), self.Epimorphisms()))

    def Endomorphisms(self) -> Category:
        if self._base.has_ambient():
            return self.property_subcategory(self._base.ambient().morphism_category(1).Endomorphisms())
        if "Endomorphisms" not in self._properties:
            self._root_property("Endomorphisms", {}, ()).predicate().register_handler(_endomorphism_by_equality)
        return self._properties["Endomorphisms"]

    def Automorphisms(self) -> Category:
        """``Mor(C).Endomorphisms().Isomorphisms()``."""
        return self.Endomorphisms().property_subcategory(self.Isomorphisms())

    def __repr__(self) -> str:
        return f"Mor({self._base!r})"


class FixedEndpointCategory[**MorphismData, **TwoMorphismData](FullSubcategory[TwoMorphismData, []]):
    """``Mor(C)(A, B)``: the full subcategory of ``Mor(C)`` on the morphisms ``A -> B``."""

    def __init__(self, morphisms: MorphismCategory[MorphismData, TwoMorphismData], domain: ObjectOfCategory, codomain: ObjectOfCategory) -> None:
        self._domain_object = domain
        self._codomain_object = codomain
        super().__init__(morphisms)

    def domain(self) -> ObjectOfCategory:
        return self._domain_object

    def codomain(self) -> ObjectOfCategory:
        return self._codomain_object

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return member(candidate, self.ambient()) & endpoints(candidate, self._domain_object, self._codomain_object)

    def __call__(self, *args: MorphismData.args, **kwargs: MorphismData.kwargs) -> MorphismOfCategory:
        """``Mor(C)(A, B)(data)``: a morphism ``A -> B`` through ``C``'s constructor."""
        return self.base_category().construct_morphism(self._domain_object, self._codomain_object, *args, **kwargs)

    def identity(self) -> MorphismOfCategory:
        assert self._domain_object is self._codomain_object, f"{self!r} has no identity: its endpoints differ"
        return self.base_category().identity_morphism(self._domain_object)

    def compose(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        """``Mor(C)(A, C).compose(g, f)`` for ``f: A -> B`` and ``g: B -> C``."""
        assert first.domain() is self._domain_object and second.codomain() is self._codomain_object
        return self.base_category().compose_morphisms(second, first)

    def Monomorphisms(self) -> Category:
        return self.property_subcategory(self.ambient().Monomorphisms())

    def Epimorphisms(self) -> Category:
        return self.property_subcategory(self.ambient().Epimorphisms())

    def Isomorphisms(self) -> Category:
        return self.property_subcategory(self.ambient().Isomorphisms())

    def narrowing_type(self) -> type[FixedEndpointProperty[MorphismData, TwoMorphismData]]:
        from sage_categories.cat.properties import FixedEndpointProperty

        return FixedEndpointProperty

    def __repr__(self) -> str:
        return f"{self.ambient()!r}({self._domain_object!r}, {self._codomain_object!r})"
