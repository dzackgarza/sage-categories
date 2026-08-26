"""``Cat()``: the category of categories, and the universal category surface (D02).

``Category`` is the local ``Cat().ObjectType``: every category in this repository
is constructed as an instance of a ``Category`` subclass, placed in ``Cat()``, and
compiled by the kernel into its three role classes ``ObjectType``, ``ElementType``,
and ``MorphismType`` (POL-CAT-002/057).  ``Category`` owns the universal surface:
construction dispatch, membership, the ``Mor(n, C)`` tower, identities and
composition, the equality predicate, and property narrowing (POL-CAT-084).

``Cat()`` is an object of ``Cat()`` by the stated runtime convention: size is
outside the model, and no kernel operation quantifies over, enumerates, or scans
the objects of ``Cat()``.  The singleton is constructed once, before any other
category, with no structural graph; its ``category()`` is itself.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from sage.structure.coerce_dict import MonoDict

import sage_categories.kernel.compiler as compiler
from sage_categories.cat.equality import equality_predicate
from sage_categories.kernel.decisions import Unknown
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory, Role

if TYPE_CHECKING:
    from sage_categories.cat.canonical import FinitePresentedCategory
    from sage_categories.cat.functors import Functor, NaturalTransformation
    from sage_categories.cat.morphisms import MorphismCategory

__all__ = ["Cat", "Category", "CategoryOfCategories", "member"]

logger = logging.getLogger("sage_categories")

# ``member(x, C)``: ``x`` is an object of ``C``.  For a plain category the
# proposition is decided by established placement alone (POL-CAT-068/073); a
# property subcategory conjoins its own predicate (``cat/properties.py``).
member = Predicate("member", 2, False)
member.register_handler(is_placed)


class Category(ObjectOfCategory):
    """The local ``Cat().ObjectType``: the universal surface of every category."""

    # The ambient category when this category was declared a full subcategory by
    # ``Fun(self, T).FullyFaithful().inclusion()`` (D08); empty otherwise.
    _inclusion_ambient: tuple[Category, ...] = ()

    def __init__(self) -> None:
        self._initialize(Cat())

    def _initialize(self, universe: Category) -> None:
        ObjectOfCategory.__init__(self, universe)
        self._morphism_categories: dict[int, MorphismCategory] = {}
        self._narrowings: dict[tuple[int, ...], Category] = {}
        self._identities: MonoDict = MonoDict()
        self._properties: dict[str, Category] = {}
        self._catalogues: dict[Role, dict[str, compiler.Entry]] = {}
        self._equality = equality_predicate()
        compiler.compile_category(self)

    # -- declarations read by the kernel --------------------------------------

    def structure_functors(self) -> tuple[Functor, ...]:
        """The selected structural graph: immediate functors, in preference order (D07)."""
        return ()

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        return getattr(type(self), role.value)

    def role_class(self, role: Role) -> type[CategoryPoint]:
        return getattr(self, role.value)

    def role_source(self, role: Role) -> tuple[Category, Role]:
        return self, role

    def catalogues(self) -> dict[Role, dict[str, compiler.Entry]]:
        return self._catalogues

    def select_functors(self, functors: tuple[Functor, ...]) -> None:
        self._selected_functors = functors

    def selected_functors(self) -> tuple[Functor, ...]:
        return self._selected_functors

    def inclusion_ambient(self) -> tuple[Category, ...]:
        """The ambient category when this category is declared as a full subcategory."""
        return self._inclusion_ambient

    def declare_full_subcategory(self, ambient: Category) -> None:
        """Record the declaration ``Fun(self, ambient).FullyFaithful().inclusion()`` (D08)."""
        if not any(ambient is declared for declared in self._inclusion_ambient):
            self._inclusion_ambient = (*self._inclusion_ambient, ambient)

    # -- membership and equality ----------------------------------------------

    def equality(self) -> Predicate:
        for ambient in self._inclusion_ambient:
            return ambient.equality()
        return self._equality

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return member(candidate, self)

    def __contains__(self, candidate: Any) -> bool:
        decision = ask(self.membership_proposition(candidate))
        if decision is Unknown:
            logger.info("membership of %r in %r was not established", candidate, self)
            return False
        return decision is True

    # -- the Mor(n, C) tower ----------------------------------------------------

    def morphism_category(self, level: int) -> Category:
        """``Mor(level, self)``: ``Mor(0, C)`` is ``C`` and ``Mor(n + 1, C)`` is ``Mor(Mor(n, C))``."""
        assert level >= 0
        if level == 0:
            return self
        if level > 1:
            return self.morphism_category(level - 1).morphism_category(1)
        if 1 not in self._morphism_categories:
            self._morphism_categories[1] = self.morphism_category_type()(self)
        return self._morphism_categories[1]

    def morphism_category_type(self) -> type[MorphismCategory]:
        from sage_categories.cat.morphisms import MorphismCategory

        return MorphismCategory

    def two_morphism_type(self) -> type[MorphismOfCategory]:
        """The local role of the morphisms of ``Mor(self)``; identities only for a 1-category."""
        from sage_categories.cat.morphisms import IdentityTwoCell

        return IdentityTwoCell

    def base_category(self) -> Category:
        """The category ``C`` such that this category is a subcategory of ``Mor(C)``."""
        for found in compiler.reachable(compiler.node(self, Role.OBJECT)):
            if found.role is Role.MORPHISM:
                return found.category
        raise AssertionError(f"{self!r} is not a category of morphisms")

    # -- identities and composition -------------------------------------------
    #
    # A full subcategory has exactly the morphisms, identities, and composites of its
    # ambient between its objects (Mathlib ``InducedCategory``): a category declared by
    # ``Fun(self, T).FullyFaithful().inclusion()`` obtains them from ``T`` and refines
    # each into ``Mor(self)``.  Every other category owns these constructions.

    def identity_morphism(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        """The one identity morphism of an object, constructed once (D15).

        An identity is its own inverse and an endomorphism: it is placed in
        ``Mor(self).Automorphisms()`` by construction (POL-CAT-079/081).
        """
        from sage_categories.kernel.refinement import refine

        if member_object not in self._identities:
            identity = self.construct_identity(member_object)
            refine(identity, self.morphism_category(1).Automorphisms())
            self._identities[member_object] = identity
        return self._identities[member_object]

    def construct_morphism(self, domain: ObjectOfCategory, codomain: ObjectOfCategory, *data: Any) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            morphism = ambient.construct_morphism(domain, codomain, *data)
            refine(morphism, self.morphism_category(1))
            return morphism
        raise AssertionError(f"{self!r} declares no morphism constructor")

    def construct_identity(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            identity = ambient.identity_morphism(member_object)
            refine(identity, self.morphism_category(1))
            return identity
        raise AssertionError(f"{self!r} declares no identity construction")

    def composite(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            composite = ambient.composite(second, first)
            refine(composite, self.morphism_category(1))
            return composite
        raise AssertionError(f"{self!r} declares no composition")

    def identity_two_morphism(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        from sage_categories.cat.morphisms import Mor
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            two_cell = ambient.identity_two_morphism(morphism)
            refine(two_cell, Mor(2, self))
            return two_cell
        two_cells = Mor(2, self)
        return two_cells.ObjectType(two_cells, morphism)

    def compose_two_morphisms(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        from sage_categories.cat.morphisms import Mor
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            two_cell = ambient.compose_two_morphisms(second, first)
            refine(two_cell, Mor(2, self))
            return two_cell
        # A 1-category has identity 2-morphisms only: the composite of two identities is either.
        assert first.domain() is first.codomain() and second.domain() is second.codomain()
        assert first.domain() is second.domain()
        return first

    def construct_two_morphism(self, first: MorphismOfCategory, second: MorphismOfCategory, *data: Any) -> MorphismOfCategory:
        from sage_categories.cat.morphisms import Mor
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            two_cell = ambient.construct_two_morphism(first, second, *data)
            refine(two_cell, Mor(2, self))
            return two_cell
        assert first is second and not data, f"{self!r} is a 1-category: its only 2-morphisms are identities"
        return self.morphism_category(1).identity_morphism(first)

    # -- points of the category as Cat elements (D06) --------------------------

    def point_functor(self, member_object: ObjectOfCategory) -> Functor:
        """The stage-``1`` point ``1 -> self`` selecting ``member_object``."""
        from sage_categories.cat.functors import Fun

        return Fun(Cat().Terminal(), self)(lambda vertex: member_object, lambda path: member_object.identity())

    def arrow_functor(self, morphism: MorphismOfCategory) -> Functor:
        """The stage-``[1]`` point ``[1] -> self`` selecting ``morphism``."""
        from sage_categories.cat.functors import Fun

        walking_arrow = Cat().Simplex(1)
        endpoints = {0: morphism.domain(), 1: morphism.codomain()}

        def on_object(vertex: ObjectOfCategory) -> ObjectOfCategory:
            return endpoints[walking_arrow.label(vertex)]

        def on_morphism(path: MorphismOfCategory) -> MorphismOfCategory:
            if path.domain() is path.codomain():
                return on_object(path.domain()).identity()
            return morphism

        return Fun(walking_arrow, self)(on_object, on_morphism)

    # -- property narrowing (POL-CAT-084) ---------------------------------------
    #
    # Every placement is a base category together with a set of root properties it
    # is narrowed by: ``D.P()`` is the narrowing of ``D`` by ``{P}``, and
    # ``D.P().Q()`` the narrowing by ``{P, Q}``.  One object exists per pair, so the
    # same intersection reached in any order is one category (D04, D09).

    def narrowing_base(self) -> Category:
        """The category this placement narrows; ``self`` when it is no narrowing."""
        return self

    def narrowing_roots(self) -> tuple[Category, ...]:
        """The root properties this placement is narrowed by."""
        return ()

    def intersection(self, roots: tuple[Category, ...]) -> Category:
        """The narrowing of ``self`` by the given root properties, one object per set of roots."""
        ordered = tuple(sorted({root.ordinal(): root for root in roots}.items()))
        if not ordered:
            return self
        if len(ordered) == 1 and ordered[0][1].inclusion_ambient()[0] is self:
            return ordered[0][1]
        key = tuple(ordinal for ordinal, _ in ordered)
        if key not in self._narrowings:
            self._narrowings[key] = self.narrowing_type()(self, tuple(root for _, root in ordered))
        return self._narrowings[key]

    def property_subcategory(self, property_category: Category) -> Category:
        """``self.P()``: the narrowing of this placement by the roots of ``P`` (POL-CAT-084)."""
        return self.narrowing_base().intersection((*self.narrowing_roots(), *property_category.narrowing_roots()))

    def narrowing_type(self) -> type[Category]:
        from sage_categories.cat.properties import NarrowedProperty

        return NarrowedProperty


class CategoryOfCategories(Category):
    """The singleton ``Cat()``."""

    def __init__(self) -> None:
        self._canonical: dict[tuple[str, tuple[int, ...]], FinitePresentedCategory] = {}
        self._initialize(self)

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        from sage_categories.cat.elements import CategoryPoint as PointRole
        from sage_categories.cat.functors import Functor

        match role:
            case Role.OBJECT:
                return Category
            case Role.ELEMENT:
                return PointRole
            case Role.MORPHISM:
                return Functor
        raise AssertionError(role)

    def morphism_category_type(self) -> type[MorphismCategory]:
        from sage_categories.cat.functors import FunctorsCategory

        return FunctorsCategory

    def two_morphism_type(self) -> type[MorphismOfCategory]:
        from sage_categories.cat.functors import NaturalTransformation

        return NaturalTransformation

    def construct_morphism(
        self,
        domain: Category,
        codomain: Category,
        on_object: Any,
        on_morphism: Any,
    ) -> Functor:
        """``Fun(C, D)(on_object, on_morphism)``: a functor from its total actions (D05)."""
        assert domain in self and codomain in self
        return self.MorphismType(self.morphism_category(1), domain, codomain, on_object, on_morphism)

    def construct_identity(self, category: Category) -> Functor:
        from sage_categories.cat.functors import Fun
        from sage_categories.kernel.refinement import refine

        identity = self.construct_morphism(category, category, lambda x: x, lambda f: f)
        # The identity functor is an equivalence: Mathlib ``CategoryTheory.Functor.id``
        # with ``IsEquivalence`` of the identity (inspected 2026-08-26).
        refine(identity, Fun(category, category).Equivalences())
        return identity

    def composite(self, second: Functor, first: Functor) -> Functor:
        """``second * first``: the composite functor, rules composed (Mathlib ``Functor.comp``)."""
        from sage_categories.cat.functors import Fun
        from sage_categories.kernel.refinement import refine

        assert first in self.morphism_category(1) and second in self.morphism_category(1)
        assert first.codomain() is second.domain()
        composite = self.construct_morphism(
            first.domain(),
            second.codomain(),
            lambda x: second.on_object(first.on_object(x)),
            lambda f: second.on_morphism(first.on_morphism(f)),
        )
        # Full, faithful, and fully faithful functors compose (Mathlib
        # ``Functor.FullyFaithful.comp``, ``Full.comp``, ``Faithful.comp``; inspected 2026-08-26).
        for property_category in (Fun.FullyFaithful(), Fun.Full(), Fun.Faithful()):
            if is_placed(first, property_category) and is_placed(second, property_category):
                refine(composite, property_category)
        return composite

    def construct_two_morphism(self, source: Functor, target: Functor, assignment: Any) -> NaturalTransformation:
        """``Mor(Fun(C, D))(F, G)(assignment)``: a natural transformation from a rule (D05)."""
        functors = self.morphism_category(1)
        assert source in functors and target in functors
        assert source.domain() is target.domain() and source.codomain() is target.codomain()
        return functors.MorphismType(functors.morphism_category(1), source, target, assignment)

    def identity_two_morphism(self, functor: Functor) -> NaturalTransformation:
        return self.construct_two_morphism(functor, functor, lambda x: functor.on_object(x).identity())

    def compose_two_morphisms(self, second: NaturalTransformation, first: NaturalTransformation) -> NaturalTransformation:
        """Vertical composition: components compose in the codomain category."""
        assert first.codomain() is second.domain()
        return self.construct_two_morphism(
            first.domain(),
            second.codomain(),
            lambda x: second.component(x) * first.component(x),
        )

    # -- canonical objects (D15) -------------------------------------------------

    def Empty(self) -> FinitePresentedCategory:
        from sage_categories.cat import canonical

        if ("empty", ()) not in self._canonical:
            self._canonical["empty", ()] = canonical.empty_category()
        return self._canonical["empty", ()]

    def Terminal(self) -> FinitePresentedCategory:
        return self.Simplex(0)

    def Simplex(self, dimension: int) -> FinitePresentedCategory:
        from sage_categories.cat import canonical

        assert dimension >= 0
        if ("simplex", (dimension,)) not in self._canonical:
            self._canonical["simplex", (dimension,)] = canonical.simplex(dimension)
        return self._canonical["simplex", (dimension,)]

    def Boundary(self, dimension: int) -> FinitePresentedCategory:
        from sage_categories.cat import canonical

        assert dimension == 2, "this unit constructs the boundary of the 2-simplex"
        if ("boundary", (dimension,)) not in self._canonical:
            self._canonical["boundary", (dimension,)] = canonical.boundary(dimension)
        return self._canonical["boundary", (dimension,)]

    def Horn(self, dimension: int, omitted_face: int) -> FinitePresentedCategory:
        from sage_categories.cat import canonical

        assert dimension == 2 and 0 <= omitted_face <= 2, "this unit constructs the horns of the 2-simplex"
        if omitted_face == 1:
            # The free category on ``0 -> 1 -> 2`` contains the composite ``0 -> 2``:
            # it is the walking composable pair ``[2]`` (nLab "walking structure":
            # the walking composable pair is the (2,1)-horn category; inspected 2026-08-26).
            return self.Simplex(2)
        if ("horn", (dimension, omitted_face)) not in self._canonical:
            self._canonical["horn", (dimension, omitted_face)] = canonical.horn(dimension, omitted_face)
        return self._canonical["horn", (dimension, omitted_face)]

    def WalkingIsomorphism(self) -> FinitePresentedCategory:
        from sage_categories.cat import canonical

        if ("walking isomorphism", ()) not in self._canonical:
            self._canonical["walking isomorphism", ()] = canonical.walking_isomorphism()
        return self._canonical["walking isomorphism", ()]

    def WalkingParallelPair(self) -> FinitePresentedCategory:
        from sage_categories.cat import canonical

        if ("walking parallel pair", ()) not in self._canonical:
            self._canonical["walking parallel pair", ()] = canonical.walking_parallel_pair()
        return self._canonical["walking parallel pair", ()]

    def classical_stages(self) -> tuple[FinitePresentedCategory, ...]:
        return (self.Terminal(), self.Simplex(1))

    def __repr__(self) -> str:
        return "Cat"


def bootstrap() -> None:
    """Construct the singleton ``Cat()`` once; ``cat/functors.py`` runs this at import."""
    global _CAT
    _CAT = CategoryOfCategories()


def Cat() -> CategoryOfCategories:
    """The category of categories."""
    return _CAT
