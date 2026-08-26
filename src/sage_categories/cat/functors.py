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

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat import category as _category
from sage_categories.cat.category import Assignment, Category, CategoryOfCategories, OnMorphism, OnObject
from sage_categories.cat.morphisms import FixedEndpointCategory, MorphismCategory
from sage_categories.cat.properties import FixedEndpointProperty, PropertySubcategory
from sage_categories.kernel.predicates import AppliedPredicate
from sage_categories.kernel.refinement import is_placed, place, refine
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory

if TYPE_CHECKING:
    from sage_categories.kernel.predicates import Predicate

__all__ = ["Fun", "Functor", "FunctorCategory", "FunctorProperty", "FunctorsCategory", "NaturalTransformation"]


def identity_on_values(value: CategoryPoint) -> CategoryPoint:
    """The object and morphism action of every inclusion: the identity on the shared values (D08)."""
    return value


# The stage comparisons ``G_D -> F(G_C)`` retained by the constructions that own a
# selected functor exposing classical element methods (POL-LEAF-003), keyed by the functor.
_stage_comparisons: MonoDict = MonoDict()


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
    """The local ``Fun.MorphismType``: ``eta: F => G`` from a component rule ``X |-> eta_X``."""

    def __init__(
        self,
        category: Category,
        source: Functor,
        target: Functor,
        assignment: Assignment,
    ) -> None:
        super().__init__(category, source, target)
        self._assignment = assignment

    def component(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        """``eta_X: F(X) -> G(X)``; naturality is a trusted declaration (POL-MATH-036)."""
        source, target = self.domain(), self.codomain()
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


class FunctorCategory(FixedEndpointCategory[[OnObject, OnMorphism], [Assignment]]):
    """``Fun(C, D)``: functors ``C -> D`` and their natural transformations.

    As the category of diagrams of shape ``C`` in ``D`` it retains its evaluation
    functors and constant diagrams (``cat/diagrams.py``, D10, D16).
    """

    def __init__(self, morphisms: MorphismCategory, domain: Category, codomain: Category) -> None:
        self._evaluations: MonoDict = MonoDict()
        self._constants: MonoDict = MonoDict()
        self._constant_values: MonoDict = MonoDict()
        super().__init__(morphisms, domain, codomain)

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

    def __repr__(self) -> str:
        return "Fun"


_category.bootstrap()
Cat = _category.Cat
Fun: FunctorsCategory = Cat().morphism_category(1)
