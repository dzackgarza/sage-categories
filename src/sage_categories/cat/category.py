"""``Cat()``: the category of categories, and the universal category surface (D02).

``Category`` is the local ``Cat().ObjectType``: every category in this repository
is constructed as an instance of a ``Category`` subclass, placed in ``Cat()``, and
compiled by the kernel into its three role classes ``ObjectType``, ``ElementType``,
and ``MorphismType`` (POL-CAT-002/057).  ``Category`` owns the universal surface:
construction dispatch, membership, the ``Mor(n, C)`` tower, identities and
composition, the equality predicate, and property narrowing (POL-CAT-084).

A category is generic over the data of its morphism constructor (``MorphismData``:
``Sets()`` takes a rule, ``Cat()`` an object action and a morphism action) and of its
2-morphism constructor (``TwoMorphismData``: empty for a 1-category, a component
assignment for ``Cat()``).  ``Mor(K)(A, B)(*data)`` is typed by ``MorphismData``.

``Cat()`` is an object of ``Cat()`` by the stated runtime convention: size is
outside the model, and no kernel operation quantifies over, enumerates, or scans
the objects of ``Cat()``.  The singleton is constructed once, before any other
category, with no structural graph; its ``category()`` is itself.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Hashable
from typing import TYPE_CHECKING, Any, Literal, overload

from sage.structure.coerce_dict import MonoDict

import sage_categories.kernel.compiler as compiler
from sage_categories.cat.equality import equality_predicate
from sage_categories.kernel.decisions import Unknown
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory, Role

if TYPE_CHECKING:
    from sage_categories.cat.canonical import FinitePresentedCategory
    from sage_categories.cat.functors import Functor, FunctorsCategory, NaturalTransformation
    from sage_categories.cat.morphisms import MorphismCategory

__all__ = ["Assignment", "Cat", "Category", "CategoryOfCategories", "OnMorphism", "OnObject", "member"]

logger = logging.getLogger("sage_categories")

# The construction data of ``Cat()``: a functor's actions and a natural
# transformation's component assignment (D05).
type OnObject = Callable[[ObjectOfCategory], ObjectOfCategory]
type OnMorphism = Callable[[MorphismOfCategory], MorphismOfCategory]
type Assignment = Callable[[ObjectOfCategory], MorphismOfCategory]

# ``member(x, C)``: ``x`` is an object of ``C``.  For a plain category the
# proposition is decided by established placement alone (POL-CAT-068/073); a
# property subcategory conjoins its own predicate (``cat/properties.py``).
member = Predicate("member", 2, False)
member.register_handler(is_placed)


class Category[**MorphismData, **TwoMorphismData](ObjectOfCategory):
    """The local ``Cat().ObjectType``: the universal surface of every category."""

    # The ambient category when this category was declared a full subcategory by
    # ``Fun(self, T).FullyFaithful().inclusion()`` (D08); empty otherwise.
    _inclusion_ambient: tuple[Category[MorphismData, TwoMorphismData], ...] = ()

    def __init__(self) -> None:
        self._initialize(Cat())

    def _initialize(self, universe: Category[[OnObject, OnMorphism], [Assignment]]) -> None:
        ObjectOfCategory.__init__(self, universe)
        self._morphism_categories: dict[int, MorphismCategory[MorphismData, TwoMorphismData]] = {}
        self._narrowings: dict[tuple[int, ...], Category[MorphismData, TwoMorphismData]] = {}
        self._identities: MonoDict = MonoDict()
        self._points: MonoDict = MonoDict()
        self._arrows: MonoDict = MonoDict()
        self._properties: dict[str, Category[MorphismData, TwoMorphismData]] = {}
        self._catalogues: dict[Role, dict[str, compiler.Entry]] = {}
        self._constructions: dict[str, Category] = {}
        self._limits: MonoDict = MonoDict()
        self._colimits: MonoDict = MonoDict()
        self._equality = equality_predicate()
        compiler.compile_category(self)

    # -- declarations read by the kernel --------------------------------------

    def structure_functors(self) -> tuple[Functor, ...]:
        """The selected structural graph: immediate functors, in preference order (D07)."""
        return ()

    def classical_stages(self) -> tuple[ObjectOfCategory, ...]:
        """The chosen representing objects whose points are the classical elements; none by default (D06)."""
        return ()

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        """The local role declaration: the nested class of this category's Python class."""
        match role:
            case Role.OBJECT:
                return type(self).ObjectType
            case Role.ELEMENT:
                return type(self).ElementType
            case Role.MORPHISM:
                return type(self).MorphismType
        raise AssertionError(role)

    def role_class(self, role: Role) -> type[CategoryPoint]:
        """The compiled role class installed on this category by the kernel."""
        match role:
            case Role.OBJECT:
                return self.ObjectType
            case Role.ELEMENT:
                return self.ElementType
            case Role.MORPHISM:
                return self.MorphismType
        raise AssertionError(role)

    def role_source(self, role: Role) -> tuple[Category[MorphismData, TwoMorphismData], Role]:
        return self, role

    def catalogues(self) -> dict[Role, dict[str, compiler.Entry]]:
        return self._catalogues

    def select_functors(self, functors: tuple[Functor, ...]) -> None:
        self._selected_functors = functors

    def selected_functors(self) -> tuple[Functor, ...]:
        return self._selected_functors

    def inclusion_ambient(self) -> tuple[Category[MorphismData, TwoMorphismData], ...]:
        """The ambient category when this category is declared as a full subcategory."""
        return self._inclusion_ambient

    def declare_full_subcategory(self, ambient: Category[MorphismData, TwoMorphismData]) -> None:
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

    @overload
    def morphism_category(self, level: Literal[0]) -> Category[MorphismData, TwoMorphismData]: ...

    @overload
    def morphism_category(self, level: Literal[1]) -> MorphismCategory[MorphismData, TwoMorphismData]: ...

    @overload
    def morphism_category(self, level: Literal[2]) -> MorphismCategory[TwoMorphismData, []]: ...

    @overload
    def morphism_category(self, level: int) -> MorphismCategory[[], []]: ...

    def morphism_category(
        self, level: int
    ) -> (
        Category[MorphismData, TwoMorphismData]
        | MorphismCategory[MorphismData, TwoMorphismData]
        | MorphismCategory[TwoMorphismData, []]
        | MorphismCategory[[], []]
    ):
        """``Mor(level, self)``: ``Mor(0, C)`` is ``C`` and ``Mor(n + 1, C)`` is ``Mor(Mor(n, C))``."""
        assert level >= 0
        if level == 0:
            return self
        if level > 1:
            return self.morphism_category(level - 1).morphism_category(1)
        if 1 not in self._morphism_categories:
            self._morphism_categories[1] = self.morphism_category_type()(self)
        return self._morphism_categories[1]

    def morphism_category_type(self) -> type[MorphismCategory[MorphismData, TwoMorphismData]]:
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

    def construct_morphism(
        self,
        domain: ObjectOfCategory,
        codomain: ObjectOfCategory,
        *args: MorphismData.args,
        **kwargs: MorphismData.kwargs,
    ) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            morphism = ambient.construct_morphism(domain, codomain, *args, **kwargs)
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

    def inverse_morphism(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        """The inverse of an isomorphism; a full subcategory inverts in its ambient (POL-KERNEL-025)."""
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            inverse = ambient.inverse_morphism(morphism)
            refine(inverse, self.morphism_category(1))
            return inverse
        raise AssertionError(f"{self!r} declares no inversion of isomorphisms")

    def identity_two_morphism(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            two_cell = ambient.identity_two_morphism(morphism)
            refine(two_cell, self.morphism_category(2))
            return two_cell
        two_cells = self.morphism_category(2)
        return two_cells.ObjectType(two_cells, morphism)

    def compose_two_morphisms(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            two_cell = ambient.compose_two_morphisms(second, first)
            refine(two_cell, self.morphism_category(2))
            return two_cell
        # A 1-category has identity 2-morphisms only: the composite of two identities is either.
        assert first.domain() is first.codomain() and second.domain() is second.codomain()
        assert first.domain() is second.domain()
        return first

    def construct_two_morphism(
        self,
        first: MorphismOfCategory,
        second: MorphismOfCategory,
        *args: TwoMorphismData.args,
        **kwargs: TwoMorphismData.kwargs,
    ) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        for ambient in self._inclusion_ambient:
            two_cell = ambient.construct_two_morphism(first, second, *args, **kwargs)
            refine(two_cell, self.morphism_category(2))
            return two_cell
        assert first is second and not args and not kwargs, f"{self!r} is a 1-category: its only 2-morphisms are identities"
        return self.morphism_category(1).identity_morphism(first)

    # -- points of the category as Cat elements (D06), retained once (D15) --------

    def point_functor(self, member_object: ObjectOfCategory) -> Functor:
        """The stage-``1`` point ``1 -> self`` selecting ``member_object``."""
        from sage_categories.cat.functors import Fun

        if member_object not in self._points:
            self._points[member_object] = Fun(Cat().Terminal(), self)(lambda vertex: member_object, lambda path: member_object.identity())
        return self._points[member_object]

    def arrow_functor(self, morphism: MorphismOfCategory) -> Functor:
        """The stage-``[1]`` point ``[1] -> self`` selecting ``morphism``."""
        from sage_categories.cat.functors import Fun

        if morphism in self._arrows:
            return self._arrows[morphism]
        walking_arrow = Cat().Simplex(1)
        endpoints = {0: morphism.domain(), 1: morphism.codomain()}

        def on_object(vertex: ObjectOfCategory) -> ObjectOfCategory:
            return endpoints[walking_arrow.label(vertex)]

        def on_morphism(path: MorphismOfCategory) -> MorphismOfCategory:
            if path.domain() is path.codomain():
                return on_object(path.domain()).identity()
            return morphism

        self._arrows[morphism] = Fun(walking_arrow, self)(on_object, on_morphism)
        return self._arrows[morphism]

    # -- universal constructions, defined once (D02, D16, POL-CAT-050/092) --------
    #
    # A full subcategory declared by an inclusion has the constructions of its
    # ambient definitionally (D08); every other category owns its own families.
    # Each family exists for every supplied shape without asserting that the
    # category has those limits (POL-CAT-051): constructing an object needs an
    # owned construction or supplied universal data.

    def Products(self) -> Category:
        """The category of chosen products over every discrete shape."""
        from sage_categories.cat.constructions import ProductsCategory

        for ambient in self._inclusion_ambient:
            return ambient.Products()
        if "Products" not in self._constructions:
            self._constructions["Products"] = ProductsCategory(self)
        return self._constructions["Products"]

    def Coproducts(self) -> Category:
        """The category of chosen coproducts over every discrete shape."""
        from sage_categories.cat.constructions import CoproductsCategory

        for ambient in self._inclusion_ambient:
            return ambient.Coproducts()
        if "Coproducts" not in self._constructions:
            self._constructions["Coproducts"] = CoproductsCategory(self)
        return self._constructions["Coproducts"]

    def Limits(self, shape: Category) -> Category:
        """``C.Limits(I)``: chosen limits of diagrams of shape ``I``, one family per shape."""
        from sage_categories.cat.constructions import limits

        for ambient in self._inclusion_ambient:
            return ambient.Limits(shape)
        assert shape in Cat(), f"{shape!r} is not a shape"
        if shape not in self._limits:
            self._limits[shape] = limits(self, shape)
        return self._limits[shape]

    def Colimits(self, shape: Category) -> Category:
        """``C.Colimits(I)``: chosen colimits of diagrams of shape ``I``, one family per shape."""
        from sage_categories.cat.constructions import colimits

        for ambient in self._inclusion_ambient:
            return ambient.Colimits(shape)
        assert shape in Cat(), f"{shape!r} is not a shape"
        if shape not in self._colimits:
            self._colimits[shape] = colimits(self, shape)
        return self._colimits[shape]

    def Pullbacks(self) -> Category:
        """``C.Limits(L(2, 2))``: limits over the walking cospan."""
        return self.Limits(Cat().Horn(2, 2))

    def Pushouts(self) -> Category:
        """``C.Colimits(L(2, 0))``: colimits over the walking span."""
        return self.Colimits(Cat().Horn(2, 0))

    def Equalizers(self) -> Category:
        return self.Limits(Cat().WalkingParallelPair())

    def Coequalizers(self) -> Category:
        return self.Colimits(Cat().WalkingParallelPair())

    def limit_construction(self, shape: Category) -> Callable[[Functor], ObjectOfCategory]:
        """The owned construction of ``I``-limits, when this category declares one."""
        raise AssertionError(f"{self!r} owns no {shape!r}-limit construction; supply universal data")

    def colimit_construction(self, shape: Category) -> Callable[[Functor], ObjectOfCategory]:
        """The owned construction of ``I``-colimits, when this category declares one."""
        raise AssertionError(f"{self!r} owns no {shape!r}-colimit construction; supply universal data")

    def biproduct(self, first: ObjectOfCategory, second: ObjectOfCategory) -> ObjectOfCategory:
        """``X @ Y``, where the category declares biproducts; no category in this unit does."""
        raise AssertionError(f"{self!r} declares no biproduct")

    def exponential(self, exponent: ObjectOfCategory, base: ObjectOfCategory) -> ObjectOfCategory:
        """``base ** exponent``, where the category is declared cartesian closed."""
        for ambient in self._inclusion_ambient:
            return ambient.exponential(exponent, base)
        raise AssertionError(f"{self!r} is not declared cartesian closed")

    # -- property narrowing (POL-CAT-084) ---------------------------------------
    #
    # Every placement is a base category together with a set of root properties it
    # is narrowed by: ``D.P()`` is the narrowing of ``D`` by ``{P}``, and
    # ``D.P().Q()`` the narrowing by ``{P, Q}``.  One object exists per pair, so the
    # same intersection reached in any order is one category (D04, D09).

    def narrowing_base(self) -> Category[MorphismData, TwoMorphismData]:
        """The category this placement narrows; ``self`` when it is no narrowing."""
        return self

    def narrowing_roots(self) -> tuple[Category[MorphismData, TwoMorphismData], ...]:
        """The root properties this placement is narrowed by."""
        return ()

    def intersection(self, roots: tuple[Category[MorphismData, TwoMorphismData], ...]) -> Category[MorphismData, TwoMorphismData]:
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

    def property_subcategory(self, property_category: Category[MorphismData, TwoMorphismData]) -> Category[MorphismData, TwoMorphismData]:
        """``self.P()``: the narrowing of this placement by the roots of ``P`` (POL-CAT-084)."""
        return self.narrowing_base().intersection((*self.narrowing_roots(), *property_category.narrowing_roots()))

    def narrowing_type(self) -> type[Category[MorphismData, TwoMorphismData]]:
        from sage_categories.cat.properties import NarrowedProperty

        return NarrowedProperty


class CategoryOfCategories(Category[[OnObject, OnMorphism], [Assignment]]):
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

    def morphism_category_type(self) -> type[FunctorsCategory]:
        from sage_categories.cat.functors import FunctorsCategory

        return FunctorsCategory

    def two_morphism_type(self) -> type[MorphismOfCategory]:
        from sage_categories.cat.functors import NaturalTransformation

        return NaturalTransformation

    def construct_morphism(
        self,
        domain: Category,
        codomain: Category,
        on_object: OnObject,
        on_morphism: OnMorphism,
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

    def construct_two_morphism(self, source: Functor, target: Functor, assignment: Assignment) -> NaturalTransformation:
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

    # -- the constructions Cat() owns (D02; ``cat/cat_constructions.py``) --------

    def limit_construction(self, shape: Category) -> Callable[[Functor], ObjectOfCategory]:
        """Products over ``Discrete(S)`` and strict pullbacks over ``L(2, 2)``; no other shape in this unit."""
        from sage_categories.cat.cat_constructions import product_of_categories, pullback_of_categories
        from sage_categories.cat.shapes import is_discrete

        if is_discrete(shape):
            return product_of_categories
        if shape is self.Horn(2, 2):
            return pullback_of_categories
        raise AssertionError(f"Cat owns no {shape!r}-limit construction in this unit: products over Discrete(S) and pullbacks over L(2, 2) are its owned shapes; supply universal data")

    def colimit_construction(self, shape: Category) -> Callable[[Functor], ObjectOfCategory]:
        """Coproducts over ``Discrete(S)``; no other shape in this unit."""
        from sage_categories.cat.cat_constructions import coproduct_of_categories
        from sage_categories.cat.shapes import is_discrete

        if is_discrete(shape):
            return coproduct_of_categories
        raise AssertionError(f"Cat owns no {shape!r}-colimit construction in this unit: coproducts over Discrete(S) are its owned shape; supply universal data")

    def exponential(self, exponent: Category, base: Category) -> Category:
        """``D ** C = Fun(C, D)``: ``Cat()`` is cartesian closed (Mathlib ``Cat.exp_obj``; inspected 2026-08-26)."""
        return self.morphism_category(1)(exponent, base)

    # -- finite presented shapes and canonical objects (D15, D16) ----------------

    def __call__(
        self,
        labels: tuple[Hashable, ...],
        generators: tuple[tuple[str, Hashable, Hashable], ...],
        relations: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
    ) -> FinitePresentedCategory:
        """``Cat()(labels, generators, relations)``: the category presented by finitely many objects, generating morphisms, and relations."""
        from sage_categories.cat import canonical

        return canonical.FinitePresentedCategory(f"Presented{tuple(labels)!r}", tuple(labels), tuple(generators), tuple(relations))

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

    def element_from_defining_morphism(self, defining_functor: Functor) -> CategoryPoint:
        """The point of a category at the stage ``T`` given by a functor ``T -> C`` (D06)."""
        assert defining_functor in self.morphism_category(1)
        return self.ElementType(defining_functor)

    def __repr__(self) -> str:
        return "Cat"


def bootstrap() -> None:
    """Construct the singleton ``Cat()`` once; ``cat/functors.py`` runs this at import.

    The theory modules that ``Category``'s signatures name form an import cycle with
    this one, so their names are bound here, once those modules exist: the kernel
    evaluates the declared signatures when it compiles a category that inherits the
    ``Category`` surface (D13).
    """
    global _CAT, FinitePresentedCategory, Functor, FunctorsCategory, MorphismCategory, NaturalTransformation
    from sage_categories.cat.canonical import FinitePresentedCategory
    from sage_categories.cat.functors import Functor, FunctorsCategory, NaturalTransformation
    from sage_categories.cat.morphisms import MorphismCategory

    _CAT = CategoryOfCategories()


def Cat() -> CategoryOfCategories:
    """The category of categories."""
    return _CAT
