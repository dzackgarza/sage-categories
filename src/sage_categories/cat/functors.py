"""Functors, ``Fun = Mor(Cat())``, and natural transformations (POL-FUN-001, POL-FUN-017, POL-FUN-027, POL-FUN-024).

A functor is a morphism of ``Cat()``: a ``Cat().MorphismType`` value with a domain,
a codomain, and total object and morphism actions (Mathlib
``CategoryTheory.Functor``: ``obj``, ``map``; inspected 2026-08-26).  Its action on
a generalized element is derived from the morphism action (POL-FUN-002).

``Fun = Mor(Cat())`` is the category whose objects are functors and whose
morphisms are natural transformations; ``Fun(C, D) = Mor(Cat())(C, D)`` owns the
construction of functors ``C -> D`` (POL-FUN-017/027).  Functor properties are
ordinary property subcategories of ``Fun`` with no computational handlers
(POL-CAT-090/091, Mathlib ``Functor.Full``, ``Functor.Faithful``,
``Functor.FullyFaithful``; inspected 2026-08-26).

This module constructs ``Cat()`` at import (``category.bootstrap()``): the local
``Cat().MorphismType`` role lives here, so the singleton exists once this module
does.  ``Fun`` is then ``Mor(Cat())``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat import category as _category
from sage_categories.cat.category import Assignment, Category, CategoryOfCategories, OnMorphism, OnObject
from sage_categories.cat.morphisms import FixedEndpointCategory, MorphismCategory, endpoints
from sage_categories.cat.properties import FixedEndpointProperty, PropertySubcategory
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed, is_retained_inclusion, refine
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of

if TYPE_CHECKING:
    from sage_categories.sets.elements import SetPoint
    from sage_categories.sets.objects import SetObject

__all__ = ["Fun", "Functor", "FunctorCategory", "FunctorProperty", "FunctorsCategory", "NaturalTransformation"]


def identity_on_values(value: CategoryPoint) -> CategoryPoint:
    """The object and morphism action of every inclusion: the identity on the shared values (POL-FUN-027)."""
    return value


def diagram_of(value: CategoryPoint) -> Functor:
    """The functor that a value of ``Fun(I, C)`` denotes: a functor itself, or the retained defining functor of a point of ``C`` at stage ``I`` (specs/functor.md, "The Mor(n, C) tower", specs/functor.md, "Slices and coslices")."""
    if is_placed(value, Fun):
        return value
    return value.defining_morphism()


def _defining_functor_equal(first: CategoryPoint, candidate: Any) -> Decision:
    """A functor ``T -> C`` equals a point of ``C`` at stage ``T`` exactly when it is that point's retained defining functor."""
    if is_placed(first, Fun) and not is_placed(candidate, Fun) and role_of(candidate) in (Role.OBJECT, Role.MORPHISM) and candidate.stage() is first.domain():
        return first is candidate.defining_morphism()
    if is_placed(candidate, Fun) and not is_placed(first, Fun) and role_of(first) in (Role.OBJECT, Role.MORPHISM) and first.stage() is candidate.domain():
        return candidate is first.defining_morphism()
    return Unknown


# The stage comparisons ``G_D -> F(G_C)`` retained by the constructions that own a
# selected functor exposing classical element methods (POL-LEAF-003), keyed by the functor.
_stage_comparisons: MonoDict = MonoDict()

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


