"""Functors, ``Fun = Mor(Cat())``, and natural transformations (D04, D05, D08, D09).

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
from sage_categories.kernel.refinement import is_placed, place, refine
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of

if TYPE_CHECKING:
    from sage_categories.sets.elements import SetPoint
    from sage_categories.sets.objects import SetObject

__all__ = ["Fun", "Functor", "FunctorCategory", "FunctorProperty", "FunctorsCategory", "NaturalTransformation"]


def identity_on_values(value: CategoryPoint) -> CategoryPoint:
    """The object and morphism action of every inclusion: the identity on the shared values (D08)."""
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
        """The image of a generalized element ``t: T -> X``: the element with defining morphism ``F(t)`` (D05).

        A classical element whose stage is not an object of the domain belongs to the
        subcategory's objects only through its ambient; an inclusion maps it to the
        same value (D06: a subcategory without the ambient's stage receives classical
        element operations through the inclusion image).
        """
        defining = element.defining_morphism()
        if element.stage() not in self.domain():
            assert self._on_object is identity_on_values, f"{element!r} is not a generalized element in {self.domain()!r}"
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
        """The identity-on-value inclusion of the domain into the codomain, asserted to have ``P`` (D08)."""
        functors = self.category().morphism_category(1)
        source, target = self._ambient.domain(), self._ambient.codomain()
        roots = self.narrowing_roots()
        if any(root is functors.FullyFaithful() for root in roots):
            inclusion = functors.full_inclusion(source, target)
            source.declare_full_subcategory(target)
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
    equality handler decides it (specs/functor.md, "The Mor(n, C) tower", specs/sets.md, "Equality").  It retains the cartesian lifts of
    ``ev_1`` by pullback and the cocartesian lifts of ``ev_0`` by pushout when the
    codomain owns those constructions (POL-FUN-029; nLab "codomain fibration", inspected
    2026-08-27: "If C has all pullbacks, then the functor is in addition a
    Grothendieck fibration", with "the cartesian lift of a morphism c_1 -> c_2 in
    C ... given by the morphism c_1 x_{c_2} c'_2 -> c'_2").
    """

    def __init__(self, morphisms: MorphismCategory, domain: Category, codomain: Category) -> None:
        self._evaluations: MonoDict = MonoDict()
        self._constants: MonoDict = MonoDict()
        self._constant_values: MonoDict = MonoDict()
        self._lifts: TripleDict = TripleDict(weak_values=False)
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

    # -- diagrams (D10, D16) -----------------------------------------------------

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

    def cartesian_lift(self, morphism: MorphismOfCategory, member_object: MorphismOfCategory) -> NaturalTransformation:
        """The cartesian lift of ``f: y -> x`` at ``p: z -> x`` for ``ev_1``: the square ``z *_x y -> y`` over ``p``, by pullback in ``C``."""
        from sage_categories.cat.diagrams import codomain_lift

        return codomain_lift(self, morphism, member_object)

    def cocartesian_lift(self, morphism: MorphismOfCategory, member_object: MorphismOfCategory) -> NaturalTransformation:
        """The cocartesian lift of ``f: x -> y`` at ``p: x -> z`` for ``ev_0``: the square from ``p`` to ``z +_x y <- y``, by pushout in ``C``."""
        from sage_categories.cat.diagrams import domain_lift

        return domain_lift(self, morphism, member_object)

    # -- functor properties (D09) -----------------------------------------------

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
        super().__init__(base)

    def fixed_endpoint_type(self) -> type[FunctorCategory]:
        return FunctorCategory

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        """A functor, or a point of a category at a categorical stage denoting its defining functor (specs/functor.md, "The Mor(n, C) tower", specs/functor.md, "Slices and coslices")."""
        return denotes_functor(candidate, self)

    # -- the functor property categories (D09) -----------------------------------

    def _bootstrap(self) -> None:
        """Build the five functor property categories and place their inclusions."""
        self._bootstrapping = True
        full = PropertySubcategory(self, "Full", {}, ())
        faithful = PropertySubcategory(self, "Faithful", {}, ())
        essentially_surjective = PropertySubcategory(self, "EssentiallySurjective", {}, ())
        # FullyFaithful implies Full and Faithful; Equivalences implies FullyFaithful
        # and EssentiallySurjective (Mathlib ``Functor.FullyFaithful.full``,
        # ``Functor.FullyFaithful.faithful``, ``Functor.IsEquivalence``; inspected 2026-08-26).
        fully_faithful = PropertySubcategory(self, "FullyFaithful", {}, (full, faithful))
        equivalences = PropertySubcategory(self, "Equivalences", {}, (fully_faithful, essentially_surjective))
        self._properties.update(
            {
                "Full": full,
                "Faithful": faithful,
                "EssentiallySurjective": essentially_surjective,
                "FullyFaithful": fully_faithful,
                "Equivalences": equivalences,
            }
        )
        self._bootstrapping = False
        self._bootstrapped = True
        for property_category in (full, faithful, essentially_surjective, fully_faithful, equivalences):
            for inclusion in property_category.selected_functors():
                refine(inclusion, fully_faithful)

    def _functor_property(self, name: str) -> Category:
        if not self._bootstrapped:
            self._bootstrap()
        return self._properties[name]

    def Full(self) -> Category:
        return self._functor_property("Full")

    def Faithful(self) -> Category:
        return self._functor_property("Faithful")

    def FullyFaithful(self) -> Category:
        return self._functor_property("FullyFaithful")

    def EssentiallySurjective(self) -> Category:
        return self._functor_property("EssentiallySurjective")

    def Equivalences(self) -> Category:
        return self._functor_property("Equivalences")

    # -- inclusions (D08) ---------------------------------------------------------

    def _inclusion(self, source: Category, target: Category, placement_name: str) -> Functor:
        """The identity-on-value inclusion ``source -> target`` placed in a functor property."""
        if not self._bootstrapped and not self._bootstrapping:
            self._bootstrap()
        inclusion = self._base.construct_morphism(source, target, identity_on_values, identity_on_values)
        if self._bootstrapped:
            place(inclusion, self._properties[placement_name])
        return inclusion

    def full_inclusion(self, source: Category, target: Category) -> Functor:
        """The inclusion of a full subcategory: fully faithful by construction (Mathlib ``ObjectProperty.ι``)."""
        return self._inclusion(source, target, "FullyFaithful")

    def faithful_inclusion(self, source: Category, target: Category) -> Functor:
        """The inclusion of a subcategory: faithful by construction."""
        return self._inclusion(source, target, "Faithful")

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
