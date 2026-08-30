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

from sage.structure.coerce_dict import TripleDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.properties import FullSubcategory, PredicateSubcategory, PropertySubcategory
from sage_categories.kernel.decisions import Decision
from sage_categories.kernel.predicates import Axiom, Predicate, Proposition, ask
from sage_categories.kernel.refinement import refine

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.properties import FixedEndpointProperty

__all__ = ["EndomorphismsCategory", "FixedEndpointCategory", "IsomorphismsCategory", "Mor", "MorphismCategory", "hom_inhabitation"]


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


# ``endpoints(f, A, B)``: the domain of ``f`` is ``A`` and its codomain is ``B``,
# decided through the equality predicate of the base category (identity first).
endpoints = Predicate("endpoints", 3, False)


def _endpoints_by_equality(
    morphism: MorphismCategory.ObjectType,
    domain: CategoryOfCategories.ElementType,
    codomain: CategoryOfCategories.ElementType,
) -> Decision:
    return ask((morphism.domain() == domain) & (morphism.codomain() == codomain))


endpoints.register_handler(_endpoints_by_equality)

# ``endpoints_in(f, D)``: the domain and codomain of ``f`` are objects of ``D``.  A full
# subcategory ``D`` of ``C`` has exactly the morphisms of ``C`` between its objects
# (Mathlib ``InducedCategory.Hom``; inspected 2026-08-26).
endpoints_in = Predicate("endpoints_in", 2, False)


def _endpoints_in_by_membership(morphism: MorphismCategory.ObjectType, subcategory: Category) -> Decision:
    return ask(subcategory.membership_proposition(morphism.domain()) & subcategory.membership_proposition(morphism.codomain()))


endpoints_in.register_handler(_endpoints_in_by_membership)


def hom_inhabitation(hom_category: Category) -> Decision:
    """The exact cases of ``H.is_inhabited()`` for ``H = Mor(C)(A, B)`` or a property narrowing of it (POL-CAT-086).

    A constructed object establishes inhabitation, so the decision is not a permanent
    fact of ``H`` and ``Cat().Inhabited()`` caches none.  The identity of ``A`` is the
    exact route when ``A is B`` and it is a member of the narrowing; otherwise the base
    category supplies the decision it owns for its hom categories.
    """
    base = hom_category.narrowing_base()
    if base.domain() is base.codomain() and base.one() in hom_category:
        return True
    return base.base_category()._chosen_hom_inhabited(hom_category)