class Functor(MorphismOfCategory):
    """The local ``Cat().MorphismType``: a functor ``C -> D`` from its total actions."""

    def __init__(
        self,
        category: Category,
        domain: Category,
        codomain: Category,
        on_object: OnObject,
        on_morphism: OnMorphism,
    ) -> None:
        super().__init__(category, domain, codomain)
        self._on_object = on_object
        self._on_morphism = on_morphism

    # A value whose placement already reaches the domain is accepted by that
    # placement (a pure graph lookup); only an unplaced value has its membership
    # proposition decided, since that decision may itself need this functor.

    def on_object(self, member_object: ObjectOfCategory) -> ObjectOfCategory:
        """The image of an object of the domain."""
        assert is_placed(member_object, self.domain()) or member_object in self.domain(), f"{member_object!r} is not an object of {self.domain()!r}"
        return self._on_object(member_object)

    def on_morphism(self, morphism: MorphismOfCategory) -> MorphismOfCategory:
        """The image of a morphism of the domain."""
        morphisms = self.domain().morphism_category(1)
        assert is_placed(morphism, morphisms) or morphism in morphisms, f"{morphism!r} is not a morphism of {self.domain()!r}"
        return self._on_morphism(morphism)

    def on_element(self, element: ElementOfObject) -> ElementOfObject:
        """The image of a generalized element ``t: T -> X``: the element with defining morphism ``F(t)`` (POL-FUN-002).

        A classical element whose stage is not an object of the domain belongs to the
        subcategory's objects only through its ambient; the retained inclusion maps
        it to the same value (``specs/functor.md``, "Inclusion functors": a subcategory
        without the ambient's stage receives classical element operations through the
        inclusion image).  No other functor has an action on it.
        """
        defining = element.defining_morphism()
        if element.stage() not in self.domain():
            assert is_retained_inclusion(self), f"{element!r} is not a generalized element in {self.domain()!r}"
            return element
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

    # -- classical stages (``specs/functor.md``, "Structural inheritance") ----------------

    def retain_stage_comparison(self, comparison: MorphismOfCategory) -> None:
        """Retain ``c: G_D -> F(G_C)`` as the defining datum of this functor's classical transport (POL-LEAF-003)."""
        (source_stage,) = self.domain().classical_stages()
        (target_stage,) = self.codomain().classical_stages()
        assert comparison in self.codomain().morphism_category(1)(target_stage, self.on_object(source_stage))
        _stage_comparisons[self] = comparison

    def stage_comparison(self) -> MorphismOfCategory:
        """``G_D -> F(G_C)``: the retained comparison, or the identity when ``F(G_C) is G_D``."""
        if self in _stage_comparisons:
            return _stage_comparisons[self]
        (source_stage,) = self.domain().classical_stages()
        (target_stage,) = self.codomain().classical_stages()
        assert self.on_object(source_stage) is target_stage, f"{self!r} retains no stage comparison"
        return target_stage.identity()

    # -- composition data ------------------------------------------------------------------

    def retain_factors(self, first: Functor, second: Functor) -> None:
        """Retain that this functor is the composite ``second * first``."""
        assert self not in _composite_factors, f"{self!r} already retains its factors"
        assert first.codomain() is second.domain() and self.domain() is first.domain() and self.codomain() is second.codomain()
        _composite_factors[self] = (first, second)

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


