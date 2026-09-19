"""Implement ``Cat()``, category declarations, and the universal category methods."""

from __future__ import annotations

import itertools
from collections.abc import Callable, Hashable
from contextvars import ContextVar
from dataclasses import dataclass
from functools import cache, partial
from typing import TYPE_CHECKING, ClassVar, Literal, overload

from sage_categories.cat.equality import equality_predicate
from sage_categories.cat.predicates import (
    AppliedQuery,
    Axiom,
    ConstructionFamily,
    Decision,
    Predicate,
    Proposition,
    Query,
    Unknown,
    UnknownClass,
    ask,
    register_handler,
)
from sage_categories.kernel.predicates import axiom_layer as _axiom_layer
from sage_categories.kernel.refinement import is_placed, is_subcategory, refine
from sage_categories.kernel.retention import (
    category_construction_functors,
    identity_key,
)
from sage_categories.kernel.roles import prepare_category_subclass
from sage_categories.kernel.sage_runtime import (
    Integer,
    MonoDict,
    cached_function,
    cached_method,
)
from sage_categories.kernel.type_aliases import ContainmentInput, EqualityInput

if TYPE_CHECKING:
    from sage_categories.cat.canonical import FinitePresentedCategory
    from sage_categories.cat.constructions import (
        LimitApexLift,
        LimitMorphismLift,
        UniversalPresentation,
    )
    from sage_categories.cat.declarations import CategoryFamily, DeclaredCategory
    from sage_categories.cat.functors import (
        Functor,
        FunctorsCategory,
        NaturalTransformation,
    )
    from sage_categories.cat.morphisms import MorphismCategory
    from sage_categories.cat.points import PointCategory
    from sage_categories.cat.slices import CommaCategory

__all__ = [
    "Assignment",
    "Cat",
    "Category",
    "CategoryOfCategories",
    "OnMorphism",
    "OnObject",
    "member",
]


# Stable category identities order the roots of an intersection. The compiler
# follows selected targets in dependency order and initializers in declaration
# order (D165 to D167).
_category_ordinals = itertools.count()

# The construction data of ``Cat()``: a functor's actions and a natural
# transformation's component assignment (POL-FUN-001).
type OnObject = Callable[[CategoryOfCategories.ElementType], CategoryOfCategories.ElementType]
type OnMorphism = Callable[["MorphismCategory.ObjectType"], "MorphismCategory.ObjectType"]
type Assignment = Callable[[CategoryOfCategories.ElementType], "MorphismCategory.ObjectType"]


# ``member(x, C)``: ``x`` is an object of ``C``.  For a plain category the
# proposition is decided by established placement alone (POL-CAT-068/073); a
# property subcategory conjoins its own predicate (``cat/properties.py``).
class _MemberPredicate(Predicate):
    name = "member"


member: Predicate = _MemberPredicate()


# ``concrete_category(C)``: a faithful functor ``C -> Sets()`` composes from the structure
# functors ``C`` declares.  ``cat/concrete.py`` decides it and implements the subcategory.
class _ConcretePredicate(Predicate):
    name = "concrete_category"


concrete_category: Predicate = _ConcretePredicate()


def _pointwise_limit_in_opposite_functor_category(
    diagram: Functor,
) -> CategoryOfCategories.ElementType:
    """Evaluate a limit in ``Fun(I, C).op()`` as the dual pointwise colimit."""
    from sage_categories.cat.cones import cone, cone_apex
    from sage_categories.cat.diagrams import _pointwise_limit_data
    from sage_categories.cat.dual_functor_categories import (
        dual_functor_category_equivalence,
    )
    from sage_categories.cat.functors import Functor, FunctorCategory
    from sage_categories.cat.opposites import OppositeCategory

    opposite_functors = diagram.codomain().narrowing_base()
    assert isinstance(opposite_functors, OppositeCategory)
    functors = opposite_functors.original()
    assert isinstance(functors, FunctorCategory)
    family = opposite_functors.Limits(diagram.domain())
    lowered = family.lowered(diagram)
    duality = dual_functor_category_equivalence(functors.domain(), functors.codomain())
    to_dual = duality.forward().op()
    from_dual = duality.inverse().op()
    transported = to_dual * lowered
    assert isinstance(transported, Functor)
    dual_apex, dual_cone, dual_mediator = _pointwise_limit_data(transported)
    apex = from_dual.on_object(dual_apex)

    def mediator(candidate_cone: NaturalTransformation) -> MorphismCategory.ObjectType:
        dual_candidate = cone(
            transported,
            to_dual.on_object(cone_apex(candidate_cone)),
            lambda vertex: to_dual.on_morphism(candidate_cone.component(vertex)),
        )
        return from_dual.on_morphism(dual_mediator(dual_candidate))

    return family.with_universal_data(
        lowered,
        apex,
        cone(
            lowered,
            apex,
            lambda vertex: from_dual.on_morphism(dual_cone.component(vertex)),
        ),
        mediator,
    )


@cache
def _morphism_set() -> Query:
    """The typed query for the set of morphisms of a category."""
    from sage_categories.cat.declarations import Sets

    query = Query("morphism_set", 1, Sets)

    def chosen(category: CategoryOfCategories.ObjectType):
        return category._chosen_morphism_set()

    query.register_handler(chosen)
    return query


def _functors():
    """Load the functor-category owner after ``Category`` is available to bootstrap it."""
    from sage_categories.cat.functors import Fun as functor_categories

    return functor_categories


def _cells_engine():
    """Load native cell retention after category-core bootstrap has established owners."""
    from sage_categories.engines import cells as cells_engine

    return cells_engine


def _catlab_engine():
    """Load Catlab execution after category-core bootstrap has established owners."""
    from sage_categories.engines import catlab as catlab_engine

    return catlab_engine


def _canonical_categories():
    """Load canonical finite category constructors after the ``Cat`` owner exists."""
    from sage_categories.cat import canonical as canonical_module

    return canonical_module


def _discrete_shape_family():
    """Load the discrete-shape family after the category core has bootstrapped."""
    from sage_categories.cat.shapes import Discrete

    return Discrete


def _declares_subcategory(functor: MorphismCategory.ObjectType) -> bool:
    """Whether ``functor`` is declared a monomorphism of ``Cat()`` and an isofibration (POL-FUN-036).

    ``Fun`` reads it off the functor's own placement, and reading a functor's declaration
    is ``Cat``'s (D175).  ``Fun`` is reached here rather than at the top of the module
    because it is built from this one, and a category with no selected functor asks
    nothing: that is the window the bootstrap runs in.
    """
    Fun = _functors()

    return Fun.declares_subcategory(functor)


def _declares_point(functor: MorphismCategory.ObjectType) -> bool:
    """Whether ``functor`` is declared a point ``* -> C`` (D154, D162).

    Read the same way and for the same reason as ``_declares_subcategory``: the
    declaration is the property category ``C.Point()`` constructed the arrow in.
    """
    Fun = _functors()

    return Fun.declares_point(functor)


def _declares_implementation(functor: MorphismCategory.ObjectType) -> Category | None:
    """The category a class selecting ``functor`` first declares itself the implementation of (D156).

    That category's identity functor is the whole declaration, so this reads the one
    fact it carries: an endofunctor that is the retained identity names its own category
    and nothing else.  Every other structure functor starts at the category under
    construction, and a point functor starts at the terminal category.
    """
    Fun = _functors()

    domain = functor.domain()
    if domain is not functor.codomain():
        return None
    return domain if functor is Fun(domain, domain).one() else None


def _finite_category_data(category: Category):
    """Read exact finite structural data through the cycle-safe category evaluator."""
    from sage_categories.cat.finite_categories import finite_category

    return finite_category(category)


