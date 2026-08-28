"""``Cat()``: the category of categories, and the universal category surface (POL-CAT-002, POL-CAT-050).

``CategoryDeclaration`` is the local ``Cat().ObjectType`` declaration.  After
bootstrap, ``Category`` is bound to the compiled ``Cat().ObjectType``.  Every
category in this repository is constructed as an instance of a ``Category``
subclass, placed in ``Cat()``, and
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

import inspect
import itertools
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Literal, overload

from sage.misc.cachefunc import cached_method
from sage.structure.coerce_dict import MonoDict, TripleDict

import sage_categories.kernel.compiler as compiler
from sage_categories.cat.equality import equality_predicate
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed, is_subcategory, refine, traces_placement
from sage_categories.kernel.roles import (
    CategoryPoint,
    ElementOfObject,
    MorphismOfCategory,
    ObjectOfCategory,
    Role,
    role_of,
)

if TYPE_CHECKING:
    from sage_categories.cat.canonical import FinitePresentedCategory
    from sage_categories.cat.declarations import CategoryFamily
    from sage_categories.cat.functors import Fun, Functor, FunctorsCategory, NaturalTransformation
    from sage_categories.cat.morphisms import MorphismCategory
    from sage_categories.cat.points import PointCategory
    from sage_categories.kernel.construction import ElementConstructionInput, MorphismConstructionInput, ObjectConstructionInput

__all__ = ["Assignment", "Cat", "Category", "CategoryOfCategories", "OnMorphism", "OnObject", "member"]


# The compilation order of categories: a category takes its ordinal after its
# selected functors exist, so decreasing ordinal is a linear extension of the
# selected graph; the kernel linearizes role classes by it and narrowings are
# canonicalized by the ordinals of their roots.
_category_ordinals = itertools.count()

# The construction data of ``Cat()``: a functor's actions and a natural
# transformation's component assignment (POL-FUN-001).
type OnObject = Callable[[ObjectOfCategory], ObjectOfCategory]
type OnMorphism = Callable[[MorphismOfCategory], MorphismOfCategory]
type Assignment = Callable[[ObjectOfCategory], MorphismOfCategory]

# ``member(x, C)``: ``x`` is an object of ``C``.  For a plain category the
# proposition is decided by established placement alone (POL-CAT-068/073); a
# property subcategory conjoins its own predicate (``cat/properties.py``).
member: Predicate = Predicate("member", 2, False)
member.register_handler(is_placed)


class CategoryDeclaration[**MorphismData, **TwoMorphismData](ObjectOfCategory):
    """The local ``Cat().ObjectType`` declaration."""

    # The declaration this class implements, named in the body of a category class that
    # claims one ``Cat`` made (D80).  A class that names none declares its own category.
    _implements: ClassVar[str]

    def __init__(self, data: None = None) -> None:
        super().__init__()
        self._initialize(self.category())

    def __init_subclass__(cls) -> None:
        """Connect a class that names the declaration it implements (D80).

        This is ``PropertySubcategory.__init_subclass__`` generalized from an axiom
        subcategory to a declared base category: there too the implementing class names
        what it implements in its own body, and the declaration holds the link.
        """
        super().__init_subclass__()
        name = cls.__dict__.get("_implements")
        if name is not None:
            Cat().implement(name, cls)

    def __mul__(self, other: Category) -> Category:
        """``C * D``: the product category."""
        return Cat().Products()((self, other))

    def __add__(self, other: Category) -> Category:
        """``C + D``: the coproduct category."""
        return Cat().Coproducts()((self, other))

    def __pow__(self, exponent: Category) -> Category:
        """``D ** C = Fun(C, D)``: the functor category."""
        from sage_categories.cat.functors import Fun

        return Fun(exponent, self)

    def _initialize(self, universe: Category[[OnObject, OnMorphism], [Assignment]]) -> None:
        self._morphism_categories: dict[int, MorphismCategory[MorphismData, TwoMorphismData]] = {}
        self._narrowings: dict[tuple[int, ...], Category[MorphismData, TwoMorphismData]] = {}
        self._identities: MonoDict = MonoDict()
        self._inverses: MonoDict = MonoDict()
        self._points: MonoDict = MonoDict()
        self._arrows: MonoDict = MonoDict()
        self._represented: MonoDict = MonoDict()
        self._elements: MonoDict = MonoDict()
        self._catalogues: dict[Role, dict[str, compiler.Entry]] = {}
        self._limits: MonoDict = MonoDict()
        self._colimits: MonoDict = MonoDict()
        self._slices: MonoDict = MonoDict()
        self._coslices: MonoDict = MonoDict()
        self._wide: MonoDict = MonoDict()
        self._retained_data: MonoDict = MonoDict()
        self._equality = equality_predicate()
        self._ambient_category: Category | None = None
        self._ambient_monomorphism: Functor | None = None
        # The selected functors are constructed before the ordinal is taken, so every
        # codomain (and every narrowing a declaration constructs) is older than this
        # category.
        functors = tuple(self.structure_functors())
        self._ordinal = next(_category_ordinals)
        compiler.compile_category(self, functors)
        from sage_categories.kernel.refinement import place

        place(self, universe)

    # -- declarations read by the kernel --------------------------------------

    def universe(self) -> CategoryOfCategories:
        """``Cat()``, whose objects are the categories.

        Not ``category()``: that is the strongest placement established for this
        category, and a point category ``{self}`` narrows it (POL-CAT-083).  Anything
        that means "the functor category" or "the shapes" wants this one.
        """
        return Cat()

    def ordinal(self) -> int:
        """The construction order of this category among all categories."""
        return self._ordinal

    def recompile(self) -> None:
        """Compile this category's roles again from its current declarations (D80).

        An implementation claims a declared category after ``Cat`` constructed it, and
        the declared object is the final one: its class was strengthened in place, and
        its nested classes and selected functors are read again here.  The ordinal is not
        retaken, so every codomain stays older than the category that selects it.
        """
        compiler.recompile_category(self, tuple(self.structure_functors()))

    def structure_functors(self) -> tuple[Functor, ...]:
        """The selected structural graph: immediate functors, in preference order (POL-CAT-016, POL-FUN-003)."""
        return ()

    def separating_family(self) -> tuple[ObjectOfCategory, ...]:
        """The chosen objects whose hom functors are jointly faithful; none by default (POL-MATH-037)."""
        return ()

    def structural_image(self, value: CategoryPoint) -> CategoryPoint:
        """The image of ``value`` in this category under the selected structural route to it.

        A method declared by ``C`` runs on every structural descendant of ``C`` with the
        descendant as its receiver (POL-KERNEL-018), so inside a ``Sets()`` declaration
        ``self`` can be a poset while the method is about that poset's underlying set.
        ``C.structural_image(x)`` is the value such a method is about: the image the kernel
        computed and retained when ``x`` was constructed (POL-KERNEL-029).  For a value of
        ``C`` itself it is that value.

        This is the image under the composite of the selected functors, not the image of a
        morphism: ``Sets().ChosenSubsets().image_of(f)`` is the set-theoretic image of a
        map, a different operation with its own name (POL-CAT-011).

        This reads the retention.  It constructs nothing, chooses no route, and owns no
        table, so a leaf keeps none (``specs/resolution.md``, final decision 6).
        """
        from sage_categories.kernel.transport import transport

        role = role_of(value)
        assert role is not None, f"{value!r} is not an owned value"
        return transport(value, compiler.node(self, role))

    def retain_datum[Datum](self, value: CategoryPoint, datum: Datum) -> None:
        """Retain the datum ``value`` was constructed with as an object of this category.

        A category whose constructor refines an existing value in place -- a property
        subcategory, a construction family -- adds no construction input of its own
        (``kernel/refinement.py``), so the structure it chose has nowhere else to live:
        the base set of ``2 ** X``, the enumeration engine of a set of finite subsets, the
        basepoint of ``X^(S)``.  It is retained here, by identity, once per value
        (POL-KERNEL-001).
        """
        assert value not in self._retained_data, f"{value!r} already retains a datum of {self!r}"
        self._retained_data[value] = datum

    def retained_datum[Datum](self, value: CategoryPoint) -> Datum:
        """The datum ``value`` was constructed with as an object of this category."""
        assert value in self._retained_data, f"{value!r} retains no datum of {self!r}"
        return self._retained_data[value]

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        """The local role declaration: the nested class of this category's Python class.

        ``Role.OBJECT.value`` is ``"ObjectType"``: a role *is* the name the category
        writes for that mathematical kind (POL-KERNEL-028), so this reads the one
        declaration the architecture fixes, not a capability discovered by probing.

        A category states only the roles whose mathematics it introduces; a role it
        declares nothing for gets the empty local declaration, which names this category
        as the node's owner and stands on the role's kernel base (POL-KERNEL-028).
        """
        declared = getattr(type(self), role.value, None)
        return declared if declared is not None else compiler.empty_local_role(self, role)

    def role_class(self, role: Role) -> type[CategoryPoint]:
        """The compiled role class the kernel installed on this category value.

        One name per kind: the declaration is the nested class of the category's Python
        class and the compiled class is the attribute of the category value, which
        shadows it.
        """
        return getattr(self, role.value)

    def role_source(self, role: Role) -> tuple[Category[MorphismData, TwoMorphismData], Role]:
        return self, role

    def catalogues(self) -> dict[Role, dict[str, compiler.Entry]]:
        return self._catalogues

    def select_functors(self, functors: tuple[Functor, ...]) -> None:
        """Record the compiled selection; the ambient is the codomain of its first placement-tracing functor (POL-CAT-016)."""
        self._selected_functors = functors
        self._ambient_monomorphism = next((functor for functor in functors if traces_placement(functor)), None)
        self._ambient_category = None if self._ambient_monomorphism is None else self._ambient_monomorphism.codomain()

    def selected_functors(self) -> tuple[Functor, ...]:
        return self._selected_functors

    def has_ambient(self) -> bool:
        """Whether this category is a declared subcategory: one selected functor traces placement (POL-FUN-036)."""
        return self._ambient_category is not None

    def has_full_ambient(self) -> bool:
        """Whether this category is a declared full subcategory: its subcategory monomorphism is also full.

        A full subcategory has the morphisms, identities, composites, and constructions
        of its ambient between its objects definitionally (POL-CAT-087); a wide
        subcategory, whose monomorphism is not full, owns its own
        (``specs/functor.md``, "Monomorphisms of ``Cat()`` and placement").
        """
        if self._ambient_monomorphism is None:
            return False
        return is_placed(self._ambient_monomorphism, self.universe().morphism_category(1).Full())

    def ambient(self) -> Category[MorphismData, TwoMorphismData]:
        """The category this one is a declared subcategory of, derived from the selected functors (POL-CAT-016, POL-FUN-036)."""
        assert self._ambient_category is not None, f"{self!r} declares no monomorphism into an ambient category"
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
        """``x in C``: established placement, which is two-valued (POL-CAT-068).

        A value entered ``C`` or it did not, so ``member`` never returns ``Unknown``.  A
        subcategory whose membership rests on a mathematical predicate rather than on
        placement -- endpoint equality in ``Mor(C)(A, B)``, for one -- can be undecided,
        and that case fails loudly here rather than being reported as non-membership.
        ``ask(C.membership_proposition(x))`` is the three-valued question.
        """
        decision = ask(self.membership_proposition(candidate))
        assert decision is not Unknown, (
            f"membership of {candidate!r} in {self!r} is not established by the available data and algorithms; "
            f"ask(this_category.membership_proposition(candidate)) for the three-valued answer"
        )
        return bool(decision)

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
    # ``Fun(self, T).Monomorphisms().Isofibrations().Full()()`` obtains them from ``T`` and refines
    # each into ``Mor(self)``.  Every other category, including a wide subcategory
    # declared by a subcategory monomorphism (``cat/wide.py``), owns these constructions.

    def identity_morphism(self, member_object: CategoryPoint) -> MorphismOfCategory:
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

        The element is retained by that exact morphism (POL-CAT-066): one defining
        morphism names one generalized element, so two callers reach one value and one
        construction input.  A declared subcategory shares its ambient's element values;
        ``Sets()`` overrides for its points, which carry a datum.
        """
        assert defining_morphism in self.morphism_category(1), f"{defining_morphism!r} is not a morphism of {self!r}"
        if self.has_ambient():
            return self.ambient().element_from_defining_morphism(defining_morphism)
        if defining_morphism not in self._elements:
            self._elements[defining_morphism] = self.ElementType(defining_morphism)
        return self._elements[defining_morphism]

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
        return two_cells.ObjectType(category=two_cells, domain=morphism, codomain=morphism)

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

    def point_functor(self, member_object: CategoryPoint) -> Functor:
        """The point ``* -> self`` selecting the object ``member_object``.

        The objects of ``Mor(C)`` are the morphisms of ``C``, so ``member_object`` is a
        morphism there and its identity is the one ``Mor(C)`` supplies (POL-CAT-021).
        """
        from sage_categories.cat.functors import Fun

        if member_object not in self._points:
            self._points[member_object] = Fun(Cat().Terminal(), self)(
                lambda vertex: member_object, lambda path: self.identity_morphism(member_object)
            )
        return self._points[member_object]

    def arrow_functor(self, morphism: MorphismOfCategory) -> Functor:
        """The diagram ``[1] -> self`` of shape the walking arrow that ``morphism`` denotes."""
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

    def represented_functor(self) -> Functor:
        """``U_C = Mor(C)(G_C, -): C -> Sets()``, the functor represented by the chosen separator.

        Its value at ``X`` is the set of morphisms ``G_C -> X``, whose points are exactly
        the points of ``X``; its value at ``f: X -> Y`` is postcomposition
        ``u |-> f . u``.  This is Mathlib's co-Yoneda embedding at ``G_C``
        (``Mathlib/CategoryTheory/Yoneda.lean:87-95``, inspected 2026-08-27: "The co-Yoneda
        embedding, as a functor from ``Cᵒᵖ`` into co-presheaves on ``C``", with the
        unification hint ``(coyoneda.obj (op X)).obj Y = X ⟶ Y``).

        The leaf's assertion that its separating family separates is what makes ``U_C``
        faithful (POL-MATH-037); this construction states the functor and not that
        property.  A separating family of several states that its hom functors
        ``Mor(C)(G^j, -)`` are *jointly* faithful (nLab, separator,
        https://ncatlab.org/nlab/show/separator, inspected 2026-08-28: "``S`` is a
        separating family if the family of hom functors ``Hom(S_a, -) : C -> Set`` (for
        ``a in A``) is jointly faithful"), which is a family of functors and not one
        functor.  ``Cat()`` is the case in hand: its separating family is ``(1, [1])``,
        so objects and morphisms separate functors jointly and no ``U_Cat`` exists.
        """
        from sage_categories.cat.declarations import Sets
        from sage_categories.cat.functors import Fun

        separators = self.separating_family()
        assert len(separators) == 1, (
            f"{self!r} chooses a separating family of {len(separators)}; such a family states that its hom functors "
            f"Mor(C)(G^j, -) are jointly faithful, which is a family of functors and not one represented functor"
        )
        (separator,) = separators
        if separator in self._represented:
            return self._represented[separator]

        images: MonoDict = MonoDict()

        def hom_set(member_object: ObjectOfCategory) -> ObjectOfCategory:
            if member_object not in images:
                hom = self.morphism_category(1)(separator, member_object)
                images[member_object] = Sets(lambda datum: ask(hom.membership_proposition(datum)) if role_of(datum) is Role.MORPHISM else False)
            return images[member_object]

        def postcompose(morphism: MorphismOfCategory) -> MorphismOfCategory:
            source, target = hom_set(morphism.domain()), hom_set(morphism.codomain())
            return Sets.morphism_category(1)(source, target)(lambda datum: morphism * datum)

        self._represented[separator] = Fun(self, Sets)(hom_set, postcompose)
        return self._represented[separator]

    # -- universal constructions, defined once (POL-CAT-050/092, POL-CAT-093) --------
    #
    # A full subcategory declared by such a monomorphism has the constructions of its
    # ambient definitionally (POL-CAT-087); every other category owns its own families.
    # Each family exists for every supplied shape without asserting that the
    # category has those limits (POL-CAT-051): constructing an object needs an
    # owned construction or supplied universal data.

    @cached_method
    def Products(self) -> Category:
        """The category of chosen products over every discrete shape."""
        from sage_categories.cat.constructions import ProductsCategory

        if self.has_full_ambient():
            return self.ambient().Products()
        return ProductsCategory(self)

    @cached_method
    def Coproducts(self) -> Category:
        """The category of chosen coproducts over every discrete shape."""
        from sage_categories.cat.constructions import CoproductsCategory

        if self.has_full_ambient():
            return self.ambient().Coproducts()
        return CoproductsCategory(self)

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

    # Each family is retained by the method that names it (Sage ``cached_method``):
    # the spelling is the method, not a key in a registry (POL-CAT-083).

    def _morphism_property_family(self, name: str, property_of: Callable[[Category], Category], over: bool) -> Category:
        from sage_categories.cat.slices import MorphismPropertyFamily

        return MorphismPropertyFamily(self, name, property_of, over)

    @cached_method
    def Subobjects(self) -> Category:
        """The monomorphisms of ``C`` as objects of ``Fun([1], C)``; ``C.Subobjects()(x)`` is the fiber over ``x`` in ``C.SliceOver(x)``."""
        if self.has_full_ambient():
            return self.ambient().Subobjects()
        return self._morphism_property_family("Subobjects", lambda morphisms: morphisms.Monomorphisms(), True)

    @cached_method
    def Superobjects(self) -> Category:
        """The monomorphisms of ``C``; ``C.Superobjects()(x)`` is the fiber under ``x`` in ``C.CosliceUnder(x)``."""
        if self.has_full_ambient():
            return self.ambient().Superobjects()
        return self._morphism_property_family("Superobjects", lambda morphisms: morphisms.Monomorphisms(), False)

    @cached_method
    def CoveringObjects(self) -> Category:
        """The epimorphisms of ``C``; ``C.CoveringObjects()(y)`` is the fiber over ``y``: pairs ``(X, p: X -> y)`` (POL-CAT-026)."""
        if self.has_full_ambient():
            return self.ambient().CoveringObjects()
        return self._morphism_property_family("CoveringObjects", lambda morphisms: morphisms.Epimorphisms(), True)

    @cached_method
    def CoveredObjects(self) -> Category:
        """The epimorphisms of ``C``; ``C.CoveredObjects()(x)`` is the fiber under ``x`` in ``C.CosliceUnder(x)``."""
        if self.has_full_ambient():
            return self.ambient().CoveredObjects()
        return self._morphism_property_family("CoveredObjects", lambda morphisms: morphisms.Epimorphisms(), False)

    # -- wide subcategories and the core (``specs/functor.md``, "Monomorphisms of ``Cat()`` and placement"; ``cat/wide.py``) --

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
        return next(point for point in self.object_set() if ask(self.object_at(point) == member_object))

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
    # Every placement is a base category together with the set of roots it is
    # narrowed by: full subcategories of the base, closed under the roots of their
    # own placements (a full subcategory of ``D`` inside ``C`` carries ``D`` as a
    # root).  ``D.P()`` is the narrowing of the base by ``{D, P}``, ``D.P().Q()`` by
    # ``{D, P, Q}``.  One object exists per set of roots, so the same intersection
    # reached in any order or from any spelling is one category (POL-API-009,
    # POL-CAT-084); a narrowing by more roots is a full subcategory of the narrowing
    # by fewer.

    def name(self) -> str:
        """The spelling of this category as a root of a narrowing."""
        return repr(self)

    def narrowing_base(self) -> Category[MorphismData, TwoMorphismData]:
        """The category whose narrowings this placement is one of; ``self`` when it is a base."""
        return self

    def narrowing_roots(self) -> tuple[Category[MorphismData, TwoMorphismData], ...]:
        """The roots this placement is narrowed by, closed under the roots of each root's own placement."""
        return ()

    def intersection(self, roots: tuple[Category[MorphismData, TwoMorphismData], ...]) -> Category[MorphismData, TwoMorphismData]:
        """The narrowing of this base by the given roots, one object per closed set of roots.

        A root containing the base narrows nothing; a set of roots that is exactly one
        root's own closed set is that root.
        """
        base = self.narrowing_base()
        if base is not self:
            return base.intersection((*self.narrowing_roots(), *roots))
        closed: dict[int, Category] = {}
        for root in roots:
            for member in root.narrowing_roots():
                if not is_subcategory(self, member):
                    closed[member.ordinal()] = member
        ordered = tuple(sorted(closed.items()))
        if not ordered:
            return self
        selected = tuple(root for _, root in ordered)
        for root in selected:
            if is_subcategory(root, self) and {member.ordinal() for member in root.narrowing_roots()} == set(closed):
                return root
        key = tuple(ordinal for ordinal, _ in ordered)
        if key not in self._narrowings:
            self._narrowings[key] = self.narrowing_type()(self, selected)
        return self._narrowings[key]

    def property_subcategory(self, property_category: Category[MorphismData, TwoMorphismData]) -> Category[MorphismData, TwoMorphismData]:
        """``self.P()``: the narrowing of this placement by the roots of ``P`` (POL-CAT-084)."""
        return self.narrowing_base().intersection((*self.narrowing_roots(), *property_category.narrowing_roots()))

    def narrowing_type(self) -> type[Category[MorphismData, TwoMorphismData]]:
        from sage_categories.cat.properties import NarrowedProperty

        return NarrowedProperty