class MorphismCategory[**MorphismData, **TwoMorphismData](Category[TwoMorphismData, []]):
    """``Mor(C)``: objects are the morphisms of ``C``, morphisms its 2-morphisms."""

    # An object of ``Mor(C)`` is a morphism of ``C``, and ``C`` is arbitrary, so the
    # Per category value the compiled class is ``C.MorphismType``.  This local class is
    # the generic declaration whose generated axiom applications the kernel installs on
    # the private morphism root.
    class ObjectType:
        """A morphism of an arbitrary category ``C``."""

    class MorphismType:
        """The identity 2-morphism of a morphism of a 1-category: the only morphisms of ``Mor(C)``."""

        def __repr__(self) -> str:
            return f"identity of {self.domain()!r}"

    class ElementType:
        """A generalized element ``t: T -> f`` of a morphism of ``C``, read in ``Mor(C)``.

        ``Mor(C).ObjectType`` is ``C.MorphismType``, so the object this is a point of is a
        morphism of ``C``, and ``t`` is a 2-morphism into it.  For a 1-category every
        2-morphism is an identity, so the only such ``t`` is ``1_f``; a 2-category
        supplies the rest through its own ``Mor(C)``.
        """

    def __init__(self, base: Category[MorphismData, TwoMorphismData]) -> None:
        self._base = base
        self._fixed_endpoints: TripleDict = TripleDict(weak_values=False)
        if base.has_ambient():
            # ``Mor(D)`` for a declared subcategory ``D`` of ``C`` is a subcategory of
            # ``Mor(C)``, and this category derives that ambient rather than receiving it
            # as construction data.  Constructing it here keeps the ordinal invariant a
            # category with an ambient otherwise gets for free: every category a category
            # selects a functor into is older than it (``Category._initialize``).
            base.ambient().morphism_category(1)
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

    def _object_role_source(self) -> tuple[Category, bool]:
        return self._base, True

    def equality(self) -> Predicate:
        return self._base.equality()

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        if self._base.has_ambient():
            return self._base.ambient().morphism_category(1).membership_proposition(candidate) & endpoints_in(candidate, self._base)
        return member(candidate, self)

    # -- fixed endpoints ---------------------------------------------------------

    def __call__(
        self,
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
    ) -> FixedEndpointCategory[MorphismData, TwoMorphismData]:
        """``Mor(C)(A, B)``: the full subcategory on morphisms ``A -> B``, one object per pair."""
        assert domain in self._base and codomain in self._base
        key = (domain, codomain, self)
        if key not in self._fixed_endpoints:
            self._fixed_endpoints[key] = self.fixed_endpoint_type()(self, domain, codomain)
        return self._fixed_endpoints[key]

    def fixed_endpoint_type(self) -> type[FixedEndpointCategory[MorphismData, TwoMorphismData]]:
        return FixedEndpointCategory

    # -- 2-morphisms ------------------------------------------------------------

    def construct_identity(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        return self._base.identity_two_morphism(morphism)

    def composite(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        return self._base.compose_two_morphisms(second, first)

    def construct_morphism(
        self,
        source: MorphismCategory.ObjectType,
        target: MorphismCategory.ObjectType,
        *args: TwoMorphismData.args,
        **kwargs: TwoMorphismData.kwargs,
    ) -> MorphismCategory.ObjectType:
        return self._base.construct_two_morphism(source, target, *args, **kwargs)

    # -- property axioms, declared once for every ``C`` (POL-FUN-024) -------------------

    # ``D`` included in ``C`` derives ``Mor(D).P()`` as the narrowing of ``Mor(C).P()``
    # (POL-CAT-084).  Each axiom states that derivation once and constructs its
    # subcategory once per morphism category; ``Mor(D)`` is the declared subcategory of
    # ``Mor(C)`` that the narrowing runs on.
    #
    # An isomorphism is monic and epic, so ``Mor(C).Isomorphisms()`` is a full subcategory
    # of both ``Mor(C).Monomorphisms()`` and ``Mor(C).Epimorphisms()``
    # (``specs/undecidable-properties.md``, "How ask() works"; D83).

    # The identifier is the whole declaration: the kernel compiles ``f.is_monomorphisms()``
    # and its three siblings from these four lines, onto the ``ObjectType`` this class
    # declares, which is every morphism of every category (D89, POL-CAT-060).

    Monomorphisms = Axiom()
    Epimorphisms = Axiom()
    Isomorphisms = Axiom(full_subcategory_of=(Monomorphisms, Epimorphisms))
    Endomorphisms = Axiom()

    def Automorphisms(self) -> Category:
        """``Mor(C).Endomorphisms().Isomorphisms()``."""
        return self.Endomorphisms().property_subcategory(self.Isomorphisms())

    def __repr__(self) -> str:
        return f"Mor({self._base!r})"


class IsomorphismsCategory[**MorphismData, **TwoMorphismData](PropertySubcategory[MorphismData, TwoMorphismData]):
    """``Mor(C).Isomorphisms()``: the implementation of the ``Isomorphisms`` axiom of ``Mor(C)``."""

    _base_category_class_and_axiom = (MorphismCategory, "Isomorphisms")

    # Invertibility constrains the morphism, not its points or the 2-morphisms between
    # two of them; ``inverse()`` is the whole delta and it is on the object below.
    class ElementType:
        """A generalized element of an isomorphism, read in ``Mor(C)``."""

    class MorphismType:
        """A 2-morphism between two isomorphisms of ``C``."""

    class ObjectType:
        """An isomorphism of ``C``: the isomorphism category owns inversion (POL-CAT-079)."""

        def inverse(self) -> MorphismCategory.ObjectType:
            """The inverse: the retained one when the construction supplied it, else the category-owned one."""
            return self.base_category().inverse_morphism(self)


class EndomorphismsCategory[**MorphismData, **TwoMorphismData](PredicateSubcategory[MorphismData, TwoMorphismData]):
    """``Mor(C).Endomorphisms()``: the implementation of the ``Endomorphisms`` axiom of ``Mor(C)``.

    Its mathematics decides membership, so it inherits ``PredicateSubcategory`` and states
    the decision as ``_predicate`` (POL-CAT-060, D97).
    """

    class ObjectType:
        """An endomorphism ``X -> X`` of ``C``.

        Equal endpoints make ``End_C(X)`` a monoid under composition, but that monoid is
        the category ``Mor(C)(X, X)`` and its unit is ``one()`` there (D84, D86), so the
        endomorphism itself gains nothing.
        """

    class ElementType:
        """A point of an endomorphism."""

    class MorphismType:
        """A 2-cell between two endomorphisms."""

    _base_category_class_and_axiom = (MorphismCategory, "Endomorphisms")

    def _predicate(self, candidate: MorphismCategory.ObjectType) -> Decision:
        """A morphism is an endomorphism exactly when its two endpoints are equal."""
        return ask(candidate.domain() == candidate.codomain())


class FixedEndpointCategory[**MorphismData, **TwoMorphismData](FullSubcategory[TwoMorphismData, []]):
    """``Mor(C)(A, B)``: the full subcategory of ``Mor(C)`` on the morphisms ``A -> B``."""

    class ObjectType:
        """A morphism ``A -> B`` of ``C``.

        Fixing the endpoints selects morphisms; it does not change what one is.  What the
        endpoints make available belongs to the hom category, which is a monoid under
        composition when ``A`` is ``B``.
        """

    class ElementType:
        """A point of such a morphism."""

    class MorphismType:
        """A 2-cell between two morphisms ``A -> B``."""

    def __init__(
        self,
        morphisms: MorphismCategory[MorphismData, TwoMorphismData],
        domain: CategoryOfCategories.ElementType,
        codomain: CategoryOfCategories.ElementType,
    ) -> None:
        self._domain_object = domain
        self._codomain_object = codomain
        super().__init__(morphisms)

    def domain(self) -> CategoryOfCategories.ElementType:
        return self._domain_object

    def codomain(self) -> CategoryOfCategories.ElementType:
        return self._codomain_object

    # A fixed-endpoint category is its own base for narrowing: ``Mor(C)(A, B).P()`` is a
    # narrowing of it, of the type it declares, and never a root of ``Mor(C)``.

    def narrowing_base(self) -> Category:
        return self

    def narrowing_roots(self) -> tuple[Category, ...]:
        return ()

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        """A morphism of ``Mor(C)`` with these endpoints (POL-CAT-087: the ambient decides which values are its morphisms)."""
        return self.ambient().membership_proposition(candidate) & endpoints(candidate, self._domain_object, self._codomain_object)

    def _chosen_inhabitation(self) -> Decision:
        return hom_inhabitation(self)

    def __call__(self, *args: MorphismData.args, **kwargs: MorphismData.kwargs) -> MorphismCategory.ObjectType:
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

    def one(self) -> MorphismCategory.ObjectType:
        """``1_X``, the unit of the endomorphism monoid ``End_C(X) = Mor(C)(X, X)`` (POL-CAT-023, D84).

        Composition makes ``Mor(C)(X, X)`` a monoid, ``compose`` is its multiplication,
        and this is its unit: ``f * 1_X`` and ``1_X * f`` are ``f`` for every endomorphism
        ``f`` of ``X`` (``specs/functor.md``, "Identity and composition").  This is the one
        spelling of the identity morphism: an identity is named by the operation it is an
        identity for, and this monoid is that operation (D86).
        """
        assert self._domain_object is self._codomain_object, (
            f"{self!r} is not an endomorphism monoid: its endpoints differ, so it has no multiplication"
        )
        return self.base_category()._identity_morphism_(self._domain_object)

    def compose(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        """``Mor(C)(A, C).compose(g, f)`` for ``f: A -> B`` and ``g: B -> C``."""
        assert first.domain() is self._domain_object and second.codomain() is self._codomain_object
        return self.base_category().compose_morphisms(second, first)

    def Monomorphisms(self) -> Category:
        return self.property_subcategory(self.ambient().Monomorphisms())

    def Epimorphisms(self) -> Category:
        return self.property_subcategory(self.ambient().Epimorphisms())

    def Isomorphisms(self) -> Category:
        return self.property_subcategory(self.ambient().Isomorphisms())

    def Endomorphisms(self) -> Category:
        return self.property_subcategory(self.ambient().Endomorphisms())

    def narrowing_type(self) -> type[FixedEndpointProperty[MorphismData, TwoMorphismData]]:
        from sage_categories.cat.properties import FixedEndpointProperty

        return FixedEndpointProperty

    def __repr__(self) -> str:
        return f"{self.ambient()!r}({self._domain_object!r}, {self._codomain_object!r})"
