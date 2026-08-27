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

This module constructs ``Cat()`` at import (``category.bootstrap()``).  The local
``Cat().MorphismType`` declaration lives here.  Bootstrap binds ``Functor`` to the
compiled role, then constructs ``Fun = Mor(Cat())`` and binds
``NaturalTransformation`` to ``Fun.MorphismType``.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat import category as _category
from sage_categories.cat.category import Assignment, Category, CategoryOfCategories, OnMorphism, OnObject
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import AppliedPredicate, Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed, is_subcategory, refine, traces_placement
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory, Role, role_of

if TYPE_CHECKING:
    from sage_categories.kernel.construction import ElementConstructionInput, MorphismConstructionInput, ObjectConstructionInput
    from sage_categories.sets.elements import SetElement
    from sage_categories.sets.objects import SetObject

__all__ = ["Fun", "Functor", "FunctorCategory", "FunctorProperty", "FunctorsCategory", "NaturalTransformation"]


def identity_on_values(value: CategoryPoint) -> CategoryPoint:
    """The object and morphism action of every subcategory monomorphism: the identity on the shared values (POL-FUN-027)."""
    return value


def diagram_of(value: CategoryPoint) -> Functor:
    """The functor that a value of ``Fun(I, C)`` denotes: a functor itself, or the retained defining functor of a point of ``C`` with domain ``I`` (specs/functor.md, "The Mor(n, C) tower", specs/functor.md, "Slices and coslices")."""
    if is_placed(value, Fun):
        return value
    return value.defining_morphism()


def _defining_functor_equal(first: CategoryPoint, candidate: Any) -> Decision:
    """A functor ``T -> C`` equals a point of ``C`` with domain ``T`` exactly when it is that point's retained defining functor."""
    if is_placed(first, Fun) and not is_placed(candidate, Fun) and role_of(candidate) in (Role.OBJECT, Role.MORPHISM) and candidate.defining_morphism().domain() is first.domain():
        return first is candidate.defining_morphism()
    if is_placed(candidate, Fun) and not is_placed(first, Fun) and role_of(first) in (Role.OBJECT, Role.MORPHISM) and first.defining_morphism().domain() is candidate.domain():
        return candidate is first.defining_morphism()
    return Unknown


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

    on_object: OnObject
    on_morphism: OnMorphism


