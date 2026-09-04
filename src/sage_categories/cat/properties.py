"""Full subcategories and property subcategories (POL-CAT-054, POL-CAT-087, POL-FUN-024).

A full subcategory ``S`` of ``T`` shares ``T``'s object, element, and morphism
values; its morphism categories, identities, and composition are inherited
definitionally from ``T`` (Mathlib ``CategoryTheory.ObjectProperty.FullSubcategory``
and the functor ``ObjectProperty.ι`` it carries, full and faithful; inspected
2026-08-26).  Its one selected structural functor is the identity-on-values
monomorphism ``Fun(S, T).Monomorphisms().Isofibrations().Full()()``.

A property subcategory ``C.P()`` is the full subcategory on the objects satisfying
a predicate ``P``.  ``C`` declares it once, as an ``Axiom`` in the body of its class,
and a separate class implements the generated subcategory by naming the declaring
category class and the axiom (POL-LEAF-059).  Its constructor is the trusted boundary of that property
(POL-CAT-038/069): it wires none of its own, carries exactly the constructors of ``C``
along the inclusion ``C.P() -> C``, and narrows what they build into ``C.P()`` (D150,
D175).  A value already constructed is placed by ``assume(X.is_P())``.
``C.P()`` is a full subcategory of ``C.Q()`` whenever the mathematics says so, and that
containment is the statement: it is recorded as the subcategory monomorphism
``C.P() -> C.Q()``, and nothing induces it from a relation between the two predicates
(D83).  ``Mor(C).Isomorphisms()`` is a full subcategory of ``Mor(C).Monomorphisms()`` and
of ``Mor(C).Epimorphisms()`` at once
(``specs/functor.md``, "Monomorphisms of ``Cat()`` and placement").  A descendant ``D`` with a selected
subcategory monomorphism into ``C`` derives ``D.P()`` as the narrowing of ``C.P()`` to ``D``
(POL-CAT-084): a full subcategory of both, with the same predicate.

The axiom makes the subcategory available; a class that also computes membership
inherits ``PredicateSubcategory`` and states that computation as ``_predicate``.  Neither
mechanism needs the other (D97).
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from types import ModuleType
from typing import TYPE_CHECKING, ClassVar

from sage_categories.cat.category import Category
from sage_categories.cat.predicates import Decision
from sage_categories.cat.predicates import Axiom, Predicate, Proposition, ask, property_predicate, register_handler
from sage_categories.kernel.predicates import axiom_layer as _axiom_layer
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.sage_runtime import TripleDict, cached_method

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.functors import Functor, FunctorsCategory
    from sage_categories.cat.morphisms import MorphismCategory

__all__ = [
    "FixedEndpointProperty",
    "FullSubcategory",
    "InverseImageSubcategory",
    "inverse_image",
    "retain_inverse_image",
    "NarrowedProperty",
    "PredicateSubcategory",
    "PropertySubcategory",
]


def _functors() -> FunctorsCategory:
    from sage_categories.cat.functors import Fun

    return Fun


def _morphisms() -> ModuleType:
    from sage_categories.cat import morphisms

    return morphisms


class FullSubcategory[**MorphismData, **TwoMorphismData](Category[MorphismData, TwoMorphismData]):
    """A full subcategory of an ambient category, declared by its monomorphism into the ambient.

    Its morphisms, identities, and composites are those of the ambient between its
    objects; ``Category`` supplies them from the ambient (POL-CAT-087).

    Every full subcategory of ``C`` is a root of the narrowings of ``C``: two of
    them, a property subcategory and a construction family (a chosen subset that
    is a chosen limit; a finite set that is a chosen product), meet in the
    narrowing of ``C`` by both (POL-CAT-084, POL-KERNEL-013).  Membership in a
    construction family is placement by construction; only a property
    subcategory owns a predicate.
    """

    class ObjectType:
        """An object of the ambient that this subcategory contains: the same value, and the ambient's whole surface.

        The monomorphism is identity on values, so a full subcategory introduces no
        object of its own and no operation on one.  A subcategory whose property makes a
        new operation available writes it here, as ``Mor(C).Isomorphisms()`` writes
        ``inverse()`` (POL-CAT-079).
        """

    class ElementType:
        """A point ``1_C -> X`` of an object of this subcategory: the point the ambient owns (POL-CAT-087).

        A point belongs to its parent, and only objects and morphisms are placed
        (``kernel/refinement.py``, ``refine``), so a full subcategory never builds a point
        of its own: ``element_from_defining_morphism`` returns the ambient's.  This class
        is therefore reached as a base, by a descendant that is not itself a full
        subcategory -- a concrete implementation of a property subcategory writing its own
        points.  A method written here runs on those and on nothing else.
        """

    class MorphismType:
        """A morphism of the ambient between two of these objects.

        Fullness is exactly this: the hom of the subcategory is the hom of the ambient
        (Mathlib ``CategoryTheory.ObjectProperty.FullSubcategory``, whose ``Hom`` is the
        ambient's), so identities and composites are the ambient's and nothing new is
        stated here.
        """

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData]) -> None:
        self._ambient = ambient
        super().__init__()

    def has_ambient(self) -> bool:
        return True

    def ambient(self) -> Category[MorphismData, TwoMorphismData]:
        """The ambient is construction data: this category declares exactly one subcategory monomorphism."""
        return self._ambient

    def narrowing_base(self) -> Category:
        return self._ambient.narrowing_base()

    def narrowing_roots(self) -> tuple[Category, ...]:
        return (*self._ambient.narrowing_roots(), self)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (_functors().full_subcategory_monomorphism(self, self._ambient),)

    def element_from_defining_morphism(
        self,
        defining_morphism: MorphismCategory.ObjectType,
    ) -> CategoryOfCategories.ElementType:
        """The elements of a full subcategory are those of its ambient on the shared values (POL-CAT-087)."""
        return self._ambient.element_from_defining_morphism(defining_morphism)

    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        return self._ambient.limit_construction(shape)

    def colimit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        return self._ambient.colimit_construction(shape)


_inverse_images: TripleDict = TripleDict(weak_values=False)


class InverseImageSubcategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):
    """``F.inverse_image(P)``: the full same-value subcategory ``D ×_C P``.

    The source projection is the subcategory monomorphism into ``D``.  The second
    projection is the restriction of ``F`` to ``P``.  The category is retained as the
    chosen pullback in ``Cat().Pullbacks()``; its values are nevertheless the values of
    ``D`` itself, so positive evidence uses the ordinary same-object refinement path.
    """

    class ObjectType:
        """An object ``X`` of ``D`` whose image ``F(X)`` lies in ``P``."""

    class ElementType:
        """A generalized element inherited from the source category."""

    class MorphismType:
        """A source morphism between objects of the inverse-image subcategory."""

    def __init__(self, functor: Functor, target_subcategory: Category) -> None:
        self._functor = functor
        self._target_subcategory = target_subcategory
        self._target_projection: Functor | None = None
        super().__init__(functor.domain())

    def defining_functor(self) -> Functor:
        return self._functor

    def target_subcategory(self) -> Category:
        return self._target_subcategory

    def subcategory_monomorphism(self) -> Functor:
        return _functors().full_subcategory_monomorphism(self, self._ambient)

    def target_projection(self) -> Functor:
        """The restriction of ``F`` to ``P``, the second projection of the retained pullback.

        It is the pullback of ``F`` along ``P -> C``.  Monomorphisms of ``Cat`` and
        isofibrations are each stable under pullback (nLab, "canonical model structure on
        Cat", https://ncatlab.org/nlab/show/canonical+model+structure+on+Cat, inspected
        2026-09-02), so when ``F`` is declared a subcategory monomorphism this projection
        is one too, and placement traces through the square (POL-FUN-036).
        """
        if self._target_projection is None:
            target = self._target_subcategory
            defining = self._functor

            def on_object(value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
                return target(defining.on_object(value))

            def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
                image = defining.on_morphism(morphism)
                refine(image, target.morphism_category(1))
                return image

            projections = _functors()(self, target)
            if _functors().declares_subcategory(defining):
                projections = projections.Monomorphisms().Isofibrations()
            self._target_projection = projections(on_object, on_morphism)
        return self._target_projection

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.subcategory_monomorphism(), self.target_projection())

    @cached_method(key=lambda self, candidate: (id(candidate), candidate))
    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return self._ambient.membership_proposition(candidate) & self._target_subcategory.membership_proposition(
            self._functor.on_object(candidate)
        )

    def __call__[Datum](self, *construction_data: Datum, **keywords: Datum) -> CategoryOfCategories.ElementType:
        """``F.inverse_image(P)(data)``: ``D``'s constructor, with the result narrowed into the pullback.

        The source projection is identity on the values of ``D``, so this subcategory
        wires no constructor of its own: it has exactly the constructors of ``D``
        (D150, ``POL-CAT-038``).  Construction here asserts that the image lies in ``P``,
        which is what makes the constructed value an object of the pullback.  A value
        already constructed is placed by ``assume(X.is_P())``, never fed back to a
        constructor (D150, ``POL-ONT-002``).
        """
        constructed = self._ambient(*construction_data, **keywords)
        refine(self._functor.on_object(constructed), self._target_subcategory)
        refine(constructed, self)
        return constructed

    def __repr__(self) -> str:
        return f"{self._functor!r}.inverse_image({self._target_subcategory!r})"


def inverse_image(functor: Functor, target_subcategory: Category) -> Category:
    """Construct and retain ``D ×_C P`` for ``F: D -> C`` and ``P -> C``.

    This is a chosen pullback in ``Cat`` whose source projection is identity on the
    values of ``D``.  The mediator is therefore the first leg of any candidate cone,
    refined into the inverse-image subcategory.

    Along a declared subcategory monomorphism ``D -> C`` the pullback is the narrowing
    of ``D`` by ``P`` (POL-CAT-084): one category, the placement the kernel joins with,
    whose monomorphisms into ``D`` and into ``P`` are the two projections.
    """
    from sage_categories.cat.functors import Cat

    key = (functor, target_subcategory, Cat())
    if key in _inverse_images:
        return _inverse_images[key]

    if _functors().declares_subcategory(functor):
        narrowing = functor.domain().property_subcategory(target_subcategory)
        functors = _functors()
        retain_inverse_image(
            functor,
            target_subcategory,
            narrowing,
            functors.full_subcategory_monomorphism(narrowing, functor.domain()),
            functors.full_subcategory_monomorphism(narrowing, target_subcategory),
        )
        return narrowing

    result = InverseImageSubcategory(functor, target_subcategory)
    retain_inverse_image(
        functor,
        target_subcategory,
        result,
        result.subcategory_monomorphism(),
        result.target_projection(),
    )
    return result


def _declared_inclusion(subcategory: Category, ambient: Category) -> Functor:
    """The monomorphism ``P -> C`` that ``P`` declares, the second leg of the cospan of ``D ×_C P``.

    A property category is a subcategory of several categories at once, and each
    containment is its own declared monomorphism (D83), so the leg is the declaration
    whose target is this pullback's ``C``: ``Left.P()`` includes into the category that
    declares ``P`` and into ``Left``, and the pullback along ``D -> Left`` is taken over
    the second.  Reading the leg off the declaration rather than off the ambient chain is
    what lets one ``D.P()`` be the pullback along each of several structure functors
    (D159, ``POL-LEAF-081``).
    """
    declared = next(
        (
            functor
            for functor in subcategory.selected_functors()
            if functor.codomain() is ambient and _functors().declares_subcategory(functor)
        ),
        None,
    )
    assert declared is not None, f"{subcategory!r} declares no subcategory monomorphism into {ambient!r}"
    return declared


def retain_inverse_image(
    functor: Functor,
    target_subcategory: Category,
    realization: Category,
    source_projection: Functor,
    target_projection: Functor,
) -> None:
    """Retain ``realization`` as the chosen pullback ``D ×_C P`` for ``F: D -> C`` and ``P -> C``.

    A leaf that declares an inherited property category calls this with its canonical
    value, so the leaf constructor and ``F.inverse_image(P)`` return one retained
    category (``specs/functor.md``, "Inverse-image subcategories";
    ``specs/ordered-sets.md``).
    """
    from sage_categories.cat.diagrams import cospan_diagram
    from sage_categories.cat.constructions import cone, cone_apex
    from sage_categories.cat.functors import Cat, Fun

    key = (functor, target_subcategory, Cat())
    assert key not in _inverse_images, (
        f"an inverse image of {target_subcategory!r} along {functor!r} is already retained"
    )
    _inverse_images[key] = realization
    diagram = cospan_diagram(Cat(), functor, _declared_inclusion(target_subcategory, functor.codomain()))
    shape = diagram.domain()
    projections = {0: source_projection, 1: target_projection}
    limiting_cone = cone(diagram, realization, lambda vertex: projections[shape.label(vertex)])

    def mediator(candidate_cone):
        source = cone_apex(candidate_cone)
        to_source = candidate_cone.component(shape(0))

        def on_object(value):
            image = to_source.on_object(value)
            refine(image, realization)
            return image

        def on_morphism(morphism):
            image = to_source.on_morphism(morphism)
            refine(image, realization.morphism_category(1))
            return image

        return Fun(source, realization)(on_object, on_morphism)

    pullbacks = Cat().Pullbacks()
    pullbacks.with_universal_data(diagram, realization, limiting_cone, mediator)
    pullbacks._apply_pullback_comparisons_at(diagram)
    containments = (
        *target_subcategory.selected_functors(),
        *pullbacks._pullback_comparisons_from(target_subcategory),
    )
    for containment in containments:
        if not _functors().declares_subcategory(containment):
            continue
        if containment.codomain() is functor.codomain():
            continue
        target_key = (functor, containment.codomain(), Cat())
        target_inclusion = next(
            (
                candidate
                for candidate in containment.codomain().selected_functors()
                if candidate.codomain() is functor.codomain() and _functors().declares_subcategory(candidate)
            ),
            None,
        )
        if target_inclusion is None:
            continue
        target_diagram = cospan_diagram(
            Cat(),
            functor,
            target_inclusion,
        )
        if target_key in _inverse_images:
            assert pullbacks.has_construction(target_diagram)
            assert pullbacks.chosen_object(target_diagram) is _inverse_images[target_key]
        pullbacks._retain_pullback_comparison(diagram, target_diagram, containment)


class PropertySubcategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):
    """``C.P()``: the full subcategory of ``C`` on the objects satisfying ``P``.

    A subclass implements one generated property subcategory by naming the declaring
    category class and the axiom in ``_base_category_class_and_axiom``, and declares its
    own ``ObjectType``, ``ElementType``, and ``MorphismType`` like any other category
    (``Axiom``, POL-LEAF-059).  The kernel reads those declarations through the ordinary
    ``Category.local_role_class``, which is the class of this value.
    """

    class ObjectType:
        """An object of the ambient satisfying the property: the same value, refined in place.

        A property subcategory adds no object of its own -- its constructor refines the
        value the ambient already owns -- so this body is empty, and a subclass whose
        property makes an operation available writes it in its own class, as
        ``IsomorphismsCategory`` does for ``inverse()``.
        """

    class ElementType:
        """A point ``1_C -> X`` of such an object: the point the ambient owns."""

    class MorphismType:
        """A morphism of the ambient between two of these objects; fullness makes it the ambient's."""

    _base_category_class_and_axiom: ClassVar[tuple[type[Category], str]]

    def __init_subclass__(cls) -> None:
        """Record this class on the axiom it names: the declaration is the one place the link lives."""
        super().__init_subclass__()
        connection = cls.__dict__.get("_base_category_class_and_axiom")
        if connection is None:
            return
        declaring_class, name = connection
        assert hasattr(declaring_class, name), f"{declaring_class.__name__}.{name} does not exist"
        axiom = getattr(declaring_class, name)
        assert isinstance(axiom, Axiom), f"{declaring_class.__name__}.{name} is not an axiom, so {cls.__name__} cannot implement it"
        axiom.implemented_by(cls)

    def __init__(
        self,
        ambient: Category[MorphismData, TwoMorphismData],
        name: str,
        full_subcategory_of: tuple[Category, ...],
    ) -> None:
        self._name = name
        self._full_subcategory_of = full_subcategory_of
        self._property_predicate = property_predicate(name, self)
        super().__init__(ambient)

    def name(self) -> str:
        return self._name

    def predicate(self) -> Predicate:
        return self._property_predicate

    def full_subcategory_of(self) -> tuple[Category, ...]:
        """The categories this one is a full subcategory of, beyond its ambient (D83)."""
        return self._full_subcategory_of

    def intersection(
        self,
        other: PropertySubcategory[MorphismData, TwoMorphismData]
        | tuple[Category[MorphismData, TwoMorphismData], ...],
    ) -> Category[MorphismData, TwoMorphismData]:
        """``self.intersection(other)`` as the retained pullback over the common ambient."""
        if isinstance(other, tuple):
            return super().intersection(other)
        from sage_categories.cat.constructions import cone, cone_apex
        from sage_categories.cat.diagrams import cospan_diagram
        from sage_categories.cat.functors import Cat, Fun

        ambient = self.narrowing_base()
        assert other.narrowing_base() is ambient, f"{self!r} and {other!r} do not have a common narrowing base"
        result = ambient.intersection((self, other))
        diagram = cospan_diagram(Cat(), self.subcategory_monomorphism(), other.subcategory_monomorphism())
        shape = diagram.domain()
        projections = {
            0: Fun.full_subcategory_monomorphism(result, self),
            1: Fun.full_subcategory_monomorphism(result, other),
        }
        limiting_cone = cone(diagram, result, lambda vertex: projections[shape.label(vertex)])

        def mediator(candidate_cone):
            source = cone_apex(candidate_cone)
            to_self = candidate_cone.component(shape(0))

            def on_object(value):
                return result(to_self.on_object(value))

            def on_morphism(morphism):
                image = to_self.on_morphism(morphism)
                refine(image, result.morphism_category(1))
                return image

            return Fun(source, result)(on_object, on_morphism)

        pullbacks = Cat().Pullbacks()
        if pullbacks.has_construction(diagram):
            assert pullbacks.chosen_object(diagram) is result
            return result
        pullbacks.with_universal_data(diagram, result, limiting_cone, mediator)
        return result

    def structure_functors(self) -> tuple[Functor, ...]:
        """The inclusion ``C.P() -> C``, then one per further recorded containment (POL-FUN-024).

        ``cat_kernel`` builds them: an axiom's property subcategory and its inclusion are
        the one construction, and generating either needs both the declaration and the
        kernel's reading of it (D148, D150, D175, ``POL-CAT-038``).
        """
        return _axiom_layer().subcategory_inclusions(self)

    @cached_method(key=lambda self, candidate: (id(candidate), candidate))
    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        """Membership in the ambient and the property's own predicate.

        ``x in C.P()`` and ``ask(x.is_P())`` are one question asked twice
        (``specs/property-refinement.md``, "Category membership is proposition-backed
        Boolean admission").  Placement is a positive evaluation case inside that one
        question -- a value that entered through the constructor already satisfies the
        predicate, so ``ask`` answers ``True`` from placement without recomputing -- and
        it is never the definition of membership.  A value that never entered still gets
        the defining predicate evaluated, and an undecided answer fails loudly at
        ``__contains__`` rather than being reported as non-membership.
        """
        return self._ambient.membership_proposition(candidate) & self._property_predicate(candidate)

    def __call__[Datum](
        self,
        *construction_data: Datum,
        **keywords: Datum,
    ) -> CategoryOfCategories.ElementType | Category[MorphismData, TwoMorphismData]:
        """``C.P()(data)``: ``C``'s constructor, with the result narrowed into ``C.P()``.

        ``C.P()`` wires no constructor of its own.  It has exactly the constructors of
        ``C``, carried along the inclusion ``C.P() -> C`` that ``cat_kernel`` builds, and
        construction here asserts the property (D21, D150, D175, ``POL-CAT-038``).  A
        value already constructed is placed by ``assume(X.is_P())``, never fed back to a
        constructor (D150, ``POL-ONT-002``).

        ``Mor(C).P()(A, B)`` is the same delegation.  ``Mor(C)``'s own call selects the
        hom subcategory ``Mor(C)(A, B)`` rather than constructing a morphism, and the
        narrowing of a subcategory of the ambient by ``P`` is ``property_subcategory``
        where the narrowing of a value of it is refinement.
        """
        constructed = self._ambient(*construction_data, **keywords)
        if isinstance(constructed, FullSubcategory) and constructed.ambient() is self._ambient:
            return constructed.property_subcategory(self)
        refine(constructed, self)
        return constructed

    def __repr__(self) -> str:
        return f"{self._ambient!r}.{self._name}()"


class PredicateSubcategory[**MorphismData, **TwoMorphismData](PropertySubcategory[MorphismData, TwoMorphismData]):
    """``C.P()`` whose membership its own mathematics decides (POL-CAT-060, D97).

    An axiom alone is already complete: it makes ``C.P()`` available, a value enters by
    construction or refinement, and ``ask`` decides membership from that placement, an
    active assumption, or a declared containment.  A class inherits this base when its
    mathematics *computes* the answer as well, and states that computation once, as
    ``_predicate``.  The base makes it the exact evaluation case of the property's
    predicate; membership stays what ``PropertySubcategory`` defines, the ambient's
    membership together with that predicate.

    These are two mechanisms and neither needs the other (D97).
    """

    class ObjectType:
        """An object the property's own predicate decides.

        Deciding membership adds no operation to the value: a computed answer and a
        trusted one place the same value in the same category.
        """

    class ElementType:
        """A point of such an object."""

    class MorphismType:
        """A morphism of the ambient between two of these objects."""

    def __init__(
        self,
        ambient: Category[MorphismData, TwoMorphismData],
        name: str,
        full_subcategory_of: tuple[Category, ...],
    ) -> None:
        super().__init__(ambient, name, full_subcategory_of)
        assert type(self)._predicate is not PredicateSubcategory._predicate, (
            f"{type(self).__name__} inherits PredicateSubcategory, so it states the predicate that decides "
            f"membership in {name}(); a property that computes nothing declares the axiom alone (POL-CAT-060)"
        )
        register_handler(self._property_predicate, self._predicate)

    @abstractmethod
    def _predicate(
        self,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        """The defining decision of membership in this property, on a value of the ambient."""


class NarrowedProperty[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):
    """``D.P().Q()...``: the objects of ``D`` in each of the root subcategories.

    It is a full subcategory of ``D``, of each root, of the narrowing of ``D`` by
    every subset of its roots (a narrowing by ``{P, Q}`` is a full subcategory of
    the narrowing by ``{P}``), and of the same narrowing of ``D``'s ambient when
    ``D`` is itself a full subcategory (POL-CAT-084).
    """

    class ObjectType:
        """An object of the base lying in every root.

        A narrowing is the property subcategory of its base by the roots jointly, so it
        states no operation of its own: the operations come from the roots, which the
        selected monomorphisms reach.
        """

    class ElementType:
        """A point of such an object."""

    class MorphismType:
        """A morphism of the base between two of these objects."""

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData], roots: tuple[FullSubcategory, ...]) -> None:
        self._roots = roots
        super().__init__(ambient)

    def narrowing_roots(self) -> tuple[Category, ...]:
        return self._roots

    def predicate(self) -> Predicate:
        """The predicate of the one root property this narrowing restricts (``D.P()``)."""
        (root,) = self._roots
        return root.predicate()

    def _subcategory_comparison(self, target: Category) -> Functor | None:
        """Select the retained comparison between these inverse-image pullbacks, if one exists."""
        from sage_categories.cat.functors import Cat

        shape = Cat().WalkingCospan()
        if not Category.Limits.is_constructed(Cat(), shape):
            return None
        return Cat().Pullbacks()._pullback_comparison(self, target)

    def structure_functors(self) -> tuple[Functor, ...]:
        """The monomorphisms into the base, into each root, into the narrowing by the roots but one, and into the same narrowing of each category the base is a subcategory of, each once.

        Dropping one root at a time reaches the narrowing by every subset of the roots,
        which is what this category is a full subcategory of and what D83 requires it to
        declare rather than leave to be induced.  ``1_X`` for ``X`` in ``C.P()`` is placed
        in ``Mor(C.P()).Isomorphisms()`` as its own inverse and in ``Mor(C.P()).Identity()``
        as an identity, so it lands in the narrowing by all three roots; without the
        monomorphism into the narrowing by ``{Mor(C.P()), Identity}`` no reader can see
        that it is an identity of ``C.P()``, and the word an equality reads stops dropping
        it (D84, D86, ``POL-CAT-023``, D169).

        The last group runs over every structure functor the base declares as a
        subcategory monomorphism, not the first of them.  ``D.P()`` is one category
        however many targets supply ``P``, and it is a full subcategory of each target's
        ``P``: that containment is the statement, and each is declared here (D83, D159,
        ``POL-LEAF-081``).  ``is_subcategory`` reads the declarations, so a containment
        the base's first ambient does not carry has nowhere else to be read from.
        """
        targets: list[Category] = [self._ambient, *self._roots]
        for omitted in self._roots:
            kept = tuple(root for root in self._roots if root is not omitted)
            if kept:
                targets.append(self._ambient.intersection(kept))
        for functor in self._ambient.selected_functors():
            if _functors().declares_subcategory(functor):
                targets.append(functor.codomain().intersection(self._roots))
        distinct: list[Category] = []
        for target in targets:
            if target is not self and not any(target is known for known in distinct):
                distinct.append(target)
        return tuple(_functors().full_subcategory_monomorphism(self, target) for target in distinct)

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        """Membership in the ambient together with membership in every root.

        Each root states its own membership: a property subcategory asks its predicate,
        and a construction family asks established placement, which is what membership in
        it means (``FullSubcategory``).
        """
        proposition = self._ambient.membership_proposition(candidate)
        for root in self._roots:
            proposition = proposition & root.membership_proposition(candidate)
        return proposition

    def __call__[Datum](self, *construction_data: Datum, **keywords: Datum) -> CategoryOfCategories.ElementType:
        """Construct through the one root that constructs, or through the base, and narrow the result.

        A narrowing wires no constructor of its own either: it has exactly the
        constructors of the category it narrows (D150, ``POL-CAT-038``).

        ``D.P()(diagram)`` constructs in ``C.P()``, which reads a diagram into ``D``
        through the subcategory monomorphism.  The result lies in ``D`` by the evidence
        ``D``'s own predicates supply -- the theorem that the construction restricts to
        the subcategory (D104) -- and then enters this narrowing.
        """
        constructing = tuple(root for root in self._roots if root._constructs_from_diagrams)
        if not constructing:
            constructed = self._ambient(*construction_data, **keywords)
            refine(constructed, self)
            return constructed
        (root,) = constructing
        constructed = root(*construction_data, **keywords)
        assert ask(self.membership_proposition(constructed)) is True, (
            f"{root!r} constructed {constructed!r}, which is not established to lie in {self!r}; "
            f"the restriction of {root.name()} to this subcategory needs its theorem"
        )
        refine(constructed, self)
        return constructed

    def __repr__(self) -> str:
        return f"{self._ambient!r}." + ".".join(f"{root.name()}()" for root in self._roots)


class FixedEndpointProperty[**MorphismData, **TwoMorphismData](NarrowedProperty[TwoMorphismData, []]):
    """``Mor(C)(A, B).P()``: constructs a morphism ``A -> B`` with property ``P``, through ``Mor(C)(A, B)``."""

    class ObjectType:
        """A morphism ``A -> B`` with the property: an object of a hom category, so a morphism of ``C``.

        Fixing the endpoints selects morphisms and does not change what one is.
        """

    class ElementType:
        """A point of such a morphism."""

    class MorphismType:
        """A 2-cell between two of these morphisms."""

    def domain(self) -> CategoryOfCategories.ElementType:
        return self._ambient.domain()

    def codomain(self) -> CategoryOfCategories.ElementType:
        return self._ambient.codomain()

    def _chosen_inhabitation(self) -> Decision:
        return _morphisms().hom_inhabitation(self)

    def one(self) -> MorphismCategory.ObjectType:
        """``1_X`` with this property: the unit of ``End_C(X)`` refined into the narrowing (POL-CAT-023, D84)."""
        identity = self._ambient.one()
        refine(identity, self)
        return identity