# Core category classes import this name while the mutually recursive ``Cat`` cluster is
# defined, before ``Cat()`` exists to be asked for its own object role.  ``bootstrap``
# binds it again from that role, which is this same class: ``Cat()`` writes
# ``CategoryDeclaration`` as its ``ObjectType`` and the compiler compiles the class a
# category writes (``specs/functor.md``, "Compiled implementation classes").
Category = CategoryDeclaration


def _shared_category(first: ObjectOfCategory, second: ObjectOfCategory) -> Category:
    """The narrowest category containing both operands, which owns their construction (POL-CAT-088).

    An object refined into ``C.P()`` and an object of ``C`` are both objects of ``C``,
    so their construction is the one in ``C``.  Identity of the two strongest recorded
    placements is an implementation fact, not this precondition (POL-CAT-073).  Operands
    with no common category, such as a set and a category, fail the assertion.  No
    operator casts an operand into a product category: an external pair is written
    ``(C * D)((X, Y))``.
    """
    from sage_categories.kernel.refinement import common_ancestor

    shared = common_ancestor(first.category(), second.category())
    assert shared is not None, (
        f"{first!r} in {first.category()!r} and {second!r} in {second.category()!r} "
        f"have no least common category along subcategory monomorphisms"
    )
    return shared


# The separator comparisons ``G_D -> F(G_C)`` retained by the constructions that own a
# selected functor exposing point methods (POL-LEAF-003), keyed by the functor.
_separator_comparisons: MonoDict = MonoDict()

