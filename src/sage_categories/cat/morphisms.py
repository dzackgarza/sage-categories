"""The ``Mor(n, C)`` tower and fixed endpoints (POL-CAT-021, POL-API-009).

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

from sage.misc.cachefunc import cached_method
from sage.structure.coerce_dict import TripleDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.properties import FullSubcategory, PropertySubcategory
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, Proposition, ask
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role

if TYPE_CHECKING:
    from sage_categories.cat.properties import FixedEndpointProperty

__all__ = ["FixedEndpointCategory", "IdentityTwoCell", "Mor", "MorphismCategory", "inhabited"]


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

    def __repr__(self) -> str:
        return f"identity of {self.domain()!r}"


# ``endpoints(f, A, B)``: the domain of ``f`` is ``A`` and its codomain is ``B``,
# decided through the equality predicate of the base category (identity first).
endpoints = Predicate("endpoints", 3, False)


def _endpoints_by_equality(morphism: MorphismOfCategory, domain: ObjectOfCategory, codomain: ObjectOfCategory) -> Decision:
    return ask((morphism.domain() == domain) & (morphism.codomain() == codomain))


endpoints.register_handler(_endpoints_by_equality)

# ``endomorphism(f)``: the domain of ``f`` is its codomain.


def _endomorphism_by_equality(morphism: MorphismOfCategory) -> Decision:
    return ask(morphism.domain() == morphism.codomain())


# ``endpoints_in(f, D)``: the domain and codomain of ``f`` are objects of ``D``.  A full
# subcategory ``D`` of ``C`` has exactly the morphisms of ``C`` between its objects
# (Mathlib ``InducedCategory.Hom``; inspected 2026-08-26).
endpoints_in = Predicate("endpoints_in", 2, False)


def _endpoints_in_by_membership(morphism: MorphismOfCategory, subcategory: Category) -> Decision:
    return ask(subcategory.membership_proposition(morphism.domain()) & subcategory.membership_proposition(morphism.codomain()))


endpoints_in.register_handler(_endpoints_in_by_membership)

# ``inhabited(H)``: the fixed-endpoint category ``H = Mor(C)(A, B)``, or a property
# narrowing of it, has an object (POL-CAT-086; ``specs/property-refinement.md``,
# "Fixed-endpoint predicates").  A constructed object establishes inhabitation, so
# the decision is not a permanent fact of ``H`` and is never cached.  The exact
# routes: the identity of ``A`` when ``A is B`` and it is a member; then the decision
# the base category owns for its hom categories (``Category.hom_inhabited``).
inhabited = Predicate("inhabited", 1, False)


def _inhabited_by_identity(hom_category: Category) -> Decision:
    base = hom_category.narrowing_base()
    if base.domain() is not base.codomain():
        return Unknown
    return True if base.domain().identity() in hom_category else Unknown


def _inhabited_by_base_category(hom_category: Category) -> Decision:
    return hom_category.narrowing_base().base_category().hom_inhabited(hom_category)


inhabited.register_handler(_inhabited_by_identity)
inhabited.register_handler(_inhabited_by_base_category)


class MorphismCategory[**MorphismData, **TwoMorphismData](Category[TwoMorphismData, []]):
    """``Mor(C)``: objects are the morphisms of ``C``, morphisms its 2-morphisms."""

    def __init__(self, base: Category[MorphismData, TwoMorphismData]) -> None:
        self._base = base
        self._fixed_endpoints: TripleDict = TripleDict(weak_values=False)
        # Each morphism category owns its element role (POL-CAT-058): a generalized
        # element of a morphism of ``C``, with no local operation.
        self._declared_element_role = type(f"Mor({base!r}).DeclaredElementType", (ElementOfObject,), {})
        super().__init__()

    def base_category(self) -> Category[MorphismData, TwoMorphismData]:
        return self._base

    # ``Mor(D)`` for ``D`` a declared subcategory of ``C`` is the full subcategory of
    # ``Mor(C)`` on the morphisms of ``D`` (Mathlib ``InducedCategory.Hom``); its
    # subcategory monomorphism is ``D``'s at the morphism role, which the node
    # normalization already places in the selected graph (POL-CAT-021, POL-CAT-087).

    def has_ambient(self) -> bool:
        return self._base.has_ambient()

    def ambient(self) -> Category:
        return self._base.ambient().morphism_category(1)

    def narrowing_base(self) -> Category:
        if self._base.has_ambient():
            return self.ambient().narrowing_base()
        return self

    def narrowing_roots(self) -> tuple[Category, ...]:
        if self._base.has_ambient():
            return (*self.ambient().narrowing_roots(), self)
        return ()

    def role_source(self, role: Role) -> tuple[Category, Role]:
        if role is Role.OBJECT:
            return self._base, Role.MORPHISM
        return self, role

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        match role:
            case Role.ELEMENT:
                return self._declared_element_role
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

    # -- property subcategories, defined once for every ``C`` (POL-FUN-024) -------------

    # ``D`` included in ``C`` derives ``Mor(D).P()`` as the narrowing of ``Mor(C).P()``
    # (POL-CAT-084).  Each root property is constructed once per morphism category
    # and retained by the method that names it (Sage ``cached_method``).

    @cached_method
    def Monomorphisms(self) -> Category:
        if self._base.has_ambient():
            return self.property_subcategory(self._base.ambient().morphism_category(1).Monomorphisms())
        return PropertySubcategory(self, "Monomorphisms", {}, ())

    @cached_method
    def Epimorphisms(self) -> Category:
        if self._base.has_ambient():
            return self.property_subcategory(self._base.ambient().morphism_category(1).Epimorphisms())
        return PropertySubcategory(self, "Epimorphisms", {}, ())

    @cached_method
    def Isomorphisms(self) -> Category:
        from sage_categories.cat.properties import IsomorphismRole

        if self._base.has_ambient():
            return self.property_subcategory(self._base.ambient().morphism_category(1).Isomorphisms())
        # An isomorphism is monic and epic (``specs/undecidable-properties.md``,
        # "How ask() works": Isomorphism implies Monomorphism and Epimorphism).
        return PropertySubcategory(self, "Isomorphisms", {Role.OBJECT: IsomorphismRole}, (self.Monomorphisms(), self.Epimorphisms()))

    @cached_method
    def Endomorphisms(self) -> Category:
        if self._base.has_ambient():
            return self.property_subcategory(self._base.ambient().morphism_category(1).Endomorphisms())
        endomorphisms = PropertySubcategory(self, "Endomorphisms", {}, ())
        endomorphisms.predicate().register_handler(_endomorphism_by_equality)
        return endomorphisms

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

    # A fixed-endpoint category is its own base for narrowing: ``Mor(C)(A, B).P()`` is a
    # narrowing of it, of the type it declares, and never a root of ``Mor(C)``.

    def narrowing_base(self) -> Category:
        return self

    def narrowing_roots(self) -> tuple[Category, ...]:
        return ()

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        """A morphism of ``Mor(C)`` with these endpoints (POL-CAT-087: the ambient decides which values are its morphisms)."""
        return self.ambient().membership_proposition(candidate) & endpoints(candidate, self._domain_object, self._codomain_object)

    def is_inhabited(self) -> AppliedPredicate:
        """The proposition that some morphism ``A -> B`` exists (POL-CAT-086)."""
        return inhabited(self)

    def is_empty(self) -> Proposition:
        """The negation of ``is_inhabited()``: the two propositions are mutually negated by construction."""
        return ~inhabited(self)

    def __call__(self, *args: MorphismData.args, **kwargs: MorphismData.kwargs) -> MorphismOfCategory:
        """``Mor(C)(A, B)(data)``: a morphism ``A -> B`` through ``C``'s constructor, placed here.

        Calling a category constructs a value in it, so the result enters ``Mor(C)(A, B)``
        (POL-CAT-068, POL-API-009).  The refinement is the same same-object narrowing a
        property subcategory's constructor performs (``cat/properties.py``), and it is
        what lets a functor whose domain is this category transport its own argument.

        Placement follows the construction path the caller took: ``C.construct_morphism``,
        ``C.composite``, and ``C.construct_identity`` called directly still place their
        result in ``Mor(C)``.
        """
        morphism = self.base_category().construct_morphism(self._domain_object, self._codomain_object, *args, **kwargs)
        refine(morphism, self)
        return morphism

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