class FunctorDeclaration(MorphismOfCategory):
    """The local ``Cat().MorphismType`` declaration."""

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
        return self._on_morphism(morphism)

    def on_element(self, element: CategoryPoint) -> CategoryPoint:
        """The image of a generalized element ``t: T -> X``: the element ``q = F(t): F(T) -> F(X)`` (POL-FUN-002).

        This action is derived, never stored: it applies ``on_morphism`` to the defining
        morphism of ``t``.  A functor retains no element callback and no element
        capability.  The element conversion a selected functor retains supplies compiler
        input only; it never answers this call, so the public image of a classical
        element keeps the domain ``F(G_C)`` rather than the target's separator
        (``specs/functor.md``, "Structural inheritance").

        A subcategory monomorphism is the identity on the objects and morphisms of its domain,
        so it is the identity on ``t: T -> X`` as well (``specs/functor.md``, "Inclusion
        functors").  Its domain and defining morphism are those of the ambient, which no
        selected route reaches from the subcategory.
        """
        assert role_of(element) is Role.ELEMENT, f"{element!r} is not a generalized element"
        if traces_placement(self):
            parent = element.parent()
            assert is_placed(parent, self.domain()) or parent in self.domain(), f"{element!r} is not a generalized element in {self.domain()!r}"
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
    # The retained morphism ``c: G_D -> F(G_C)`` is the whole datum of the classical
    # transport.  By the covariant Yoneda lemma it *is* the natural transformation
    # ``phi_F: U_C => U_D . F`` between the represented classical-element functors:
    # Mathlib ``CategoryTheory.coyonedaEquiv : (coyoneda.obj (op X) ⟶ F) ≃ F.obj X``
    # (inspected 2026-08-27) with ``X = G_C`` and the presheaf ``U_D . F``, whose value
    # at ``G_C`` is ``Mor(D)(G_D, F(G_C))``.  The construction therefore retains the
    # separator morphism and no natural-transformation carrier on ``F``.

    def retain_separator_comparison(self, comparison: MorphismOfCategory) -> None:
        """Retain ``c: G_D -> F(G_C)`` as the defining datum of this functor's classical transport (POL-LEAF-003)."""
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
        """The compiler input for the image of ``t``: that of ``q = F(t)``, or of ``p = q . c_F`` for a classical ``t`` (POL-FUN-002/035).

        Applying the morphism conversion to the defining morphism of ``t`` gives the
        defining morphism of ``q: F(T) -> F(X)``, the value public element application
        returns.  This derivation is the whole element action; the functor retains no
        element conversion of its own.

        A classical source ``t: G_C -> X`` instead supplies the target's classical
        element methods, which read a point of the target's own separator.
        Precomposing ``q`` with the retained comparison ``c_F: G_D -> F(G_C)`` produces
        that point ``p: G_D -> F(X)``.  When ``c_F`` is an identity, ``F(G_C)`` is
        ``G_D`` and ``p`` is ``q``: they then share one identity and one cache entry
        (POL-CAT-066).
        """
        from sage_categories.kernel.construction import (
            GeneralCategoryPointIdentity,
            retained_element_input,
            retained_morphism_input,
        )

        assert isinstance(source.identity, GeneralCategoryPointIdentity)
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

    def _assert_complete_constructor_conversions(self) -> None:
        """Reject selection until the object and morphism conversions are retained (POL-CAT-071).

        The element conversion is derived from the morphism one (POL-FUN-002), so a
        retained morphism conversion already supplies the selected target element role.
        """
        assert self in _object_constructor_conversions, f"{self!r} retains no object constructor conversion"
        assert self in _morphism_constructor_conversions, f"{self!r} retains no morphism constructor conversion"

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


@dataclass(frozen=True, eq=False, slots=True)
class NaturalTransformationData:
    """The local state introduced by the natural-transformation role."""

    assignment: Assignment