# The lifts a functor ``p: E -> B`` retains over a stated class of morphisms of ``B``
# (POL-FUN-029, ``specs/functor.md``, "Slices and coslices"): the owner of the
# functor registers one rule per direction, and each lift is constructed once per
# ``(morphism, object)`` and retained by identity.  The rule states the class of
# morphisms it lifts and fails loudly outside it.
type LiftRule = Callable[[MorphismOfCategory, CategoryPoint], MorphismOfCategory]

_cartesian_rules: MonoDict = MonoDict()
_cocartesian_rules: MonoDict = MonoDict()
_cartesian_lifts: TripleDict = TripleDict(weak_values=False)
_cocartesian_lifts: TripleDict = TripleDict(weak_values=False)

# The factors ``(first, second)`` of every composite ``second * first`` constructed by
# ``Cat()``: an explicit composite names its construction (``specs/functor.md``,
# "Structural inheritance": a selected composite retains its factor functors).
_composite_factors: MonoDict = MonoDict()

# A selected functor owns the object and morphism conversions that construct its
# codomain role state.  They are retained on the functor itself, not in a compiler
# registry (POL-FUN-003/035).  There is no third, element conversion: the element
# action is derived from the morphism action (POL-FUN-002), so a functor stores no
# element callback and a leaf declares none.  Ordinary mathematical functors need no
# conversions at all.
_object_constructor_conversions = MonoDict()
_morphism_constructor_conversions = MonoDict()


