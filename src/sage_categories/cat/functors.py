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
from typing import Any

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat import category as _category
from sage_categories.cat.category import Assignment, Category, CategoryOfCategories, OnMorphism, OnObject
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed, is_subcategory, refine
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of

__all__ = ["Fun", "Functor", "FunctorCategory", "FunctorProperty", "FunctorsCategory", "NaturalTransformation"]


def identity_on_values(value: CategoryPoint) -> CategoryPoint:
    """The object and morphism action of every subcategory monomorphism: the identity on the shared values (POL-FUN-027)."""
    return value


def diagram_of(value: CategoryPoint) -> Functor:
    """The functor that a value of ``Fun(I, C)`` denotes (specs/functor.md, "The Mor(n, C) tower", specs/functor.md, "Slices and coslices").

    A functor denotes itself.  An object of ``C`` is a point ``* -> C`` and denotes that
    point.  A morphism of ``C`` is an object of ``Mor(C)``, so the point it retains is
    ``* -> Mor(C)``; the diagram it denotes in ``C`` is the arrow functor ``[1] -> C``,
    which is how the objects of ``Fun([1], C)`` are the morphisms of ``C``.
    """
    if is_placed(value, Fun):
        return value
    if role_of(value) is Role.MORPHISM:
        return value.base_category().arrow_functor(value)
    return value.defining_morphism()


def _defining_functor_equal(first: CategoryPoint, candidate: Any) -> Decision:
    """A functor ``I -> C`` equals a value of ``Fun(I, C)`` when it is the diagram that value denotes.

    The retained diagram is the exact positive route, and ``diagram_of`` is its one owner:
    the point ``* -> C`` of an object, the arrow functor ``[1] -> C`` of a morphism.
    Another functor ``I -> C`` selects some value, and whether that value equals this one
    is the question ``Cat()`` has no further exact route for, so it stays ``Unknown``.
    """
    if is_placed(first, Fun) and not is_placed(candidate, Fun) and role_of(candidate) in (Role.OBJECT, Role.MORPHISM):
        return True if first is diagram_of(candidate) else Unknown
    if is_placed(candidate, Fun) and not is_placed(first, Fun) and role_of(first) in (Role.OBJECT, Role.MORPHISM):
        return True if candidate is diagram_of(first) else Unknown
    return Unknown


@dataclass(frozen=True, eq=False, slots=True)
class NaturalTransformationData:
    """The local state introduced by the natural-transformation role."""

    assignment: Assignment


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


# ``denotes_diagram(x, Fun(I, C))``: ``x`` is a functor ``I -> C``, or a value that denotes
# one.  The objects of ``Fun(1, K)`` are the objects of ``K``, each a point ``* -> K``, and
# the objects of ``Fun([1], C)`` are the morphisms of ``C``, each an object of ``Mor(C)``
# (specs/functor.md, "The Mor(n, C) tower", specs/functor.md, "Canonical objects of Cat"): one value, denoting one diagram.
denotes_diagram: Predicate = Predicate("denotes_diagram", 2, False)


def _denotes_diagram_by_domain(candidate: CategoryPoint, functors: FunctorCategory) -> Decision:
    if is_placed(candidate, functors.ambient()):
        return ask(endpoints(candidate, functors.domain(), functors.codomain()))
    if role_of(candidate) is Role.MORPHISM and functors.domain() is Cat().Simplex(1):
        # A morphism of ``C`` is an object of ``Mor(C)``, and the diagram it denotes is its
        # arrow functor ``[1] -> C``: this is how the objects of ``Fun([1], C)`` are the
        # morphisms of ``C``.
        return is_subcategory(candidate.base_category(), functors.codomain())
    if role_of(candidate) in (Role.OBJECT, Role.MORPHISM):
        # Every object of a category ``K`` is a point ``* -> K``.  The parent is a
        # placement, so the question there is containment in the codomain, not identity
        # (POL-CAT-068, POL-FUN-027): a set refined into ``Sets().Finite()`` is still a
        # diagram of shape ``1`` in ``Sets()``.
        return functors.domain() is Cat().Terminal() and is_subcategory(candidate.parent(), functors.codomain())
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
        """The functor ``I -> C`` that a value of this category denotes: its point for ``I = *``, else ``diagram_of``."""
        if is_placed(value, self.ambient()):
            return value
        assert value in self, f"{value!r} is not a diagram of shape {self.domain()!r} in {self.codomain()!r}"
        if self.domain() is Cat().Terminal():
            return value.defining_morphism()
        return diagram_of(value)

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

    def object_set(self) -> ObjectOfCategory:
        """For ``I = [1]``: the morphism set of ``C``, since the objects are the morphisms of ``C``."""
        assert self.domain() is Cat().Simplex(1), f"{self!r} declares no set of objects"
        morphisms = self.codomain().morphism_set()
        assert morphisms is not Unknown, f"{self.codomain()!r} chooses no finite set of morphisms"
        return morphisms

    def object_at(self, point: ElementOfObject) -> MorphismOfCategory:
        assert self.domain() is Cat().Simplex(1), f"{self!r} declares no set of objects"
        return self.codomain().morphism_at(point)

    def morphism_set(self) -> ObjectOfCategory | UnknownClass:
        """For ``I = [1]``: the finite set of commuting squares, when ``C`` chooses a finite set of morphisms."""
        from sage_categories.cat.diagrams import square_set

        if self.domain() is not Cat().Simplex(1) or self.codomain().morphism_set() is Unknown:
            return Unknown
        return square_set(self)

    def morphism_at(self, point: ElementOfObject) -> NaturalTransformation:
        from sage_categories.cat.diagrams import square_at

        return square_at(self, point)

    # -- functor properties (POL-FUN-024) -----------------------------------------------

    def narrowing_type(self) -> type[FunctorProperty]:
        return FunctorProperty

    def __repr__(self) -> str:
        return f"Fun({self.domain()!r}, {self.codomain()!r})"


class FunctorsCategory(MorphismCategory[[OnObject, OnMorphism], [Assignment]]):
    """``Fun = Mor(Cat())``."""

    class MorphismType(MorphismOfCategory):
        """A natural transformation: the 2-morphisms of ``Cat()``.

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
        self._full = PropertySubcategory(self, "Full", ())
        self._faithful = PropertySubcategory(self, "Faithful", ())
        self._essentially_surjective = PropertySubcategory(self, "EssentiallySurjective", ())
        # FullyFaithful is a full subcategory of Full and of Faithful; Equivalences of
        # FullyFaithful and of EssentiallySurjective (Mathlib ``Functor.FullyFaithful.full``,
        # ``Functor.FullyFaithful.faithful``, ``Functor.IsEquivalence``; inspected 2026-08-26).
        self._fully_faithful = PropertySubcategory(self, "FullyFaithful", (self._full, self._faithful))
        self._equivalences = PropertySubcategory(self, "Equivalences", (self._fully_faithful, self._essentially_surjective))
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
        self._monomorphisms = PropertySubcategory(self, "Monomorphisms", (self._faithful,))
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
        """Monic functors: faithful and injective on objects, so this is a full subcategory of ``Faithful()``."""
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
_category.Fun = Fun
_category.NaturalTransformation = NaturalTransformation
Cat().equality().register_handler(_defining_functor_equal)