class NaturalTransformationDeclaration(MorphismOfCategory):
    """The local ``Fun.MorphismType`` declaration.

    Its domain and codomain are the objects of ``Fun(I, C)`` as supplied (a functor,
    or the morphism of ``C`` it denotes when ``I = [1]``); the functors they denote
    are retained for the components.
    """

    def __init__(self, data: NaturalTransformationData) -> None:
        self._assignment = data.assignment
        self._components: MonoDict = MonoDict()
        super().__init__()

    def source_functor(self) -> Functor:
        return diagram_of(self.domain())

    def target_functor(self) -> Functor:
        return diagram_of(self.codomain())

    def component(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        """``eta_X: F(X) -> G(X)``, one morphism per object; naturality is a trusted declaration (POL-MATH-036).

        A natural transformation has one component at each object, so the assignment runs
        once per object and its value is retained by identity (POL-CAT-012).  This is what
        makes the projections of a chosen product and the injections of a chosen coproduct
        one morphism each: they are the components of the limiting cone and cocone.
        """
        if member_object in self._components:
            return self._components[member_object]
        source, target = self.source_functor(), self.target_functor()
        component = self._assignment(member_object)
        assert component in source.codomain().morphism_category(1)(source.on_object(member_object), target.on_object(member_object))
        self._components[member_object] = component
        return component

    def __repr__(self) -> str:
        return f"NaturalTransformation({self.domain()!r} => {self.codomain()!r})"


Functor = FunctorDeclaration
NaturalTransformation = NaturalTransformationDeclaration

_category.bootstrap()
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

    def Isofibrations(self) -> Category:
        return self.property_subcategory(self.ambient().Isofibrations())

    def Monomorphisms(self) -> Category:
        return self.property_subcategory(self.ambient().Monomorphisms())


class FunctorProperty(FunctorProperties, FixedEndpointProperty[[OnObject, OnMorphism], [Assignment]]):
    """``Fun(C, D).P()``: functors ``C -> D`` with property ``P``; constructs one and owns ``identity()``."""

    def __call__(self, *args: OnObject | OnMorphism, **kwargs: OnObject | OnMorphism) -> Functor:
        """``Fun(S, T).P()(on_object, on_morphism)``, or ``Fun(S, T).P()()`` for the subcategory monomorphism.

        With no data the constructed functor is the identity on the values ``S`` and ``T``
        share, which is a functor exactly when ``S`` is a subcategory of ``T``.  That is
        the declaration ``POL-FUN-036`` names: the leaf states the relation by
        constructing in ``Fun(S, T).Monomorphisms().Isofibrations()``, and the kernel
        trusts it (``specs/functor.md``, "Monomorphisms of Cat() and placement").
        """
        if args or kwargs:
            return super().__call__(*args, **kwargs)
        functors = self.universe().morphism_category(1)
        roots = self.narrowing_roots()
        assert any(root is functors.Monomorphisms() for root in roots), (
            f"{self!r} takes a functor's object and morphism actions; only a monomorphism of Cat() is "
            f"determined by its endpoints, as the identity on their shared values"
        )
        source, target = self._ambient.domain(), self._ambient.codomain()
        if any(root is functors.Full() for root in roots):
            functor = functors.full_subcategory_monomorphism(source, target)
        else:
            functor = functors.subcategory_monomorphism(source, target)
        refine(functor, self)
        return functor


# ``denotes_diagram(x, Fun(I, C))``: ``x`` is a functor ``I -> C``, or a point of ``C`` at
# domain ``I`` (specs/functor.md, "Slices and coslices": an object of ``C`` is a point with domain ``1`` and a morphism a point with
# domain ``[1]``), whose defining functor is such a diagram.  Thus the objects of
# ``Fun(1, C)`` are the objects of ``C`` and the objects of ``Fun([1], C)`` are the
# morphisms of ``C`` (specs/functor.md, "The Mor(n, C) tower", specs/functor.md, "Canonical objects of Cat"): one value, denoting its retained defining functor.
denotes_diagram: Predicate = Predicate("denotes_diagram", 2, False)


def _denotes_diagram_by_domain(candidate: CategoryPoint, functors: FunctorCategory) -> Decision:
    if is_placed(candidate, functors.ambient()):
        return ask(endpoints(candidate, functors.domain(), functors.codomain()))
    if role_of(candidate) in (Role.OBJECT, Role.MORPHISM):
        # The domain is one of the canonical shapes, compared by identity; the parent is a
        # placement, so the question there is containment in the codomain, not identity
        # (POL-CAT-068, POL-FUN-027): a set refined into ``Sets().Finite()`` is still a
        # diagram of shape ``1`` in ``Sets()``.
        return candidate.defining_morphism().domain() is functors.domain() and is_subcategory(candidate.parent(), functors.codomain())
    return False


denotes_diagram.register_handler(_denotes_diagram_by_domain)

# ``denotes_functor(x, Fun)``: ``x`` is a functor by placement, or a point of a category
# with a category as domain, which denotes its defining functor (specs/functor.md, "Slices and coslices").
denotes_functor: Predicate = Predicate("denotes_functor", 2, False)


def _denotes_functor_by_domain(candidate: CategoryPoint, functors: FunctorsCategory) -> Decision:
    if is_placed(candidate, functors):
        return True
    return role_of(candidate) in (Role.OBJECT, Role.MORPHISM) and candidate.defining_morphism().domain() in Cat()


denotes_functor.register_handler(_denotes_functor_by_domain)


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

    def __init__(self, morphisms: MorphismCategory, domain: Category, codomain: Category) -> None:
        self._evaluations: MonoDict = MonoDict()
        self._constants: MonoDict = MonoDict()
        self._constant_values: MonoDict = MonoDict()
        self._finite_data: MonoDict = MonoDict()
        super().__init__(morphisms, domain, codomain)

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return denotes_diagram(candidate, self)

    def diagram(self, value: CategoryPoint) -> Functor:
        """The functor ``I -> C`` that a value of this category denotes: itself, or the defining functor of a point of ``C`` with domain ``I``."""
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

    def object_at(self, point: SetElement) -> MorphismOfCategory:
        assert self.domain() is Cat().Simplex(1), f"{self!r} declares no set of objects"
        return self.codomain().morphism_at(point)

    def morphism_set(self) -> SetObject | UnknownClass:
        """For ``I = [1]``: the finite set of commuting squares, when ``C`` chooses a finite set of morphisms."""
        from sage_categories.cat.diagrams import square_set

        if self.domain() is not Cat().Simplex(1) or self.codomain().morphism_set() is Unknown:
            return Unknown
        return square_set(self)

    def morphism_at(self, point: SetElement) -> NaturalTransformation:
        from sage_categories.cat.diagrams import square_at

        return square_at(self, point)

    # -- functor properties (POL-FUN-024) -----------------------------------------------

    def narrowing_type(self) -> type[FunctorProperty]:
        return FunctorProperty

    def __repr__(self) -> str:
        return f"Fun({self.domain()!r}, {self.codomain()!r})"


class FunctorsCategory(MorphismCategory[[OnObject, OnMorphism], [Assignment]]):
    """``Fun = Mor(Cat())``."""

    def __init__(self, base: CategoryOfCategories) -> None:
        self._bootstrapping = False
        self._bootstrapped = False
        # The one identity-on-values functor per ``(source, target)``, constructed once
        # and retained by identity (POL-FUN-027).  It is the kernel's own witness that
        # ``source`` is a subcategory of ``target``; the declaration a leaf makes is
        # placement in ``Fun(S, T).Monomorphisms().Isofibrations()``, and that placement,
        # not this table, is what placement follows (POL-FUN-036).
        self._shared_value_functors: TripleDict = TripleDict(weak_values=False)
        self._pending: list[tuple[Functor, bool]] = []
        self._declaring: MonoDict = MonoDict()
        super().__init__(base)

    def fixed_endpoint_type(self) -> type[FunctorCategory]:
        return FunctorCategory

    def __call__(self, shape: ObjectOfCategory, target: ObjectOfCategory | Functor) -> FunctorCategory | Functor:
        """``Fun(I, D)`` is the functor category; ``Fun(I, F)`` for a functor ``F: D -> E`` is ``(-) ** I`` applied to it.

        The exponential ``D ** I = Fun(I, D)`` is a functor in ``D``, so the second
        argument selects the action: a category selects the fixed-endpoint category, a
        morphism of ``Cat()`` the morphism action ``Fun(I, D) -> Fun(I, E)``
        (``Cat().exponential_on_morphism``).
        """
        if is_placed(target, self):
            return self.base_category().exponential_on_morphism(shape, target)
        return super().__call__(shape, target)

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
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

    # -- the functor property categories (POL-FUN-024) -----------------------------------

    def _bootstrap(self) -> None:
        """Build the functor property categories once and place the kernel's own subcategory monomorphisms.

        Those are constructed while the properties do not yet exist, so they are placed
        afterwards, in the property category a full subcategory declares.
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
        # A subcategory of ``T`` is a subobject of ``T`` in ``Cat()``, and the two
        # conditions on the monomorphism that presents it are monicity and repleteness of
        # the image, which is exactly the isofibration condition (Kerodon, Example
        # 4.4.1.12, https://kerodon.net/tag/01EX, inspected 2026-08-28; nLab, replete
        # subcategory, inspected 2026-08-28).  Placement follows a functor with both, and
        # no other (POL-FUN-036; ``specs/functor.md``, "Monomorphisms of Cat() and placement").
        self._isofibrations = PropertySubcategory(self, "Isofibrations", {}, ())
        # A monomorphism of ``Cat()`` is faithful and injective on objects, so
        # faithfulness is a recorded implication (nLab, subcategory,
        # https://ncatlab.org/nlab/show/subcategory, inspected 2026-08-28: "A functor is
        # easily verified to be monic iff it is faithful and injective on objects").
        self._monomorphisms = PropertySubcategory(self, "Monomorphisms", {}, (self._faithful,))
        partial = self._monomorphisms.property_subcategory(self._isofibrations)
        declared = {False: partial, True: partial.property_subcategory(self._full)}
        self._bootstrapped = True
        # Placing a deferred functor can construct a further narrowing of ``Fun``, whose
        # own subcategory monomorphisms defer in turn, so the queue is drained until it
        # stays empty.  There are finitely many narrowings, so it does.
        while self._pending:
            batch, self._pending = self._pending, []
            for functor, full in batch:
                refine(functor, declared[full])
        self._bootstrapping = False
        self._isofibrations.predicate().register_handler(self._is_shared_value_functor)
        self._monomorphisms.predicate().register_handler(self._is_shared_value_functor)

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

    def Isofibrations(self) -> Category:
        if not self._bootstrapped:
            self._bootstrap()
        return self._isofibrations

    def Monomorphisms(self) -> Category:
        """Monic functors: faithful and injective on objects, so ``Faithful`` is a recorded implication."""
        if not self._bootstrapped:
            self._bootstrap()
        return self._monomorphisms

    # -- subcategory monomorphisms (POL-FUN-027, POL-FUN-036) -----------------------------
    #
    # A leaf declares that ``S`` is a subcategory of ``T`` by constructing in
    # ``Fun(S, T).Monomorphisms().Isofibrations()`` (``FunctorProperty.__call__``).  The
    # kernel's own subcategories are built while those property categories do not yet
    # exist, so they route through the two methods below, which construct the same one
    # identity-on-values functor and place it once ``_bootstrap`` has run.

    def _shared_value_functor(self, source: Category, target: Category, full: bool) -> Functor:
        """The one identity-on-values functor ``source -> target``, placed in the declared property.

        While ``_bootstrap`` runs, the property category to place it in does not exist yet
        (or is itself under construction), so the placement is queued and ``_bootstrap``
        drains the queue.
        """
        if not self._bootstrapped and not self._bootstrapping:
            self._bootstrap()
        key = (source, target, self)
        if key not in self._shared_value_functors:
            self._shared_value_functors[key] = self._base.construct_morphism(source, target, identity_on_values, identity_on_values)
            self._shared_value_functors[key]._retain_identity_constructor_conversions()
        functor = self._shared_value_functors[key]
        if self._bootstrapping:
            self._pending.append((functor, full))
        else:
            refine(functor, self._declared_subcategory(full))
        return functor

    def _is_shared_value_functor(self, functor: Functor) -> Decision:
        """The exact route for a functor the kernel itself built: it shares the values of its endpoints.

        Such a functor is injective on objects and on morphisms, hence monic
        (nLab, subcategory, https://ncatlab.org/nlab/show/subcategory, inspected
        2026-08-28: "A functor is easily verified to be monic iff it is faithful and
        injective on objects"), and its image is everything the source has, so an
        isomorphism of the target with one endpoint in the source is one of the source.
        A functor the kernel did not build decides nothing here: the leaf declares it.
        """
        key = (functor.domain(), functor.codomain(), self)
        if key in self._shared_value_functors and self._shared_value_functors[key] is functor:
            return True
        return Unknown

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


Fun: FunctorsCategory = Cat().morphism_category(1)
NaturalTransformation = Fun.MorphismType
_category.NaturalTransformation = NaturalTransformation
Cat().equality().register_handler(_defining_functor_equal)
