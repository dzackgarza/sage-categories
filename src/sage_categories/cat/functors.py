"""Implement functors, natural transformations, and the ``Fun`` bootstrap."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sympy import ask as sympy_ask

from sage_categories.cat import category as _category
from sage_categories.cat.category import (
    Assignment,
    Category,
    CategoryOfCategories,
    Decision,
    OnMorphism,
    OnObject,
    Predicate,
    Proposition,
    Unknown,
    UnknownClass,
    ask,
    is_placed,
    is_subcategory,
    refine,
)
from sage_categories.cat.properties import Axiom
from sage_categories.cat.predicates import predicate, register_handler
from sage_categories.kernel.sage_runtime import LazyFamily, MonoDict, TripleDict

__all__ = ["Fun", "Functor", "FunctorCategory", "FunctorProperty", "FunctorsCategory", "NaturalTransformation"]


def identity_on_values(value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    """The object and morphism action of every subcategory monomorphism: the identity on the shared values (POL-FUN-027)."""
    return value


def diagram_of(value: CategoryOfCategories.ElementType) -> Functor:
    """Return the functor represented by a functor, object, or morphism value."""
    if is_placed(value, Fun):
        return value
    if value._is_morphism():
        return value.base_category().arrow_functor(value)
    return value.defining_morphism()


def _defining_functor_equal(
    first: CategoryOfCategories.ElementType,
    candidate: CategoryOfCategories.ElementType,
    assumptions: Proposition,
) -> bool | None:
    """Compare a retained diagram with the functor represented by a value."""
    if not isinstance(candidate, Cat().ElementType):
        return None
    candidate_denotes = candidate._is_object() or candidate._is_morphism()
    if is_placed(first, Fun) and not is_placed(candidate, Fun) and candidate_denotes:
        return True if first is diagram_of(candidate) else None
    if is_placed(candidate, Fun) and not is_placed(first, Fun) and (first._is_object() or first._is_morphism()):
        return True if candidate is diagram_of(first) else None
    return None


@dataclass(frozen=True, eq=False, slots=True)
class NaturalTransformationData:
    """The local state introduced by the natural-transformation role."""

    assignment: Assignment


Cat = _category.Cat
Category = _category.Category
Functor = Cat().MorphismType
_category.Functor = Functor

from sage_categories.cat.morphisms import FixedEndpointCategory, MorphismCategory, endpoints
from sage_categories.cat.properties import FixedEndpointProperty, PropertySubcategory


class FunctorProperties:
    """The property subcategories of ``Fun``, narrowed to ``Fun(C, D)`` and to its own narrowings.

    ``Fun(C, D).Monomorphisms().Isofibrations().Full()`` is one category however it is
    spelled (POL-CAT-084), so the same accessors sit on the fixed-endpoint category and on
    each narrowing of it, and each narrows the placement it is called on.
    """

    def Full(self) -> Category:
        return self.property_subcategory(self.ambient().Full())

    def Faithful(self) -> Category:
        return self.property_subcategory(self.ambient().Faithful())

    def FullyFaithful(self) -> Category:
        return self.property_subcategory(self.ambient().FullyFaithful())

    def EssentiallySurjective(self) -> Category:
        return self.property_subcategory(self.ambient().EssentiallySurjective())

    def Equivalences(self) -> Category:
        return self.property_subcategory(self.ambient().Equivalences())

    def PreservesLimits(self, shape: Category) -> Category:
        """Functors preserving limits of ``shape`` (D107, POL-FUN-039)."""
        return self.property_subcategory(self.ambient().PreservesLimits(shape))

    def CreatesLimits(self, shape: Category) -> Category:
        """Functors creating limits of ``shape`` (D107, POL-FUN-039)."""
        return self.property_subcategory(self.ambient().CreatesLimits(shape))

    def Isofibrations(self) -> Category:
        return self.property_subcategory(self.ambient().Isofibrations())

    def Fibrations(self) -> Category:
        """Grothendieck fibrations: a cartesian lift of an isomorphism is an isomorphism, so this sits inside ``Isofibrations()`` (D169)."""
        return self.property_subcategory(self.ambient().Fibrations())

    def Opfibrations(self) -> Category:
        """Grothendieck opfibrations: a cocartesian lift of an isomorphism is an isomorphism, so this sits inside ``Isofibrations()`` (D169)."""
        return self.property_subcategory(self.ambient().Opfibrations())

    def Monomorphisms(self) -> Category:
        return self.property_subcategory(self.ambient().Monomorphisms())


class ShapeIndexedFunctorProperty(
    FunctorProperties,
    PropertySubcategory[[OnObject, OnMorphism], [Assignment]],
):
    """A shape-indexed property subcategory of one fixed-endpoint functor category."""

    class ObjectType:
        """A functor with the stated shape-indexed universal-construction property."""

    class ElementType:
        """A generalized element of such a functor."""

    class MorphismType:
        """A natural transformation between such functors."""

    def __init__(self, ambient: FunctorCategory, property_name: str, shape: Category) -> None:
        self._shape = shape
        self._property_name = property_name
        super().__init__(ambient, property_name, ())

    def shape(self) -> Category:
        return self._shape

    def narrowing_type(self) -> type[FunctorProperty]:
        return FunctorProperty

    def __call__(self, *args: OnObject | OnMorphism, **kwargs: OnObject | OnMorphism) -> Functor:
        return _construct_property_functor(self, args, kwargs)

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.{self._property_name}({self._shape!r})"


class FunctorProperty(FunctorProperties, FixedEndpointProperty[[OnObject, OnMorphism], [Assignment]]):
    """``Fun(C, D).P()``: functors ``C -> D`` with property ``P``; constructs one, and ``one()`` is ``1_C`` with ``P``."""

    class ObjectType:
        """A functor ``C -> D`` with the property.

        Fullness, faithfulness and the rest are properties of the functor: they narrow
        which functors this category has and add nothing to one.
        """

    class ElementType:
        """A point of such a functor."""

    class MorphismType:
        """A natural transformation between two functors with the property."""

    def __call__(self, *args: OnObject | OnMorphism, **kwargs: OnObject | OnMorphism) -> Functor:
        """``Fun(S, T).P()(on_object, on_morphism)``, or ``Fun(S, T).P()()`` for the subcategory monomorphism.

        With no data the constructed functor is the identity on the values ``S`` and ``T``
        share, which is a functor exactly when ``S`` is a subcategory of ``T``.  That is
        the declaration ``POL-FUN-036`` names: the leaf states the relation by
        constructing in ``Fun(S, T).Monomorphisms().Isofibrations()``, and the kernel
        trusts it (``specs/functor.md``, "Monomorphisms of Cat() and placement").
        The functor is placed in exactly the property category the call named, so
        ``Fun(S, T).Monomorphisms()()`` declares a monomorphism and nothing further
        (D146, D162).
        """
        return _construct_property_functor(self, args, kwargs)


def _construct_property_functor(
    property_category: ShapeIndexedFunctorProperty | FunctorProperty,
    args: tuple[OnObject | OnMorphism, ...],
    kwargs: dict[str, OnObject | OnMorphism],
) -> Functor:
    """Construct a functor through its exact property category.

    ``Fun(S, T).P()`` wires no constructor of its own: it has exactly the constructors of
    ``Fun(S, T)``, carried along its inclusion, and construction here asserts the property
    (D150, ``POL-CAT-038``).  A functor already constructed is placed by
    ``assume(F.is_p())``, never fed back to a constructor (D150, ``POL-ONT-002``).

    The zero-argument form declares an inclusion, and it is available only on a
    monomorphism subcategory: a functor that computes nothing is a subcategory
    monomorphism, and every other functor is written with its two actions and constructed
    into the strongest property subcategory that states what is known about it (D08, D21,
    D146, D162).  The property category the call names is the whole declaration, so the
    result is placed there and in nothing wider or narrower.
    """
    ambient = property_category.ambient()
    if args or kwargs:
        functor = ambient(*args, **kwargs)
    else:
        functors = property_category.universe().morphism_category(1)
        assert any(root is functors.Monomorphisms() for root in property_category.narrowing_roots()), (
            f"{property_category!r} is not a monomorphism subcategory of Fun, so it requires "
            f"object and morphism actions (D146, D162)"
        )
        functor = functors.identity_on_values(ambient.domain(), ambient.codomain())
    refine(functor, property_category)
    return functor


# ``denotes_diagram(x, Fun(I, C))``: ``x`` is a functor ``I -> C``, or a value that denotes
# one.  The objects of ``Fun(1, K)`` are the objects of ``K``, each a point ``* -> K``, and
# the objects of ``Fun([1], C)`` are the morphisms of ``C``, each an object of ``Mor(C)``
# (specs/functor.md, "The Mor(n, C) tower", specs/functor.md, "Canonical objects of Cat"): one value, denoting one diagram.
denotes_diagram: Predicate = predicate("denotes_diagram")


def _denotes_diagram_by_domain(
    candidate: CategoryOfCategories.ElementType,
    functors: FunctorCategory,
    assumptions: Proposition,
) -> bool | None:
    if not isinstance(candidate, Cat().ElementType):
        return False
    if is_placed(candidate, functors.ambient()):
        return sympy_ask(endpoints(candidate, functors.domain(), functors.codomain()), assumptions)
    if candidate._is_morphism() and functors.domain() is Cat().Simplex(1):
        # A morphism of ``C`` is an object of ``Mor(C)``, and the diagram it denotes is its
        # arrow functor ``[1] -> C``: this is how the objects of ``Fun([1], C)`` are the
        # morphisms of ``C``.
        return is_subcategory(candidate.base_category(), functors.codomain())
    if candidate._is_object() or candidate._is_morphism():
        # Every object of a category ``K`` is a point ``* -> K``.  The parent is a
        # placement, so the question there is containment in the codomain, not identity
        # (POL-CAT-068, POL-FUN-027): a set refined into ``Sets().Finite()`` is still a
        # diagram of shape ``1`` in ``Sets()``.
        return functors.domain() is Cat().Terminal() and is_subcategory(candidate.parent(), functors.codomain())
    return False


# ``denotes_functor(x, Fun)``: ``x`` is a functor by placement, or a point of a category
# with a category as domain, which denotes its defining functor (specs/functor.md, "Slices and coslices").
denotes_functor: Predicate = predicate("denotes_functor")


def _denotes_functor_by_domain(
    candidate: CategoryOfCategories.ElementType,
    functors: FunctorsCategory,
    assumptions: Proposition,
) -> bool:
    if not isinstance(candidate, Cat().ElementType):
        return False
    if is_placed(candidate, functors):
        return True
    return (candidate._is_object() or candidate._is_morphism()) and candidate.defining_morphism().domain() in Cat()


class FunctorCategory(FunctorProperties, FixedEndpointCategory[[OnObject, OnMorphism], [Assignment]]):
    """``Fun(C, D)``: functors ``C -> D`` and their natural transformations.

    As the category of diagrams of shape ``C`` in ``D`` it retains its evaluation
    functors and constant diagrams (``cat/diagrams.py``, POL-FUN-029, specs/functor.md, "Diagram shapes and universal constructions").  ``Fun([1], C)``
    is the category of morphisms of ``C`` and commuting squares: a square
    ``f -> g`` is a natural transformation with components ``(a, b)`` satisfying
    ``g * a == b * f``, a trusted declaration checked where the finite set-map
    equality handler decides it (specs/functor.md, "The Mor(n, C) tower", specs/sets.md, "Equality").  Its evaluation
    ``ev_1`` retains cartesian lifts by pullback and ``ev_0`` cocartesian lifts by
    pushout, constructed when the codomain owns those constructions
    (``cat/diagrams.py``; POL-FUN-029; nLab "codomain fibration", inspected
    2026-08-27: "If C has all pullbacks, then the functor is in addition a
    Grothendieck fibration", with "the cartesian lift of a morphism c_1 -> c_2 in
    C ... given by the morphism c_1 x_{c_2} c'_2 -> c'_2").
    """

    class ObjectType:
        """A functor ``C -> D``, which is a morphism of ``Cat()``.

        For ``C = [1]`` the objects are the morphisms of ``D``, and those are objects of
        ``Mor(D)``: they reach this category by denoting a diagram, which is why
        ``diagram()`` is owned by the category and not by the object.
        """

    class ElementType:
        """A point of a functor."""

    class MorphismType:
        """A natural transformation ``F => G``."""

    def __init__(self, morphisms: MorphismCategory, domain: Category, codomain: Category) -> None:
        self._evaluations: MonoDict = MonoDict()
        self._constants: MonoDict = MonoDict()
        self._constant_values: MonoDict = MonoDict()
        self._diagonal: Functor | None = None
        self._finite_data: MonoDict = MonoDict()
        self._preserves_limits: MonoDict = MonoDict()
        self._creates_limits: MonoDict = MonoDict()
        super().__init__(morphisms, domain, codomain)

    def PreservesLimits(self, shape: Category) -> Category:
        """Functors preserving limits of ``shape`` (D107, POL-FUN-039); cached per shape on this fixed-endpoint category."""
        if shape not in self._preserves_limits:
            self._preserves_limits[shape] = ShapeIndexedFunctorProperty(self, "PreservesLimits", shape)
        return self._preserves_limits[shape]

    def CreatesLimits(self, shape: Category) -> Category:
        """Functors creating limits of ``shape`` (D107, POL-FUN-039); cached per shape on this fixed-endpoint category."""
        if shape not in self._creates_limits:
            self._creates_limits[shape] = ShapeIndexedFunctorProperty(self, "CreatesLimits", shape)
        return self._creates_limits[shape]

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return denotes_diagram(candidate, self)

    def diagram(self, value: CategoryOfCategories.ElementType) -> Functor:
        """The functor ``I -> C`` that a value of this category denotes: its point for ``I = *``, else ``diagram_of``."""
        if is_placed(value, self.ambient()):
            return value
        assert value in self, f"{value!r} is not a diagram of shape {self.domain()!r} in {self.codomain()!r}"
        if self.domain() is Cat().Terminal():
            return value.defining_morphism()
        return diagram_of(value)

    def construct_morphism(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        assignment: Assignment,
    ) -> NaturalTransformation:
        """``Mor(Fun(I, C))(F, G)(assignment)``; for ``I = [1]`` the two components must form a commuting square."""
        walking_arrow = Cat().Simplex(1)
        if self.domain() is walking_arrow:
            generator = walking_arrow.generator("0->1")
            first, second = assignment(walking_arrow(0)), assignment(walking_arrow(1))
            square_source, square_target = self.diagram(source).on_morphism(generator), self.diagram(target).on_morphism(generator)
            assert ask(square_target * first == second * square_source) is not False, (
                f"({first!r}, {second!r}) is not a commuting square from {square_source!r} to {square_target!r}"
            )
        return super().construct_morphism(source, target, assignment)

    # -- diagrams (POL-FUN-029) -----------------------------------------------------

    def evaluation(self, vertex: CategoryOfCategories.ElementType) -> Functor:
        """``ev_i: Fun(I, C) -> C``, the evaluation at the object ``i`` of the shape."""
        from sage_categories.cat.diagrams import evaluation

        return evaluation(self, vertex)

    def constant(self, value: CategoryOfCategories.ElementType) -> Functor:
        """The constant diagram at an object of the codomain."""
        from sage_categories.cat.diagrams import constant

        return constant(self, value)

    def diagonal(self) -> Functor:
        """The diagonal functor from the codomain into this functor category."""
        from sage_categories.cat.diagrams import diagonal

        return diagonal(self)

    def TotalCones(self) -> Category:
        """The total category of cones over diagrams in this functor category."""
        from sage_categories.cat.total_cones import total_cones

        return total_cones(self)

    def has_constant_value(self, diagram: Functor) -> bool:
        return diagram in self._constant_values

    def constant_value(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        """The object at which a retained constant diagram is constant."""
        assert diagram in self._constant_values, f"{diagram!r} is not a retained constant diagram"
        return self._constant_values[diagram]

    def from_object_rule(self, rule: OnObject) -> Functor:
        """A diagram over a discrete shape from its object rule alone."""
        from sage_categories.cat.diagrams import from_object_rule

        return from_object_rule(self, rule)

    # -- ``Fun([1], C)``: its finite data and its fibration lifts (POL-FUN-029, specs/functor.md, "Diagram shapes and universal constructions") -----------

    def object_set(self) -> CategoryOfCategories.ElementType:
        """For ``I = [1]``: the morphism set of ``C``, since the objects are the morphisms of ``C``."""
        assert self.domain() is Cat().Simplex(1), f"{self!r} declares no set of objects"
        morphisms = ask(self.codomain().morphism_set())
        assert morphisms is not Unknown, f"{self.codomain()!r} chooses no finite set of morphisms"
        return morphisms

    def object_at(self, point: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        assert self.domain() is Cat().Simplex(1), f"{self!r} declares no set of objects"
        return self.codomain().morphism_at(point)

    def _chosen_morphism_set(self) -> CategoryOfCategories.ElementType | UnknownClass:
        """For ``I = [1]``: the finite set of commuting squares, when ``C`` chooses a finite set of morphisms."""
        from sage_categories.cat.diagrams import square_set

        if self.domain() is not Cat().Simplex(1) or ask(self.codomain().morphism_set()) is Unknown:
            return Unknown
        return square_set(self)

    def morphism_at(self, point: CategoryOfCategories.ElementType) -> NaturalTransformation:
        from sage_categories.cat.diagrams import square_at

        return square_at(self, point)

    # -- functor properties (POL-FUN-024) -----------------------------------------------

    def narrowing_type(self) -> type[FunctorProperty]:
        return FunctorProperty

    def __repr__(self) -> str:
        return f"Fun({self.domain()!r}, {self.codomain()!r})"


class FunctorsCategory(MorphismCategory[[OnObject, OnMorphism], [Assignment]]):
    """``Fun = Mor(Cat())``."""

    # An object of ``Fun`` is a morphism of ``Cat()``, so ``Fun`` writes ``Cat()``'s
    # morphism declaration for its own objects (POL-CAT-057).  The five functor property
    # axioms below write their applications onto it.
    ObjectType = CategoryOfCategories.MorphismType

    class ElementType:
        """A generalized element ``t: T -> F`` of a functor: a natural transformation into it.

        ``Cat()`` is the one category here whose 2-morphisms are not all identities, so
        these are the substantive points of a morphism category (``MorphismCategory.ElementType``).
        """

    class MorphismType:
        """A natural transformation: the 2-morphisms of ``Cat()``.

        Its domain and codomain are the objects of ``Fun(I, C)`` as supplied (a functor,
        or the morphism of ``C`` it denotes when ``I = [1]``); the functors they denote
        are retained for the components.
        """

        def __init__(self, data: NaturalTransformationData) -> None:
            self._assignment = data.assignment
            self._components: MonoDict = MonoDict()
            self._component_family = LazyFamily(self.source_functor().domain(), self._component_from_assignment)

        def source_functor(self) -> Functor:
            return diagram_of(self.domain())

        def target_functor(self) -> Functor:
            return diagram_of(self.codomain())

        def _component_from_assignment(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            if member_object in self._components:
                return self._components[member_object]
            source, target = self.source_functor(), self.target_functor()
            component = self._assignment(member_object)
            expected = source.codomain().morphism_category(1)(source.on_object(member_object), target.on_object(member_object))
            assert component in expected, f"{component!r} is not a morphism of {expected!r}, so it is not a component of {self!r}"
            self._components[member_object] = component
            return component

        def component(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            """``eta_X: F(X) -> G(X)``, retained lazily as an indexed Sage family.

            The public declaration remains the rule ``X |-> eta_X``.  ``LazyFamily`` owns
            the potentially infinite indexed assignment, while ``MonoDict`` retains each
            realized component by source-object identity because owned equality is
            proposition-valued (D60, POL-SAGE-013).
            """
            assert member_object in self.source_functor().domain(), (
                f"{member_object!r} is not an object of {self.source_functor().domain()!r}"
            )
            return self._component_family[member_object]

        def op(self) -> NaturalTransformation:
            """Return the retained reversed transformation between opposite functors."""
            from sage_categories.cat.opposites import opposite_transformation

            return opposite_transformation(self)

        def whisker_left(self, functor: Functor) -> NaturalTransformation:
            """``H . eta``: left whiskering by ``H`` (specs/functor.md)."""
            return Cat().whisker_left(functor, self)

        def whisker_right(self, functor: Functor) -> NaturalTransformation:
            """``eta . F``: right whiskering by ``F`` (specs/functor.md)."""
            return Cat().whisker_right(self, functor)

        def horizontal(self, transformation: NaturalTransformation) -> NaturalTransformation:
            """Horizontal composition ``transformation * self`` (specs/functor.md)."""
            return Cat().horizontal_composite(transformation, self)

        def __repr__(self) -> str:
            return f"NaturalTransformation({self.domain()!r} => {self.codomain()!r})"

    def __init__(self, base: CategoryOfCategories) -> None:
        # Until ``_bootstrap`` runs, at the foot of this module, ``Fun`` has no property
        # category to place a subcategory monomorphism in, so every placement queues.
        self._bootstrapping = True
        self._bootstrapped = False
        # The one identity-on-values functor per ``(source, target)``, constructed once
        # and retained by identity (POL-FUN-027).  It is the kernel's own witness that
        # ``source`` is a subcategory of ``target``; the declaration a leaf makes is
        # placement in ``Fun(S, T).Monomorphisms().Isofibrations()``, and that placement,
        # not this table, is what placement follows (POL-FUN-036).
        self._shared_value_functors: TripleDict = TripleDict(weak_values=False)
        self._pending: list[tuple[Functor, bool]] = []
        self._declaring: MonoDict = MonoDict()
        self._inheriting: MonoDict = MonoDict()
        super().__init__(base)

    def fixed_endpoint_type(self) -> type[FunctorCategory]:
        return FunctorCategory

    def __call__(self, shape: Category, target: Category | Functor) -> FunctorCategory | Functor:
        """``Fun(I, D)`` is the functor category; ``Fun(I, F)`` for a functor ``F: D -> E`` is ``(-) ** I`` applied to it.

        The exponential ``D ** I = Fun(I, D)`` is a functor in ``D``, so the second
        argument selects the action: a category selects the fixed-endpoint category, a
        morphism of ``Cat()`` the morphism action ``Fun(I, D) -> Fun(I, E)``
        (``Cat().exponential_on_morphism``).
        """
        if is_placed(target, self):
            return self.base_category().exponential_on_morphism(shape, target)
        return super().__call__(shape, target)

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        """A functor, or a point of a category with a category as domain denoting its defining functor (specs/functor.md, "The Mor(n, C) tower", specs/functor.md, "Slices and coslices")."""
        return denotes_functor(candidate, self)

    # -- the functor property categories (POL-FUN-024) -----------------------------------
    def _symbolic_inverse_(self, transformation: NaturalTransformation) -> NaturalTransformation:
        """The componentwise inverse of a natural transformation placed in ``Mor(Fun).Isomorphisms()``.

        A natural transformation is an isomorphism exactly when every component is
        (Mathlib ``CategoryTheory.NatIso.isIso_of_isIso_app`` and
        ``NatTrans.isIso_iff_isIso_app``, ``Mathlib/CategoryTheory/NatIso.lean``;
        inspected 2026-08-27), and its inverse has components ``(eta_X)⁻¹``.
        """
        source, target = transformation.domain(), transformation.codomain()
        return self.morphism_category(1)(target, source).Isomorphisms()(lambda member_object: transformation.component(member_object).inverse())

    # -- the functor property categories (POL-FUN-024, POL-CAT-090) ----------------------

    # The five properties of functors, each an ordinary property axiom of ``Fun``
    # (POL-CAT-090).  The identifier is the whole declaration: the kernel compiles
    # ``F.is_full()`` and its four siblings from these five lines, onto this class's
    # ``ObjectType``, and no category writes one (``Axiom._derive_application``, D89).
    #
    # FullyFaithful is a full subcategory of Full and of Faithful; Equivalences of
    # FullyFaithful and of EssentiallySurjective (Mathlib ``Functor.FullyFaithful.full``,
    # ``Functor.FullyFaithful.faithful``, ``Functor.IsEquivalence``; inspected 2026-08-26).
    #
    # None of the five registers a computational handler (POL-CAT-091): ``ask`` answers
    # from placement, an active assumption, or a declared containment, and returns
    # ``Unknown`` otherwise.
    Full = Axiom()
    Faithful = Axiom()
    EssentiallySurjective = Axiom()
    FullyFaithful = Axiom(full_subcategory_of=(Full, Faithful))
    Equivalences = Axiom(full_subcategory_of=(FullyFaithful, EssentiallySurjective))

    def _bootstrap(self) -> None:
        """Build the two property categories placement itself reads, and place the deferred monomorphisms.

        Every subcategory monomorphism is placed in a property category of ``Fun``, and
        the monomorphism presenting one of those property categories as a subcategory of
        ``Fun`` is one of them, so the placements are queued until this runs and this
        drains the queue (``_shared_value_functor``).  It runs once, when this module
        constructs ``Fun``.
        """
        # A subcategory of ``T`` is a subobject of ``T`` in ``Cat()``, and the two
        # conditions on the monomorphism that presents it are monicity and repleteness of
        # the image, which is exactly the isofibration condition (Kerodon, Example
        # 4.4.1.12, https://kerodon.net/tag/01EX, inspected 2026-08-28; nLab, replete
        # subcategory, inspected 2026-08-28).  Placement follows a functor with both, and
        # no other (POL-FUN-036; ``specs/functor.md``, "Monomorphisms of Cat() and placement").
        self._isofibrations = PropertySubcategory(self, "Isofibrations", ())
        # A monomorphism of ``Cat()`` is faithful and injective on objects, so
        # ``Monomorphisms`` is a full subcategory of ``Faithful`` (nLab, subcategory,
        # https://ncatlab.org/nlab/show/subcategory, inspected 2026-08-28: "A functor is
        # easily verified to be monic iff it is faithful and injective on objects").
        self._monomorphisms = PropertySubcategory(self, "Monomorphisms", (self.Faithful(),))
        # A cartesian lift of an isomorphism is an isomorphism, and so is a cocartesian
        # one, so a Grothendieck fibration and opfibration are isofibrations; each states
        # that containment by the monomorphism it retains into ``Isofibrations()`` and
        # nothing induces it from the predicates (D83, D169; ``specs/functor.md``,
        # "Functors as morphisms of Cat").  Neither is a subcategory of ``Faithful()``:
        # ``Fun([1], C).ev(1)``, the codomain fibration, is a fibration and is faithful on
        # no ``C`` with two parallel morphisms.
        self._fibrations = PropertySubcategory(self, "Fibrations", (self._isofibrations,))
        self._opfibrations = PropertySubcategory(self, "Opfibrations", (self._isofibrations,))
        self._bootstrapped = True
        # Placing a deferred functor can construct a further narrowing of ``Fun``, whose
        # own subcategory monomorphisms defer in turn, so the queue grows while it is read
        # and is drained until nothing is added.  There are finitely many narrowings, so
        # it ends.  Each entry stays in the queue while the drain runs, because the queue
        # is the declaration every entry carries until its placement exists
        # (``declares_inheritance``).
        drained = 0
        while drained < len(self._pending):
            functor, full = self._pending[drained]
            drained += 1
            refine(functor, self._declared_subcategory(full))
        self._pending.clear()
        self._bootstrapping = False

    def Isofibrations(self) -> Category:
        return self._isofibrations

    def Fibrations(self) -> Category:
        """Grothendieck fibrations, a retained full subcategory of ``Isofibrations()`` (D169)."""
        return self._fibrations

    def Opfibrations(self) -> Category:
        """Grothendieck opfibrations, a retained full subcategory of ``Isofibrations()`` (D169)."""
        return self._opfibrations

    def Monomorphisms(self) -> Category:
        """Monic functors: faithful and injective on objects, so this is a full subcategory of ``Faithful()``."""
        return self._monomorphisms

    # -- subcategory monomorphisms (POL-FUN-027, POL-FUN-036) -----------------------------
    #
    # A leaf declares that ``S`` is a subcategory of ``T`` by constructing in
    # ``Fun(S, T).Monomorphisms().Isofibrations()`` (``FunctorProperty.__call__``).  The
    # kernel's own subcategories are built while those property categories do not yet
    # exist, so they request the inclusion by name instead, through the two named methods
    # at the foot of this section; both declare the same property, and both reach the one
    # identity-on-values functor the leaf's own declaration reaches.

    def identity_on_values(self, source: Category, target: Category) -> Functor:
        """The one functor ``source -> target`` that is the identity on the values they share, retained by identity (POL-FUN-027).

        It is a functor exactly when ``source`` is a subcategory of ``target``, and this
        states nothing about which relation holds: the caller declares that by placing the
        result, and a placement made twice for one pair narrows the one retained value.
        """
        key = (source, target, self)
        if key not in self._shared_value_functors:
            self._shared_value_functors[key] = self._base.construct_morphism(source, target, identity_on_values, identity_on_values)
        return self._shared_value_functors[key]

    def _shared_value_functor(self, source: Category, target: Category, full: bool) -> Functor:
        """The identity-on-values functor ``source -> target``, placed in the declared property.

        Until ``_bootstrap`` has finished, the property category to place it in does not
        exist yet (or is itself under construction), so the declaration is queued and
        ``_bootstrap`` drains the queue.
        """
        functor = self.identity_on_values(source, target)
        if self._bootstrapping:
            self._pending.append((functor, full))
        else:
            refine(functor, self._declared_subcategory(full))
        return functor

    def declares_inheritance(self, functor: Functor) -> bool:
        """Whether ``functor`` carries inheritance from its target (D164 to D167).

        Among a leaf's selected structure functors, the ones declared into
        ``Fun(C, D).Isofibrations()`` or a subcategory of it carry inheritance; a
        selected functor without that property gives access to the structure it selects
        and inherits nothing (``specs/functor.md``, "Structure functors and inherited
        classes").  ``(L, b) |-> L`` is a faithful isofibration and a lattice inherits
        along it; ``(L, b) |-> b`` is not one, and reaches ``L.b()`` without making a
        lattice a bilinear form.

        Placement asks more: a monomorphism that is an isofibration (D169,
        ``declares_subcategory``).  Inheritance needs the arrow condition alone, since
        ``Groups() -> Sets()`` is not injective on objects.
        """
        if any(declared is functor for declared, _ in self._pending):
            # While the queue drains, a declaration made by name has nowhere to be placed
            # yet, so the queue holds it.  The queue is that declaration, read here
            # exactly as the placement is read below, and it is empty once bootstrap ends.
            return True
        if not self._bootstrapped:
            return False
        placement = functor.category()
        if placement not in self._inheriting:
            self._inheriting[placement] = any(root is self._isofibrations for root in placement.narrowing_roots())
        return self._inheriting[placement]

    def declares_subcategory(self, functor: Functor) -> bool:
        """Whether ``functor`` is declared a monomorphism of ``Cat()`` and an isofibration (POL-FUN-036).

        Both conditions are read off the functor's own placement, which is what the leaf
        stated by constructing in ``Fun(S, T).Monomorphisms().Isofibrations()``.  Before
        those property categories exist no functor is placed in them, so none is declared.
        """
        if not self._bootstrapped:
            return False
        # The answer depends only on the placement, whose roots are fixed once the
        # category exists, so it is decided once per placement rather than per functor.
        placement = functor.category()
        if placement not in self._declaring:
            roots = placement.narrowing_roots()
            self._declaring[placement] = any(root is self._monomorphisms for root in roots) and any(root is self._isofibrations for root in roots)
        return self._declaring[placement]

    def declares_point(self, functor: Functor) -> bool:
        """Whether ``functor`` is declared a point ``* -> C``: a monomorphism whose domain is the terminal category (D146, D154, D162).

        ``C.Point()`` constructs the arrow in ``Fun(*, C).Monomorphisms()``, and that
        construction is the declaration.  The arrow is not an isofibration, because an
        isomorphism ``X -> Y`` of ``C`` has nothing to lift to in ``*``, which has one
        morphism; so it traces neither placement nor inheritance, and the inclusion
        ``<X> -> C`` of the replete full subcategory its image generates carries both
        (D161, D169).  The domain is what separates a point from the other monomorphisms
        that are not isofibrations, the skeletal inclusions such as ``Cardinal() -> Sets()``.
        """
        if not self._bootstrapped:
            return False
        if functor.domain() is not self.base_category().Terminal():
            return False
        return any(root is self._monomorphisms for root in functor.category().narrowing_roots())

    def _declared_subcategory(self, full: bool) -> Category:
        """``Fun.Monomorphisms().Isofibrations()``, with fullness for a full subcategory (POL-FUN-036)."""
        declared = self.Monomorphisms().property_subcategory(self.Isofibrations())
        return declared.property_subcategory(self.Full()) if full else declared

    def subcategory_monomorphism(self, source: Category, target: Category) -> Functor:
        """The monomorphism presenting ``source`` as a subcategory of ``target``, identity on the shared values."""
        return self._shared_value_functor(source, target, False)

    def full_subcategory_monomorphism(self, source: Category, target: Category) -> Functor:
        """The same for a full subcategory, which adds fullness (Mathlib ``ObjectProperty.ι``)."""
        return self._shared_value_functor(source, target, True)

    # -- limits of functors, pointwise (specs/functor.md, "Diagram shapes and universal constructions"; ``cat/diagrams.py``) ------------------------

    def limit_construction(
        self,
        shape: Category,
    ) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        """``Fun(I, C)`` has the ``J``-limits that ``C`` has, computed by evaluation."""
        from sage_categories.cat.diagrams import pointwise_limit

        return pointwise_limit

    def __repr__(self) -> str:
        return "Fun"


Fun: FunctorsCategory = Cat().morphism_category(1)
NaturalTransformation = Fun.MorphismType
_category.Fun = Fun
_category.NaturalTransformation = NaturalTransformation
Fun._bootstrap()
register_handler(denotes_diagram, _denotes_diagram_by_domain)
register_handler(denotes_functor, _denotes_functor_by_domain)
register_handler(Cat().equality(), _defining_functor_equal)
# The two property subcategories of ``Cat()`` are constructed here, after ``Fun`` exists to
# supply their subcategory monomorphisms.  ``Inhabited`` reads the exact case a category
# owns, in the shape ``morphism_set()`` uses; ``Empty`` is its negation, the one route
# ``Sets()`` uses for a complementary pair (``sets/category.py``).  Neither decides
# inhabitation itself (POL-CAT-091).
def _chosen_inhabitation(
    category: CategoryOfCategories.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    decision = category._chosen_inhabitation()
    return None if decision is Unknown else decision


def _chosen_emptiness(
    category: CategoryOfCategories.ObjectType,
    assumptions: Proposition,
) -> bool | None:
    return sympy_ask(~category.is_inhabited(), assumptions)


register_handler(Cat().Inhabited().predicate(), _chosen_inhabitation)
register_handler(Cat().Empty().predicate(), _chosen_emptiness)
