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

``C.Products()`` is the family of chosen products over every discrete shape, with
the sequence convenience ``(X_0, ..., X_n)`` and ``product_projection(i)``
(POL-CAT-093); ``C.Limits(Discrete(S))`` is its full subcategory on the products
indexed by ``Discrete(S)``, since a limit over a discrete shape is a product by
definition (Mathlib ``CategoryTheory.Limits.HasProduct``: ``HasLimit
(Discrete.functor f)``; inspected 2026-08-26).  ``C.Coproducts()`` and
``C.Colimits(Discrete(S))`` are dual with cocones.

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

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.cones import (
    ConeCategory,
    LimitConesCategory,
    cocone,
    cocone_apex,
    cocones,
    colimit_cocones,
    cone,
    cone_apex,
    cones,
    limit_cones,
    vertex_of,
)
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import FullSubcategory
from sage_categories.cat.shapes import is_discrete
from sage_categories.cat.predicates import Decision, Unknown
from sage_categories.cat.predicates import Predicate, Proposition, predicate, register_handler
from sage_categories.kernel.refinement import is_placed, is_subcategory, refine

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = [
    "ApexCategory",
    "ColimitsCategory",
    "CoproductsCategory",
    "DiscreteColimits",
    "DiscreteLimits",
    "LimitsCategory",
    "ProductsCategory",
    "cocone",
    "cocone_apex",
    "colimits",
    "cone",
    "cone_apex",
    "limits",
    "presenting_family",
    "vertex_of",
]

type Mediator = Callable[[NaturalTransformation], MorphismCategory.ObjectType]
type Construction = Callable[[Functor], "CategoryOfCategories.ElementType"]


type UniversalPresentation = LimitConesCategory.ObjectType


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


# -- construction families --------------------------------------------------------------------
#
# A family is a full subcategory of ``C``, so its object declaration compiles onto
# ``C.ObjectType`` and adds the universal surface of the construction.  Each
# declaration reads the universal data through the family, which retains it per
# diagram (POL-CAT-046, POL-FUN-019).  One declaration serves every ambient ``C``,
# and the kernel compiles a class per family (POL-API-025, POL-KERNEL-028).


class ApexCategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):
    """``C.Products()``, ``C.Limits(I)``, and their duals: the full subcategory of ``C`` on the chosen apexes.

    Its objects are the constructed objects themselves and its morphisms are the
    morphisms of ``C`` between them; its one selected functor is the retained
    monomorphism ``Fun(P, C).Monomorphisms().Isofibrations().Full()()``, identity on values
    (POL-CAT-046, POL-FUN-019).  The family retains the universal data of each
    diagram it constructed from.
    """

    # An apex is a value of ``C``, not a wrapper around one, and the family's
    # monomorphism is identity on values.  A subclass nests its own ``ObjectType`` for
    # the surface its universal data gives it.
    class ObjectType:
        """A chosen apex: an object of ``C``, the constructed value itself and not a wrapper around one."""

    class ElementType:
        """A point of a chosen apex, which is a point of ``C``."""

    class MorphismType:
        """A morphism of ``C`` between two chosen apexes."""

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData]) -> None:
        self._data: MonoDict = MonoDict()
        self._constructed: MonoDict = MonoDict()
        self._source_diagrams: MonoDict = MonoDict()
        self._lowered: MonoDict = MonoDict()
        self._image_factor: Functor | None = None
        super().__init__(ambient)

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

    # A point of a chosen limit is a cone over the diagram with apex ``1_C``; the
    # mediator of a cone is a morphism of ``C`` and not a further kind.
    class ElementType:
        """A point of a chosen limit: a cone over the diagram with apex ``1_C``."""

    class MorphismType:
        """A morphism of ``C`` between two chosen limits; the mediator of a cone is one of these."""

    class ObjectType:
        """A chosen limit apex. Its limiting presentation is a separate owned cone."""

    def __init__(self, ambient: Category, shape: Category) -> None:
        self._shape = shape
        self._limit_functor: MonoDict = MonoDict()
        self._limit_adjunction: CategoryOfCategories.ElementType | None = None
        super().__init__(ambient)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self.ambient())

    def __call__(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        """``C.Limits(I)(diagram)``: the chosen limit, through ``C.limit_construction(I)``."""
        self.accepts(diagram, self._shape)
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
        return self._limit_functor[self]

    def defining_functor(self) -> Functor:
        return self.limit_functor()

    def factorization(self) -> tuple[Functor, Functor]:
        return self._factor_through_image(self.limit_functor()), self.subcategory_monomorphism()

    def adjunction(self) -> CategoryOfCategories.ElementType:
        """Return the selected adjunction ``Delta_I |- Lim_I``."""
        if self._limit_adjunction is None:
            self._limit_adjunction = limit_adjunction(self)
        return self._limit_adjunction

    def name(self) -> str:
        return f"Limits({self._shape!r})"

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.Limits({self._shape!r})"


class ProductsCategory(ApexCategory):
    """``C.Products()``: chosen products over every discrete shape (POL-CAT-093)."""

    # A point of a chosen product is a family of points, one into each factor.
    class ElementType:
        """A point of a chosen product: a family of points, one into each factor."""

    class MorphismType:
        """A morphism of ``C`` between two chosen products."""

    class ObjectType:
        """A chosen product over a discrete shape: an object of ``C`` with its projections and mediator rule."""

        def product_factors(self) -> Functor:
            """The retained indexed family ``i |-> X_i`` (``specs/functor.md``, "Diagram shapes and universal constructions")."""
            presentation = presenting_family(self).presentation(self)
            assert isinstance(presentation, ConeCategory.ObjectType)
            return presentation.diagram()

        def index_category(self) -> Category:
            return self.product_factors().domain()

        def cone(self) -> NaturalTransformation:
            """The product cone ``constant(self) => diagram``, whose components are the projections."""
            presentation = presenting_family(self).presentation(self)
            assert isinstance(presentation, ConeCategory.ObjectType)
            return presentation.transformation()

        def product_projection(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            """``pi_i: self -> X_i`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            presentation = presenting_family(self).presentation(self)
            assert isinstance(presentation, ConeCategory.ObjectType)
            return presentation.leg(index)

        def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismCategory.ObjectType:
            """The mediating morphism from the apex of another cone over the same diagram."""
            presentation = presenting_family(self).presentation(self)
            assert isinstance(presentation, LimitConesCategory.ObjectType)
            return presentation.lift(cones(presentation.diagram())(candidate_cone))

    def __init__(self, ambient: Category) -> None:
        self._full_image_families: list[Category] = []
        super().__init__(ambient)

    def retain_full_image(self, family: Category) -> None:
        if family not in self._full_image_families:
            self._full_image_families.append(family)

    def full_images(self) -> tuple[Category, ...]:
        """Return the full-image families whose union this category owns."""
        return tuple(self._full_image_families)

    def diagrams(self, shape: Category) -> Category:
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
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
    ) -> CategoryOfCategories.ElementType:
        """``C.Products()(diagram)`` for a diagram over ``Discrete(S)``; ``C.Products()((X_0, ..., X_n))`` for the sequence form."""
        diagram = self._sequence_diagram(family) if isinstance(family, tuple) else family
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self.ambient().limit_construction(shape))

    def with_universal_data(
        self,
        diagram: Functor,
        apex: CategoryOfCategories.ElementType,
        limiting_cone: NaturalTransformation,
        mediator: Mediator,
    ) -> CategoryOfCategories.ElementType:
        """The chosen product from supplied universal data (POL-MATH-037)."""
        diagrams = self.diagrams(diagram.domain())
        assert diagram in diagrams
        assert limiting_cone in diagrams.morphism_category(1)(diagrams.constant(apex), diagram)
        presentation = limit_cones(diagram).with_universal_data(
            limiting_cone,
            lambda candidate: mediator(candidate.transformation()),
        )
        return self._retain(diagram, apex, presentation)

    def name(self) -> str:
        return "Products"

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.Products()"


class ColimitsCategory(ApexCategory):
    """``C.Colimits(I)``: chosen colimits of diagrams of one shape ``I``."""

    # The universal property of a colimit describes the morphisms *out* of the apex, so
    # it fixes nothing about a point of it.  That is the asymmetry with ``LimitsCategory``.
    class ElementType:
        """A point of a chosen colimit, which its universal property leaves unconstrained."""

    class MorphismType:
        """A morphism of ``C`` between two chosen colimits."""

    class ObjectType:
        """A chosen colimit apex. Its presentation is a limiting cone in the opposite category."""

        def diagram(self) -> Functor:
            return presenting_family(self).presentation(self).diagram().op()

        def index_category(self) -> Category:
            return self.diagram().domain()

        def cocone(self) -> NaturalTransformation:
            """The colimiting cocone ``diagram => constant(self)``."""
            return presenting_family(self).presentation(self).transformation().op()

        def injection(self, index: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            """The cocone component ``D(i) -> self``."""
            return presenting_family(self).presentation(self).leg(index).op()

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismCategory.ObjectType:
            """The mediating morphism to the apex of another cocone under the same diagram."""
            presentation = presenting_family(self).presentation(self)
            candidate = cocones(self.diagram())(candidate_cocone.op())
            return presentation.lift(candidate).op()

    def __init__(self, ambient: Category, shape: Category) -> None:
        self._shape = shape
        self._colimit_functor: MonoDict = MonoDict()
        super().__init__(ambient)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self.ambient())

    def __call__(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        """``C.Colimits(I)(diagram)``: the chosen colimit, through ``C.colimit_construction(I)``."""
        self.accepts(diagram, self._shape)
        return self.chosen(diagram, self.ambient().colimit_construction(self._shape))

    def with_universal_data(
        self,
        diagram: Functor,
        apex: CategoryOfCategories.ElementType,
        colimiting_cocone: NaturalTransformation,
        mediator: Mediator,
    ) -> CategoryOfCategories.ElementType:
        """The chosen colimit from supplied universal data (POL-MATH-037)."""
        assert diagram in self.diagrams()
        assert colimiting_cocone in self.diagrams().morphism_category(1)
        assert colimiting_cocone.domain() is diagram
        assert cocone_apex(colimiting_cocone) is apex
        presentation = colimit_cocones(diagram).with_universal_data(
            colimiting_cocone.op(),
            lambda candidate: mediator(candidate.transformation().op()).op(),
        )
        return self._retain(diagram, apex, presentation)

    def colimit_functor(self) -> Functor:
        """``Colim_I: Fun(I, C) -> C``, retained once."""
        if self not in self._colimit_functor:
            self._colimit_functor[self] = colimit_functor(self)
        return self._colimit_functor[self]

    def name(self) -> str:
        return f"Colimits({self._shape!r})"

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.Colimits({self._shape!r})"


class CoproductsCategory(ApexCategory):
    """``C.Coproducts()``: chosen coproducts over every discrete shape (POL-CAT-093)."""

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
            return presenting_family(self).presentation(self).diagram().op()

        def index_category(self) -> Category:
            return self.coproduct_summands().domain()

        def cocone(self) -> NaturalTransformation:
            """The coproduct cocone ``diagram => constant(self)``, whose components are the injections."""
            return presenting_family(self).presentation(self).transformation().op()

        def coproduct_injection(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            """``iota_i: X_i -> self`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            presentation = presenting_family(self).presentation(self)
            return presentation.leg(index).op()

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismCategory.ObjectType:
            """The mediating morphism to the apex of another cocone under the same diagram."""
            presentation = presenting_family(self).presentation(self)
            candidate = cocones(self.coproduct_summands())(candidate_cocone.op())
            return presentation.lift(candidate).op()

    def diagrams(self, shape: Category) -> Category:
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
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
    ) -> CategoryOfCategories.ElementType:
        """``C.Coproducts()(diagram)`` for a diagram over ``Discrete(S)``; ``C.Coproducts()((X_0, ..., X_n))`` for the sequence form."""
        diagram = family if family in self.universe().morphism_category(1) else self._sequence_diagram(tuple(family))
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self.ambient().colimit_construction(shape))

    def with_universal_data(
        self,
        diagram: Functor,
        apex: CategoryOfCategories.ElementType,
        colimiting_cocone: NaturalTransformation,
        mediator: Mediator,
    ) -> CategoryOfCategories.ElementType:
        """The chosen coproduct from supplied universal data (POL-MATH-037)."""
        diagrams = self.diagrams(diagram.domain())
        assert diagram in diagrams
        assert colimiting_cocone in diagrams.morphism_category(1)
        assert colimiting_cocone.domain() is diagram
        assert cocone_apex(colimiting_cocone) is apex
        presentation = colimit_cocones(diagram).with_universal_data(
            colimiting_cocone.op(),
            lambda candidate: mediator(candidate.transformation().op()).op(),
        )
        return self._retain(diagram, apex, presentation)

    def name(self) -> str:
        return "Coproducts"

    def __repr__(self) -> str:
        return f"{self.ambient()!r}.Coproducts()"


# ``indexed_by(P, family)``: the chosen apex ``P`` is indexed by the family's shape.
indexed_by = predicate("indexed_by")


def _indexed_by_shape(
    constructed: CategoryOfCategories.ElementType,
    family: Category,
    assumptions: Proposition,
) -> bool | None:
    if not is_placed(constructed, family.ambient()):
        return None
    diagrams = family.ambient().presenting_diagrams(constructed)
    return any(diagram.domain() is family.shape() for diagram in diagrams)


register_handler(indexed_by, _indexed_by_shape)


class DiscreteLimits(FullSubcategory[[MorphismCategory.ObjectType], []]):
    """``C.Limits(Discrete(S))``: the full subcategory of ``C.Products()`` on the products indexed by ``Discrete(S)``."""

    # Fixing the index adds no operation: ``product_projection(i)`` is already available
    # from ``C.Products()`` and is the same morphism here.
    class ObjectType:
        """A chosen product indexed by ``Discrete(S)``: the same object, with the same projections."""

    class ElementType:
        """A point of such a product."""

    class MorphismType:
        """A morphism of ``C`` between two such products."""

    def __init__(self, products: ProductsCategory, shape: Category) -> None:
        self._shape = shape
        self._limit_functor: MonoDict = MonoDict()
        self._limit_adjunction: CategoryOfCategories.ElementType | None = None
        self._image_factor: Functor | None = None
        super().__init__(products)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return self._ambient.diagrams(self._shape)

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return member(candidate, self._ambient) & indexed_by(candidate, self)

    def lowered(self, diagram: Functor) -> Functor:
        return self._ambient.lowered(diagram)

    def universal_data(self, diagram: Functor) -> UniversalPresentation:
        return self._ambient.universal_data(diagram)

    def presenting_diagrams(self, constructed: CategoryOfCategories.ElementType) -> tuple[Functor, ...]:
        return self._ambient.presenting_diagrams(constructed)

    def presentation(self, constructed: CategoryOfCategories.ElementType) -> UniversalPresentation:
        return self._ambient.presentation(constructed)

    def __call__(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        self._ambient.accepts(diagram, self._shape)
        constructed = self._ambient(diagram)
        refine(constructed, self)
        return constructed

    def with_universal_data(
        self,
        diagram: Functor,
        apex: CategoryOfCategories.ElementType,
        limiting_cone: NaturalTransformation,
        mediator: Mediator,
    ) -> CategoryOfCategories.ElementType:
        assert diagram in self.diagrams()
        constructed = self._ambient.with_universal_data(diagram, apex, limiting_cone, mediator)
        refine(constructed, self)
        return constructed

    def limit_functor(self) -> Functor:
        """``Lim_{Discrete(S)}: Fun(Discrete(S), C) -> C``, retained once."""
        if self not in self._limit_functor:
            self._limit_functor[self] = limit_functor(self)
            from sage_categories.cat.images import register_full_image

            register_full_image(self._limit_functor[self], self)
            self._ambient.retain_full_image(self)
        return self._limit_functor[self]

    def defining_functor(self) -> Functor:
        return self.limit_functor()

    def factorization(self) -> tuple[Functor, Functor]:
        if self._image_factor is None:
            self._image_factor = Fun(self.diagrams(), self)(
                lambda diagram: self(diagram),
                lambda transformation: induced_limit_morphism(self, transformation),
            )
        inclusion = self._ambient.subcategory_monomorphism() * self.subcategory_monomorphism()
        return self._image_factor, inclusion

    def adjunction(self) -> CategoryOfCategories.ElementType:
        """Return the selected adjunction ``Delta_I |- Lim_I``."""
        if self._limit_adjunction is None:
            self._limit_adjunction = limit_adjunction(self)
        return self._limit_adjunction

    def name(self) -> str:
        return f"Limits({self._shape!r})"

    def __repr__(self) -> str:
        return f"{self.diagrams().codomain()!r}.Limits({self._shape!r})"


class DiscreteColimits(FullSubcategory[[MorphismCategory.ObjectType], []]):
    """``C.Colimits(Discrete(S))``: the full subcategory of ``C.Coproducts()`` on the coproducts indexed by ``Discrete(S)``."""

    # Fixing the index adds no operation, as for ``DiscreteLimits``.
    class ObjectType:
        """A chosen coproduct indexed by ``Discrete(S)``: the same object, with the same injections."""

    class ElementType:
        """A point of such a coproduct."""

    class MorphismType:
        """A morphism of ``C`` between two such coproducts."""

    def __init__(self, coproducts: CoproductsCategory, shape: Category) -> None:
        self._shape = shape
        self._colimit_functor: MonoDict = MonoDict()
        super().__init__(coproducts)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return self._ambient.diagrams(self._shape)

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return member(candidate, self._ambient) & indexed_by(candidate, self)

    def lowered(self, diagram: Functor) -> Functor:
        return self._ambient.lowered(diagram)

    def universal_data(self, diagram: Functor) -> UniversalPresentation:
        return self._ambient.universal_data(diagram)

    def presenting_diagrams(self, constructed: CategoryOfCategories.ElementType) -> tuple[Functor, ...]:
        return self._ambient.presenting_diagrams(constructed)

    def presentation(self, constructed: CategoryOfCategories.ElementType) -> UniversalPresentation:
        return self._ambient.presentation(constructed)

    def __call__(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        self._ambient.accepts(diagram, self._shape)
        constructed = self._ambient(diagram)
        refine(constructed, self)
        return constructed

    def with_universal_data(
        self,
        diagram: Functor,
        apex: CategoryOfCategories.ElementType,
        colimiting_cocone: NaturalTransformation,
        mediator: Mediator,
    ) -> CategoryOfCategories.ElementType:
        assert diagram in self.diagrams()
        constructed = self._ambient.with_universal_data(diagram, apex, colimiting_cocone, mediator)
        refine(constructed, self)
        return constructed

    def colimit_functor(self) -> Functor:
        """``Colim_{Discrete(S)}: Fun(Discrete(S), C) -> C``, retained once."""
        if self not in self._colimit_functor:
            self._colimit_functor[self] = colimit_functor(self)
        return self._colimit_functor[self]

    def name(self) -> str:
        return f"Colimits({self._shape!r})"

    def __repr__(self) -> str:
        return f"{self.diagrams().codomain()!r}.Colimits({self._shape!r})"


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
    target = constructed_data(family, transformation.codomain())
    assert isinstance(source, ConeCategory.ObjectType)
    assert isinstance(target, LimitConesCategory.ObjectType)
    induced_cone = cone(
        target.diagram(),
        source.apex(),
        lambda vertex: transformation.component(vertex) * source.leg(vertex),
    )
    return target.lift(cones(target.diagram())(induced_cone))


def induced_colimit_morphism(family: Category, transformation: NaturalTransformation) -> MorphismCategory.ObjectType:
    """``Colim(eta): L_D -> L_D'`` for ``eta: D => D'``: the mediator of the cocone ``iota'_i after eta_i``."""
    source = constructed_data(family, transformation.domain())
    target = constructed_data(family, transformation.codomain())
    dual_transformation = transformation.op()
    induced_cone = cone(
        source.diagram(),
        target.apex(),
        lambda vertex: dual_transformation.component(vertex) * target.leg(vertex),
    )
    return source.lift(cones(source.diagram())(induced_cone)).op()


def limit_functor(family: Category) -> Functor:
    """``Lim_I: Fun(I, C) -> C`` for a limit family: the chosen limit and the induced morphism between two of them."""
    return Fun(family.diagrams(), family.diagrams().codomain())(
        lambda diagram: family(diagram),
        lambda transformation: induced_limit_morphism(family, transformation),
    )


def colimit_functor(family: Category) -> Functor:
    """``Colim_I: Fun(I, C) -> C`` for a colimit family."""
    return Fun(family.diagrams(), family.diagrams().codomain())(
        lambda diagram: family(diagram),
        lambda transformation: induced_colimit_morphism(family, transformation),
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


# -- the families owned once on ``Category`` (POL-CAT-050) ---------------------------


def limits(ambient: Category, shape: Category) -> Category:
    """``C.Limits(I)``: the full subcategory of ``C.Products()`` for a discrete shape, else the general family."""
    family = DiscreteLimits(ambient.Products(), shape) if is_discrete(shape) else LimitsCategory(ambient, shape)
    family.limit_functor()
    return family


def colimits(ambient: Category, shape: Category) -> Category:
    """``C.Colimits(I)``: the full subcategory of ``C.Coproducts()`` for a discrete shape, else the general family."""
    if is_discrete(shape):
        return DiscreteColimits(ambient.Coproducts(), shape)
    return ColimitsCategory(ambient, shape)