class NaturalTransformation(MorphismOfCategory):
    """The local ``Fun.MorphismType``: ``eta: F => G`` from a component rule ``X |-> eta_X``.

    Its domain and codomain are the objects of ``Fun(I, C)`` as supplied (a functor,
    or the morphism of ``C`` it denotes when ``I = [1]``); the functors they denote
    are retained for the components.
    """

    def __init__(
        self,
        category: Category,
        source: CategoryPoint,
        target: CategoryPoint,
        source_functor: Functor,
        target_functor: Functor,
        assignment: Assignment,
    ) -> None:
        super().__init__(category, source, target)
        self._source_functor = source_functor
        self._target_functor = target_functor
        self._assignment = assignment

    def source_functor(self) -> Functor:
        return self._source_functor

    def target_functor(self) -> Functor:
        return self._target_functor

    def component(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        """``eta_X: F(X) -> G(X)``; naturality is a trusted declaration (POL-MATH-036)."""
        source, target = self._source_functor, self._target_functor
        component = self._assignment(member_object)
        assert component in source.codomain().morphism_category(1)(source.on_object(member_object), target.on_object(member_object))
        return component

    def __repr__(self) -> str:
        return f"NaturalTransformation({self.domain()!r} => {self.codomain()!r})"


class FunctorProperty(FixedEndpointProperty[[OnObject, OnMorphism], [Assignment]]):
    """``Fun(C, D).P()``: functors ``C -> D`` with property ``P``; owns ``inclusion()`` and ``identity()``."""

    def inclusion(self) -> Functor:
        """The identity-on-value inclusion of the domain into the codomain, asserted to have ``P`` (POL-FUN-027, POL-MATH-037)."""
        functors = self.universe().morphism_category(1)
        source, target = self._ambient.domain(), self._ambient.codomain()
        roots = self.narrowing_roots()
        if any(root is functors.FullyFaithful() for root in roots):
            inclusion = functors.full_inclusion(source, target)
        else:
            assert any(root is functors.Faithful() for root in roots), f"an inclusion is faithful or fully faithful, not {self!r}"
            inclusion = functors.faithful_inclusion(source, target)
        refine(inclusion, self)
        return inclusion


# ``denotes_diagram(x, Fun(I, C))``: ``x`` is a functor ``I -> C``, or a point of ``C`` at
# stage ``I`` (specs/functor.md, "Slices and coslices": an object of ``C`` is a point at stage ``1`` and a morphism a point at
# stage ``[1]``), whose defining functor is such a diagram.  Thus the objects of
# ``Fun(1, C)`` are the objects of ``C`` and the objects of ``Fun([1], C)`` are the
# morphisms of ``C`` (specs/functor.md, "The Mor(n, C) tower", specs/functor.md, "Canonical objects of Cat"): one value, denoting its retained defining functor.
denotes_diagram = Predicate("denotes_diagram", 2, False)


def _denotes_diagram_by_stage(candidate: CategoryPoint, functors: FunctorCategory) -> Decision:
    if is_placed(candidate, functors.ambient()):
        return ask(endpoints(candidate, functors.domain(), functors.codomain()))
    if role_of(candidate) in (Role.OBJECT, Role.MORPHISM):
        return candidate.stage() is functors.domain() and candidate.parent() is functors.codomain()
    return False


denotes_diagram.register_handler(_denotes_diagram_by_stage)

# ``denotes_functor(x, Fun)``: ``x`` is a functor by placement, or a point of a category
# at a categorical stage, which denotes its defining functor (specs/functor.md, "Slices and coslices").
denotes_functor = Predicate("denotes_functor", 2, False)


def _denotes_functor_by_stage(candidate: CategoryPoint, functors: FunctorsCategory) -> Decision:
    if is_placed(candidate, functors):
        return True
    return role_of(candidate) in (Role.OBJECT, Role.MORPHISM) and candidate.stage() in Cat()


denotes_functor.register_handler(_denotes_functor_by_stage)


class FunctorCategory(FixedEndpointCategory[[OnObject, OnMorphism], [Assignment]]):
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

    def __init__(self, morphisms: MorphismCategory, domain: Category, codomain: Category) -> None:
        self._evaluations: MonoDict = MonoDict()
        self._constants: MonoDict = MonoDict()
        self._constant_values: MonoDict = MonoDict()
        self._finite_data: MonoDict = MonoDict()
        super().__init__(morphisms, domain, codomain)

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return denotes_diagram(candidate, self)

    def diagram(self, value: CategoryPoint) -> Functor:
        """The functor ``I -> C`` that a value of this category denotes: itself, or the defining functor of a point of ``C`` at stage ``I``."""
        if is_placed(value, self.ambient()):
            return value
        assert value in self, f"{value!r} is not a diagram of shape {self.domain()!r} in {self.codomain()!r}"
        return value.defining_morphism()

    def construct_morphism(self, source: CategoryPoint, target: CategoryPoint, assignment: Assignment) -> NaturalTransformation:
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

    def evaluation(self, vertex: ObjectOfCategory) -> Functor:
        """``ev_i: Fun(I, C) -> C``, the evaluation at the object ``i`` of the shape."""
        from sage_categories.cat.diagrams import evaluation

        return evaluation(self, vertex)

    def constant(self, value: ObjectOfCategory) -> Functor:
        """The constant diagram at an object of the codomain."""
        from sage_categories.cat.diagrams import constant

        return constant(self, value)

    def has_constant_value(self, diagram: Functor) -> bool:
        return diagram in self._constant_values

    def constant_value(self, diagram: Functor) -> ObjectOfCategory:
        """The object at which a retained constant diagram is constant."""
        assert diagram in self._constant_values, f"{diagram!r} is not a retained constant diagram"
        return self._constant_values[diagram]

    def from_object_rule(self, rule: OnObject) -> Functor:
        """A diagram over a discrete shape from its object rule alone."""
        from sage_categories.cat.diagrams import from_object_rule

        return from_object_rule(self, rule)

    # -- ``Fun([1], C)``: its finite data and its fibration lifts (POL-FUN-029, specs/functor.md, "Diagram shapes and universal constructions") -----------

    def object_set(self) -> SetObject:
        """For ``I = [1]``: the morphism set of ``C``, since the objects are the morphisms of ``C``."""
        assert self.domain() is Cat().Simplex(1), f"{self!r} declares no set of objects"
        morphisms = self.codomain().morphism_set()
        assert morphisms is not Unknown, f"{self.codomain()!r} chooses no finite set of morphisms"
        return morphisms

    def object_at(self, point: SetPoint) -> MorphismOfCategory:
        assert self.domain() is Cat().Simplex(1), f"{self!r} declares no set of objects"
        return self.codomain().morphism_at(point)

    def morphism_set(self) -> SetObject | UnknownClass:
        """For ``I = [1]``: the finite set of commuting squares, when ``C`` chooses a finite set of morphisms."""
        from sage_categories.cat.diagrams import square_set

        if self.domain() is not Cat().Simplex(1) or self.codomain().morphism_set() is Unknown:
            return Unknown
        return square_set(self)

    def morphism_at(self, point: SetPoint) -> NaturalTransformation:
        from sage_categories.cat.diagrams import square_at

        return square_at(self, point)

    # -- functor properties (POL-FUN-024) -----------------------------------------------

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

    def narrowing_type(self) -> type[FunctorProperty]:
        return FunctorProperty

    def __repr__(self) -> str:
        return f"Fun({self.domain()!r}, {self.codomain()!r})"


class FunctorsCategory(MorphismCategory[[OnObject, OnMorphism], [Assignment]]):
    """``Fun = Mor(Cat())``."""

    def __init__(self, base: CategoryOfCategories) -> None:
        self._bootstrapping = False
        self._bootstrapped = False
        # One inclusion per ``(source, target)``, constructed once and retained by
        # identity (POL-FUN-027); "``F`` is an inclusion" is decided against this table.
        self._inclusions: TripleDict = TripleDict(weak_values=False)
        super().__init__(base)

    def fixed_endpoint_type(self) -> type[FunctorCategory]:
        return FunctorCategory

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        """A functor, or a point of a category at a categorical stage denoting its defining functor (specs/functor.md, "The Mor(n, C) tower", specs/functor.md, "Slices and coslices")."""
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

    # -- the functor property categories (POL-FUN-024) -----------------------------------

    def _bootstrap(self) -> None:
        """Build the five functor property categories once and place their inclusions.

        Their own inclusions into ``Fun`` are constructed while the properties do not
        yet exist, so they are placed in ``FullyFaithful()`` afterwards.
        """
        self._bootstrapping = True
        self._full = PropertySubcategory(self, "Full", {}, ())
        self._faithful = PropertySubcategory(self, "Faithful", {}, ())
        self._essentially_surjective = PropertySubcategory(self, "EssentiallySurjective", {}, ())
        # FullyFaithful implies Full and Faithful; Equivalences implies FullyFaithful
        # and EssentiallySurjective (Mathlib ``Functor.FullyFaithful.full``,
        # ``Functor.FullyFaithful.faithful``, ``Functor.IsEquivalence``; inspected 2026-08-26).
        self._fully_faithful = PropertySubcategory(self, "FullyFaithful", {}, (self._full, self._faithful))
        self._equivalences = PropertySubcategory(self, "Equivalences", {}, (self._fully_faithful, self._essentially_surjective))
        self._bootstrapping = False
        self._bootstrapped = True
        for property_category in (self._full, self._faithful, self._essentially_surjective, self._fully_faithful, self._equivalences):
            for inclusion in property_category.selected_functors():
                refine(inclusion, self._fully_faithful)

    def Full(self) -> Category:
        if not self._bootstrapped:
            self._bootstrap()
        return self._full

    def Faithful(self) -> Category:
        if not self._bootstrapped:
            self._bootstrap()
        return self._faithful

    def FullyFaithful(self) -> Category:
        if not self._bootstrapped:
            self._bootstrap()
        return self._fully_faithful

    def EssentiallySurjective(self) -> Category:
        if not self._bootstrapped:
            self._bootstrap()
        return self._essentially_surjective

    def Equivalences(self) -> Category:
        if not self._bootstrapped:
            self._bootstrap()
        return self._equivalences

    # -- inclusions (POL-FUN-027) ---------------------------------------------------------

    def _inclusion(self, source: Category, target: Category, placement: Callable[[], Category]) -> Functor:
        """The one identity-on-value inclusion ``source -> target``, placed in the declared functor property."""
        if not self._bootstrapped and not self._bootstrapping:
            self._bootstrap()
        key = (source, target, self)
        if key not in self._inclusions:
            self._inclusions[key] = self._base.construct_morphism(source, target, identity_on_values, identity_on_values)
        inclusion = self._inclusions[key]
        if self._bootstrapped:
            refine(inclusion, placement())
        return inclusion

    def retains_inclusion(self, source: Category, target: Category) -> bool:
        return (source, target, self) in self._inclusions

    def inclusion_of(self, source: Category, target: Category) -> Functor:
        """The retained inclusion ``source -> target``."""
        assert (source, target, self) in self._inclusions, f"no inclusion {source!r} -> {target!r} was declared"
        return self._inclusions[source, target, self]

    def full_inclusion(self, source: Category, target: Category) -> Functor:
        """The inclusion of a full subcategory: fully faithful by construction (Mathlib ``ObjectProperty.ι``)."""
        return self._inclusion(source, target, self.FullyFaithful)

    def faithful_inclusion(self, source: Category, target: Category) -> Functor:
        """The inclusion of a subcategory: faithful by construction."""
        return self._inclusion(source, target, self.Faithful)

    # -- limits and colimits of functors, pointwise (specs/functor.md, "Diagram shapes and universal constructions"; ``cat/diagrams.py``) -----------

    def limit_construction(self, shape: Category) -> Callable[[Functor], ObjectOfCategory]:
        """``Fun(I, C)`` has the ``J``-limits that ``C`` has, computed by evaluation."""
        from sage_categories.cat.diagrams import pointwise_limit

        return pointwise_limit

    def colimit_construction(self, shape: Category) -> Callable[[Functor], ObjectOfCategory]:
        from sage_categories.cat.diagrams import pointwise_colimit

        return pointwise_colimit

    def __repr__(self) -> str:
        return "Fun"


_category.bootstrap()
Cat = _category.Cat
Fun: FunctorsCategory = Cat().morphism_category(1)
Cat().equality().register_handler(_defining_functor_equal)
