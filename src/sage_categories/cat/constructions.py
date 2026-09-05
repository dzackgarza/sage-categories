"""Universal constructions as full subcategories of the ambient category (POL-CAT-046, POL-CAT-050, POL-FUN-019, POL-FUN-029).

For a category ``C`` and a shape ``I in Cat()``, ``C.Limits(I)`` is the full
subcategory of ``C`` on the chosen limits of diagrams ``I -> C``.  Constructing
one returns the limit itself: one value, an object of ``C``, carrying the whole
surface of ``C`` and placed in the family.  A chosen set product is an object of
``Sets()`` and answers ``cardinality()`` with no product-specific method.  The
one selected functor of the family is its subcategory monomorphism
``Fun(C.Limits(I), C).Monomorphisms().Isofibrations().Full()()``, identity on values, so
``is_placed(X * Y, Sets())`` is ``True`` and the morphisms, identities, and
composites of the family are those of ``C`` between its objects (POL-CAT-087).

The universal data belongs to the diagram.  For each diagram ``D`` the family
retains ``D``, the limiting cone (a natural transformation from the constant
diagram at the constructed object), and the mediator rule (POL-FUN-008), read
back by ``universal_data(D)``.  Distinct diagrams have distinct universal data
even when they construct one object: a divisibility ambient constructs ``1`` as
the product of ``(2, 3)`` and again as the product of ``(1, 6)``, and the cone of
each diagram is still exact.  The object-level accessors ``product_projection``,
``projection``, ``cone``, and ``universal_morphism`` read ``presentation``, the
data of the one diagram the object presents; an object two diagrams constructed
has no one cone, so ``presentation`` fails loudly there, naming both diagrams,
and the caller reads the data it means at that diagram.

``C.Products()`` is the union of the full images of ``Lim_I`` for discrete shapes
whose owned object-set cardinality is at least two.  It supplies the sequence
convenience ``(X_0, ..., X_n)`` and ``product_projection(i)`` (POL-CAT-093).
The shape family ``C.Limits(I)`` remains the sole owner of the universal data, and
being one of the full images the union runs over is the containment
``C.Limits(I) -> C.Products()``, declared as that subcategory monomorphism (D83).
An apex is therefore placed once, in its shape family, and reaches the union along
the declaration.  Singleton and unresolved discrete shapes declare no such
monomorphism and remain only in ``C.Limits(I)``.
``C.Coproducts()`` and ``C.Colimits(Discrete(S))`` are dual with cocones.

Constructing an object of ``C.Limits(I)`` calls the category-owned
``C.limit_construction(I)``, which fails loudly unless ``C`` owns an ``I``-limit
construction; ``with_universal_data`` places a supplied object from supplied data,
trusted by the writer (POL-MATH-037).  The construction category exists for every
supplied shape without asserting completeness (POL-CAT-051).

Each family retains its construction functor ``Lim_I: Fun(I, C) -> C``, acting on
a morphism of diagrams by the induced morphism of the constructed objects: the
mediator of the cone whose components are ``eta_i`` after the projections (Mathlib
``CategoryTheory.Limits.limMap``; inspected 2026-08-26).
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import TYPE_CHECKING

from sage_categories.cat.category import Category, member
from sage_categories.cat.declarations import Sets
from sage_categories.cat.cones import (
    LimitConesCategory,
    cocone,
    cocone_apex,
    colimit_cocones,
    cone,
    cone_apex,
    cones,
    limit_cones,
    vertex_of,
)
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.dual_functor_categories import dual_functor_category_equivalence
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import PredicateSubcategory, PropertySubcategory
from sage_categories.cat.predicates import Unknown
from sage_categories.cat.predicates import Proposition, ask
from sage_categories.kernel.refinement import is_placed, is_subcategory, refine, traces_placement
from sage_categories.kernel.sage_runtime import MonoDict, TripleDict

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = [
    "ApexCategory",
    "ColimitsCategory",
    "CoproductsCategory",
    "LimitsCategory",
    "ProductsCategory",
    "cocone",
    "cocone_apex",
    "cone",
    "cone_apex",
    "presenting_family",
    "vertex_of",
]

type Mediator = Callable[[NaturalTransformation], MorphismCategory.ObjectType]
type Construction = Callable[[Functor], "CategoryOfCategories.ElementType"]


type UniversalPresentation = LimitConesCategory.ObjectType


def _nontrivial_discrete(shape: Category) -> bool | None:
    """Return whether the owned object-set cardinality proves a nontrivial discrete shape; ``None`` while undecided."""
    if not shape.is_discrete():
        return False
    from sage_categories.cat.canonical import FinitePresentedCategory
    from sage_categories.cat.opposites import OppositeCategory

    if isinstance(shape, OppositeCategory):
        return _nontrivial_discrete(shape.original())
    # A finite presented shape decides by its label count without touching the owned
    # object set, so the categorical core stays executable before the production Sets
    # leaf (D126, D129).
    if isinstance(shape, FinitePresentedCategory):
        return len(shape.labels()) >= 2
    object_set = shape.object_set()
    if Sets.Finite().has_chosen_enumeration(object_set):
        return len(Sets.Finite().chosen_enumeration(object_set)) >= 2
    cardinal = ask(object_set.cardinality())
    if cardinal is Unknown:
        return None
    decision = ask(cardinal >= 2)
    return decision if decision is not Unknown else None


def _union_containment(union: Category, shape: Category) -> tuple[Category, ...]:
    """``union`` when ``shape`` is known nontrivial discrete, so that the containment is declared (D83).

    ``C.Products()`` is the union of the full images of the ``Lim_J`` for nontrivial
    discrete ``J`` (``specs/functor.md``, "Diagram shapes and universal constructions"),
    and ``C.Limits(J)`` is the full image of ``Lim_J``, so the mathematics says
    ``C.Limits(J)`` is a full subcategory of ``C.Products()``.  That containment is
    recorded as the monomorphism ``C.Limits(J) -> C.Products()`` and nothing induces it
    from a relation between the two predicates (D83), so an apex is placed once, in its
    shape family, and reaches the union along the declaration.  A singleton or undecided
    shape declares nothing and its apexes stay in ``C.Limits(J)`` alone.
    """
    return (union,) if _nontrivial_discrete(shape) is True else ()


def presenting_family(constructed: CategoryOfCategories.ElementType) -> Category:
    """The construction family that retains the universal data of ``constructed``.

    A family refines its apex into itself, so the family is the apex's placement, or one
    of that placement's narrowing roots when the apex was also refined into a property
    (``kernel/refinement.py``).  Two incomparable construction families reaching one value
    is a name collision the compiler already rejects, so at most one root presents it.
    """
    placement = constructed.category()
    for candidate in (placement, *placement.narrowing_roots()):
        if candidate.presenting_diagrams(constructed):
            return candidate
    raise AssertionError(f"{constructed!r} is in no construction family of {placement!r}")


def family_owner(category: Category) -> Category:
    """The category whose construction families retain universal data: the root of the declared-subcategory chain.

    A declared subcategory's family is the narrowing of the root's family (D31, D83), so
    the universal data of every apex lives at the root.
    """
    owner = category.narrowing_base()
    while owner.has_ambient():
        owner = owner.ambient()
    return owner


def product_presenting_family(constructed: CategoryOfCategories.ElementType) -> Category:
    """The shape-specific limit family that presents one product apex."""
    return family_owner(constructed.category()).Products().presenting_family(constructed)


def coproduct_presenting_family(constructed: CategoryOfCategories.ElementType) -> Category:
    """The shape-specific colimit family that presents one coproduct apex."""
    return family_owner(constructed.category()).Coproducts().presenting_family(constructed)


# -- construction families --------------------------------------------------------------------
#
# A family is a full subcategory of ``C``, so its object declaration compiles onto
# ``C.ObjectType`` and adds the universal surface of the construction.  Each
# declaration reads the universal data through the family, which retains it per
# diagram (POL-CAT-046, POL-FUN-019).  One declaration serves every ambient ``C``,
# and the kernel compiles a class per family (POL-API-025, POL-KERNEL-028).


class ApexCategory[**MorphismData, **TwoMorphismData](PropertySubcategory[MorphismData, TwoMorphismData]):
    """``C.Limits(I)``: the property subcategory of ``C`` on chosen apexes, an axiom implementation.

    Its objects are the constructed objects themselves and its morphisms are the
    morphisms of ``C`` between them; its one selected functor is the retained
    monomorphism ``Fun(P, C).Monomorphisms().Isofibrations().Full()()``, identity on values
    (POL-CAT-046, POL-FUN-019).  The family retains the universal data of each
    diagram it constructed from, and a constructed apex enters by placement, which
    is how the axiom's predicate decides membership (D97).
    """

    _constructs_from_diagrams = True

    # An apex is a value of ``C``, not a wrapper around one, and the family's
    # monomorphism is identity on values.  A subclass nests its own ``ObjectType`` for
    # the surface its universal data gives it.
    class ObjectType:
        """A chosen apex: an object of ``C``, the constructed value itself and not a wrapper around one."""

    class ElementType:
        """A point of a chosen apex, which is a point of ``C``."""

    class MorphismType:
        """A morphism of ``C`` between two chosen apexes."""

    def __init__(
        self,
        ambient: Category[MorphismData, TwoMorphismData],
        name: str,
        full_subcategory_of: tuple[Category, ...],
    ) -> None:
        self._data: MonoDict = MonoDict()
        self._constructed: MonoDict = MonoDict()
        self._source_diagrams: MonoDict = MonoDict()
        self._lowered: MonoDict = MonoDict()
        self._image_factor: Functor | None = None
        super().__init__(ambient, name, full_subcategory_of)

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        """Membership in a construction family is established placement, two-valued: the family is the full image of its construction (POL-CAT-068)."""
        return member(candidate, self)

    # -- the diagrams this family accepts ----------------------------------------------

    def accepts(self, diagram: Functor, shape: Category) -> None:
        """A diagram of shape ``shape`` into ``C`` or into a subcategory of ``C`` (a diagram into ``Sets().Uncountable()`` is a diagram into ``Sets()``)."""
        assert diagram in self.universe().morphism_category(1) and diagram.domain() is shape, f"{diagram!r} is not a diagram of shape {shape!r}"
        assert is_subcategory(diagram.codomain(), self.ambient()), f"{diagram!r} does not land in {self.ambient()!r}"

    def lowered(self, diagram: Functor) -> Functor:
        """The diagram as a diagram in ``C``: itself, or its composite with the subcategory monomorphism of its codomain, retained per diagram."""
        ambient = self.ambient()
        codomain = diagram.codomain()
        if codomain is ambient:
            return diagram
        assert is_subcategory(codomain, ambient), f"{codomain!r} is not a declared subcategory of {ambient!r}"
        if diagram not in self._lowered:
            self._lowered[diagram] = Fun(codomain, ambient).Monomorphisms().Isofibrations().Full()() * diagram
        return self._lowered[diagram]

    # -- the retained constructions ----------------------------------------------------

    def has_construction(self, diagram: Functor) -> bool:
        return diagram in self._constructed

    def chosen_object(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        """The object this family constructed for ``diagram`` (POL-CAT-046, POL-FUN-019)."""
        assert diagram in self._constructed, f"{self!r} constructed nothing for {diagram!r}"
        return self._constructed[diagram]

    def universal_data(self, diagram: Functor) -> UniversalPresentation:
        """The universal data retained for ``diagram``: its diagram, cone or cocone, and mediator rule."""
        assert diagram in self._data, f"{self!r} retains no construction of {diagram!r}"
        return self._data[diagram]

    def presenting_diagrams(self, constructed: CategoryOfCategories.ElementType) -> tuple[Functor, ...]:
        """The diagrams this family constructed ``constructed`` from, in construction order; none for an object it did not construct."""
        return self._source_diagrams[constructed] if constructed in self._source_diagrams else ()

    def presentation(self, constructed: CategoryOfCategories.ElementType) -> UniversalPresentation:
        """The universal data of the one diagram ``constructed`` presents.

        A cone belongs to its diagram, so an object that two diagrams construct answers no
        one cone: this names both and the caller reads ``universal_data`` at the diagram
        it means.
        """
        diagrams = self.presenting_diagrams(constructed)
        assert diagrams, f"{self!r} constructed no object {constructed!r}"
        assert len(diagrams) == 1, (
            f"{self!r} constructed {constructed!r} from {' and from '.join(repr(diagram) for diagram in diagrams)}; "
            "read the universal data at the diagram whose cone you want"
        )
        return self._data[diagrams[0]]

    def chosen(self, diagram: Functor, construction: Construction) -> CategoryOfCategories.ElementType:
        """The constructed object of ``diagram``, constructed once; a diagram and its lowering share it."""
        if not self.has_construction(diagram):
            construction(diagram)
            lowered = self.lowered(diagram)
            if lowered is not diagram:
                self._constructed[diagram] = self.chosen_object(lowered)
        return self.chosen_object(diagram)

    def _retain(
        self,
        diagram: Functor,
        constructed: CategoryOfCategories.ElementType,
        data: UniversalPresentation,
    ) -> CategoryOfCategories.ElementType:
        """Place ``constructed`` in this family, retain the universal data of its diagram, and return it."""
        ambient = self.ambient()
        assert constructed in ambient, f"{constructed!r} is not an object of {ambient!r}"
        assert diagram not in self._data, f"{self!r} already retains the construction of {diagram!r}"
        retained = self._source_diagrams[constructed] if constructed in self._source_diagrams else ()
        self._data[diagram] = data
        self._constructed[diagram] = constructed
        self._source_diagrams[constructed] = (*retained, diagram)
        refine(constructed, self)
        return constructed

    def _factor_through_image(self, defining_functor: Functor) -> Functor:
        if self._image_factor is None:
            self._image_factor = Fun(defining_functor.domain(), self)(
                lambda diagram: self(diagram),
                lambda transformation: induced_limit_morphism(self, transformation),
            )
        return self._image_factor


class LimitsCategory(ApexCategory):
    """``C.Limits(I)``: chosen limits of diagrams of one shape ``I``."""

    _base_category_class_and_axiom = (Category, "Limits")

    # A point of a chosen limit is a cone over the diagram with apex ``1_C``; the
    # mediator of a cone is a morphism of ``C`` and not a further kind.
    class ElementType:
        """A point of a chosen limit: a cone over the diagram with apex ``1_C``."""

    class MorphismType:
        """A morphism of ``C`` between two chosen limits; the mediator of a cone is one of these."""

    class ObjectType:
        """A chosen limit apex. Its limiting presentation is a separate owned cone."""

    def __init__(
        self,
        ambient: Category,
        name: str,
        full_subcategory_of: tuple[Category, ...],
        shape: Category,
    ) -> None:
        assert shape in Cat(), f"{shape!r} is not a shape"
        self._shape = shape
        self._limit_functor: MonoDict = MonoDict()
        self._pullback_transformations: TripleDict = TripleDict(weak_values=False)
        self._limit_adjunction: CategoryOfCategories.ElementType | None = None
        super().__init__(ambient, name, (*full_subcategory_of, *_union_containment(ambient.Products(), shape)))
        self.limit_functor()

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self.ambient())

    def __call__(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        """``C.Limits(I)(diagram)``: the chosen limit, through ``C.limit_construction(I)``.

        A retained diagram answers from its universal data; only a new diagram asks the
        ambient for its owned construction, which fails loudly when none is declared.
        """
        self.accepts(diagram, self._shape)
        if self.has_construction(diagram):
            return self.chosen_object(diagram)
        return self.chosen(diagram, self.ambient().limit_construction(self._shape))

    def with_universal_data(
        self,
        diagram: Functor,
        apex: CategoryOfCategories.ElementType,
        limiting_cone: NaturalTransformation,
        mediator: Mediator,
    ) -> CategoryOfCategories.ElementType:
        """The chosen limit from supplied universal data; the writer asserts the universal property (POL-MATH-037)."""
        assert diagram in self.diagrams()
        assert limiting_cone in self.diagrams().morphism_category(1)(self.diagrams().constant(apex), diagram)
        presentations = limit_cones(diagram)
        presentation = presentations.with_universal_data(
            limiting_cone,
            lambda candidate: mediator(candidate.transformation()),
        )
        return self._retain(diagram, apex, presentation)

    def limit_functor(self) -> Functor:
        """``Lim_I: Fun(I, C) -> C``, retained once."""
        if self not in self._limit_functor:
            self._limit_functor[self] = limit_functor(self)
            from sage_categories.cat.images import register_full_image

            register_full_image(self._limit_functor[self], self)
        if self._shape.is_discrete():
            self.ambient().Products().retain_full_image(self)
        return self._limit_functor[self]

    def defining_functor(self) -> Functor:
        return self.limit_functor()

    def _retain_pullback_comparison(
        self,
        source_diagram: Functor,
        target_diagram: Functor,
        middle_component: Functor,
    ) -> Functor | None:
        """Retain the functor induced by ``(1_D, middle_component, 1_C)`` between two chosen pullbacks."""
        shape = self.shape()
        assert self.ambient() is Cat() and shape is Cat().WalkingCospan()
        key = (source_diagram, target_diagram, middle_component)
        left, middle, apex = (shape(index) for index in range(3))
        source_left = source_diagram.on_object(left)
        target_left = target_diagram.on_object(left)
        source_middle = source_diagram.on_object(middle)
        target_middle = target_diagram.on_object(middle)
        source_apex = source_diagram.on_object(apex)
        target_apex = target_diagram.on_object(apex)
        assert source_left is target_left and source_apex is target_apex
        assert middle_component.domain() is source_middle and middle_component.codomain() is target_middle
        assert traces_placement(middle_component)
        assert is_placed(middle_component, Fun.Full())
        if key not in self._pullback_transformations:
            self._pullback_transformations[key] = None
        return self._apply_pullback_comparison(source_diagram, target_diagram, middle_component)

    def _apply_pullback_comparison(
        self,
        source_diagram: Functor,
        target_diagram: Functor,
        middle_component: Functor,
    ) -> Functor | None:
        """Realize a retained cospan map after both endpoint pullbacks are retained."""
        if not self.has_construction(source_diagram) or not self.has_construction(target_diagram):
            return None
        key = (source_diagram, target_diagram, middle_component)
        transformation = self._pullback_transformations[key]
        if transformation is None:
            shape = self.shape()
            left, _, apex = (shape(index) for index in range(3))
            identities = {
                0: Cat().morphism_category(1)(source_diagram.on_object(left), source_diagram.on_object(left)).one(),
                1: middle_component,
                2: Cat().morphism_category(1)(source_diagram.on_object(apex), source_diagram.on_object(apex)).one(),
            }
            transformation = self.diagrams().morphism_category(1)(source_diagram, target_diagram)(
                lambda vertex: identities[shape.label(vertex)]
            )
            self._pullback_transformations[key] = transformation
        comparison = self.limit_functor().on_morphism(transformation)
        refine(comparison, Fun._declared_subcategory(True))
        self.chosen_object(source_diagram)._retain_structure_functor(comparison)
        return comparison

    def _apply_pullback_comparisons_at(self, diagram: Functor) -> None:
        """Apply each retained cospan morphism whose last missing endpoint is ``diagram``."""
        for (source_diagram, target_diagram, middle_component), _ in tuple(self._pullback_transformations.items()):
            if source_diagram is diagram or target_diagram is diagram:
                self._apply_pullback_comparison(source_diagram, target_diagram, middle_component)

    def _pullback_comparisons_from(self, source: Category) -> tuple[Functor, ...]:
        """Return all retained induced comparisons with domain ``source``."""
        limit = self.limit_functor()
        return tuple(
            limit.on_morphism(transformation)
            for (source_diagram, _, _), transformation in self._pullback_transformations.items()
            if transformation is not None and self.chosen_object(source_diagram) is source
        )

    def factorization(self) -> tuple[Functor, Functor]:
        return self._factor_through_image(self.limit_functor()), self.subcategory_monomorphism()

    def adjunction(self) -> CategoryOfCategories.ElementType:
        """Return the selected adjunction ``Delta_I |- Lim_I``."""
        if self._limit_adjunction is None:
            self._limit_adjunction = limit_adjunction(self)
        return self._limit_adjunction

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.{self.name()}({self._shape!r})"


class ProductsCategory(PredicateSubcategory[[MorphismCategory.ObjectType], []]):
    """``C.Products()``: the union of full images of the known nontrivial discrete limit functors."""

    _base_category_class_and_axiom = (Category, "Products")
    _constructs_from_diagrams = True

    # A point of a chosen product is a family of points, one into each factor.
    class ElementType:
        """A point of a chosen product: a family of points, one into each factor."""

    class MorphismType:
        """A morphism of ``C`` between two chosen products."""

    class ObjectType:
        """A chosen product over a discrete shape: an object of ``C`` with its projections and mediator rule."""

        def product_factors(self) -> Functor:
            """The retained indexed family ``i |-> X_i`` (``specs/functor.md``, "Diagram shapes and universal constructions")."""
            presentation = product_presenting_family(self).presentation(self)
            return presentation.diagram()

        def cone(self) -> NaturalTransformation:
            """The product cone ``constant(self) => diagram``, whose components are the projections."""
            presentation = product_presenting_family(self).presentation(self)
            return presentation.transformation()

        def product_projection(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            """``pi_i: self -> X_i`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            presentation = product_presenting_family(self).presentation(self)
            return presentation.leg(index)

    def __init__(self, ambient: Category, name: str, full_subcategory_of: tuple[Category, ...]) -> None:
        self._candidate_families: list[LimitsCategory] = []
        super().__init__(ambient, name, full_subcategory_of)

    def retain_full_image(self, family: Category) -> None:
        assert isinstance(family, LimitsCategory)
        assert family.shape().is_discrete()
        # Families are retained by identity: list containment would ask the
        # proposition-valued equality of two distinct families (POL-SAGE-013).
        if not any(family is known for known in self._candidate_families):
            self._candidate_families.append(family)

    def full_images(self) -> tuple[Category, ...]:
        """Return the full-image families whose union this category owns."""
        return tuple(family for family in self._candidate_families if _nontrivial_discrete(family.shape()) is True)

    def _predicate(
        self,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        """Whether a retained limit presentation currently has a nontrivial discrete shape."""
        decisions: list[bool | None] = []
        for family in self._candidate_families:
            membership = ask(family.membership_proposition(candidate))
            nontrivial = _nontrivial_discrete(family.shape())
            if membership is False or nontrivial is False:
                decisions.append(False)
            elif membership is True and nontrivial is True:
                decisions.append(True)
            else:
                decisions.append(None)
        if any(decision is True for decision in decisions):
            return True
        if any(decision is None for decision in decisions):
            return None
        return False

    def presenting_family(self, apex: CategoryOfCategories.ElementType) -> Category:
        families = tuple(
            family
            for family in self._candidate_families
            if _nontrivial_discrete(family.shape()) is True
            and ask(family.membership_proposition(apex)) is True
        )
        assert len(families) == 1, f"{apex!r} has {len(families)} product-family presentations"
        return families[0]

    def diagrams(self, shape: Category) -> Category:
        assert shape.is_discrete(), f"{shape!r} is not a discrete shape"
        return Fun(shape, self.ambient())

    def _sequence_diagram(self, sequence: tuple[CategoryOfCategories.ElementType, ...]) -> Functor:
        """The sequence diagram on objects of ``C``, retained per sequence."""
        ambient = self.ambient()
        for member_object in sequence:
            assert member_object in ambient, f"{member_object!r} is not an object of {ambient!r}"
        return from_sequence(ambient, sequence)

    def __call__(
        self,
        family: Functor | tuple[CategoryOfCategories.ElementType, ...],
        *factors: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        """Construct a known nontrivial discrete limit, or use the sequence form."""
        if factors:
            diagram = self._sequence_diagram((family, *factors))
        else:
            diagram = self._sequence_diagram(family) if isinstance(family, tuple) else family
        shape = diagram.domain()
        assert _nontrivial_discrete(shape) is True, (
            f"{shape!r} is not known to have at least two objects; use {self.ambient()!r}.Limits({shape!r})"
        )
        ambient = self.ambient()
        return ambient.Limits(shape)(diagram)

    def with_universal_data(
        self,
        diagram: Functor,
        apex: CategoryOfCategories.ElementType,
        limiting_cone: NaturalTransformation,
        mediator: Mediator,
    ) -> CategoryOfCategories.ElementType:
        """The chosen product from supplied universal data (POL-MATH-037)."""
        shape = diagram.domain()
        assert _nontrivial_discrete(shape) is True, (
            f"{shape!r} is not known to have at least two objects; use {self.ambient()!r}.Limits({shape!r})"
        )
        diagrams = self.diagrams(shape)
        assert diagram in diagrams
        assert limiting_cone in diagrams.morphism_category(1)(diagrams.constant(apex), diagram)
        return self.ambient().Limits(diagram.domain()).with_universal_data(
            diagram,
            apex,
            limiting_cone,
            mediator,
        )


class ColimitsCategory(PropertySubcategory[[MorphismCategory.ObjectType], []]):
    """``C.Colimits(I)``: the public opposite view of ``C.op().Limits(I.op())``."""

    _base_category_class_and_axiom = (Category, "Colimits")
    _constructs_from_diagrams = True

    class ElementType:
        """A point of a chosen colimit."""

    class MorphismType:
        """A morphism of ``C`` between two chosen colimits."""

    class ObjectType:
        """A chosen colimit apex presented by one limiting cone in ``C.op()``."""

        def cocone(self) -> NaturalTransformation:
            """The colimiting cocone ``diagram => constant(self)``."""
            return presenting_family(self).presentation(self).transformation()

        def injection(self, index: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            """The cocone component ``D(i) -> self``."""
            return presenting_family(self).presentation(self).leg(index)

    def __init__(
        self,
        ambient: Category,
        name: str,
        full_subcategory_of: tuple[Category, ...],
        shape: Category,
    ) -> None:
        assert shape in Cat(), f"{shape!r} is not a shape"
        self._shape = shape
        self._duality = dual_functor_category_equivalence(shape, ambient)
        self._dual_limits = ambient.op().Limits(shape.op())
        self._lowered: MonoDict = MonoDict()
        self._dual_diagrams: MonoDict = MonoDict()
        self._presentations: MonoDict = MonoDict()
        self._colimit_functor: Functor | None = None
        super().__init__(ambient, name, (*full_subcategory_of, *_union_containment(ambient.Coproducts(), shape)))
        self.colimit_functor()

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        """Membership in a construction family is established placement, two-valued (POL-CAT-068)."""
        return member(candidate, self)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self.ambient())

    def accepts(self, diagram: Functor) -> None:
        assert diagram in self.universe().morphism_category(1) and diagram.domain() is self._shape, (
            f"{diagram!r} is not a diagram of shape {self._shape!r}"
        )
        assert is_subcategory(diagram.codomain(), self.ambient()), f"{diagram!r} does not land in {self.ambient()!r}"

    def lowered(self, diagram: Functor) -> Functor:
        codomain = diagram.codomain()
        if codomain is self.ambient():
            return diagram
        assert is_subcategory(codomain, self.ambient()), f"{codomain!r} is not a declared subcategory of {self.ambient()!r}"
        if diagram not in self._lowered:
            self._lowered[diagram] = Fun(codomain, self.ambient()).Monomorphisms().Isofibrations().Full()() * diagram
        return self._lowered[diagram]

    def _dual_diagram(self, diagram: Functor) -> Functor:
        if diagram not in self._dual_diagrams:
            dual_diagram = self._duality.forward().on_object(self.lowered(diagram))
            assert isinstance(dual_diagram, Functor)
            self._dual_diagrams[diagram] = dual_diagram
        return self._dual_diagrams[diagram]

    def _original_diagrams(self, dual_diagram: Functor) -> tuple[Functor, ...]:
        diagrams = tuple(
            diagram
            for diagram, associated_dual in self._dual_diagrams.items()
            if associated_dual is dual_diagram
        )
        if diagrams:
            return diagrams
        diagram = self._duality.inverse().on_object(dual_diagram)
        assert isinstance(diagram, Functor)
        return (diagram,)

    def _associate(
        self,
        presentation: LimitConesCategory.ObjectType,
    ) -> CategoryOfCategories.ElementType:
        apex = presentation.apex()
        assert apex in self.ambient(), f"{apex!r} is not an object of {self.ambient()!r}"
        refine(apex, self)
        return apex

    def has_construction(self, diagram: Functor) -> bool:
        dual_diagram = self._dual_diagram(diagram)
        return self._dual_limits.has_construction(self._dual_limits.lowered(dual_diagram))

    def chosen_object(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        return self.universal_data(diagram).apex()

    def universal_data(self, diagram: Functor) -> UniversalPresentation:
        from sage_categories.cat.opposites import opposite_morphism

        if diagram not in self._presentations:
            dual_diagram = self._dual_diagram(diagram)
            dual = self._dual_limits.universal_data(self._dual_limits.lowered(dual_diagram))
            transformation = cocone(diagram, dual.apex(), lambda vertex: opposite_morphism(dual.leg(vertex)))
            self._presentations[diagram] = colimit_cocones(diagram).with_universal_data(
                transformation,
                lambda candidate: opposite_morphism(dual.lift(cones(dual.diagram())(candidate.transformation().op()))),
            )
        return self._presentations[diagram]

    def presenting_diagrams(self, constructed: CategoryOfCategories.ElementType) -> tuple[Functor, ...]:
        return tuple(
            diagram
            for dual_diagram in self._dual_limits.presenting_diagrams(constructed)
            for diagram in self._original_diagrams(dual_diagram)
        )

    def presenting_diagram(self, constructed: CategoryOfCategories.ElementType) -> Functor:
        diagrams = self.presenting_diagrams(constructed)
        assert len(diagrams) == 1, f"{constructed!r} has {len(diagrams)} colimit-family presentations"
        return diagrams[0]

    def presentation(self, constructed: CategoryOfCategories.ElementType) -> UniversalPresentation:
        return self.universal_data(self.presenting_diagram(constructed))

    def __call__(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        """Construct the chosen colimit as the dual limit in ``C.op()``."""
        self.accepts(diagram)
        dual_diagram = self._dual_diagram(diagram)
        if not self._dual_limits.has_construction(self._dual_limits.lowered(dual_diagram)):
            self._dual_limits(dual_diagram)
        presentation = self._dual_limits.universal_data(self._dual_limits.lowered(dual_diagram))
        return self._associate(presentation)

    def with_universal_data(
        self,
        diagram: Functor,
        apex: CategoryOfCategories.ElementType,
        colimiting_cocone: NaturalTransformation,
        mediator: Mediator,
    ) -> CategoryOfCategories.ElementType:
        """Select the dual limiting cone from supplied colimit data."""
        from sage_categories.cat.opposites import opposite_morphism

        assert diagram in self.diagrams()
        assert colimiting_cocone in self.diagrams().morphism_category(1)
        assert colimiting_cocone.domain() is diagram
        assert cocone_apex(colimiting_cocone) is apex
        dual_diagram = self._dual_diagram(diagram)
        self._dual_limits.with_universal_data(
            dual_diagram,
            self.ambient().op()(apex),
            colimiting_cocone.op(),
            lambda candidate: opposite_morphism(mediator(candidate.op())),
        )
        presentation = self._dual_limits.universal_data(self._dual_limits.lowered(dual_diagram))
        return self._associate(presentation)

    def colimit_functor(self) -> Functor:
        """``Colim_I: Fun(I, C) -> C``, derived from the opposite limit functor."""
        if self._colimit_functor is None:
            self._colimit_functor = self._dual_limits.limit_functor().op() * self._duality.forward()
            from sage_categories.cat.images import register_full_image

            register_full_image(self._colimit_functor, self)
        if self._shape.is_discrete():
            self.ambient().Coproducts().retain_full_image(self)
        return self._colimit_functor

    def defining_functor(self) -> Functor:
        return self.colimit_functor()

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.{self.name()}({self._shape!r})"


class CoproductsCategory(PredicateSubcategory[[MorphismCategory.ObjectType], []]):
    """``C.Coproducts()``: the union of nontrivial discrete colimit full images."""

    _base_category_class_and_axiom = (Category, "Coproducts")
    _constructs_from_diagrams = True

    # A point of a chosen coproduct is unconstrained, as for a colimit.  That a point of
    # a disjoint union factors through one injection is a fact about ``Sets()``.
    class ElementType:
        """A point of a chosen coproduct, unconstrained as for a colimit."""

    class MorphismType:
        """A morphism of ``C`` between two chosen coproducts."""

    class ObjectType:
        """A chosen coproduct over a discrete shape: an object of ``C`` with its injections and mediator rule."""

        def coproduct_summands(self) -> Functor:
            """The retained indexed family ``i |-> X_i`` (``specs/functor.md``, "Diagram shapes and universal constructions")."""
            return coproduct_presenting_family(self).presenting_diagram(self)

        def coproduct_injection(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            """``iota_i: X_i -> self`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            return coproduct_presenting_family(self).presentation(self).leg(index)

    def __init__(self, ambient: Category, name: str, full_subcategory_of: tuple[Category, ...]) -> None:
        self._candidate_families: list[ColimitsCategory] = []
        super().__init__(ambient, name, full_subcategory_of)

    def retain_full_image(self, family: Category) -> None:
        assert isinstance(family, ColimitsCategory)
        assert family.shape().is_discrete()
        # Families are retained by identity: list containment would ask the
        # proposition-valued equality of two distinct families (POL-SAGE-013).
        if not any(family is known for known in self._candidate_families):
            self._candidate_families.append(family)

    def full_images(self) -> tuple[Category, ...]:
        return tuple(family for family in self._candidate_families if _nontrivial_discrete(family.shape()) is True)

    def _predicate(
        self,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        decisions: list[bool | None] = []
        for family in self._candidate_families:
            membership = ask(family.membership_proposition(candidate))
            nontrivial = _nontrivial_discrete(family.shape())
            if membership is False or nontrivial is False:
                decisions.append(False)
            elif membership is True and nontrivial is True:
                decisions.append(True)
            else:
                decisions.append(None)
        if any(decision is True for decision in decisions):
            return True
        if any(decision is None for decision in decisions):
            return None
        return False

    def presenting_family(self, apex: CategoryOfCategories.ElementType) -> ColimitsCategory:
        families = tuple(
            family
            for family in self._candidate_families
            if _nontrivial_discrete(family.shape()) is True
            and ask(family.membership_proposition(apex)) is True
        )
        assert len(families) == 1, f"{apex!r} has {len(families)} coproduct-family presentations"
        return families[0]

    def diagrams(self, shape: Category) -> Category:
        assert shape.is_discrete(), f"{shape!r} is not a discrete shape"
        return Fun(shape, self.ambient())

    def _sequence_diagram(self, sequence: tuple[CategoryOfCategories.ElementType, ...]) -> Functor:
        """The sequence diagram on objects of ``C``, retained per sequence."""
        ambient = self.ambient()
        for member_object in sequence:
            assert member_object in ambient, f"{member_object!r} is not an object of {ambient!r}"
        return from_sequence(ambient, sequence)

    def __call__(
        self,
        family: Functor | tuple[CategoryOfCategories.ElementType, ...],
        *summands: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        """Construct a known nontrivial discrete colimit, or use the sequence form."""
        if summands:
            diagram = self._sequence_diagram((family, *summands))
        else:
            diagram = self._sequence_diagram(family) if isinstance(family, tuple) else family
        shape = diagram.domain()
        assert _nontrivial_discrete(shape) is True, (
            f"{shape!r} is not known to have at least two objects; use {self.ambient()!r}.Colimits({shape!r})"
        )
        assert diagram in self.universe().morphism_category(1) and diagram.domain() is shape
        assert is_subcategory(diagram.codomain(), self.ambient()), f"{diagram!r} does not land in {self.ambient()!r}"
        return self.ambient().Colimits(shape)(diagram)

    def with_universal_data(
        self,
        diagram: Functor,
        apex: CategoryOfCategories.ElementType,
        colimiting_cocone: NaturalTransformation,
        mediator: Mediator,
    ) -> CategoryOfCategories.ElementType:
        """Delegate supplied data to the exact discrete colimit family."""
        shape = diagram.domain()
        assert _nontrivial_discrete(shape) is True, (
            f"{shape!r} is not known to have at least two objects; use {self.ambient()!r}.Colimits({shape!r})"
        )
        diagrams = self.diagrams(diagram.domain())
        assert diagram in diagrams
        return self.ambient().Colimits(shape).with_universal_data(
            diagram,
            apex,
            colimiting_cocone,
            mediator,
        )


# -- the construction functors -------------------------------------------------------------


def constructed_data(family: Category, diagram: Functor) -> UniversalPresentation:
    """The universal data of ``diagram`` in ``family``, constructing it if this is its first call.

    The construction functor acts on the two diagrams a morphism of diagrams connects, so
    it reads their data at the diagrams: one object can present several of them.
    """
    family(diagram)
    return family.universal_data(family.lowered(diagram))


def induced_limit_morphism(family: Category, transformation: NaturalTransformation) -> MorphismCategory.ObjectType:
    """``Lim(eta): L_D -> L_D'`` for ``eta: D => D'``: the mediator of the cone ``eta_i after pi_i``."""
    source = constructed_data(family, transformation.domain())
    diagram_identity = family.diagrams().morphism_category(1)(transformation.domain(), transformation.domain()).one()
    if transformation is diagram_identity:
        return family.ambient().morphism_category(1)(source.apex(), source.apex()).one()
    target = constructed_data(family, transformation.codomain())

    def induced_leg(vertex: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        component = transformation.component(vertex)
        identity = target.diagram().codomain().morphism_category(1)(component.domain(), component.domain()).one()
        return source.leg(vertex) if component is identity else component * source.leg(vertex)

    induced_cone = cone(
        target.diagram(),
        source.apex(),
        induced_leg,
    )
    return target.lift(cones(target.diagram())(induced_cone))


def limit_functor(family: Category) -> Functor:
    """``Lim_I: Fun(I, C) -> C`` for a limit family: the chosen limit and the induced morphism between two of them."""
    return Fun(family.diagrams(), family.diagrams().codomain())(
        lambda diagram: family(diagram),
        lambda transformation: induced_limit_morphism(family, transformation),
    )


def limit_adjunction(family: Category) -> CategoryOfCategories.ElementType:
    """Select ``Delta_I |- Lim_I`` from the retained limiting cones."""
    from sage_categories.cat.adjunctions import Adjunctions

    diagrams = family.diagrams()
    base = diagrams.codomain()
    diagonal_functor = diagrams.diagonal()
    limit = family.limit_functor()

    def unit_component(member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        diagram = diagrams.constant(member_object)
        presentation = constructed_data(family, diagram)
        identity = base.morphism_category(1)(member_object, member_object).one()
        candidate = cones(diagram)(cone(diagram, member_object, lambda vertex: identity))
        return presentation.lift(candidate)

    unit_endofunctors = Fun(base, base)
    unit = unit_endofunctors.morphism_category(1)(
        unit_endofunctors.one(),
        limit * diagonal_functor,
    )(unit_component)
    counit_endofunctors = Fun(diagrams, diagrams)
    counit = counit_endofunctors.morphism_category(1)(
        diagonal_functor * limit,
        counit_endofunctors.one(),
    )(lambda diagram: constructed_data(family, diagram).transformation())
    return Adjunctions(diagonal_functor, limit)(unit, counit)