class CategoryDeclaration[
    **MorphismData,
    **TwoMorphismData,
    ObjectRole = "CategoryOfCategories.ElementType",
    ElementRole = "CategoryOfCategories.ElementType",
    MorphismRole = "MorphismCategory.ObjectType",
]:
    """The local ``Cat().ObjectType`` declaration."""

    _constructs_from_diagrams: ClassVar[bool] = False

    def __init__(self, data: None = None) -> None:
        if "_ordinal" in vars(self):
            return
        if not any(all(name in vars(found) for name in ("ObjectType", "ElementType", "MorphismType")) for found in type(self).__mro__):
            return
        self._initialize(self.category())

    def is_discrete(self) -> bool:
        """Whether this category is one of the kernel's discrete diagram representations.

        Discrete shapes are the retained images ``Discrete(S)`` of owned sets, their
        opposites, and finite presented shapes with no nonidentity generators
        (``cat/shapes.py``).  This decides the representation, an implementation fact
        that is two-valued by construction (POL-ASSUME-005); it is not the mathematical
        proposition that an arbitrary category is discrete.
        """
        return False

    def construction_owner(self) -> Category:
        """The category whose constructors own the values of this placement (POL-CAT-088).

        An object refined into ``C.P()`` and an object of ``C`` are both objects of
        ``C``, so their constructions are owned where the constructors are declared: a
        declared subcategory defers to its ambient, and a category that supplies its own
        construction surface overrides this to return itself.
        """
        return self.ambient().construction_owner() if self.has_ambient() else self

    def subobjects_type(self) -> type:
        """The slice-property class implementing ``C.Subobjects(X)`` (POL-CAT-092).

        A category whose specification owns subobject-specific constructors, such as
        ``Sets()`` with ``from_predicate`` (D84), overrides this; the generic slice
        property serves every other category.
        """
        from sage_categories.cat.slices import SliceProperty

        return SliceProperty

    def __init_subclass__(cls) -> None:
        """Require the three declarations, and connect a class that names what it implements (D80).

        A category class states its three implementation classes in its own body
        (POL-CAT-057), and the ``class`` statement is where an omission happens, so it is
        where the omission is reported.  ``compiler`` builds role classes over this one at
        runtime; those state no category and are not checked.

        This declaration calls no base hook: ``Cat()``'s own ``ObjectType`` is a
        declaration like any other, and a declaration calls no base initializer or
        subclass hook (D110, D13).  ``Generic``'s subclass protocol is not needed here;
        PEP 695 gives each subclass its own type parameters, and the compiler supplies
        the subscript surface of a compiled class itself (``_install_written_body``).
        The kernel's own work for a new category class is named here rather than
        reached through a base hook.
        """
        prepare_category_subclass(cls)
        _axiom_layer().install_subclass_applications(cls)
        if cls.__dict__.get("ObjectType") is CategoryDeclaration:
            # ``Cat()``'s declaration: its points are the objects of every category
            # (POL-CAT-058), the owner of the applications of the base-class axioms.
            _axiom_layer().install_base_applications(cls.__dict__["ElementType"])

    def __mul__(self, other: Category) -> Category:
        """``C * D``: the product category."""
        return Cat().Products()((self, other))

    def __add__(self, other: Category) -> Category:
        """``C + D``: the coproduct category."""
        return Cat().Coproducts()((self, other))

    def __pow__(self, exponent: Category) -> Category:
        """``D ** C = Fun(C, D)``: the functor category."""
        Fun = _functors()

        return Fun(exponent, self)

    def op(self) -> Category:
        """Return the retained opposite category."""
        from sage_categories.cat.opposites import opposite_category

        return opposite_category(self)

    def _initialize(self, universe: Category[[OnObject, OnMorphism], [Assignment]]) -> None:
        from sage_categories.kernel.construction import retain_category_universe

        retain_category_universe(self, universe)
        self._inverses: MonoDict = MonoDict()
        self._biproduct_constructor: Callable[[object, object], object] | None = None
        self._zero_morphism_constructor: Callable[[object, object], object] | None = None
        self._colimit_constructors: MonoDict = MonoDict()
        self._equality = equality_predicate()
        self._ambient_category: Category | None = None
        self._ambient_monomorphism: Functor | None = None
        self._implementation_selected_functors: tuple[Functor, ...] = ()
        self._installed_category_implementations: tuple[type[Category], ...] = ()
        functors = category_construction_functors(self)
        self._selected_functors = functors
        implemented = _declares_implementation(functors[0]) if functors else None
        if implemented is not None:
            # The declaration says this class implements a category that already exists,
            # so there is no second category to construct: ``Cat`` strengthens that value
            # to this class in place (D156).  The construction stops here, before an
            # ordinal is taken, and this half-built value is discarded.
            self.universe()._adopt(implemented, type(self), functors)
            return
        self._ordinal = next(_category_ordinals)
        self._compile_category(functors)
        self._place_selected_point(functors)

    def _place_selected_point(self, functors: tuple[Functor, ...]) -> None:
        """Place this category at the object selected by its defining point functor."""
        from sage_categories.kernel.refinement import place

        # A selected point functor ``* -> D`` places this category as an object of ``D``
        # rather than of its universe, and the level shift follows that placement (D154,
        # D161, D169; ``place``).  The arrow declares the point and is not itself an
        # isofibration; the monic isofibration ``POL-FUN-036`` requires placement to
        # follow is the inclusion ``<X> -> D`` of the replete full subcategory its image
        # generates, so the placement is read off that inclusion (``specs/functor.md``,
        # "Point categories and point functors").
        points = tuple(functor for functor in functors if _declares_point(functor))
        assert len(points) <= 1, (
            f"{self!r} selects {len(points)} point functors; the kernel places a category along one point functor today. "
            "Several is the shape D161 describes for NN lifting its point to magmas in two ways, a kernel capability that does not exist yet"
        )
        inclusions = tuple(functor.codomain().EssentialImage(functor).inclusion_functor() for functor in points)
        place(self, inclusions[0].codomain() if inclusions else self.category())

    def _select_functors(self) -> tuple[Functor, ...]:
        """Read the declaration ``structure_functors()`` once and retain what it selected.

        A declaration constructs its functors when it is read, and a point functor
        ``D.Point()`` names the object under construction, so the kernel reads it inside
        this category's own constructor chain and never again: every later kernel read
        is ``selected_functors()`` (D111, D154).
        """
        declared = tuple(self.structure_functors())
        extensions = self._implementation_selected_functors
        functors = declared + tuple(functor for functor in extensions if not any(functor is known for known in declared))
        self._selected_functors = functors
        self._ambient_monomorphism = next((functor for functor in functors if _declares_subcategory(functor)), None)
        self._ambient_category = None if self._ambient_monomorphism is None else self._ambient_monomorphism.codomain()
        return functors

    # -- declarations read by the kernel --------------------------------------

    def universe(self) -> CategoryOfCategories:
        """``Cat()``, whose objects are the categories.

        Not ``category()``: that is the strongest placement established for this
        category.  Anything that means "the functor category" or "the shapes" wants
        this one.
        """
        return Cat()

    def ordinal(self) -> int:
        """The construction order of this category among all categories."""
        return self._ordinal

    def recompile(self) -> None:
        """Compile this category's roles again from its current declarations (D80).

        An implementation claims a declared category after ``Cat`` constructed it, and
        the declared object is the final one: its class was strengthened in place, and
        its nested classes and structure functors are read again here. Its ordinal
        continues to identify it in retained intersections.
        """
        functors = self._complete_declarations()
        self._recompile_category(functors)
        self._place_selected_point(functors)

    def _complete_declarations(self) -> tuple[Functor, ...]:
        """Identify this category's intersection and select its defining functors."""
        base = self.narrowing_base()
        if base is not self:
            base.retain_intersection(self.narrowing_roots(), self)
        return self._select_functors()

    def structure_functors(self) -> tuple[Functor, ...]:
        """The selected structural graph: immediate functors, in preference order (POL-CAT-016, POL-FUN-003)."""
        return ()

    def selected_functors(self) -> tuple[Functor, ...]:
        """The retained structural graph: initial declarations and later construction-owned comparisons."""
        return self._selected_functors

    def _retain_structure_functor(self, functor: Functor) -> None:
        """Retain a structural functor supplied after this category's construction."""
        assert functor.domain() is self
        if not any(functor is known for known in self._selected_functors):
            self._selected_functors = (*self._selected_functors, functor)

    def has_ambient(self) -> bool:
        """Whether this category is a declared subcategory: one selected functor traces placement (POL-FUN-036)."""
        return self._ambient_category is not None

    def has_full_ambient(self) -> bool:
        """Whether this category is a declared full subcategory: its subcategory monomorphism is also full.

        A full subcategory has the morphisms, identities, composites, and constructions
        of its ambient between its objects definitionally (POL-CAT-087); a core, whose
        monomorphism is not full, owns its own
        (``specs/functor.md``, "Monomorphisms of ``Cat()`` and placement").
        """
        if self._ambient_monomorphism is None:
            return False
        return is_placed(self._ambient_monomorphism, self.universe().morphism_category(1).Full())

    def ambient(
        self,
    ) -> Category[
        MorphismData,
        TwoMorphismData,
        ObjectRole,
        ElementRole,
        MorphismRole,
    ]:
        """The category this one is a declared subcategory of, derived from the selected functors (POL-CAT-016, POL-FUN-036)."""
        assert self._ambient_category is not None, f"{self!r} declares no monomorphism into an ambient category"
        return self._ambient_category

    def subcategory_monomorphism(self) -> Functor:
        """The retained monomorphism that presents this category as a subcategory."""
        assert self._ambient_monomorphism is not None, f"{self!r} is not a declared subcategory"
        return self._ambient_monomorphism

    def _chosen_inhabitation(self) -> Decision:
        """The exact evaluation case of ``is_inhabited()``, which a category owning one overrides.

        This is the one handler of ``Cat().Inhabited()``, in the shape
        ``_chosen_morphism_set`` already uses for ``morphism_set()``: the public method
        returns the containment proposition and never a ``Decision``, and the exact case a
        category owns is a private hook its subclasses implement (POL-CAT-086).
        """
        return Unknown

    def _chosen_hom_inhabited(self, hom_category: Category) -> Decision:
        """The exact decision this category owns for one fixed-endpoint category.

        This covers ``Mor(self)(A, B)`` and its property narrowings
        (POL-CAT-086, POL-MATH-042).

        A full subcategory has the morphism categories of its ambient (POL-CAT-087); every
        other category decides nothing by default.
        """
        if self.has_full_ambient():
            return self.ambient()._chosen_hom_inhabited(hom_category)
        return Unknown

    def _morphism_equality(
        self,
        first: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
    ) -> bool | None:
        """A leaf engine's exact equality decision for two parallel morphisms, when it owns one."""
        if self.has_full_ambient():
            return self.ambient()._morphism_equality(first, second)
        return None

    # -- membership and equality ----------------------------------------------

    def equality(self) -> Predicate:
        if self.has_ambient():
            return self.ambient().equality()
        return self._equality

    def owns_equality(self) -> bool:
        """Whether the predicate this category answers equality with is its own.

        A subcategory shares its ambient's, and an image its target's, so an exact handler
        for what every category's morphisms have is registered once, by the owner.
        """
        return self.equality() is self._equality

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return member(candidate, self)

    def __contains__(self, candidate: ContainmentInput) -> bool:
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

    def _refinement_admissible(self, candidate: CategoryOfCategories.ElementType) -> bool:
        """Whether ``candidate`` may be placed in this exact category by refinement.

        Ordinary subcategory refinement is trusted construction data, so the default is
        unrestricted.  A category whose property would otherwise expose an operation
        without the data needed to execute it overrides this at that property owner.
        """
        return True

    # -- the Mor(n, C) tower ----------------------------------------------------

    @overload
    def morphism_category(self, level: Literal[0]) -> Category[MorphismData, TwoMorphismData]: ...

    @overload
    def morphism_category(self, level: Literal[1]) -> MorphismCategory[MorphismData, TwoMorphismData]: ...

    @overload
    def morphism_category(self, level: Literal[2]) -> MorphismCategory[TwoMorphismData, []]: ...

    @overload
    def morphism_category(self, level: int | Integer) -> MorphismCategory[[], []]: ...

    @cached_method
    def morphism_category(
        self, level: int | Integer
    ) -> Category[MorphismData, TwoMorphismData] | MorphismCategory[MorphismData, TwoMorphismData] | MorphismCategory[TwoMorphismData, []] | MorphismCategory[[], []]:
        """``Mor(level, self)``: ``Mor(0, C)`` is ``C`` and ``Mor(n + 1, C)`` is ``Mor(Mor(n, C))``."""
        assert level >= 0
        if level == 0:
            return self
        if level > 1:
            return self.morphism_category(level - 1).morphism_category(1)
        return self.morphism_category_type()(self)

    def morphism_category_type(
        self,
    ) -> type[MorphismCategory[MorphismData, TwoMorphismData]]:
        from sage_categories.cat.morphisms import MorphismCategory

        return MorphismCategory

    def base_category(self) -> Category:
        """The strongest category ``C`` such that this category is a subcategory of ``Mor(C)``.

        A narrowing carries the roots it is narrowed by, and a root that is itself a
        category of morphisms narrows the base by its own base: the narrowing of
        ``Mor(C)`` by ``{Mor(C.P()), Isomorphisms, Identity}`` is a subcategory of
        ``Mor(C.P())``, so its base is ``C.P()``.  That narrowing is where ``1_X`` for
        ``X`` in ``C.P()`` is placed (``cat/properties.py``,
        ``NarrowedProperty.structure_functors``), and answering ``C`` there replaces an
        established placement with an ancestor, which POL-CAT-074 forbids.  A root that
        is a property of ``Mor(C)`` narrows the morphisms and not the base, so it
        contributes nothing here.
        """
        source, is_morphism = self._object_role_source()
        if is_morphism:
            return source
        assert self.has_ambient(), f"{self!r} is not a category of morphisms"
        morphism_roots = tuple(root.base_category() for root in self.narrowing_roots() if root._object_role_source()[1])
        ambient = self.ambient().base_category()
        bases = tuple(root.narrowing_base() for root in morphism_roots)
        common = tuple(base for base in bases if all(is_subcategory(root, base) for root in morphism_roots))
        owner = next(
            (base for base in common if all(is_subcategory(base, other) for other in common)),
            ambient,
        )
        return owner.intersection(morphism_roots)

    # -- identities and composition -------------------------------------------
    #
    # ``Cat`` defines each of these once and every category has them (D44, D85,
    # POL-LEAF-065).  Two cases, and they are the two relations a selected functor can
    # carry.
    #
    # A full subcategory has exactly the morphisms, identities, and composites of its
    # ambient between its objects (Mathlib ``InducedCategory``), and its monomorphism is
    # the identity on values: a category declared by
    # ``Fun(self, T).Monomorphisms().Isofibrations().Full()()`` obtains the ambient's own
    # value and refines it into ``Mor(self)``, so ``1_X`` stays one morphism.
    #
    # Every other category constructs its own value, in ``self.MorphismType``.  That is
    # where the inherited implementation is: ``self.MorphismType`` is compiled from this
    # category's declaration and, for each selected structure functor declared an
    # isofibration ``F: self -> D``, from ``D.MorphismType`` (D164 to D167), and the
    # kernel initializes each reached owner with the datum ``F``'s own morphism action
    # feeds to that owner's constructor (D13, D110).  So the category that owns the
    # operation for the morphisms of ``self`` is ``D``, the operation reaches ``self``
    # as ordinary compiled inheritance, and the result is a morphism of ``self`` because
    # it is constructed as an object of ``Mor(self)``.  A core, whose monomorphism is
    # not full, and a category whose morphisms carry data it composes, state their own
    # (``cat/core.py``, ``cat/shapes.py``, ``Sets()`` under D132).

    @cached_method(key=lambda self, member_object: identity_key(member_object))
    def _identity_morphism_(self, member_object: ObjectRole) -> MorphismRole:
        """The private construction of ``1_X``, run once per object (POL-CAT-083).

        The mathematical owner of ``1_X`` is the endomorphism monoid, and its one public
        spelling is ``End_C(X).one()`` (POL-CAT-023, D84); this is the construction that
        monoid's unit calls, on the category that owns identities.  A category whose
        identities are another category's overrides it.

        An identity is its own inverse and an endomorphism: it retains itself as its
        inverse and is placed in ``Mor(self).Automorphisms()`` by construction
        (POL-CAT-079/081).
        """

        identity = self.construct_identity(member_object)
        cells = _cells_engine()

        cells.retain_identity(self, identity)
        self.retain_inverses(identity, identity)
        refine(identity, self.morphism_category(1).Identity())
        return identity

    def retained_inverse(self, morphism: MorphismRole) -> MorphismRole | None:
        """The inverse this category retained for ``morphism``, or ``None``; it constructs nothing.

        ``inverse_morphism`` constructs a symbolic inverse when none is retained, which is
        the right answer to the question it asks and the wrong one for a reader deciding
        whether two adjacent factors of a word cancel.
        """
        match morphism in self._inverses:
            case True:
                return self._inverses[morphism]
            case False:
                return None

    def retain_inverses(
        self,
        forward: MorphismRole,
        backward: MorphismRole,
    ) -> None:
        """Record two morphisms as mutually inverse; both enter ``Mor(self).Isomorphisms()`` (POL-MATH-037)."""

        self._inverses[forward] = backward
        self._inverses[backward] = forward
        isomorphisms = self.morphism_category(1).Isomorphisms()
        refine(forward, isomorphisms)
        refine(backward, isomorphisms)
        cells = _cells_engine()

        cells.retain_inverses(self, forward, backward)

    def compose_morphisms(self, second: MorphismRole, first: MorphismRole) -> MorphismRole:
        """``second * first`` through the owned composition; a composite of retained-invertible morphisms retains ``first⁻¹ * second⁻¹``."""
        assert first.codomain() is second.domain()
        if self._identity_morphism_.is_in_cache(first.domain()) and self._identity_morphism_(first.domain()) is first:
            return second
        if self._identity_morphism_.is_in_cache(second.domain()) and self._identity_morphism_(second.domain()) is second:
            return first
        composite = self.composite(second, first)
        if first in self._inverses and second in self._inverses and composite not in self._inverses:
            self.retain_inverses(composite, self.composite(self._inverses[first], self._inverses[second]))
        return composite

    def inverse_morphism(self, morphism: MorphismRole) -> MorphismRole:
        """The inverse of a morphism placed in ``Mor(self).Isomorphisms()`` (POL-CAT-079, POL-KERNEL-025).

        The retained inverse when this category retained one (an identity, a
        two-rule construction, a composite of invertibles); the ambient's inverse for
        a declared subcategory; else the owned symbolic inverse, constructed in
        ``Mor(self)(B, A).Isomorphisms()`` by ``_symbolic_inverse_`` and whose equations
        hold by placement (``specs/undecidable-properties.md``, isomorphism inversion).
        """

        if morphism in self._inverses:
            return self._inverses[morphism]
        if self.has_ambient():
            inverse = self.ambient().inverse_morphism(morphism)
            refine(inverse, self.morphism_category(1))
            return inverse
        symbolic = self._symbolic_inverse_(morphism)
        self.retain_inverses(morphism, symbolic)
        return symbolic

    def _symbolic_inverse_(self, morphism: MorphismRole) -> MorphismRole:
        """The symbolic inverse of ``morphism``, constructed in ``Mor(self)(B, A).Isomorphisms()`` with no executable rule.

        A category whose morphisms carry no data constructs it from none; a category
        whose morphisms carry a rule supplies a rule that fails when evaluated.
        """
        return self.morphism_category(1)(morphism.codomain(), morphism.domain()).Isomorphisms()()

    def element_from_defining_morphism(self, defining_morphism: MorphismRole) -> ElementRole:
        """The generalized element ``t: T -> X`` of ``X`` given by a morphism into it (POL-CAT-058).

        The element is retained by that exact morphism (POL-CAT-066): one defining
        morphism names one generalized element, so two callers reach one value. A declared subcategory shares its ambient's element values;
        ``Sets()`` overrides for its points, which carry a datum.
        """
        assert defining_morphism in self.morphism_category(1), f"{defining_morphism!r} is not a morphism of {self!r}"
        if self.has_ambient():
            return self.ambient().element_from_defining_morphism(defining_morphism)
        return self._retained_element(defining_morphism)

    @cached_method(key=lambda self, defining_morphism: identity_key(defining_morphism))
    def _retained_element(self, defining_morphism: MorphismRole) -> ElementRole:
        """The one generalized element retained by an exact defining morphism."""
        return self.ElementType(defining_morphism)

    def construct_morphism(
        self,
        domain: ObjectRole,
        codomain: ObjectRole,
        *args: MorphismData.args,
        **kwargs: MorphismData.kwargs,
    ) -> MorphismRole:
        """The morphism ``domain -> codomain`` this category's morphism data names."""

        if self.has_full_ambient():
            morphism = self.ambient().construct_morphism(domain, codomain, *args, **kwargs)
            refine(morphism, self.morphism_category(1))
            return morphism
        return self.MorphismType(domain, codomain, *args, **kwargs)

    def construct_identity(self, member_object: ObjectRole) -> MorphismRole:
        """``1_X``: the morphism with both endpoints ``X``, which its object determines and no datum names.

        A subcategory contains the identities of its objects, full or not, so the guard
        is the ambient itself and the ambient's identity refines into this category.
        """

        if self.has_ambient():
            ambient = self.ambient()
            identity = ambient.morphism_category(1)(member_object, member_object).one()
            refine(identity, self.morphism_category(1))
            return identity
        return self.MorphismType(member_object, member_object)

    def composite(self, second: MorphismRole, first: MorphismRole) -> MorphismRole:
        """``second * first``: the morphism its two factors determine, retained on the pair.

        A subcategory is closed under composition, full or not, so the guard is the
        ambient itself.  With no ambient the category composes formally: ``g * f`` is
        determined by ``g`` and ``f`` and not by ``dom f`` and ``cod g``, so the
        composite is retained on the pair and retains the pair as its factors (D44).
        """

        assert first.codomain() is second.domain(), (
            f"{second!r} after {first!r} is not composable: the first ends at {first.codomain()!r} and the second starts at {second.domain()!r}"
        )
        if self.has_ambient():
            composite = self.ambient().composite(second, first)
            refine(composite, self.morphism_category(1))
            return composite
        return self._formal_composite(second, first)

    @cached_method(key=lambda self, second, first: identity_key(second, first))
    def _formal_composite(self, second: MorphismRole, first: MorphismRole) -> MorphismRole:
        """The retained formal composite in a category with no ambient owner."""
        formal = self.MorphismType(first.domain(), second.codomain())
        formal.retain_factors(first, second)
        _cells_engine().retain_composite(self, formal, first, second)
        return formal

    def identity_two_morphism(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:

        if self.has_full_ambient():
            two_cell = self.ambient().identity_two_morphism(morphism)
            refine(two_cell, self.morphism_category(2))
            return two_cell
        two_cells = self.morphism_category(2)
        two_cell = two_cells.ObjectType(domain=morphism, codomain=morphism)
        cells = _cells_engine()

        cells.retain_identity(self.morphism_category(1), two_cell)
        return two_cell

    def compose_two_morphisms(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:

        if self.has_full_ambient():
            two_cell = self.ambient().compose_two_morphisms(second, first)
            refine(two_cell, self.morphism_category(2))
            return two_cell
        # A 1-category has identity 2-morphisms only: the composite of two identities is either.
        assert first.domain() is first.codomain() and second.domain() is second.codomain()
        assert first.domain() is second.domain()
        cells = _cells_engine()

        cells.retain_composite(self.morphism_category(1), first, first, second)
        return first

    def construct_two_morphism(
        self,
        first: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
        *args: TwoMorphismData.args,
        **kwargs: TwoMorphismData.kwargs,
    ) -> MorphismCategory.ObjectType:

        if self.has_full_ambient():
            two_cell = self.ambient().construct_two_morphism(first, second, *args, **kwargs)
            refine(two_cell, self.morphism_category(2))
            return two_cell
        assert first is second and not args and not kwargs, f"{self!r} is a 1-category: its only 2-morphisms are identities"
        return self.morphism_category(2)(first, first).one()

    # -- points of the category as Cat elements (POL-CAT-058), retained once (POL-CAT-083) --------

    def Terminal(self) -> ObjectRole:
        """``1_C``: the chosen terminal object, whose points ``1_C -> X`` are the points of ``X``.

        A category that states no terminal object has no points; the ones this
        repository builds points in state theirs.
        """
        raise AssertionError(f"{self!r} declares no terminal object")

    def point_morphism(self, point: ElementRole) -> MorphismRole:
        """The morphism ``1_C -> X`` that selects a point of ``X``, the converse of ``element_from_defining_morphism``.

        A category whose points are morphisms from its terminal object states this
        reading; it is what lets a generalized-element diagram such as ``μ ∘ ⟨x, y⟩`` be
        evaluated on points.
        """
        raise AssertionError(f"{self!r} declares no morphism from its terminal object selecting a point")

    @cached_method(key=lambda self, member_object: identity_key(member_object))
    def point_functor(self, member_object: ObjectRole) -> Functor:
        """The point ``* -> self`` selecting the object ``member_object``.

        The objects of ``Mor(C)`` are the morphisms of ``C``, so ``member_object`` is a
        morphism there and its identity is the one ``Mor(C)`` supplies (POL-CAT-021).

        The arrow is constructed in ``Fun(*, self).Monomorphisms()``, and that call is the
        declaration ``cat_kernel`` reads (D146, D162, ``POL-CAT-069``).  It is the
        strongest of ``Fun``'s named properties that holds for every ``self`` and every
        object of it: a functor out of the terminal category is faithful and injective on
        objects, hence monic, while an isomorphism ``X -> Y`` of ``self`` has nothing to
        lift to in ``*``, so the arrow is not an isofibration.  Its fullness, which holds
        exactly when ``member_object`` has no nonidentity endomorphism, is not declared.
        """
        Fun = _functors()

        # The identity is the morphism action's own result, computed when the action
        # runs.  A point selected by a class under construction is the arrow that places
        # its object, so the arrow exists before the object is an object of ``self``
        # (D154, D169).  The identity-keyed Sage method cache retains the one point
        # functor for that exact object without invoking proposition-valued equality.
        return Fun(Cat().Terminal(), self).Monomorphisms()(
            lambda vertex: member_object,
            lambda path: self.morphism_category(1)(member_object, member_object).one(),
        )

    def Point(self) -> Functor:
        """The point functor ``* -> self`` selecting the object under construction (D154).

        A leaf class places its object in ``self`` by adding this to its structure
        functors, and that object is the value the class is being constructed for, so
        the kernel's construction context names it (``specs/functor.md``, "Point
        categories and point functors").  Selecting it places the object in ``self`` and
        gives it the ``self.ObjectType`` inheritance and its ``ObjectType`` the
        ``self.ElementType`` inheritance, through the categorical level shift (D128,
        D154, D161, D169).
        """
        from sage_categories.kernel.construction import active_object_context

        context = active_object_context()
        assert context is not None, f"{self!r}.Point() selects the object under construction, and none is being constructed here"
        return self.point_functor(context.canonical_image)

    @cached_method(key=lambda self, morphism: identity_key(morphism))
    def arrow_functor(self, morphism: MorphismRole) -> Functor:
        """The diagram ``[1] -> self`` of shape the walking arrow that ``morphism`` denotes."""
        Fun = _functors()
        walking_arrow = Cat().Simplex(1)
        endpoints = {0: morphism.domain(), 1: morphism.codomain()}

        def on_object(
            vertex: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            return endpoints[walking_arrow.label(vertex)]

        def on_morphism(
            path: MorphismCategory.ObjectType,
        ) -> MorphismCategory.ObjectType:
            if path.domain() is path.codomain():
                # The identity of the endpoint as an object of this category: for an
                # endpoint that is itself a morphism, the identity square, not its 2-cell.
                endpoint = on_object(path.domain())
                return self.morphism_category(1)(endpoint, endpoint).one()
            return morphism

        return Fun(walking_arrow, self)(on_object, on_morphism)

    # -- universal constructions, declared once (D31, POL-CAT-050/092, POL-CAT-093) --------
    #
    # A construction family is a regressive functorial construction, which is an
    # axiom: ``X`` is in ``C.Products()`` exactly when it lies in the image of the
    # nontrivial product functor.  Declared here on the base class, every category
    # receives ``C.Products()``, ``C.Coproducts()``, ``C.Limits(I)``, and
    # ``C.Colimits(I)`` from ``cat_kernel``, which builds every axiom's subcategory
    # (D175): a declared subcategory as the inverse image
    # of its ambient's family, any other category as the family's own implementation
    # (``cat/constructions.py``).  Each family exists for every supplied shape without
    # asserting that the category has those limits (POL-CAT-051): constructing an
    # object needs an owned construction or supplied universal data.
    Products = ConstructionFamily()
    Coproducts = ConstructionFamily()
    Limits = ConstructionFamily()
    Colimits = ConstructionFamily()

    # ``D.EssentialImage(F)``, the objects of ``D`` isomorphic to some ``F(X)``, is the
    # axiom the row above is the special case of: being a product is membership in the
    # essential image of the nontrivial product functor, and axioms can be parameterized
    # (D168).  Its parameter is the functor, a morphism of ``Cat()`` rather than an
    # object, which is the whole of what it turns on; ``cat/images.py`` implements it.
    EssentialImage = Axiom()

    def Pullbacks(self) -> Category:
        """``C.Limits(L(2, 2))``: limits over the walking cospan."""
        return self.Limits(Cat().WalkingCospan())

    def Pushouts(self) -> Category:
        """``C.Colimits(L(2, 0))``: colimits over the walking span."""
        return self.Colimits(Cat().WalkingSpan())

    def Equalizers(self) -> Category:
        return self.Limits(Cat().WalkingParallelPair())

    def Coequalizers(self) -> Category:
        return self.Colimits(Cat().WalkingParallelPair())

    def StrictImage(self, functor: Functor) -> Category:
        """Return the literal object-and-morphism image of ``functor`` in this category."""
        from sage_categories.cat.images import strict_image

        return strict_image(self, functor)

    def FullImage(self, functor: Functor) -> Category:
        """Return the full subcategory on the literal object image of ``functor``."""
        from sage_categories.cat.images import full_image

        return full_image(self, functor)

    def limit_construction(self, shape: Category) -> Callable[[Functor], ObjectRole]:
        """The owned construction of ``I``-limits, when this category declares one."""
        from sage_categories.cat.constructions import lift_limit
        from sage_categories.cat.functors import FunctorCategory
        from sage_categories.cat.opposites import OppositeCategory

        for functor in self.selected_functors():
            lifting = functor.limit_lifting(shape)
            if lifting is not None:
                apex_lift, morphism_lift = lifting
                return lambda diagram: lift_limit(functor, diagram, apex_lift, morphism_lift)
        if isinstance(self, OppositeCategory):
            original = self.original()
            if original is Cat():
                from sage_categories.cat.cat_constructions import (
                    _limit_of_opposite_categories,
                )

                return _limit_of_opposite_categories
            if isinstance(original, FunctorCategory):
                return _pointwise_limit_in_opposite_functor_category
            construction = original.colimit_construction(shape.op())
            return lambda diagram: construction(diagram.op())
        if not shape.is_discrete() and shape is not Cat().WalkingParallelPair() and shape.op() is not Cat().WalkingParallelPair():
            from sage_categories.cat.limit_basis import limit_from_products_equalizers

            return limit_from_products_equalizers
        raise AssertionError(f"{self!r} owns no {shape!r}-limit construction; supply universal data")

    def colimit_construction(self, shape: Category) -> Callable[[Functor], ObjectRole]:
        """Use this category's retained construction, then derive general colimits from coproducts and coequalizers."""
        if shape in self._colimit_constructors:
            return self._colimit_constructors[shape]
        if not shape.is_discrete() and shape is not Cat().WalkingParallelPair() and shape.op() is not Cat().WalkingParallelPair():
            from sage_categories.cat.limit_basis import (
                colimit_from_coproducts_coequalizers,
            )

            return colimit_from_coproducts_coequalizers
        raise AssertionError(f"{self!r} owns no {shape!r}-colimit construction; supply universal data")

    def presenting_diagrams(self, constructed: ObjectRole) -> tuple[Functor, ...]:
        """The diagrams this category constructed ``constructed`` from; a category that constructs nothing retains none.

        A construction family retains them per object (``cat/constructions.py``), and this
        is how an apex finds the family it was refined into among the roots of its
        placement.
        """
        return ()

    # -- slices, coslices, and the categories of subobjects (POL-FUN-029, POL-CAT-095, POL-SCOPE-003) --

    @cached_method(key=lambda self, member_object: identity_key(member_object))
    def SliceOver(self, member_object: ObjectRole) -> Category:
        """``C.SliceOver(x)``: the strict pullback of ``ev_1: Fun([1], C) -> C`` along ``x: * -> C``."""
        from sage_categories.cat.slices import slice_over

        assert member_object in self, f"{member_object!r} is not an object of {self!r}"
        return slice_over(self, member_object)

    @cached_method(key=lambda self, member_object: identity_key(member_object))
    def CosliceUnder(self, member_object: ObjectRole) -> Category:
        """``C.CosliceUnder(x) = C.op().SliceOver(x).op()``."""
        from sage_categories.cat.slices import coslice_under

        assert member_object in self, f"{member_object!r} is not an object of {self!r}"
        return coslice_under(self, member_object)

    # The four fixed-object construction categories, defined once here so that every
    # category inherits them (POL-CAT-092).  The ambient named in the call fixes the role
    # of ``X``: an object of two categories gives two of these calls, not one.

    def Subobjects(self, member_object: ObjectRole) -> Category:
        """``C.Subobjects(X) = C.SliceOver(X).Monomorphisms()``: the monomorphisms into ``X`` with their domains."""
        return self.SliceOver(member_object).Monomorphisms()

    def Superobjects(self, member_object: ObjectRole) -> Category:
        """``C.Superobjects(X) = C.CosliceUnder(X).Monomorphisms()``."""
        return self.CosliceUnder(member_object).Monomorphisms()

    def CoveringObjects(self, member_object: ObjectRole) -> Category:
        """``C.CoveringObjects(X) = C.SliceOver(X).Epimorphisms()``: the pairs ``(Y, p: Y -> X)`` with ``p`` an epimorphism (POL-CAT-026)."""
        return self.SliceOver(member_object).Epimorphisms()

    def CoveredObjects(self, member_object: ObjectRole) -> Category:
        """``C.CoveredObjects(X) = C.CosliceUnder(X).Epimorphisms()``."""
        return self.CosliceUnder(member_object).Epimorphisms()

    # -- the core (D99; ``specs/functor.md``, "The core functor"; ``cat/core.py``) --------

    def Core(self) -> Category:
        """``Core.on_object(self)``: the objects of ``self`` with its isomorphisms as morphisms."""
        from sage_categories.cat.core import Core

        return Core.on_object(self)

    # -- the chosen sets of objects and morphisms of a small shape (specs/functor.md, "Diagram shapes and universal constructions") -----------------
    #
    # A shape used as a diagram index exposes its objects as an object of ``Sets()``
    # and, when it has finitely many morphisms, its morphisms too; the points of
    # those sets select objects and morphisms.  A category that declares neither
    # has all generalized elements and no enumeration; a set limit over it is then
    # undecided (specs/functor.md, "Diagram shapes and universal constructions").
    # Each shape narrows the generic ``Cat().ElementType`` annotations to its exact
    # ``Sets()`` types.

    def object_set(self) -> CategoryOfCategories.ElementType:
        """The set of objects, an object of ``Sets()``, when this category declares one."""
        raise AssertionError(f"{self!r} declares no set of objects")

    def object_at(self, point: CategoryOfCategories.ElementType) -> ObjectRole:
        """The object selected by a point of ``object_set()``."""
        raise AssertionError(f"{self!r} declares no set of objects")

    def object_point(self, member_object: ObjectRole) -> CategoryOfCategories.ElementType:
        """The point of ``object_set()`` selecting an object: the one whose object equals it."""
        return next(point for point in self.object_set() if ask(self.object_at(point) == member_object))

    def morphism_set(self) -> AppliedQuery:
        """Return the typed query for this category's set of morphisms."""
        return _morphism_set()(self)

    def _chosen_morphism_set(self) -> CategoryOfCategories.ElementType | UnknownClass:
        """The exact evaluation case of ``morphism_set()``, which a category that chooses a finite enumeration of its morphisms overrides."""
        return Unknown

    def morphism_at(self, point: CategoryOfCategories.ElementType) -> MorphismRole:
        """The morphism selected by a point of ``morphism_set()``."""
        raise AssertionError(f"{self!r} declares no set of morphisms")

    def generating_morphisms(
        self,
    ) -> tuple[MorphismRole, ...] | UnknownClass:
        """A finite family of morphisms generating this category under composition, or ``Unknown``.

        The default is every morphism when the morphism set is finite and enumerated, or
        when the owned exact finite evaluation enumerates it (``hom_morphisms`` reads the
        same evaluation): a finite comma category states its compatibility conditions this way.
        """
        morphisms = ask(self.morphism_set())
        if morphisms is not Unknown:
            return tuple(self.morphism_at(point) for point in morphisms)
        finite = _finite_category_data(self)
        return Unknown if finite is Unknown else finite.morphisms

    def hom_morphisms(
        self,
        source: ObjectRole,
        target: ObjectRole,
    ) -> tuple[MorphismRole, ...] | UnknownClass:
        """An exact finite enumeration of a hom, when owned evaluation supplies it."""
        finite = _finite_category_data(self)
        if finite is Unknown:
            return Unknown
        return tuple(arrow for arrow in finite.morphisms if arrow.domain() is source and arrow.codomain() is target)

    def image_factorization(self, arrow: MorphismRole) -> tuple[MorphismRole, MorphismRole]:
        """The chosen regular epimorphism/monomorphism factorization, when supplied."""
        raise AssertionError(f"{self!r} declares no regular image factorization")

    def factor_through_monomorphism(self, mono: MorphismRole, arrow: MorphismRole) -> MorphismRole | Literal[False] | UnknownClass:
        """Find the unique factor through a mono, decide nonexistence, or remain undecided."""
        return Unknown

    def retain_biproduct_operations(
        self,
        biproduct: Callable[[object, object], object],
        zero_morphism: Callable[[object, object], object],
    ) -> None:
        """Retain this exact category's selected biproduct and zero-morphism operations."""
        self._biproduct_constructor = biproduct
        self._zero_morphism_constructor = zero_morphism

    def retain_colimit_construction(
        self,
        shape: Category,
        construction: Callable[[Functor], ObjectRole],
    ) -> None:
        """Retain this exact category's selected colimit construction for ``shape``."""
        self._colimit_constructors[shape] = construction

    def biproduct(
        self,
        first: ObjectRole,
        second: ObjectRole,
    ) -> ObjectRole:
        """``X @ Y``, through this category's retained additive construction."""
        assert self._biproduct_constructor is not None, f"{self!r} declares no biproduct"
        return self._biproduct_constructor(first, second)

    def zero_morphism(
        self,
        source: ObjectRole,
        target: ObjectRole,
    ) -> MorphismRole:
        """The selected additive zero ``source -> target`` when this category supplies one."""
        assert self._zero_morphism_constructor is not None, f"{self!r} declares no zero morphisms"
        return self._zero_morphism_constructor(source, target)

    def exponential(
        self,
        exponent: ObjectRole,
        base: ObjectRole,
    ) -> ObjectRole:
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

    def narrowing_base(
        self,
    ) -> Category[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole]:
        """The category whose narrowings this placement is one of; ``self`` when it is a base."""
        return self

    def narrowing_roots(
        self,
    ) -> tuple[
        Category[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole],
        ...,
    ]:
        """The roots this placement is narrowed by, closed under the roots of each root's own placement."""
        return ()

    def intersection(
        self,
        roots: tuple[
            Category[
                MorphismData,
                TwoMorphismData,
                ObjectRole,
                ElementRole,
                MorphismRole,
            ],
            ...,
        ],
    ) -> Category[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole]:
        """The narrowing of this base by the given roots, one object per closed set of roots.

        A root containing the base narrows nothing; a set of roots that is exactly one
        root's own closed set is that root.

        A root belongs to this base when it narrows it, which the root states directly.
        Established placement is the wrong question: a subcategory monomorphism of ``Fun``
        is itself placed in a property category of ``Fun``, so those placements are queued
        until ``FunctorsCategory._bootstrap`` drains them, and a narrowing taken before
        that would build a second value for a category that already exists.  One
        mathematical category with two values cannot compile one class.
        """
        base = self.narrowing_base()
        if base is not self:
            return base.intersection((*self.narrowing_roots(), *roots))
        selected = self.closed_roots(roots)
        if not selected:
            return self
        key = tuple(root.ordinal() for root in selected)
        for root in (*roots, *selected):
            belongs = root.narrowing_base() is self or is_subcategory(root, self)
            if belongs and tuple(member.ordinal() for member in self.closed_roots((root,))) == key:
                return root
        return self._narrowing(selected)

    @cached_method(key=lambda self, selected: identity_key(*selected))
    def _narrowing(
        self,
        selected: tuple[Category[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole], ...],
    ) -> Category[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole]:
        """Construct the canonical narrowing for one exact closed root family."""
        return self.narrowing_type()(self, selected)

    def closed_roots(
        self, roots: tuple[Category[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole], ...]
    ) -> tuple[Category[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole], ...]:
        """The roots of the narrowing of this base by ``roots``: every root each one carries, in ordinal order, omitting those containing the base."""
        closed: dict[int, Category] = {}
        for root in roots:
            for member in root.narrowing_roots() or (root,):
                if not is_subcategory(self, member):
                    closed[member.ordinal()] = member
        return tuple(root for _, root in sorted(closed.items()))

    def property_subcategory(
        self,
        property_category: Category[
            MorphismData,
            TwoMorphismData,
            ObjectRole,
            ElementRole,
            MorphismRole,
        ],
    ) -> Category[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole]:
        """``self.P()``: the narrowing of this placement by the roots of ``P`` (POL-CAT-084)."""
        return self.narrowing_base().intersection((*self.narrowing_roots(), *property_category.narrowing_roots()))

    def retain_intersection(self, roots: tuple[Category, ...], intersection: Category) -> None:
        """Identify a constructed category with the intersection of these roots."""
        assert intersection.narrowing_base() is self
        selected = self.closed_roots(roots)
        assert selected, "an externally retained intersection must narrow the base"
        if self._narrowing.is_in_cache(selected):
            assert self._narrowing(selected) is intersection
            return
        self._narrowing.set_cache(intersection, selected)

    def __getattr__(
        self, name: str
    ) -> Callable[
        ...,
        Category[
            MorphismData,
            TwoMorphismData,
            ObjectRole,
            ElementRole,
            MorphismRole,
        ],
    ]:
        """``C.P().Q()``: an axiom of the ambient is an axiom here, along the subcategory monomorphism (D77 item 4).

        An axiom is a descriptor on the class that declares it, and a declared
        subcategory is a value of another class -- ``C.P()`` is a ``PropertySubcategory``
        -- so the accessor a category class writes is out of reach of ordinary attribute
        lookup on its own subcategories.  The declaration is still the one owner: this
        finds it along the ambient chain and applies it here, where ``Axiom`` takes the
        inverse image along this category's monomorphism (D83).  Nothing is patched onto
        a value and no second accessor exists (``POL-LEAF-064``).

        Private names are not axioms, and answering for one would hide a genuine missing
        attribute behind an ambient walk.
        """
        if name.startswith("_"):
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
        from sage_categories.cat.predicates import declared_axiom

        axiom = declared_axiom(self, name)
        if axiom is None:
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
        return axiom.__get__(self, type(self))

    def narrowing_type(
        self,
    ) -> type[
        Category[
            MorphismData,
            TwoMorphismData,
            ObjectRole,
            ElementRole,
            MorphismRole,
        ]
    ]:
        from sage_categories.cat.properties import NarrowedProperty

        return NarrowedProperty


# Core category classes import this name while the mutually recursive ``Cat`` cluster is
# defined, before ``Cat()`` exists to be asked for its own object role.  ``bootstrap``
# binds it again from that role, which is this same class: ``Cat()`` writes
# ``CategoryDeclaration`` as its ``ObjectType`` and the compiler compiles the class a
# category writes (``specs/functor.md``, "Compiled implementation classes").
Category = CategoryDeclaration


@dataclass(frozen=True, slots=True)
class _ImplementationInvocation:
    """The constructor currently being read by ``Cat().implement``."""

    category_type: type[Category]
    initialize: Callable[[Category], None]


_implementation_invocation: ContextVar[_ImplementationInvocation | None] = ContextVar(
    "category implementation invocation",
    default=None,
)


def _shared_category(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> Category:
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
    assert shared is not None, f"{first!r} in {first.category()!r} and {second!r} in {second.category()!r} have no least common category along subcategory monomorphisms"
    return shared.construction_owner()


# The lifts a functor ``p: E -> B`` retains over a stated class of morphisms of ``B``
# (POL-FUN-029, ``specs/functor.md``, "Slices and coslices"): the owner of the
# functor registers one rule per direction, and each lift is constructed once per
# ``(morphism, object)`` and retained by identity.  The rule states the class of
# morphisms it lifts and fails loudly outside it.
type LiftRule = Callable[
    [MorphismCategory.ObjectType, CategoryOfCategories.ElementType],
    MorphismCategory.ObjectType,
]

# The factors ``(first, second)`` of every composite ``second * first`` constructed by
# ``Cat()``: an explicit composite names its construction (``specs/functor.md``,
# "Structural inheritance": a selected composite retains its factor functors).
_composite_factors: MonoDict = MonoDict()


def retain_composite_factors(
    composite: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> None:
    """Retain that ``composite`` is ``second * first`` (``Mor(C).ObjectType.retain_factors``)."""
    assert composite not in _composite_factors, f"{composite!r} already retains its factors"
    assert first.codomain() is second.domain(), f"{second!r} after {first!r} is not composable"
    assert composite.domain() is first.domain() and composite.codomain() is second.codomain(), f"{composite!r} does not run {first.domain()!r} -> {second.codomain()!r}"
    _composite_factors[composite] = (first, second)


def composite_factors(
    composite: MorphismCategory.ObjectType,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    """The retained factors ``(first, second)`` of ``second * first`` (``Mor(C).ObjectType.factors``)."""
    assert composite in _composite_factors, f"{composite!r} is not a retained composite"
    return _composite_factors[composite]


def is_composite(morphism: MorphismCategory.ObjectType) -> bool:
    """Whether ``morphism`` retains two factors (``Mor(C).ObjectType.is_composite``)."""
    return morphism in _composite_factors


def _composite_sequence(functor: Functor) -> tuple[Functor, ...]:
    if functor not in _composite_factors:
        return (functor,)
    first, second = _composite_factors[functor]
    return (*_composite_sequence(first), *_composite_sequence(second))


@dataclass(frozen=True, eq=False, slots=True)
class FunctorData:
    """The two complete executable actions of a functor (D123, POL-FUN-002)."""

    on_object: OnObject
    on_morphism: OnMorphism


@dataclass(frozen=True, eq=False, slots=True)
class _StructuralFunctorData:
    """A functor whose execution is determined by retained categorical structure."""


class CategoryOfCategories(CategoryDeclaration[[OnObject, OnMorphism], [Assignment]]):
    """The singleton ``Cat()``."""

    # The three classes ``Cat()`` writes, in the one form every category class uses: name
    # the class this category's role is.  ``Cat()`` is an object of ``Cat()``, so this
    # class derives from the one below and Python evaluates a base before the body, which
    # is why that class is written above rather than between these lines.  Where it is
    # written is not a second form; ``ObjectType = FullSubcategory.ObjectType`` and
    # ``Mor(K).ObjectType = K.MorphismType`` are the same level identity.
    ObjectType = CategoryDeclaration

    # Inhabitation and emptiness of a category, as the two property subcategories
    # POL-CAT-086 names.  The kernel derives ``is_inhabited()`` and ``is_empty()`` from
    # these two identifiers and writes them onto the ``ObjectType`` above, so every
    # category receives them (D89).  They state mutually negated propositions and both
    # can stay unresolved (``specs/property-refinement.md``, "Fixed-endpoint predicates").
    #
    # ``Cat().Empty()`` is this property subcategory; the empty category itself is the
    # object ``Cat().Initial()`` (``specs/functor.md``, "Canonical objects of Cat").
    Inhabited = Axiom()
    Empty = Axiom()

    # ``Cat().Concrete()``: the categories a faithful functor carries to ``Sets()``.
    # ``Sets()`` is concrete by its identity, and a category with a faithful selected
    # functor to a concrete one is concrete along it, because faithful functors compose.
    # So a leaf declares only its immediate structure functor and never names ``Sets()``:
    # a lattice declares its functor to the modules over its base, that category declares
    # its functor to the abelian groups, and the composite is what this axiom's
    # implementation builds (``cat/concrete.py``, ``functor_to_sets``).
    def _concrete(self, category: CategoryOfCategories.ElementType) -> Proposition:
        return concrete_category(category)

    Concrete = Axiom(_concrete)

    class ElementType:
        """A point ``* -> C`` of a category, whose value is an object of ``C`` (POL-CAT-058).

        Every owned value is such a point, so the compiled class of this declaration sits
        under all three implementation roles and states what every point shares: what it
        is a point of, the morphism defining it, its placement, and its equality (D173).
        The two cases below are the two kinds of point: a point of a category, whose
        placement the kernel retains and refines, and a generalized element ``t: T -> X``
        of an object, whose placement is the slice over ``X``.  The kernel's role test
        tells them apart and its retained point identity carries the datum of each; this
        declaration says what the datum means, and names no kernel type to read it (D130,
        D173, ``specs/resolution.md``, "The closed kernel surface").
        """

        def parent(self) -> CategoryOfCategories.ElementType:
            """The object this is a point of: the category for a point ``* -> C``, the object for a point of one."""
            if self._is_element():
                return self._cat_element_identity.defining_morphism.codomain()
            return self._cat_element_identity.parent

        def defining_morphism(self) -> MorphismCategory.ObjectType:
            """The morphism that defines this point: its own for an element, the point functor's arrow for an object."""
            if self._is_element():
                return self._cat_element_identity.defining_morphism
            return self._cat_element_identity.parent.point_functor(self)

        def category(self) -> Category:
            """The strongest placement established for this point.

            A point ``* -> C`` reads the placement the kernel installed from its
            construction context and refined since (``refinement.place``), including one
            established while the value is still under construction: a category class
            that selects a point functor ``D.Point()`` is placed in ``D`` inside its own
            constructor chain, and the level shift reads that placement (D154, D169).
            A generalized element ``t: T -> X`` is an object of the slice over ``X``.
            """
            if self._is_element():
                return self.parent().category().SliceOver(self.parent())
            return self._category

        def _deciding_category(self) -> Category:
            """The category that decides equality of this point: its placement, or its parent's category for an element."""
            if self._is_element():
                return self.parent().category()
            if self._is_morphism():
                return self.base_category()
            return self._category

        def __eq__(self, candidate: EqualityInput) -> Predicate:
            return self._deciding_category().equality()(self, candidate)

        def __ne__(self, candidate: EqualityInput) -> Proposition:
            return ~self._deciding_category().equality()(self, candidate)

        def __hash__(self) -> int:
            return object.__hash__(self)

        def __mul__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            """``X * Y``: the product in the least category receiving both."""
            return _shared_category(self, other).Products()((self, other))

        def __add__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            """``X + Y``: the coproduct in the least category receiving both."""
            return _shared_category(self, other).Coproducts()((self, other))

        def __matmul__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            """``X @ Y``: the biproduct in the least category receiving both."""
            return _shared_category(self, other).biproduct(self, other)

        def __pow__(self, exponent: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            """``Y ** X``: the exponential object in the least category receiving both."""
            return _shared_category(self, exponent).exponential(exponent, self)

        def _universal_presentation(self) -> UniversalPresentation:
            from sage_categories.cat.constructions import presenting_family

            return presenting_family(self).presentation(self)

        def diagram(self) -> Functor:
            """The diagram of this object's unique selected universal presentation."""
            return self._universal_presentation().diagram()

        def index_category(self) -> Category:
            """The exact index category retained by the selected presentation."""
            return self.diagram().domain()

        def projection(self, index: CategoryOfCategories.ElementType | int) -> MorphismCategory.ObjectType:
            """The leg of the selected limiting presentation."""
            return self._universal_presentation().leg(index)

        def universal_morphism(self, candidate: NaturalTransformation) -> MorphismCategory.ObjectType:
            """The universal map determined by a cone or cocone over the selected diagram."""
            from sage_categories.cat.cones import cocones, cones

            presentation = self._universal_presentation()
            diagram = presentation.diagram()
            presentations = cocones(diagram) if candidate.domain() is diagram else cones(diagram)
            return presentation.lift(presentations(candidate))

        def __repr__(self) -> str:
            return f"point of {self.parent()!r}"

    class MorphismType[
        DomainCategory: "Category[..., ...]" = "Category[..., ...]",
        CodomainCategory: "Category[..., ...]" = "Category[..., ...]",
        DomainObject: "CategoryOfCategories.ElementType" = "CategoryOfCategories.ElementType",
        DomainElement: "CategoryOfCategories.ElementType" = "CategoryOfCategories.ElementType",
        DomainMorphism: "MorphismCategory.ObjectType" = "MorphismCategory.ObjectType",
        CodomainObject: "CategoryOfCategories.ElementType" = "CategoryOfCategories.ElementType",
        CodomainElement: "CategoryOfCategories.ElementType" = "CategoryOfCategories.ElementType",
        CodomainMorphism: "MorphismCategory.ObjectType" = "MorphismCategory.ObjectType",
    ]:
        """A functor: a morphism of ``Cat()`` with a domain, a codomain, and total object and morphism actions."""

        def __init__(self, data: FunctorData | _StructuralFunctorData) -> None:
            self._functor_data = data
            self._limit_liftings: MonoDict = MonoDict()
            self._cartesian_lift_rule = None
            self._cocartesian_lift_rule = None
            self._constant_diagram_value: tuple[CategoryOfCategories.ElementType, ...] = ()
            self._initialize_functor_image_cache()

        # The admission condition is the one the image construction needs.  A retained
        # monomorphism is the identity on the objects and morphisms of its domain
        # (``specs/functor.md``, "Monomorphisms of ``Cat()`` and placement"), so it constructs nothing and
        # admits exactly the members of its domain: a core has every object of
        # its ambient, and that is a membership fact its ambient decides, not a placement
        # its objects ever entered through (POL-CAT-068, POL-FUN-027).  Every other functor
        # builds its image from the domain's construction input, so it admits exactly the
        # values whose placement reaches that node.

        def on_object(self, member_object: DomainObject) -> CodomainObject:
            """The image of an object of the domain, executed by the retained Catlab functor."""
            return self._cached_object_image(member_object, self._construct_object_image)

        def _has_retained_object_image(self, candidate: CategoryOfCategories.ElementType) -> bool:
            """Protected image-category query for an exact retained object action value."""
            return self._image_cache.has_object_image(candidate)

        def _has_retained_morphism_image(self, candidate: MorphismCategory.ObjectType) -> bool:
            """Protected image-category query for an exact retained morphism action value."""
            return self._image_cache.has_morphism_image(candidate)

        def _retain_object_action_result(
            self,
            member_object: CategoryOfCategories.ElementType,
            image: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            assert is_placed(member_object, self.domain()) or member_object in self.domain(), f"{member_object!r} is not an object of {self.domain()!r}"
            assert is_placed(image, self.codomain()) or image in self.codomain(), f"{image!r} is not an object of {self.codomain()!r}"
            from sage_categories.cat.images import retain_object_image

            retain_object_image(self, image)
            return image

        def _declared_object_image(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            """Execute this functor's declared object action through its retained image cache."""
            data = self._functor_data
            assert isinstance(data, FunctorData), f"{self!r} has no primitive object action"
            return self._cached_object_image(
                member_object,
                lambda value: self._retain_object_action_result(value, data.on_object(value)),
            )

        def _construct_object_image(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            catlab = _catlab_engine()

            return self._retain_object_action_result(
                member_object,
                catlab.functor_object_image(self, member_object),
            )

        def _retain_isomorphism_image(
            self,
            morphism: MorphismCategory.ObjectType,
            image: MorphismCategory.ObjectType,
            on_object: Callable[[CategoryOfCategories.ElementType], CategoryOfCategories.ElementType],
            construct: Callable[[MorphismCategory.ObjectType], MorphismCategory.ObjectType],
        ) -> MorphismCategory.ObjectType:
            source, target = self.domain(), self.codomain()
            if is_placed(morphism, source.morphism_category(1).Isomorphisms()):
                inverse = source.retained_inverse(morphism)
                if inverse is not None and target.retained_inverse(image) is None:
                    inverse_image = self._cached_morphism_image(inverse, on_object, construct)
                    target.retain_inverses(image, inverse_image)
                refine(image, target.morphism_category(1).Isomorphisms())
            return image

        def on_morphism(self, morphism: DomainMorphism) -> CodomainMorphism:
            """The image of a morphism of the domain, executed by the retained Catlab functor."""
            image = self._cached_morphism_image(
                morphism,
                self.on_object,
                self._construct_morphism_image,
            )
            return self._retain_isomorphism_image(
                morphism,
                image,
                self.on_object,
                self._construct_morphism_image,
            )

        def _retain_morphism_action_result(
            self,
            morphism: MorphismCategory.ObjectType,
            image: MorphismCategory.ObjectType,
            on_object: Callable[[CategoryOfCategories.ElementType], CategoryOfCategories.ElementType],
        ) -> MorphismCategory.ObjectType:
            morphisms = self.domain().morphism_category(1)
            assert morphism in morphisms, f"{morphism!r} is not a morphism of {self.domain()!r}"
            expected = self.codomain().morphism_category(1)(
                on_object(morphism.domain()),
                on_object(morphism.codomain()),
            )
            assert image in expected, f"{image!r} is not a morphism of {expected!r}"
            refine(image, expected)
            from sage_categories.cat.images import retain_morphism_image

            retain_morphism_image(self, image)
            return image

        def _declared_morphism_image(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            """Execute this functor's declared morphism action through its retained image cache."""
            data = self._functor_data
            assert isinstance(data, FunctorData), f"{self!r} has no primitive morphism action"

            def construct(
                value: MorphismCategory.ObjectType,
            ) -> MorphismCategory.ObjectType:
                return self._retain_morphism_action_result(
                    value,
                    data.on_morphism(value),
                    self._declared_object_image,
                )

            image = self._cached_morphism_image(
                morphism,
                self._declared_object_image,
                construct,
            )
            return self._retain_isomorphism_image(
                morphism,
                image,
                self._declared_object_image,
                construct,
            )

        def _construct_morphism_image(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            catlab = _catlab_engine()

            return self._retain_morphism_action_result(
                morphism,
                catlab.functor_morphism_image(self, morphism),
                self.on_object,
            )

        def on_element(self, element: DomainElement) -> CodomainElement:
            """Transport ``t: T -> X`` along ``self: X -> Y`` by composition (D17)."""
            defining = element.defining_morphism()
            assert defining.codomain() is self.domain()
            return Cat().element_from_defining_morphism(self * defining)

        def __call__(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            """Apply the functor to an object or a morphism of its domain."""
            if value in self.domain():
                return self.on_object(value)
            assert value in self.domain().morphism_category(1), f"{value!r} is neither an object nor a morphism of {self.domain()!r}"
            return self.on_morphism(value)

        def inverse_image(self, subcategory: Category) -> Category:
            """``F.inverse_image(P) = D ×_C P`` for a subcategory ``P -> C``."""
            from sage_categories.cat.properties import inverse_image

            return inverse_image(self, subcategory)

        def base_change(self, defining_functor: Functor) -> Functor:
            """Return the pullback projection ``D ×_C E -> D`` for ``self: D -> C`` and ``defining_functor: E -> C``."""
            from sage_categories.cat.base_change import base_change

            return base_change(self, defining_functor)

        @cached_method(key=lambda self, source, target: identity_key(source, target))
        def restrict(self, source: Category, target: Category) -> Functor:
            """Restrict both actions along supplied subcategory inclusions.

            The caller supplies the factorization theorem; the actions retain its exact target placement.
            See Mathlib CategoryTheory.Functor.factorization through a full subcategory.
            """
            Fun = _functors()

            assert is_subcategory(source, self.domain())
            assert is_subcategory(target, self.codomain())

            def on_object(
                value: CategoryOfCategories.ElementType,
            ) -> CategoryOfCategories.ElementType:
                image = self.on_object(value)
                refine(image, target)
                return image

            def on_morphism(
                value: MorphismCategory.ObjectType,
            ) -> MorphismCategory.ObjectType:
                image = self.on_morphism(value)
                refine(image, target.morphism_category(1))
                return image

            return Fun(source, target)(on_object, on_morphism)

        def op(self) -> Functor:
            """Return the retained opposite functor."""
            from sage_categories.cat.opposites import opposite_functor

            return opposite_functor(self)

        def Fiber(self, member_object: CategoryOfCategories.ElementType) -> Category:
            """Return the strict fiber over ``member_object``."""
            from sage_categories.cat.fibers import fiber

            return fiber(self, member_object)

        def with_limit_lifting(
            self,
            shape: Category | Functor,
            on_apex: LimitApexLift,
            on_morphism: LimitMorphismLift,
        ) -> Functor:
            """Choose exact limit lifts along this faithful functor.

            ``on_apex(K, c)`` adds source structure to the apex of the limiting
            cone ``c`` over ``self * K``. ``on_morphism(X, Y, f)`` lifts the
            resulting projections and mediators to the stated endpoints.
            Existence of these lifts is the supplied mathematical theorem;
            faithfulness makes their cone equations and uniqueness follow.
            """
            Fun = _functors()
            Discrete = _discrete_shape_family()

            assert self in Fun.Faithful(), "limit reconstruction requires a faithful functor"
            assert shape in Cat() or shape is Discrete, "supply a shape or the discrete shape family"
            assert shape not in self._limit_liftings, "this shape already has chosen limit lifts"
            self._limit_liftings[shape] = (on_apex, on_morphism)
            return self

        def limit_lifting(self, shape: Category) -> tuple[LimitApexLift, LimitMorphismLift] | None:
            """Return the chosen lifts for this shape or the discrete shape family."""
            Discrete = _discrete_shape_family()

            if shape in self._limit_liftings:
                return self._limit_liftings[shape]
            if Discrete in self._limit_liftings and shape.is_discrete():
                return self._limit_liftings[Discrete]
            return None

        # A functor is a morphism of ``Cat()``, so ``retain_factors`` and ``factors``
        # arrive from ``Mor(C).ObjectType``, where every morphism's composite factors are
        # declared once (D44, D85, D173).

        # -- fibration and opfibration lifts (POL-FUN-029) ------------------------------------

        def retain_cartesian_lifts(self, rule: LiftRule) -> None:
            """Retain the rule constructing the cartesian lift of ``f: y -> p(e)`` at ``e`` over the class of morphisms the owner states."""
            assert self._cartesian_lift_rule is None, f"{self!r} already retains its cartesian lifts"
            self._cartesian_lift_rule = rule

        def retain_cocartesian_lifts(self, rule: LiftRule) -> None:
            """Retain the rule constructing the cocartesian lift of ``f: p(e) -> y`` at ``e`` over the class of morphisms the owner states."""
            assert self._cocartesian_lift_rule is None, f"{self!r} already retains its cocartesian lifts"
            self._cocartesian_lift_rule = rule

        @cached_method(key=lambda self, morphism, member_object: identity_key(morphism, member_object))
        def cartesian_lift(
            self,
            morphism: MorphismCategory.ObjectType,
            member_object: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            """The cartesian lift of ``morphism: y -> p(e)`` at ``e``: a morphism of the domain ending at ``e`` over ``morphism``, retained once per pair."""
            rule = self._cartesian_lift_rule
            assert rule is not None, f"{self!r} retains no cartesian lifts"
            assert morphism in self.codomain().morphism_category(1), f"{morphism!r} is not a morphism of {self.codomain()!r}"
            assert morphism.codomain() is self.on_object(member_object), f"{morphism!r} does not end at the image of {member_object!r}"
            return rule(morphism, member_object)

        @cached_method(key=lambda self, morphism, member_object: identity_key(morphism, member_object))
        def cocartesian_lift(
            self,
            morphism: MorphismCategory.ObjectType,
            member_object: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            """The cocartesian lift of ``morphism: p(e) -> y`` at ``e``: a morphism of the domain starting at ``e`` over ``morphism``, retained once per pair."""
            rule = self._cocartesian_lift_rule
            assert rule is not None, f"{self!r} retains no cocartesian lifts"
            assert morphism in self.codomain().morphism_category(1), f"{morphism!r} is not a morphism of {self.codomain()!r}"
            assert morphism.domain() is self.on_object(member_object), f"{morphism!r} does not start at the image of {member_object!r}"
            return rule(morphism, member_object)

        def __repr__(self) -> str:
            return f"Functor({self.domain()!r} -> {self.codomain()!r})"

    def __init__(self) -> None:
        self._declarations: MonoDict = MonoDict()
        self._implementations: MonoDict = MonoDict()
        self._open_declarations: MonoDict = MonoDict()
        super().__init__()

    # -- the categories Cat declares (D80, D82) ------------------------------------

    def declare(self, declared: DeclaredCategory) -> DeclaredCategory:
        """Retain ``declared`` as a named category the repository expects to exist.

        A declaration is a functor into ``Cat()``, and this is the terminal-domain case:
        the point ``* -> Cat()``, whose value is this already constructed category.
        ``Cat`` retains that mathematical object by identity; its display name is data of
        the declaration object, not a key that binds the later implementation.  A
        parameterized family is retained through ``declare_family`` instead (POL-API-021).

        A declaration no implementation claims is open work, readable through
        ``declarations()``.  It is never a check that fails a build.
        """
        assert declared not in self._declarations, f"{declared!r} is already declared"
        self._declarations[declared] = True
        self._open_declarations[declared] = True
        return declared

    def declare_family(self, declared: CategoryFamily) -> CategoryFamily:
        """Retain ``declared`` as a parameterized category family the repository expects to exist.

        The family itself retains the domain of the functor into ``Cat()`` and its display
        name.  A parameterized family has no category to return until an implementation
        supplies its object and morphism actions; neither fact is keyed by a string here.
        """
        assert declared not in self._declarations, f"{declared!r} is already declared"
        self._declarations[declared] = True
        self._open_declarations[declared] = True
        return declared

    def declarations(self) -> tuple[CategoryDeclaration | CategoryFamily, ...]:
        """The actual categories and category families ``Cat`` declares (D82)."""
        return tuple(declared for declared, _ in self._declarations.items())

    @overload
    def open_declaration(self, declared: DeclaredCategory) -> DeclaredCategory | None: ...

    @overload
    def open_declaration(self, declared: CategoryFamily) -> CategoryFamily | None: ...

    @overload
    def open_declaration[**MorphismData, **TwoMorphismData, ObjectRole, ElementRole, MorphismRole](
        self,
        declared: CategoryDeclaration[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole],
    ) -> CategoryDeclaration[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole] | None: ...

    def open_declaration(self, declared: CategoryDeclaration | CategoryFamily) -> CategoryDeclaration | CategoryFamily | None:
        """Return ``declared`` itself while no implementation claims it, else ``None``."""
        match declared in self._open_declarations:
            case True:
                return declared
            case False:
                return None

    def implementation[**MorphismData, **TwoMorphismData, ObjectRole, ElementRole, MorphismRole](
        self,
        declared: CategoryDeclaration[MorphismData, TwoMorphismData, ObjectRole, ElementRole, MorphismRole],
    ) -> type[Category] | None:
        """The class implementing the exact declared category ``declared``, or ``None``."""
        return self._implementations[declared] if declared in self._implementations else None

    def implement(self, implementation: type[Category] | partial[Category]) -> None:
        """Connect ``implementation`` to the category it declares itself the implementation of (D156).

        The class says which category by selecting that category's identity functor
        first among its structure functors, and that selection is the whole declaration:
        there is no binding field and no name written as a string.

        Constructing the class is what reads it.  A declaration is written against the
        category under construction -- a leaf's other structure functors are
        ``Fun(self, D)(...)`` -- so it is only readable there, and reading it early would
        build those functors over a value that does not exist yet.  An implementing class
        has no category of its own to construct, so the construction stops at the
        declaration and ``Cat`` strengthens the declared value instead (``_initialize``).
        """
        match implementation:
            case partial(func=category_type, args=arguments, keywords=keywords):
                assert isinstance(category_type, type) and issubclass(category_type, Category)
                options = {} if keywords is None else keywords

                def initialize(category: Category) -> None:
                    category_type.__init__(category, *arguments, **options)

            case type() as category_type:
                assert issubclass(category_type, Category)
                initialize = category_type.__init__
            case _:
                raise TypeError(f"{implementation!r} is not a category implementation constructor")
        token = _implementation_invocation.set(_ImplementationInvocation(category_type, initialize))
        try:
            implementation()
        finally:
            _implementation_invocation.reset(token)

    def _adopt(
        self,
        declared: CategoryDeclaration,
        implementation: type[Category],
        selected_functors: tuple[Functor, ...],
    ) -> None:
        """Strengthen the declaration ``declared`` to ``implementation`` in place (D80, D156).

        The declared object is the final object, so nothing is constructed here: its
        class is strengthened to the implementing class -- the same in-place
        strengthening every value receives when its placement improves -- and its roles
        are compiled again onto it, from the same declaration read on the value it now
        carries.  **The ordinal is not retaken.**  Every reference written against the
        declaration therefore uses the implementation the moment it lands, with no edit
        and no resolution pass.
        """
        from sage_categories.kernel.compiler import implement_category

        assert issubclass(implementation, self.ObjectType)
        invocation = _implementation_invocation.get()
        assert invocation is not None and invocation.category_type is implementation
        open_declaration = self.open_declaration(declared)
        if open_declaration is not None:
            self._implementations[declared] = implementation
            del self._open_declarations[declared]
        implement_category(
            declared,
            implementation,
            selected_functors,
            invocation.initialize,
            augment=open_declaration is None,
        )

    def morphism_category_type(self) -> type[FunctorsCategory]:
        from sage_categories.cat.functors import FunctorsCategory

        return FunctorsCategory

    @cached_method(key=lambda self, domain, codomain, on_object, on_morphism: identity_key(domain, codomain, on_object, on_morphism))
    def construct_morphism(
        self,
        domain: CategoryOfCategories.ObjectType,
        codomain: CategoryOfCategories.ObjectType,
        on_object: OnObject,
        on_morphism: OnMorphism,
    ) -> CategoryOfCategories.MorphismType:
        """``Fun(C, D)(on_object, on_morphism)``: the functor selected by its four identity components (POL-FUN-001/027)."""
        assert domain in self and codomain in self
        return self.MorphismType(
            domain=domain,
            codomain=codomain,
            data=FunctorData(on_object, on_morphism),
        )

    def construct_identity(self, category: CategoryOfCategories.ObjectType) -> CategoryOfCategories.MorphismType:
        Fun = _functors()
        identity = self.MorphismType(
            domain=category,
            codomain=category,
            data=_StructuralFunctorData(),
        )
        cells = _cells_engine()

        cells.retain_identity(self, identity)
        # The identity functor is an equivalence: Mathlib ``CategoryTheory.Functor.id``
        # with ``IsEquivalence`` of the identity (inspected 2026-08-26).
        refine(identity, Fun.Equivalences())
        return identity

    def composite(
        self,
        second: CategoryOfCategories.MorphismType,
        first: CategoryOfCategories.MorphismType,
    ) -> CategoryOfCategories.MorphismType:
        """``second * first``: the composite functor, rules composed (Mathlib ``Functor.comp``)."""
        Fun = _functors()

        assert first in self.morphism_category(1) and second in self.morphism_category(1)
        assert first.codomain() is second.domain()
        factors = (*_composite_sequence(first), *_composite_sequence(second))
        composite = self._composite_functor(factors, first, second)
        # Full, faithful, fully faithful, essentially surjective, and equivalence
        # functors compose (Mathlib ``Functor.FullyFaithful.comp``, ``Full.comp``,
        # ``Faithful.comp``, ``EssSurj.comp``, and ``Functor.IsEquivalence.comp``;
        # inspected 2026-08-26). Isofibrations compose by successive lifting of
        # isomorphisms (Kerodon 4.4.1.10, https://kerodon.net/tag/01ER).
        for property_category in (
            Fun.FullyFaithful(),
            Fun.Full(),
            Fun.Faithful(),
            Fun.EssentiallySurjective(),
            Fun.Equivalences(),
            Fun.Isofibrations(),
        ):
            if is_placed(first, property_category) and is_placed(second, property_category):
                refine(composite, property_category)
        return composite

    @cached_method(key=lambda self, factors, first, second: identity_key(*factors))
    def _composite_functor(
        self,
        factors: tuple[Functor, ...],
        first: CategoryOfCategories.MorphismType,
        second: CategoryOfCategories.MorphismType,
    ) -> CategoryOfCategories.MorphismType:
        """Construct the canonical composite for one exact flattened factor sequence.

        ``first`` and ``second`` record the binary presentation that first constructed
        this value.  The cache key is the flattened factor sequence, preserving the
        existing strict associativity of selected functor composition without a nested
        hand-written identity table.
        """
        assert factors == (*_composite_sequence(first), *_composite_sequence(second))

        composite = self.MorphismType(
            domain=first.domain(),
            codomain=second.codomain(),
            data=_StructuralFunctorData(),
        )
        composite.retain_factors(first, second)
        _cells_engine().retain_composite(self, composite, first, second)
        return composite

    def _construct_transformation(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        assignment: Assignment,
        source_functor: Functor | None = None,
        target_functor: Functor | None = None,
    ) -> NaturalTransformation:
        """Construct one owned transformation and its Catlab callable semantics."""
        from sage_categories.cat.functors import NaturalTransformationData, diagram_of

        functors = self.morphism_category(1)
        source_functor = diagram_of(source) if source_functor is None else source_functor
        target_functor = diagram_of(target) if target_functor is None else target_functor
        assert source_functor in functors and target_functor in functors
        assert source_functor.domain() is target_functor.domain() and source_functor.codomain() is target_functor.codomain()
        transformation = functors.MorphismType(
            domain=source,
            codomain=target,
            data=NaturalTransformationData(assignment, source_functor, target_functor),
        )
        return transformation

    def construct_two_morphism(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        assignment: Assignment,
        source_functor: Functor | None = None,
        target_functor: Functor | None = None,
    ) -> NaturalTransformation:
        """``Mor(Fun(C, D))(F, G)(assignment)``: a native-backed natural transformation."""
        transformation = self._construct_transformation(source, target, assignment, source_functor, target_functor)
        cells = _cells_engine()

        cells.retain_generator(self.morphism_category(1), transformation)
        return transformation

    def identity_two_morphism(self, member_object: CategoryOfCategories.ElementType) -> NaturalTransformation:
        from sage_categories.cat.functors import diagram_of

        catlab, cells = _catlab_engine(), _cells_engine()

        functor = diagram_of(member_object)

        def component(
            x: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            image = functor.on_object(x)
            return image.category().morphism_category(1)(image, image).one()

        transformation = self._construct_transformation(member_object, member_object, component)
        catlab.identity_transformation(transformation)
        cells.retain_identity(self.morphism_category(1), transformation)
        return transformation

    def compose_two_morphisms(self, second: NaturalTransformation, first: NaturalTransformation) -> NaturalTransformation:
        """Vertical composition in Catlab and homotopy-core, with one owned result."""
        assert first.codomain() is second.domain()
        catlab, cells = _catlab_engine(), _cells_engine()

        def component(
            value: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            return first.source_functor().codomain().compose_morphisms(second.component(value), first.component(value))

        result = self._construct_transformation(
            first.domain(),
            second.codomain(),
            component,
            first.source_functor(),
            second.target_functor(),
        )
        catlab.compose_transformations(result, first, second)
        result.retain_factors(first, second)
        cells.retain_composite(self.morphism_category(1), result, first, second)
        return result

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
        catlab, cells = _catlab_engine(), _cells_engine()

        source_image = self.postcompose(functor, transformation.domain())
        target_image = self.postcompose(functor, transformation.codomain())

        def component(
            value: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            return functor.on_morphism(transformation.component(value))

        result = self._construct_transformation(source_image, target_image, component)
        catlab.whisker_left(result, functor, transformation)
        cells.retain_whisker_left(self.morphism_category(1), result, functor, transformation)
        return result

    def whisker_right(self, transformation: NaturalTransformation, functor: Functor) -> NaturalTransformation:
        """``theta . F: H F => K F`` for ``theta: H => K`` in ``Fun(D, E)`` and ``F: I -> D``; its component at ``X`` is ``theta_{F(X)}``."""
        source, target = (
            transformation.source_functor(),
            transformation.target_functor(),
        )
        assert functor.codomain() is source.domain()
        catlab, cells = _catlab_engine(), _cells_engine()

        source_image = self.compose_morphisms(source, functor)
        target_image = self.compose_morphisms(target, functor)

        def component(
            value: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            return transformation.component(functor.on_object(value))

        result = self._construct_transformation(source_image, target_image, component)
        catlab.whisker_right(result, transformation, functor)
        cells.retain_whisker_right(self.morphism_category(1), result, transformation, functor)
        return result

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
        catlab, cells = _catlab_engine(), _cells_engine()

        def component(
            value: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            return inner.component(value) * outer.component(value)

        result = self._construct_transformation(outer.domain(), inner.codomain(), component)
        catlab.horizontal_composite(result, first, second)
        cells.retain_composite(self.morphism_category(1), result, outer, inner)
        return result

    # -- the constructions Cat() owns (POL-CAT-050; ``cat/cat_constructions.py``) --------

    def limit_construction(self, shape: Category) -> Callable[[CategoryOfCategories.MorphismType], CategoryOfCategories.ObjectType]:
        """The category of compatible object and morphism families over the supplied shape."""
        from sage_categories.cat.cat_constructions import (
            limit_of_categories,
            product_of_categories,
            pullback_of_categories,
        )

        if shape.is_discrete():
            return product_of_categories
        if shape is self.WalkingCospan():
            return pullback_of_categories
        return lambda diagram: limit_of_categories(diagram, self.Limits(shape))

    def exponential(
        self,
        exponent: CategoryOfCategories.ObjectType,
        base: CategoryOfCategories.ObjectType,
    ) -> CategoryOfCategories.ObjectType:
        """``D ** C = Fun(C, D)``: ``Cat()`` is cartesian closed (Mathlib ``Cat.exp_obj``; inspected 2026-08-26)."""
        return self.morphism_category(1)(exponent, base)

    @cached_method(key=identity_key)
    def Comma(self, first: Functor, second: Functor) -> CommaCategory:
        """``Comma(F, G)`` for functors with a common codomain, retained per ordered pair."""
        from sage_categories.cat.slices import _construct_comma_category

        assert first in self.morphism_category(1) and second in self.morphism_category(1)
        assert first.codomain() is second.codomain(), f"{first!r} and {second!r} have different codomains"
        return _construct_comma_category(first, second)

    def postcompose(self, functor: Functor, diagram: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        """``F . G`` for an object ``G`` of ``Fun(I, D)`` and ``F: D -> E``: the object action of ``Fun(I, F)``.

        An object of ``Fun(I, D)`` is a functor ``I -> D`` or a point of ``D`` with domain
        ``I`` denoting one (``specs/functor.md``, "The Mor(n, C) tower").  A point keeps
        that spelling under the action: its image is the point image, so
        ``Fun(1, F).on_object(x) is F.on_object(x)`` and
        ``Fun([1], F).on_object(f) is F.on_morphism(f)``.
        """
        if is_placed(diagram, self.morphism_category(1)):
            return self.compose_morphisms(functor, diagram)
        return functor(diagram)

    @cached_method(key=lambda self, exponent, functor: identity_key(exponent, functor))
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
        return self.morphism_category(1)(
            self.exponential(exponent, functor.domain()),
            self.exponential(exponent, functor.codomain()),
        )(
            lambda diagram: self.postcompose(functor, diagram),
            lambda transformation: self.whisker_left(functor, transformation),
        )

    # -- finite presented shapes and canonical objects (POL-CAT-083) ----------------

    def __call__(
        self,
        labels: tuple[Hashable, ...],
        generators: tuple[tuple[str, Hashable, Hashable], ...],
        relations: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
    ) -> FinitePresentedCategory:
        """``Cat()(labels, generators, relations)``: the category presented by finitely many objects, generating morphisms, and relations."""
        canonical = _canonical_categories()

        return canonical.FinitePresentedCategory(
            f"Presented{tuple(labels)!r}",
            tuple(labels),
            tuple(generators),
            tuple(relations),
        )

    def Initial(self) -> FinitePresentedCategory:
        """The empty category, the initial object of ``Cat()`` (``specs/functor.md``, "Canonical objects of Cat")."""
        canonical = _canonical_categories()
        return self._canonical_shape("empty", (), canonical.empty_category)

    def Terminal(self) -> FinitePresentedCategory:
        return self.Simplex(0)

    @overload
    def Point(self) -> CategoryOfCategories.MorphismType: ...

    @overload
    def Point(self, member: CategoryOfCategories.ElementType) -> PointCategory: ...

    def Point(self, member: CategoryOfCategories.ElementType | None = None) -> CategoryOfCategories.MorphismType | PointCategory:
        """The point functor under construction, or the one-object category ``{X}``."""
        match member:
            case None:
                return CategoryDeclaration.Point(self)
            case _:
                return self._point_category(member)

    @cached_method(key=lambda self, member: identity_key(member))
    def _point_category(self, member: CategoryOfCategories.ElementType) -> PointCategory:
        """The retained one-object category on ``member``."""
        from sage_categories.cat.points import PointCategory

        assert member._is_object(), f"{member!r} is not an object of a category"
        return PointCategory(member)

    def Simplex(self, dimension: int | Integer) -> FinitePresentedCategory:
        canonical = _canonical_categories()

        assert dimension >= 0
        return self._canonical_shape("simplex", (dimension,), lambda: canonical.simplex(dimension))

    def Boundary(self, dimension: int | Integer) -> FinitePresentedCategory:
        canonical = _canonical_categories()

        assert dimension == 2, "Cat owns the boundary of the 2-simplex only"
        return self._canonical_shape("boundary", (dimension,), lambda: canonical.boundary(dimension))

    def Horn(self, dimension: int, omitted_face: int) -> FinitePresentedCategory:
        canonical = _canonical_categories()

        assert dimension == 2 and 0 <= omitted_face <= 2, "Cat owns the horns of the 2-simplex only"
        if omitted_face == 1:
            # The free category on ``0 -> 1 -> 2`` contains the composite ``0 -> 2``:
            # it is the walking composable pair ``[2]`` (nLab "walking structure":
            # the walking composable pair is the (2,1)-horn category; inspected 2026-08-26).
            return self.Simplex(2)
        return self._canonical_shape("horn", (dimension, omitted_face), lambda: canonical.horn(dimension, omitted_face))

    def WalkingIsomorphism(self) -> FinitePresentedCategory:
        canonical = _canonical_categories()
        return self._canonical_shape("walking isomorphism", (), canonical.walking_isomorphism)

    def WalkingSpan(self) -> FinitePresentedCategory:
        """The free category on ``0 <- 1 -> 2``."""
        return self.Horn(2, 0)

    def WalkingCospan(self) -> FinitePresentedCategory:
        """The free category on ``0 -> 1 <- 2``."""
        return self.Horn(2, 2)

    def WalkingParallelPair(self) -> FinitePresentedCategory:
        canonical = _canonical_categories()
        return self._canonical_shape("walking parallel pair", (), canonical.walking_parallel_pair)

    @cached_method(key=lambda self, name, parameters, construct: (name, tuple(int(parameter) for parameter in parameters)))
    def _canonical_shape(
        self,
        name: str,
        parameters: tuple[int | Integer, ...],
        construct: Callable[[], FinitePresentedCategory],
    ) -> FinitePresentedCategory:
        """Retain one canonical finite shape by its mathematical presentation key."""
        return construct()

    def element_from_defining_morphism(self, defining_functor: Functor) -> CategoryOfCategories.ElementType:
        """The point of a category with domain ``T``, given by a functor ``T -> C``."""
        assert defining_functor in self.morphism_category(1)
        if defining_functor.domain() is self.Terminal():
            return defining_functor.on_object(self.Terminal()(0))
        return self.ElementType(defining_functor)

    def __repr__(self) -> str:
        return "Cat"


def _member_by_placement(
    candidate: CategoryOfCategories.ElementType,
    category: Category,
    assumptions: Proposition,
) -> bool:
    return is_placed(candidate, category)


def _integer_member_by_placement(candidate: int, category: Category, assumptions: Proposition) -> bool:
    return is_placed(candidate, category)


register_handler(member, _member_by_placement)
register_handler(member, _integer_member_by_placement)


@cached_function
def Cat() -> CategoryOfCategories:
    """The category of categories, installed exactly once by the bootstrap."""
    raise AssertionError("Cat is not bootstrapped")


def bootstrap() -> None:
    """Bind the singleton ``Cat()`` after the kernel constructs its three roles.

    ``Cat()`` is self-referential mathematics: ``Cat().ObjectType`` is ``Category``,
    ``Cat().MorphismType`` is ``Functor``, and ``Functor`` is itself an object of
    ``Fun = Mor(Cat())``.  The theory first defines their distinct local declarations.
    The kernel compiles ``Cat()``, and this function binds the semantic names to its
    public roles.  Modules that declare other category classes import only after this
    function returns.  Their classes therefore derive from the compiled ``Category``
    role and enter its generated constructor chain normally.

    ``cat/__init__.py`` constructs the private runtime value before it imports
    ``cat/functors.py``.  Binding these names completes one Cat declaration identity.
    """
    from sage_categories.kernel.compiler import construct_category_singleton

    global Category, Functor
    assert not Cat.is_in_cache(), "Cat is already bound"
    category = construct_category_singleton(CategoryOfCategories)
    Cat.set_cache(category)
    Category = category.ObjectType
    Functor = category.MorphismType