def _identity_object_constructor_input[Value: ObjectOfCategory, Datum](
    source: ObjectConstructionInput[Value, Datum],
) -> ObjectConstructionInput[Value, Datum]:
    return source


def _identity_morphism_constructor_input[Value: MorphismOfCategory, Datum](
    source: MorphismConstructionInput[Value, Datum],
) -> MorphismConstructionInput[Value, Datum]:
    return source


@dataclass(frozen=True, eq=False, slots=True)
class FunctorData:
    """The local state introduced by the functor role."""

    # A structural functor whose images are values the domain's defining data already
    # names has no value-level action of its own: its images exist before any value of the
    # domain does, so the kernel builds them from construction inputs and never calls a
    # callback (POL-FUN-035).  Its actions are ``None``.
    on_object: OnObject | None
    on_morphism: OnMorphism | None


class CategoryOfCategories(CategoryDeclaration[[OnObject, OnMorphism], [Assignment]]):
    """The singleton ``Cat()``."""

    # The three classes ``Cat()`` writes.  ``ObjectType`` is a statement rather than a
    # nested class because ``Cat()`` is an object of ``Cat()``: this class is itself a
    # ``CategoryDeclaration``, and Python evaluates a base before the body that would
    # nest it.
    ObjectType = CategoryDeclaration

    class ElementType(CategoryPoint):
        """A point ``* -> C`` of a category, whose value is an object of ``C`` (POL-CAT-058)."""

        def __mul__(self, other: ObjectOfCategory) -> ObjectOfCategory:
            """``X * Y``: the product in the least category receiving both."""
            return _shared_category(self, other).Products()((self, other))

        def __add__(self, other: ObjectOfCategory) -> ObjectOfCategory:
            """``X + Y``: the coproduct in the least category receiving both."""
            return _shared_category(self, other).Coproducts()((self, other))

        def __matmul__(self, other: ObjectOfCategory) -> ObjectOfCategory:
            """``X @ Y``: the biproduct in the least category receiving both."""
            return _shared_category(self, other).biproduct(self, other)

        def __pow__(self, exponent: ObjectOfCategory) -> ObjectOfCategory:
            """``Y ** X``: the exponential object in the least category receiving both."""
            return _shared_category(self, exponent).exponential(exponent, self)

        def __repr__(self) -> str:
            return f"point of {self.parent()!r}"

    class MorphismType(MorphismOfCategory):
        """A functor: a morphism of ``Cat()`` with a domain, a codomain, and total object and morphism actions."""

        def __init__(self, data: FunctorData) -> None:
            self._on_object = data.on_object
            self._on_morphism = data.on_morphism
            # ``F(f)`` is one morphism, not a fresh one per call: a functor assigns each
            # morphism of its domain a single image (POL-CAT-012, POL-FUN-001).  The object
            # action is canonical already, through the construction that retains one object
            # per construction datum and through the transport caches.
            self._morphism_images: MonoDict = MonoDict()
            super().__init__()

        # The admission condition is the one the image construction needs.  A retained
        # monomorphism is the identity on the objects and morphisms of its domain
        # (``specs/functor.md``, "Monomorphisms of ``Cat()`` and placement"), so it constructs nothing and
        # admits exactly the members of its domain: a wide subcategory has every object of
        # its ambient, and that is a membership fact its ambient decides, not a placement
        # its objects ever entered through (POL-CAT-068, POL-FUN-027).  Every other functor
        # builds its image from the domain's construction input, so it admits exactly the
        # values whose placement reaches that node.

        def on_object(self, member_object: ObjectOfCategory) -> ObjectOfCategory:
            """The image of an object of the domain."""
            if self in _object_constructor_conversions:
                from sage_categories.kernel import compiler
                from sage_categories.kernel.transport import construction_input

                if not is_placed(member_object, self.domain()):
                    assert traces_placement(self) and member_object in self.domain(), (
                        f"{member_object!r} is placed in {member_object.category()!r}; {self!r} constructs its image from the "
                        f"placement {self.domain()!r}, which that placement does not reach"
                    )
                    return member_object
                source = construction_input(member_object, compiler.node(self.domain(), Role.OBJECT))
                return self.object_constructor_input(source).canonical_image
            assert member_object in self.domain(), f"{member_object!r} is not an object of {self.domain()!r}"
            assert self._on_object is not None, f"{self!r} retains neither an object action nor an object constructor conversion"
            return self._on_object(member_object)

        def on_morphism(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
            """The image of a morphism of the domain, one value per morphism."""
            if morphism in self._morphism_images:
                return self._morphism_images[morphism]
            image = self._construct_morphism_image(morphism)
            self._morphism_images[morphism] = image
            return image

        def _construct_morphism_image(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
            morphisms = self.domain().morphism_category(1)
            if self in _morphism_constructor_conversions:
                from sage_categories.kernel import compiler
                from sage_categories.kernel.transport import construction_input

                if not is_placed(morphism, morphisms):
                    assert traces_placement(self) and morphism in morphisms, (
                        f"{morphism!r} is placed in {morphism.category()!r}; {self!r} constructs its image from the "
                        f"placement {morphisms!r}, which that placement does not reach"
                    )
                    return morphism
                source = construction_input(morphism, compiler.node(self.domain(), Role.MORPHISM))
                return self.morphism_constructor_input(source).canonical_image
            assert morphism in morphisms, f"{morphism!r} is not a morphism of {self.domain()!r}"
            assert self._on_morphism is not None, f"{self!r} retains neither a morphism action nor a morphism constructor conversion"
            return self._on_morphism(morphism)

        def on_element(self, element: CategoryPoint) -> CategoryPoint:
            """The image of a point ``t: 1_C -> X``: the element ``q = F(t): F(1_C) -> F(X)`` (POL-FUN-002).

            This action is derived, never stored: it applies ``on_morphism`` to the defining
            morphism of ``t``.  A functor retains no element callback and no element
            capability.  The element conversion a selected functor retains supplies compiler
            input only; it never answers this call, so the public image keeps the domain
            ``F(1_C)`` rather than the target's separator (``specs/functor.md``, "Structural
            inheritance").

            A subcategory monomorphism is the identity on the objects and morphisms of its domain,
            so it is the identity on ``t: 1_C -> X`` as well (``specs/functor.md``, "Inclusion
            functors").  Its domain and defining morphism are those of the ambient, which no
            selected route reaches from the subcategory.
            """
            assert role_of(element) is Role.ELEMENT, f"{element!r} is not a point of an object"
            if traces_placement(self):
                parent = element.parent()
                assert is_placed(parent, self.domain()) or parent in self.domain(), f"{element!r} is not a point of an object of {self.domain()!r}"
                return element
            defining = element.defining_morphism()
            image = self.on_morphism(defining)
            if image is defining:
                return element
            return self.codomain().element_from_defining_morphism(image)

        def __call__(self, value: CategoryPoint) -> CategoryPoint:
            """Apply the functor to an object or a morphism of its domain."""
            if value in self.domain():
                return self.on_object(value)
            assert value in self.domain().morphism_category(1), f"{value!r} is neither an object nor a morphism of {self.domain()!r}"
            return self.on_morphism(value)

        # -- separators (``specs/functor.md``, "Structural inheritance") ----------------
        #
        # The retained morphism ``c: G_D -> F(G_C)`` is the whole datum of the separator
        # transport.  By the covariant Yoneda lemma it *is* the natural transformation
        # ``phi_F: U_C => U_D . F`` between the represented point functors:
        # Mathlib ``CategoryTheory.coyonedaEquiv : (coyoneda.obj (op X) ⟶ F) ≃ F.obj X``
        # (inspected 2026-08-27) with ``X = G_C`` and the presheaf ``U_D . F``, whose value
        # at ``G_C`` is ``Mor(D)(G_D, F(G_C))``.  The construction therefore retains the
        # separator morphism and no natural-transformation carrier on ``F``.

        def retain_separator_comparison(self, comparison: MorphismOfCategory) -> None:
            """Retain ``c: G_D -> F(G_C)`` as the defining datum of this functor's transport at the separator (POL-LEAF-003)."""
            (source_separator,) = self.domain().separating_family()
            (target_separator,) = self.codomain().separating_family()
            assert comparison in self.codomain().morphism_category(1)(target_separator, self.on_object(source_separator))
            _separator_comparisons[self] = comparison

        def separator_comparison(self) -> MorphismOfCategory:
            """``G_D -> F(G_C)``: the retained comparison, or the identity when ``F(G_C) is G_D``."""
            if self in _separator_comparisons:
                return _separator_comparisons[self]
            (source_separator,) = self.domain().separating_family()
            (target_separator,) = self.codomain().separating_family()
            assert self.on_object(source_separator) is target_separator, f"{self!r} retains no separator comparison"
            return target_separator.identity()

        # -- composition data ------------------------------------------------------------------

        def retain_object_constructor_conversion[
            SourceValue: ObjectOfCategory,
            SourceDatum,
            TargetValue: ObjectOfCategory,
            TargetDatum,
        ](
            self,
            conversion: Callable[
                [ObjectConstructionInput[SourceValue, SourceDatum]],
                ObjectConstructionInput[TargetValue, TargetDatum],
            ],
        ) -> None:
            """Retain the sole object-action implementation used by structural construction (POL-FUN-035)."""
            signature = inspect.signature(conversion)
            assert len(signature.parameters) == 1, "an object constructor conversion accepts one complete input"
            parameter = next(iter(signature.parameters.values()))
            assert parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            assert self not in _object_constructor_conversions, f"{self!r} already retains an object constructor conversion"
            _object_constructor_conversions[self] = conversion

        def retain_morphism_constructor_conversion[
            SourceValue: MorphismOfCategory,
            SourceDatum,
            TargetValue: MorphismOfCategory,
            TargetDatum,
        ](
            self,
            conversion: Callable[
                [MorphismConstructionInput[SourceValue, SourceDatum]],
                MorphismConstructionInput[TargetValue, TargetDatum],
            ],
        ) -> None:
            """Retain the sole morphism-action implementation used by structural construction (POL-FUN-035)."""
            signature = inspect.signature(conversion)
            assert len(signature.parameters) == 1, "a morphism constructor conversion accepts one complete input"
            parameter = next(iter(signature.parameters.values()))
            assert parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            assert self not in _morphism_constructor_conversions, f"{self!r} already retains a morphism constructor conversion"
            _morphism_constructor_conversions[self] = conversion

        def retain_structural_images[ObjectDatum, MorphismDatum](
            self,
            object_image: Callable[[ObjectDatum], ObjectOfCategory],
            morphism_image: Callable[[MorphismDatum], MorphismOfCategory],
        ) -> None:
            """Retain the structural action of a functor whose images are already-constructed values.

            The usual selected functor forgets structure: the underlying set of a poset, the
            representing set of a cardinal.  Its image is then not built at the moment the
            functor is applied -- it is a value the domain's defining data already names, and
            the domain's own constructor made it.  Each rule states that mathematics and
            nothing else: it reads one node's local datum and returns the image value.  The
            kernel supplies the construction inputs the compiler consumes and the public object
            and morphism actions (POL-FUN-035, POL-LEAF-054).
            """
            from sage_categories.kernel.construction import retained_input

            def object_conversion[Value: ObjectOfCategory](
                source: ObjectConstructionInput[Value, ObjectDatum],
            ) -> ObjectConstructionInput[ObjectOfCategory, object]:
                return retained_input(object_image(source.datum))

            def morphism_conversion[Value: MorphismOfCategory](
                source: MorphismConstructionInput[Value, MorphismDatum],
            ) -> MorphismConstructionInput[MorphismOfCategory, object]:
                return retained_input(morphism_image(source.datum))

            self.retain_object_constructor_conversion(object_conversion)
            self.retain_morphism_constructor_conversion(morphism_conversion)

        def object_constructor_input[
            SourceValue: ObjectOfCategory,
            SourceDatum,
            TargetValue: ObjectOfCategory,
            TargetDatum,
        ](
            self,
            source: ObjectConstructionInput[SourceValue, SourceDatum],
        ) -> ObjectConstructionInput[TargetValue, TargetDatum]:
            """Return the root input retained by this object's canonical functor image.

            The image is read in its own role: the objects of a morphism category are the
            morphisms of its base and retain a morphism input (POL-CAT-021).
            """
            from sage_categories.kernel.construction import retained_input

            assert self in _object_constructor_conversions, f"{self!r} retains no object constructor conversion"
            target = _object_constructor_conversions[self](source)
            assert retained_input(target.canonical_image) is target, f"{self!r} constructed a parallel object input"
            return target

        def element_constructor_input[
            SourceValue: CategoryPoint,
            SourceDatum,
            TargetValue: CategoryPoint,
            TargetDatum,
        ](
            self,
            source: ElementConstructionInput[SourceValue, SourceDatum],
        ) -> ElementConstructionInput[TargetValue, TargetDatum]:
            """The compiler input for the image of ``t``: that of ``q = F(t)``, or of ``p = q . c_F`` for a ``t`` at the separator (POL-FUN-002/035).

            Applying the morphism conversion to the defining morphism of ``t`` gives the
            defining morphism of ``q: F(T) -> F(X)``, the value public element application
            returns.  This derivation is the whole element action; the functor retains no
            element conversion of its own.

            A source ``t: G_C -> X`` at the separator instead supplies the target's
            element methods, which read a point of the target's own separator.
            Precomposing ``q`` with the retained comparison ``c_F: G_D -> F(G_C)`` produces
            that point ``p: G_D -> F(X)``.  When ``c_F`` is an identity, ``F(G_C)`` is
            ``G_D`` and ``p`` is ``q``: they then share one identity and one cache entry
            (POL-CAT-066).
            """
            from sage_categories.kernel.construction import (
                ElementRoleIdentity,
                retained_element_input,
                retained_morphism_input,
            )

            assert isinstance(source.identity, ElementRoleIdentity)
            source_defining = source.identity.defining_morphism
            image = self.morphism_constructor_input(retained_morphism_input(source_defining)).canonical_image
            separators = self.domain().separating_family()
            if self in _separator_comparisons and len(separators) == 1 and source_defining.domain() is separators[0]:
                comparison = _separator_comparisons[self]
                if comparison is not comparison.domain().identity():
                    image = image * comparison
            if image is source_defining:
                return source
            return retained_element_input(self.codomain().element_from_defining_morphism(image))

        def morphism_constructor_input[
            SourceValue: MorphismOfCategory,
            SourceDatum,
            TargetValue: MorphismOfCategory,
            TargetDatum,
        ](
            self,
            source: MorphismConstructionInput[SourceValue, SourceDatum],
        ) -> MorphismConstructionInput[TargetValue, TargetDatum]:
            """Return the root input retained by this morphism's canonical functor image."""
            from sage_categories.kernel.construction import retained_morphism_input

            assert self in _morphism_constructor_conversions, f"{self!r} retains no morphism constructor conversion"
            target = _morphism_constructor_conversions[self](source)
            assert retained_morphism_input(target.canonical_image) is target, f"{self!r} constructed a parallel morphism input"
            return target

        def _derive_selected_constructor_conversions(self) -> None:
            """Read this functor's two rules as construction data, which is what selecting it means.

            A functor is built once, by ``Fun(C, D)(object_rule, morphism_rule)``; selection is
            compiler input and makes no second kind of functor (POL-CAT-085).  What selection
            adds is the reading: the rules of a selected functor state how one of ``C``'s own
            constructions produces the data ``D``'s constructor consumes, so each takes one
            node's local datum and names the value ``D`` made from it (POL-LEAF-058).  The
            kernel turns them into the construction inputs the compiler consumes and into the
            public object and morphism actions (POL-FUN-035); the leaf names no canonical
            image, construction input, or transport (POL-LEAF-054).

            A functor that is never selected keeps its rules as its ordinary value-level
            actions: the represented functor ``Mor(C)(G, -)``, a constant diagram, a Kan
            extension.  A construction that retained its conversions already -- a subcategory
            monomorphism, an identity, an explicit composite -- keeps them.

            The element conversion is derived from the morphism one (POL-FUN-002), so a
            retained morphism conversion already supplies the selected target element role.
            """
            if self in _object_constructor_conversions and self in _morphism_constructor_conversions:
                return
            assert self._on_object is not None and self._on_morphism is not None, (
                f"{self!r} states neither its two rules nor its constructor conversions, so it cannot be selected"
            )
            self.retain_structural_images(self._on_object, self._on_morphism)

        def _retain_identity_constructor_conversions(self) -> None:
            """Retain the identity conversions for an identity-on-value functor."""
            if self not in _object_constructor_conversions:
                self.retain_object_constructor_conversion(_identity_object_constructor_input)
            if self not in _morphism_constructor_conversions:
                self.retain_morphism_constructor_conversion(_identity_morphism_constructor_input)

        def retain_factors(self, first: Functor, second: Functor) -> None:
            """Retain that this functor is the composite ``second * first``."""
            assert self not in _composite_factors, f"{self!r} already retains its factors"
            assert first.codomain() is second.domain() and self.domain() is first.domain() and self.codomain() is second.codomain()
            _composite_factors[self] = (first, second)

            if first in _object_constructor_conversions and second in _object_constructor_conversions:

                def object_conversion[
                    SourceValue: ObjectOfCategory,
                    SourceDatum,
                    TargetValue: ObjectOfCategory,
                    TargetDatum,
                ](
                    source: ObjectConstructionInput[SourceValue, SourceDatum],
                ) -> ObjectConstructionInput[TargetValue, TargetDatum]:
                    return second.object_constructor_input(first.object_constructor_input(source))

                self.retain_object_constructor_conversion(object_conversion)
            if first in _morphism_constructor_conversions and second in _morphism_constructor_conversions:

                def morphism_conversion[
                    SourceValue: MorphismOfCategory,
                    SourceDatum,
                    TargetValue: MorphismOfCategory,
                    TargetDatum,
                ](
                    source: MorphismConstructionInput[SourceValue, SourceDatum],
                ) -> MorphismConstructionInput[TargetValue, TargetDatum]:
                    return second.morphism_constructor_input(first.morphism_constructor_input(source))

                self.retain_morphism_constructor_conversion(morphism_conversion)

        def factors(self) -> tuple[Functor, Functor]:
            """The retained factors ``(first, second)`` of an explicit composite ``second * first``, in categorical order."""
            assert self in _composite_factors, f"{self!r} is not a retained composite"
            return _composite_factors[self]

        # -- fibration and opfibration lifts (POL-FUN-029) ------------------------------------

        def retain_cartesian_lifts(self, rule: LiftRule) -> None:
            """Retain the rule constructing the cartesian lift of ``f: y -> p(e)`` at ``e`` over the class of morphisms the owner states."""
            assert self not in _cartesian_rules, f"{self!r} already retains its cartesian lifts"
            _cartesian_rules[self] = rule

        def retain_cocartesian_lifts(self, rule: LiftRule) -> None:
            """Retain the rule constructing the cocartesian lift of ``f: p(e) -> y`` at ``e`` over the class of morphisms the owner states."""
            assert self not in _cocartesian_rules, f"{self!r} already retains its cocartesian lifts"
            _cocartesian_rules[self] = rule

        def cartesian_lift(self, morphism: MorphismOfCategory, member_object: CategoryPoint) -> MorphismOfCategory:
            """The cartesian lift of ``morphism: y -> p(e)`` at ``e``: a morphism of the domain ending at ``e`` over ``morphism``, retained once per pair."""
            assert self in _cartesian_rules, f"{self!r} retains no cartesian lifts"
            assert morphism in self.codomain().morphism_category(1), f"{morphism!r} is not a morphism of {self.codomain()!r}"
            assert morphism.codomain() is self.on_object(member_object), f"{morphism!r} does not end at the image of {member_object!r}"
            key = (morphism, member_object, self)
            if key not in _cartesian_lifts:
                _cartesian_lifts[key] = _cartesian_rules[self](morphism, member_object)
            return _cartesian_lifts[key]

        def cocartesian_lift(self, morphism: MorphismOfCategory, member_object: CategoryPoint) -> MorphismOfCategory:
            """The cocartesian lift of ``morphism: p(e) -> y`` at ``e``: a morphism of the domain starting at ``e`` over ``morphism``, retained once per pair."""
            assert self in _cocartesian_rules, f"{self!r} retains no cocartesian lifts"
            assert morphism in self.codomain().morphism_category(1), f"{morphism!r} is not a morphism of {self.codomain()!r}"
            assert morphism.domain() is self.on_object(member_object), f"{morphism!r} does not start at the image of {member_object!r}"
            key = (morphism, member_object, self)
            if key not in _cocartesian_lifts:
                _cocartesian_lifts[key] = _cocartesian_rules[self](morphism, member_object)
            return _cocartesian_lifts[key]

        def is_full(self) -> AppliedPredicate:
            return Fun.Full().predicate()(self)

        def is_faithful(self) -> AppliedPredicate:
            return Fun.Faithful().predicate()(self)

        def is_fully_faithful(self) -> AppliedPredicate:
            return Fun.FullyFaithful().predicate()(self)

        def is_essentially_surjective(self) -> AppliedPredicate:
            return Fun.EssentiallySurjective().predicate()(self)

        def is_equivalence(self) -> AppliedPredicate:
            return Fun.Equivalences().predicate()(self)

        def __repr__(self) -> str:
            return f"Functor({self.domain()!r} -> {self.codomain()!r})"

    def __init__(self) -> None:
        self._canonical: dict[tuple[str, tuple[int, ...]], FinitePresentedCategory] = {}
        self._point_categories: MonoDict = MonoDict()
        self._declared_functors: TripleDict = TripleDict(weak_values=False)
        self._exponential_actions: TripleDict = TripleDict(weak_values=False)
        self._declarations: dict[str, Category | CategoryFamily] = {}
        self._implementations: dict[str, type[Category] | Functor] = {}
        self._open_declarations: MonoDict = MonoDict()
        super().__init__()

    # -- the categories Cat declares (D80, D82) ------------------------------------

    @overload
    def declare(self, name: str, domain: None = None) -> Category: ...

    @overload
    def declare(self, name: str, domain: Category) -> CategoryFamily: ...

    def declare(self, name: str, domain: Category | None = None) -> Category | CategoryFamily:
        """``Cat().declare(name, domain)``: the category the repository expects to exist.

        ``domain`` is the domain of the functor into ``Cat()`` that the declaration is,
        and a declaration with no ``domain`` is the terminal-domain case: the point
        ``* -> Cat()``, whose value is a category.  That value is constructed now and is
        the final object -- it takes its ordinal, it is placed in ``Cat()``, and its three
        implementation classes are the empty ones a category declaring nothing already
        receives.  A parameterized family has no category to return until an
        implementation supplies its object and morphism actions.

        A declaration no implementation claims is open work, readable through
        ``declarations()``.  It is never a check that fails a build.
        """
        from sage_categories.cat.declarations import CategoryFamily, DeclaredCategory

        assert name not in self._declarations, f"{name!r} is already declared"
        declared = DeclaredCategory(name) if domain is None else CategoryFamily(name, domain)
        self._declarations[name] = declared
        self._open_declarations[declared] = name
        return declared

    def declarations(self) -> dict[str, Category | CategoryFamily]:
        """The categories ``Cat`` declares, by name; one with no implementation is open work (D82)."""
        return dict(self._declarations)

    def open_declaration(self, declared: Category | CategoryFamily) -> str | None:
        """The name ``declared`` was declared under while no implementation claims it, else ``None``."""
        return self._open_declarations[declared] if declared in self._open_declarations else None

    def implementation(self, name: str) -> type[Category] | Functor | None:
        """The class or functor implementing the declaration ``name``, or ``None``."""
        return self._implementations.get(name)

    def implement(self, name: str, implementation: type[Category] | Functor) -> None:
        """Connect ``implementation`` to the declaration it names (D80).

        The declared object is the final object, so nothing is constructed here: its
        class is strengthened to the implementing class in place -- the same in-place
        strengthening every value receives when its placement improves -- and its roles
        are compiled again onto it.  **The ordinal is not retaken.**  Every reference
        written against the declaration therefore uses the implementation the moment it
        lands, with no edit and no resolution pass.
        """
        assert name in self._declarations, (
            f"{implementation!r} implements {name!r}, which Cat declares nothing for"
        )
        assert name not in self._implementations, (
            f"{name!r} is already implemented by {self._implementations[name]!r}, not {implementation!r}"
        )
        declared = self._declarations[name]
        self._implementations[name] = implementation
        del self._open_declarations[declared]
        declared.implemented_by(implementation)

    def morphism_category_type(self) -> type[FunctorsCategory]:
        from sage_categories.cat.functors import FunctorsCategory

        return FunctorsCategory

    def construct_morphism(
        self,
        domain: Category,
        codomain: Category,
        on_object: OnObject,
        on_morphism: OnMorphism,
    ) -> Functor:
        """``Fun(C, D)(on_object, on_morphism)``: the functor selected by its four identity components (POL-FUN-001/027)."""
        assert domain in self and codomain in self
        key = (domain, codomain, on_object)
        if key not in self._declared_functors:
            self._declared_functors[key] = MonoDict()
        by_morphism_action = self._declared_functors[key]
        if on_morphism not in by_morphism_action:
            by_morphism_action[on_morphism] = self.MorphismType(
                category=self.morphism_category(1),
                domain=domain,
                codomain=codomain,
                data=FunctorData(on_object, on_morphism),
            )
        return by_morphism_action[on_morphism]

    def construct_identity(self, category: Category) -> Functor:
        from sage_categories.cat.functors import Fun
        from sage_categories.kernel.refinement import refine

        identity = self.construct_morphism(category, category, lambda x: x, lambda f: f)
        identity._retain_identity_constructor_conversions()
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
        composite.retain_factors(first, second)
        # Full, faithful, and fully faithful functors compose (Mathlib
        # ``Functor.FullyFaithful.comp``, ``Full.comp``, ``Faithful.comp``; inspected 2026-08-26).
        for property_category in (Fun.FullyFaithful(), Fun.Full(), Fun.Faithful()):
            if is_placed(first, property_category) and is_placed(second, property_category):
                refine(composite, property_category)
        return composite

    def construct_two_morphism(self, source: CategoryPoint, target: CategoryPoint, assignment: Assignment) -> NaturalTransformation:
        """``Mor(Fun(C, D))(F, G)(assignment)``: a natural transformation from a rule (POL-FUN-007).

        The endpoints are objects of ``Fun(C, D)``: functors, or the points of ``D``
        with domain ``C`` that denote their defining functors (specs/functor.md, "The Mor(n, C) tower").
        """
        from sage_categories.cat.functors import NaturalTransformationData, diagram_of

        functors = self.morphism_category(1)
        source_functor, target_functor = diagram_of(source), diagram_of(target)
        assert source_functor in functors and target_functor in functors
        assert source_functor.domain() is target_functor.domain() and source_functor.codomain() is target_functor.codomain()
        return functors.MorphismType(
            category=functors.morphism_category(1),
            domain=source,
            codomain=target,
            data=NaturalTransformationData(assignment),
        )

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

    # -- horizontal composition with 1-morphisms: whiskering (POL-CAT-021, POL-MATH-036) ---
    #
    # nLab "whiskering", Idea (inspected 2026-08-27): "In a 2-category, the horizontal
    # composition of a 2-morphism with 1-morphisms is sometimes called whiskering."  Its
    # Examples section states both operations in detail: "If F,G: C -> D and H: D -> E are
    # functors and eta: F -> G is a natural transformation whose coordinate at any object
    # A of C is eta_A, then whiskering H and eta yields the natural transformation
    # H . eta: (H . F) -> (H . G) whose coordinate at A is H(eta_A)"; and "If F: C -> D and
    # G,H: D -> E are functors and eta: G -> H is a natural transformation whose coordinate
    # at A is eta_A, then whiskering eta and F yields the natural transformation
    # eta . F: (G . F) -> (H . F) whose coordinate at A is eta_{F(A)}."
    #
    # Mathlib writes composition in the opposite order, so its ``whiskerRight alpha H``
    # (``Mathlib/CategoryTheory/Whiskering.lean:56-58``: "has components ``F.map (α.app X)``")
    # is the left whiskering here, and its ``whiskerLeft F alpha``
    # (``Whiskering.lean:44-46``: "has components ``α.app (F.obj X)``") the right one; both
    # inspected 2026-08-27.  Naturality of every result is a trusted declaration
    # (POL-MATH-036), as is the interchange law that identifies the two builds of a
    # horizontal composite.

    def whisker_left(self, functor: Functor, transformation: NaturalTransformation) -> NaturalTransformation:
        """``H . eta: H F => H G`` for ``eta: F => G`` in ``Fun(I, D)`` and ``H: D -> E``; its component at ``X`` is ``H(eta_X)``."""
        source = transformation.source_functor()
        assert source.codomain() is functor.domain()
        images = self.exponential(source.domain(), functor.codomain())
        return images.morphism_category(1)(
            self.postcompose(functor, transformation.domain()),
            self.postcompose(functor, transformation.codomain()),
        )(lambda member_object: functor.on_morphism(transformation.component(member_object)))

    def whisker_right(self, transformation: NaturalTransformation, functor: Functor) -> NaturalTransformation:
        """``theta . F: H F => K F`` for ``theta: H => K`` in ``Fun(D, E)`` and ``F: I -> D``; its component at ``X`` is ``theta_{F(X)}``."""
        source, target = transformation.source_functor(), transformation.target_functor()
        assert functor.codomain() is source.domain()
        images = self.exponential(functor.domain(), source.codomain())
        return images.morphism_category(1)(
            self.composite(source, functor),
            self.composite(target, functor),
        )(lambda member_object: transformation.component(functor.on_object(member_object)))

    def horizontal_composite(self, second: NaturalTransformation, first: NaturalTransformation) -> NaturalTransformation:
        """``theta * eta: H F => K G`` for ``eta: F => G`` in ``Fun(I, D)`` and ``theta: H => K`` in ``Fun(D, E)``.

        Its component at ``X`` is ``K(eta_X) . theta_{F(X)}``: the component of the right
        whiskering ``theta . F: H F => K F``, then that of the left whiskering
        ``K . eta: K F => K G``, which is the vertical composite of the two.  Mathlib
        ``NatTrans.hcomp`` (``Mathlib/CategoryTheory/Functor/Category.lean:122-131``;
        inspected 2026-08-27) is this same component formula,
        ``app := fun X => β.app (F.obj X) ≫ I.map (α.app X)``, in the opposite composition
        order.  Its ``hcomp_app'`` gives the other build, ``theta_{G(X)} . H(eta_X)``; the
        two agree by the interchange law (POL-MATH-036).
        """
        outer = self.whisker_right(second, first.source_functor())
        inner = self.whisker_left(second.target_functor(), first)
        images = self.exponential(first.source_functor().domain(), second.target_functor().codomain())
        return images.morphism_category(1)(outer.domain(), inner.codomain())(
            lambda member_object: inner.component(member_object) * outer.component(member_object)
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

    def postcompose(self, functor: Functor, diagram: CategoryPoint) -> CategoryPoint:
        """``F . G`` for an object ``G`` of ``Fun(I, D)`` and ``F: D -> E``: the object action of ``Fun(I, F)``.

        An object of ``Fun(I, D)`` is a functor ``I -> D`` or a point of ``D`` with domain
        ``I`` denoting one (``specs/functor.md``, "The Mor(n, C) tower").  A point keeps
        that spelling under the action: its image is the point image, so
        ``Fun(1, F).on_object(x) is F.on_object(x)`` and
        ``Fun([1], F).on_object(f) is F.on_morphism(f)``.
        """
        if is_placed(diagram, self.morphism_category(1)):
            return self.composite(functor, diagram)
        return functor(diagram)

    def exponential_on_morphism(self, exponent: Category, functor: Functor) -> Functor:
        """``Fun(I, F): Fun(I, D) -> Fun(I, E)`` for ``F: D -> E``: the action of ``(-) ** I`` on a morphism of ``Cat()``.

        Post-composition with ``F``: a diagram ``G`` goes to ``F . G`` and a natural
        transformation ``eta`` to the left whiskering ``F . eta``.  Mathlib
        ``CategoryTheory.whiskeringRight`` (``Mathlib/CategoryTheory/Whiskering.lean:95-98``;
        inspected 2026-08-27) is this functor: ``obj H := { obj := fun F => F ⋙ H,
        map := fun α => whiskerRight α H }``, with "``(whiskeringRight.obj H).obj F``
        evaluates to ``F ⋙ H``, and ``(whiskeringRight.obj H).map α`` produces
        ``whiskerRight α H``" (``Whiskering.lean:91-92``).  One functor per
        ``(exponent, functor)``, retained by identity.
        """
        assert functor in self.morphism_category(1)
        key = (exponent, functor, self)
        if key not in self._exponential_actions:
            self._exponential_actions[key] = self.morphism_category(1)(
                self.exponential(exponent, functor.domain()),
                self.exponential(exponent, functor.codomain()),
            )(
                lambda diagram: self.postcompose(functor, diagram),
                lambda transformation: self.whisker_left(functor, transformation),
            )
        return self._exponential_actions[key]

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

    def Point(self, member: CategoryPoint, targets: tuple[Category, ...] = ()) -> PointCategory:
        """``{X}``: the one-object category on ``member``, retained by identity (POL-CAT-083).

        ``targets`` are the categories the point functors place ``member`` in.  Building
        ``{X}`` installs that placement by same-object refinement: ``member`` keeps its
        identity and its role classes keep theirs, and the level shift puts the point
        functors' generalized-element surface on the objects and morphisms of ``member``
        when ``member`` is itself a category (``specs/functor.md``, "The level shift").

        One point category exists per object, so calling this again returns the retained
        one and its declared targets stand.
        """
        from sage_categories.cat.points import PointCategory
        from sage_categories.kernel.refinement import refine

        assert role_of(member) is Role.OBJECT, f"{member!r} is not an object of a category"
        if member not in self._point_categories:
            point = PointCategory(member, targets)
            self._point_categories[member] = point
            refine(member, point)
            compiler.install_level_shift(point)
        return self._point_categories[member]

    def retained_point(self, member: CategoryPoint) -> PointCategory | None:
        """The point category retained for ``member``, or ``None``; the compiler reads this table."""
        return self._point_categories[member] if member in self._point_categories else None

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

    def separating_family(self) -> tuple[FinitePresentedCategory, ...]:
        """``{1, [1]}``.  The writer asserts that this family separates ``Cat()`` (POL-MATH-037).

        nLab "separator", Definitions: a family separates when ``f . e = g . e`` for every
        ``e`` sourced in it forces ``f = g`` (inspected 2026-08-27).  Functors ``1 -> C``
        are the objects of ``C`` and functors ``[1] -> C`` its morphisms (nLab "walking
        morphism", Applications: ``Arr(D) := [I, D]``, whose objects are the morphisms of
        ``D``; inspected 2026-08-27), and a functor is determined by those two actions.
        ``1`` alone does not separate: ``Mor(Cat())(1, -)`` forgets the morphism action.
        """
        return (self.Terminal(), self.Simplex(1))

    def element_from_defining_morphism(self, defining_functor: Functor) -> CategoryPoint:
        """The point of a category with domain ``T``, given by a functor ``T -> C``."""
        assert defining_functor in self.morphism_category(1)
        return self.ElementType(defining_functor)

    def __repr__(self) -> str:
        return "Cat"


# The singleton, bound by ``bootstrap``.  It is ``None`` while ``Cat()`` compiles its own
# roles, which is the one moment the kernel can reach this module before it exists.
_CAT: CategoryOfCategories | None = None


def bootstrap() -> None:
    """Construct the singleton ``Cat()`` once; ``cat/functors.py`` runs this at import.

    ``Cat()`` is self-referential mathematics: ``Cat().ObjectType`` is ``Category``,
    ``Cat().MorphismType`` is ``Functor``, and ``Functor`` is itself an object of
    ``Fun = Mor(Cat())``.  The bootstrap first defines their distinct local
    declarations.  It then compiles ``Cat()`` and binds the semantic names to its
    public roles.  Modules that declare other category classes import only after this
    function returns.  Their classes therefore derive from the compiled ``Category``
    role and enter its generated constructor chain normally.  The kernel evaluates
    deferred signatures after the semantic names are bound (POL-KERNEL-021).

    The theory is therefore one import layer with one entry point.
    ``cat/__init__.py`` imports ``cat/functors.py``.  That module defines the two
    local roles, calls this function, and only then imports dependent category
    classes.  Binding these names completes the bootstrap.  It does not create a
    lookup registry.
    """
    global _CAT, Category, Functor
    _CAT = compiler.construct_category_singleton(CategoryOfCategories)
    Category = _CAT.ObjectType
    Functor = _CAT.MorphismType


def Cat() -> CategoryOfCategories:
    """The category of categories."""
    return _CAT
