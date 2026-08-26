"""``Cat()``: the category of categories, and the universal category surface (POL-CAT-002, POL-CAT-050).

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
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed, is_retained_inclusion
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role

if TYPE_CHECKING:
    from sage_categories.cat.canonical import FinitePresentedCategory
    from sage_categories.cat.functors import Functor, FunctorsCategory, NaturalTransformation
    from sage_categories.cat.morphisms import MorphismCategory
    from sage_categories.kernel.decisions import UnknownClass

__all__ = ["Assignment", "Cat", "Category", "CategoryOfCategories", "OnMorphism", "OnObject", "member"]

logger = logging.getLogger("sage_categories")

# The construction data of ``Cat()``: a functor's actions and a natural
# transformation's component assignment (POL-FUN-001).
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

    def __init__(self) -> None:
        self._initialize(Cat())

    def _initialize(self, universe: Category[[OnObject, OnMorphism], [Assignment]]) -> None:
        ObjectOfCategory.__init__(self, universe)
        self._morphism_categories: dict[int, MorphismCategory[MorphismData, TwoMorphismData]] = {}
        self._narrowings: dict[tuple[int, ...], Category[MorphismData, TwoMorphismData]] = {}
        self._identities: MonoDict = MonoDict()
        self._inverses: MonoDict = MonoDict()
        self._points: MonoDict = MonoDict()
        self._arrows: MonoDict = MonoDict()
        self._properties: dict[str, Category[MorphismData, TwoMorphismData]] = {}
        self._catalogues: dict[Role, dict[str, compiler.Entry]] = {}
        self._constructions: dict[str, Category] = {}
        self._limits: MonoDict = MonoDict()
        self._colimits: MonoDict = MonoDict()
        self._slices: MonoDict = MonoDict()
        self._coslices: MonoDict = MonoDict()
        self._wide: MonoDict = MonoDict()
        self._equality = equality_predicate()
        self._ambient_category: Category | None = None
        self._ambient_inclusion: Functor | None = None
        compiler.compile_category(self)

    # -- declarations read by the kernel --------------------------------------

    def structure_functors(self) -> tuple[Functor, ...]:
        """The selected structural graph: immediate functors, in preference order (POL-CAT-016, POL-FUN-003)."""
        return ()

    def classical_stages(self) -> tuple[ObjectOfCategory, ...]:
        """The chosen representing objects whose points are the classical elements; none by default."""
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
        """Record the compiled selection; the ambient is the codomain of its first retained inclusion (POL-CAT-016)."""
        self._selected_functors = functors
        self._ambient_inclusion = next((functor for functor in functors if is_retained_inclusion(functor)), None)
        self._ambient_category = None if self._ambient_inclusion is None else self._ambient_inclusion.codomain()

    def selected_functors(self) -> tuple[Functor, ...]:
        return self._selected_functors

    def has_ambient(self) -> bool:
        """Whether this category is a declared subcategory: one selected functor is a retained inclusion."""
        return self._ambient_category is not None

    def has_full_ambient(self) -> bool:
        """Whether this category is a declared full subcategory: its retained inclusion is placed in ``Fun.FullyFaithful()``.

        A full subcategory has the morphisms, identities, composites, and constructions
        of its ambient between its objects definitionally (POL-CAT-087); a wide
        subcategory, whose inclusion is faithful only, owns its own
        (``specs/functor.md``, "Inclusion functors").
        """
        if self._ambient_inclusion is None:
            return False
        return is_placed(self._ambient_inclusion, self.category().morphism_category(1).FullyFaithful())

    def ambient(self) -> Category[MorphismData, TwoMorphismData]:
        """The category this one is a declared subcategory of, derived from the selected inclusions (POL-CAT-016, POL-FUN-027)."""
        assert self._ambient_category is not None, f"{self!r} declares no inclusion into an ambient category"
        return self._ambient_category

    def hom_inhabited(self, hom_category: Category) -> Decision:
        """The exact decision this category owns for the inhabitation of one of its fixed-endpoint categories ``Mor(self)(A, B)`` or a property narrowing of it (POL-CAT-086, POL-MATH-042).

        A full subcategory has the morphism categories of its ambient (POL-CAT-087); every
        other category decides nothing by default.
        """
        if self.has_full_ambient():
            return self.ambient().hom_inhabited(hom_category)
        return Unknown

    # -- membership and equality ----------------------------------------------

    def equality(self) -> Predicate:
        if self.has_ambient():
            return self.ambient().equality()
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
    # each into ``Mor(self)``.  Every other category, including a wide subcategory
    # declared by a faithful inclusion (``cat/wide.py``), owns these constructions.

    def identity_morphism(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        """The one identity morphism of an object, constructed once (POL-CAT-083).

        An identity is its own inverse and an endomorphism: it retains itself as its
        inverse and is placed in ``Mor(self).Automorphisms()`` by construction
        (POL-CAT-079/081).
        """
        from sage_categories.kernel.refinement import refine

        if member_object not in self._identities:
            identity = self.construct_identity(member_object)
            self._identities[member_object] = identity
            self.retain_inverses(identity, identity)
            refine(identity, self.morphism_category(1).Automorphisms())
        return self._identities[member_object]

    def retain_inverses(self, forward: MorphismOfCategory, backward: MorphismOfCategory) -> None:
        """Record two morphisms as mutually inverse; both enter ``Mor(self).Isomorphisms()`` (POL-MATH-037)."""
        from sage_categories.kernel.refinement import refine

        self._inverses[forward] = backward
        self._inverses[backward] = forward
        isomorphisms = self.morphism_category(1).Isomorphisms()
        refine(forward, isomorphisms)
        refine(backward, isomorphisms)

    def compose_morphisms(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        """``second * first`` through the owned composition; a composite of retained-invertible morphisms retains ``first⁻¹ * second⁻¹``."""
        composite = self.composite(second, first)
        if first in self._inverses and second in self._inverses and composite not in self._inverses:
            self.retain_inverses(composite, self.composite(self._inverses[first], self._inverses[second]))
        return composite

    def inverse_morphism(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        """The inverse of a morphism placed in ``Mor(self).Isomorphisms()`` (POL-CAT-079, POL-KERNEL-025).

        The retained inverse when this category retained one (an identity, a
        two-rule construction, a composite of invertibles); the ambient's inverse for
        a declared subcategory; else the owned symbolic inverse, constructed in
        ``Mor(self)(B, A).Isomorphisms()`` by ``_symbolic_inverse_`` and whose equations
        hold by placement (``specs/undecidable-properties.md``, isomorphism inversion).
        """
        from sage_categories.kernel.refinement import refine

        if morphism in self._inverses:
            return self._inverses[morphism]
        if self.has_ambient():
            inverse = self.ambient().inverse_morphism(morphism)
            refine(inverse, self.morphism_category(1))
            return inverse
        symbolic = self._symbolic_inverse_(morphism)
        self.retain_inverses(morphism, symbolic)
        return symbolic

    def _symbolic_inverse_(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        """The symbolic inverse of ``morphism``, constructed in ``Mor(self)(B, A).Isomorphisms()`` with no executable rule.

        A category whose morphisms carry no data constructs it from none; a category
        whose morphisms carry a rule supplies a rule that fails when evaluated.
        """
        return self.morphism_category(1)(morphism.codomain(), morphism.domain()).Isomorphisms()()

    def element_from_defining_morphism(self, defining_morphism: MorphismOfCategory) -> CategoryPoint:
        """The generalized element ``t: T -> X`` of ``X`` given by a morphism into it (POL-CAT-058).

        A declared subcategory shares its ambient's element values; ``Sets()``
        overrides for its classical points, which carry a datum.
        """
        assert defining_morphism in self.morphism_category(1), f"{defining_morphism!r} is not a morphism of {self!r}"
        if self.has_ambient():
            return self.ambient().element_from_defining_morphism(defining_morphism)
        return self.ElementType(defining_morphism)

    def construct_morphism(
        self,
        domain: ObjectOfCategory,
        codomain: ObjectOfCategory,
        *args: MorphismData.args,
        **kwargs: MorphismData.kwargs,
    ) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        if self.has_full_ambient():
            morphism = self.ambient().construct_morphism(domain, codomain, *args, **kwargs)
            refine(morphism, self.morphism_category(1))
            return morphism
        raise AssertionError(f"{self!r} declares no morphism constructor")

    def construct_identity(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        if self.has_full_ambient():
            identity = self.ambient().identity_morphism(member_object)
            refine(identity, self.morphism_category(1))
            return identity
        raise AssertionError(f"{self!r} declares no identity construction")

    def composite(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        if self.has_full_ambient():
            composite = self.ambient().composite(second, first)
            refine(composite, self.morphism_category(1))
            return composite
        raise AssertionError(f"{self!r} declares no composition")

    def identity_two_morphism(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        if self.has_full_ambient():
            two_cell = self.ambient().identity_two_morphism(morphism)
            refine(two_cell, self.morphism_category(2))
            return two_cell
        two_cells = self.morphism_category(2)
        return two_cells.ObjectType(two_cells, morphism)

    def compose_two_morphisms(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        from sage_categories.kernel.refinement import refine

        if self.has_full_ambient():
            two_cell = self.ambient().compose_two_morphisms(second, first)
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

        if self.has_full_ambient():
            two_cell = self.ambient().construct_two_morphism(first, second, *args, **kwargs)
            refine(two_cell, self.morphism_category(2))
            return two_cell
        assert first is second and not args and not kwargs, f"{self!r} is a 1-category: its only 2-morphisms are identities"
        return self.morphism_category(1).identity_morphism(first)

    # -- points of the category as Cat elements (POL-CAT-058), retained once (POL-CAT-083) --------

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

    # -- universal constructions, defined once (POL-CAT-050/092, POL-CAT-093) --------
    #
    # A full subcategory declared by an inclusion has the constructions of its
    # ambient definitionally (POL-CAT-087); every other category owns its own families.
    # Each family exists for every supplied shape without asserting that the
    # category has those limits (POL-CAT-051): constructing an object needs an
    # owned construction or supplied universal data.

    def Products(self) -> Category:
        """The category of chosen products over every discrete shape."""
        from sage_categories.cat.constructions import ProductsCategory

        if self.has_full_ambient():
            return self.ambient().Products()
        if "Products" not in self._constructions:
            self._constructions["Products"] = ProductsCategory(self)
        return self._constructions["Products"]

    def Coproducts(self) -> Category:
        """The category of chosen coproducts over every discrete shape."""
        from sage_categories.cat.constructions import CoproductsCategory

        if self.has_full_ambient():
            return self.ambient().Coproducts()
        if "Coproducts" not in self._constructions:
            self._constructions["Coproducts"] = CoproductsCategory(self)
        return self._constructions["Coproducts"]

    def Limits(self, shape: Category) -> Category:
        """``C.Limits(I)``: chosen limits of diagrams of shape ``I``, one family per shape."""
        from sage_categories.cat.constructions import limits

        if self.has_full_ambient():
            return self.ambient().Limits(shape)
        assert shape in Cat(), f"{shape!r} is not a shape"
        if shape not in self._limits:
            self._limits[shape] = limits(self, shape)
        return self._limits[shape]

    def Colimits(self, shape: Category) -> Category:
        """``C.Colimits(I)``: chosen colimits of diagrams of shape ``I``, one family per shape."""
        from sage_categories.cat.constructions import colimits

        if self.has_full_ambient():
            return self.ambient().Colimits(shape)
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

    # -- slices, coslices, and the categories of subobjects (POL-FUN-029, POL-CAT-095, POL-SCOPE-003) --

    def SliceOver(self, member_object: ObjectOfCategory) -> Category:
        """``C.SliceOver(x)``: the strict pullback of ``ev_1: Fun([1], C) -> C`` along ``x: 1 -> C``."""
        from sage_categories.cat.slices import slice_over

        if self.has_full_ambient():
            return self.ambient().SliceOver(member_object)
        assert member_object in self, f"{member_object!r} is not an object of {self!r}"
        if member_object not in self._slices:
            self._slices[member_object] = slice_over(self, member_object)
        return self._slices[member_object]

    def CosliceUnder(self, member_object: ObjectOfCategory) -> Category:
        """``C.CosliceUnder(x)``: the strict pullback of ``ev_0: Fun([1], C) -> C`` along ``x: 1 -> C``."""
        from sage_categories.cat.slices import coslice_under

        if self.has_full_ambient():
            return self.ambient().CosliceUnder(member_object)
        assert member_object in self, f"{member_object!r} is not an object of {self!r}"
        if member_object not in self._coslices:
            self._coslices[member_object] = coslice_under(self, member_object)
        return self._coslices[member_object]

    def _morphism_property_family(self, name: str, property_of: Callable[[Category], Category], over: bool) -> Category:
        from sage_categories.cat.slices import MorphismPropertyFamily

        if self.has_full_ambient():
            return self.ambient()._morphism_property_family(name, property_of, over)
        if name not in self._constructions:
            self._constructions[name] = MorphismPropertyFamily(self, name, property_of, over)
        return self._constructions[name]

    def Subobjects(self) -> Category:
        """The monomorphisms of ``C`` as objects of ``Fun([1], C)``; ``C.Subobjects()(x)`` is the fiber over ``x`` in ``C.SliceOver(x)``."""
        return self._morphism_property_family("Subobjects", lambda morphisms: morphisms.Monomorphisms(), True)

    def Superobjects(self) -> Category:
        """The monomorphisms of ``C``; ``C.Superobjects()(x)`` is the fiber under ``x`` in ``C.CosliceUnder(x)``."""
        return self._morphism_property_family("Superobjects", lambda morphisms: morphisms.Monomorphisms(), False)

    def CoveringObjects(self) -> Category:
        """The epimorphisms of ``C``; ``C.CoveringObjects()(y)`` is the fiber over ``y``: pairs ``(X, p: X -> y)`` (POL-CAT-026)."""
        return self._morphism_property_family("CoveringObjects", lambda morphisms: morphisms.Epimorphisms(), True)

    def CoveredObjects(self) -> Category:
        """The epimorphisms of ``C``; ``C.CoveredObjects()(x)`` is the fiber under ``x`` in ``C.CosliceUnder(x)``."""
        return self._morphism_property_family("CoveredObjects", lambda morphisms: morphisms.Epimorphisms(), False)

    # -- wide subcategories and the core (``specs/functor.md``, "Inclusion functors"; ``cat/wide.py``) --

    def WideSubcategory(self, morphism_property: Category) -> Category:
        """The wide subcategory on the morphisms placed in a property subcategory ``P`` of ``Mor(self)``, one per ``P``."""
        from sage_categories.cat.wide import wide_subcategory

        if morphism_property not in self._wide:
            self._wide[morphism_property] = wide_subcategory(self, morphism_property)
        return self._wide[morphism_property]

    def Core(self) -> Category:
        """The core: the wide subcategory on the isomorphisms, the maximal groupoid inside ``self`` (nLab "core"; Mathlib ``CategoryTheory.Core``; both inspected 2026-08-27)."""
        return self.WideSubcategory(self.morphism_category(1).Isomorphisms())

    # -- the chosen sets of objects and morphisms of a small shape (specs/functor.md, "Diagram shapes and universal constructions") -----------------
    #
    # A shape used as a diagram index exposes its objects as an object of ``Sets()``
    # and, when it has finitely many morphisms, its morphisms too; the points of
    # those sets select objects and morphisms.  A category that declares neither
    # has all generalized elements and no enumeration; a set limit over it is then
    # undecided (specs/functor.md, "Diagram shapes and universal constructions").  The sets are typed by their kernel roles here because the
    # theory of ``Sets()`` is constructed through this module; each shape declares
    # the exact ``Sets()`` types.

    def object_set(self) -> ObjectOfCategory:
        """The set of objects, an object of ``Sets()``, when this category declares one."""
        raise AssertionError(f"{self!r} declares no set of objects")

    def object_at(self, point: ElementOfObject) -> ObjectOfCategory:
        """The object selected by a point of ``object_set()``."""
        raise AssertionError(f"{self!r} declares no set of objects")

    def object_point(self, member_object: ObjectOfCategory) -> ElementOfObject:
        """The point of ``object_set()`` selecting an object: the one whose object equals it."""
        return next(point for point in self.object_set() if ask(self.object_at(point) == member_object) is True)

    def morphism_set(self) -> ObjectOfCategory | UnknownClass:
        """The set of morphisms as a finite enumerated object of ``Sets()``, or ``Unknown`` when none is chosen."""
        return Unknown

    def morphism_at(self, point: ElementOfObject) -> MorphismOfCategory:
        """The morphism selected by a point of ``morphism_set()``."""
        raise AssertionError(f"{self!r} declares no set of morphisms")

    def generating_morphisms(self) -> tuple[MorphismOfCategory, ...] | UnknownClass:
        """A finite family of morphisms generating this category under composition, or ``Unknown``.

        The default is every morphism when the morphism set is finite and enumerated.
        """
        morphisms = self.morphism_set()
        if morphisms is Unknown:
            return Unknown
        return tuple(self.morphism_at(point) for point in morphisms)

    def biproduct(self, first: ObjectOfCategory, second: ObjectOfCategory) -> ObjectOfCategory:
        """``X @ Y``, where the category declares biproducts; no owned category declares them."""
        raise AssertionError(f"{self!r} declares no biproduct")

    def exponential(self, exponent: ObjectOfCategory, base: ObjectOfCategory) -> ObjectOfCategory:
        """``base ** exponent``, where the category is declared cartesian closed."""
        if self.has_full_ambient():
            return self.ambient().exponential(exponent, base)
        raise AssertionError(f"{self!r} is not declared cartesian closed")

    # -- property narrowing (POL-CAT-084) ---------------------------------------
    #
    # Every placement is a base category together with a set of root properties it
    # is narrowed by: ``D.P()`` is the narrowing of ``D`` by ``{P}``, and
    # ``D.P().Q()`` the narrowing by ``{P, Q}``.  One object exists per pair, so the
    # same intersection reached in any order is one category (POL-API-009, POL-CAT-084).

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
        if len(ordered) == 1 and ordered[0][1].ambient() is self:
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
        """``Fun(C, D)(on_object, on_morphism)``: a functor from its total actions (POL-FUN-001)."""
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

    def _symbolic_inverse_(self, functor: Functor) -> Functor:
        """The inverse of a functor placed in ``Fun.Isomorphisms()`` by declaration: its actions have no executable rule."""

        def no_action(value: CategoryPoint) -> CategoryPoint:
            assert False, f"the inverse of {functor!r} has no executable action; its equations hold by placement in Isomorphisms()"

        return self.morphism_category(1)(functor.codomain(), functor.domain()).Isomorphisms()(no_action, no_action)

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

    def construct_two_morphism(self, source: CategoryPoint, target: CategoryPoint, assignment: Assignment) -> NaturalTransformation:
        """``Mor(Fun(C, D))(F, G)(assignment)``: a natural transformation from a rule (POL-FUN-007).

        The endpoints are objects of ``Fun(C, D)``: functors, or the points of ``D``
        at stage ``C`` that denote their defining functors (specs/functor.md, "The Mor(n, C) tower").
        """
        from sage_categories.cat.functors import diagram_of

        functors = self.morphism_category(1)
        source_functor, target_functor = diagram_of(source), diagram_of(target)
        assert source_functor in functors and target_functor in functors
        assert source_functor.domain() is target_functor.domain() and source_functor.codomain() is target_functor.codomain()
        return functors.MorphismType(functors.morphism_category(1), source, target, source_functor, target_functor, assignment)

    def identity_two_morphism(self, member_object: CategoryPoint) -> NaturalTransformation:
        from sage_categories.cat.functors import diagram_of

        functor = diagram_of(member_object)
        return self.construct_two_morphism(member_object, member_object, lambda x: functor.on_object(x).identity())

    def compose_two_morphisms(self, second: NaturalTransformation, first: NaturalTransformation) -> NaturalTransformation:
        """Vertical composition: components compose in the codomain category."""
        assert first.codomain() is second.domain()
        return self.construct_two_morphism(
            first.domain(),
            second.codomain(),
            lambda x: second.component(x) * first.component(x),
        )

    # -- the constructions Cat() owns (POL-CAT-050; ``cat/cat_constructions.py``) --------

    def limit_construction(self, shape: Category) -> Callable[[Functor], ObjectOfCategory]:
        """Products over ``Discrete(S)`` and strict pullbacks over ``L(2, 2)``; ``Cat()`` owns no other limit construction."""
        from sage_categories.cat.cat_constructions import product_of_categories, pullback_of_categories
        from sage_categories.cat.shapes import is_discrete

        if is_discrete(shape):
            return product_of_categories
        if shape is self.Horn(2, 2):
            return pullback_of_categories
        raise AssertionError(f"Cat owns no {shape!r}-limit construction: products over Discrete(S) and pullbacks over L(2, 2) are its owned shapes; supply universal data")

    def colimit_construction(self, shape: Category) -> Callable[[Functor], ObjectOfCategory]:
        """Coproducts over ``Discrete(S)``; ``Cat()`` owns no other colimit construction."""
        from sage_categories.cat.cat_constructions import coproduct_of_categories
        from sage_categories.cat.shapes import is_discrete

        if is_discrete(shape):
            return coproduct_of_categories
        raise AssertionError(f"Cat owns no {shape!r}-colimit construction: coproducts over Discrete(S) are its owned shape; supply universal data")

    def exponential(self, exponent: Category, base: Category) -> Category:
        """``D ** C = Fun(C, D)``: ``Cat()`` is cartesian closed (Mathlib ``Cat.exp_obj``; inspected 2026-08-26)."""
        return self.morphism_category(1)(exponent, base)

    # -- finite presented shapes and canonical objects (POL-CAT-083) ----------------

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

        assert dimension == 2, "Cat owns the boundary of the 2-simplex only"
        if ("boundary", (dimension,)) not in self._canonical:
            self._canonical["boundary", (dimension,)] = canonical.boundary(dimension)
        return self._canonical["boundary", (dimension,)]

    def Horn(self, dimension: int, omitted_face: int) -> FinitePresentedCategory:
        from sage_categories.cat import canonical

        assert dimension == 2 and 0 <= omitted_face <= 2, "Cat owns the horns of the 2-simplex only"
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
        """The point of a category at the stage ``T`` given by a functor ``T -> C``."""
        assert defining_functor in self.morphism_category(1)
        return self.ElementType(defining_functor)

    def __repr__(self) -> str:
        return "Cat"


def bootstrap() -> None:
    """Construct the singleton ``Cat()`` once; ``cat/functors.py`` runs this at import.

    The theory modules that ``Category``'s signatures name form an import cycle with
    this one, so their names are bound here, once those modules exist: the kernel
    evaluates the declared signatures when it compiles a category that inherits the
    ``Category`` surface (POL-KERNEL-021).
    """
    global _CAT, FinitePresentedCategory, Functor, FunctorsCategory, MorphismCategory, NaturalTransformation, UnknownClass
    from sage_categories.cat.canonical import FinitePresentedCategory
    from sage_categories.cat.functors import Functor, FunctorsCategory, NaturalTransformation
    from sage_categories.cat.morphisms import MorphismCategory
    from sage_categories.kernel.decisions import UnknownClass

    _CAT = CategoryOfCategories()


def Cat() -> CategoryOfCategories:
    """The category of categories."""
    return _CAT
