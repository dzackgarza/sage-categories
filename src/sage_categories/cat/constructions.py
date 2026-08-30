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
from typing import TYPE_CHECKING, NamedTuple

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import FullSubcategory
from sage_categories.cat.shapes import is_discrete
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate, Proposition
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


# -- cones and cocones as natural transformations -------------------------------------
#
# A cone over ``D: I -> C`` with apex ``N`` is a natural transformation
# ``constant(N) => D``; a cocone is ``D => constant(N)`` (Mathlib
# ``CategoryTheory.Limits.Cone``, ``Cocone``; inspected 2026-08-26).


def cone(
    diagram: Functor,
    apex: CategoryOfCategories.ElementType,
    components: Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType],
) -> NaturalTransformation:
    """The cone over ``diagram`` with the given apex and components ``i |-> N -> D(i)``."""
    functors = Fun(diagram.domain(), diagram.codomain())
    return functors.morphism_category(1)(functors.constant(apex), diagram)(components)


def cocone(
    diagram: Functor,
    apex: CategoryOfCategories.ElementType,
    components: Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType],
) -> NaturalTransformation:
    """The cocone under ``diagram`` with the given apex and components ``i |-> D(i) -> N``."""
    functors = Fun(diagram.domain(), diagram.codomain())
    return functors.morphism_category(1)(diagram, functors.constant(apex))(components)


def cone_apex(transformation: NaturalTransformation) -> CategoryOfCategories.ElementType:
    """The apex ``N`` of a cone ``constant(N) => D``: the value of its retained constant domain."""
    constant = transformation.domain()
    return Fun(constant.domain(), constant.codomain()).constant_value(constant)


def cocone_apex(transformation: NaturalTransformation) -> CategoryOfCategories.ElementType:
    """The apex ``N`` of a cocone ``D => constant(N)``."""
    constant = transformation.codomain()
    return Fun(constant.domain(), constant.codomain()).constant_value(constant)


def vertex_of(shape: Category, index: CategoryOfCategories.ElementType | Hashable) -> CategoryOfCategories.ElementType:
    """An object of a shape, given directly or as a datum of its object set."""
    if index in shape:
        return index
    return shape.object_at(shape.object_set().point(index))


class UniversalData(NamedTuple):
    """What one diagram's construction retains: the constructed object, the diagram, its limiting cone or cocone, and its mediator rule."""

    constructed: CategoryOfCategories.ElementType
    diagram: Functor
    transformation: NaturalTransformation
    mediator: Mediator


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
        super().__init__(ambient)

    # -- the diagrams this family accepts ----------------------------------------------

    def accepts(self, diagram: Functor, shape: Category) -> None:
        """A diagram of shape ``shape`` into ``C`` or into a subcategory of ``C`` (a diagram into ``Sets().Uncountable()`` is a diagram into ``Sets()``)."""
        assert diagram in self.universe().morphism_category(1) and diagram.domain() is shape, f"{diagram!r} is not a diagram of shape {shape!r}"
        assert is_subcategory(diagram.codomain(), self.narrowing_base()), f"{diagram!r} does not land in {self.narrowing_base()!r}"

    def lowered(self, diagram: Functor) -> Functor:
        """The diagram as a diagram in ``C``: itself, or its composite with the subcategory monomorphism of its codomain, retained per diagram."""
        ambient = self.narrowing_base()
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

    def universal_data(self, diagram: Functor) -> UniversalData:
        """The universal data retained for ``diagram``: its diagram, cone or cocone, and mediator rule."""
        assert diagram in self._data, f"{self!r} retains no construction of {diagram!r}"
        return self._data[diagram]

    def presenting_diagrams(self, constructed: CategoryOfCategories.ElementType) -> tuple[Functor, ...]:
        """The diagrams this family constructed ``constructed`` from, in construction order; none for an object it did not construct."""
        return self._source_diagrams[constructed] if constructed in self._source_diagrams else ()

    def presentation(self, constructed: CategoryOfCategories.ElementType) -> UniversalData:
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
        constructed: CategoryOfCategories.ElementType,
        data: UniversalData,
    ) -> CategoryOfCategories.ElementType:
        """Place ``constructed`` in this family, retain the universal data of its diagram, and return it."""
        ambient = self.narrowing_base()
        assert constructed in ambient, f"{constructed!r} is not an object of {ambient!r}"
        assert data.diagram not in self._data, f"{self!r} already retains the construction of {data.diagram!r}"
        retained = self._source_diagrams[constructed] if constructed in self._source_diagrams else ()
        self._data[data.diagram] = data
        self._constructed[data.diagram] = constructed
        self._source_diagrams[constructed] = (*retained, data.diagram)
        refine(constructed, self)
        return constructed


class LimitsCategory(ApexCategory):
    """``C.Limits(I)``: chosen limits of diagrams of one shape ``I``."""

    # A point of a chosen limit is a cone over the diagram with apex ``1_C``; the
    # mediator of a cone is a morphism of ``C`` and not a further kind.
    class ElementType:
        """A point of a chosen limit: a cone over the diagram with apex ``1_C``."""

    class MorphismType:
        """A morphism of ``C`` between two chosen limits; the mediator of a cone is one of these."""

    class ObjectType:
        """A chosen limit: an object of ``C`` whose family retains its diagram, limiting cone, and mediator rule."""

        def diagram(self) -> Functor:
            return presenting_family(self).presentation(self).diagram

        def index_category(self) -> Category:
            return presenting_family(self).presentation(self).diagram.domain()

        def cone(self) -> NaturalTransformation:
            """The limiting cone ``constant(self) => diagram``."""
            return presenting_family(self).presentation(self).transformation

        def projection(self, index: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            """The cone component ``self -> D(i)``."""
            return presenting_family(self).presentation(self).transformation.component(index)

        def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismCategory.ObjectType:
            """The mediating morphism from the apex of another cone over the same diagram."""
            data = presenting_family(self).presentation(self)
            assert candidate_cone.codomain() is data.diagram, f"{candidate_cone!r} is not a cone over {data.diagram!r}"
            return data.mediator(candidate_cone)

    def __init__(self, ambient: Category, shape: Category) -> None:
        self._shape = shape
        self._limit_functor: MonoDict = MonoDict()
        super().__init__(ambient)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self.narrowing_base())

    def __call__(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        """``C.Limits(I)(diagram)``: the chosen limit, through ``C.limit_construction(I)``."""
        self.accepts(diagram, self._shape)
        return self.chosen(diagram, self.narrowing_base().limit_construction(self._shape))

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
        return self._retain(apex, UniversalData(apex, diagram, limiting_cone, mediator))

    def limit_functor(self) -> Functor:
        """``Lim_I: Fun(I, C) -> C``, retained once."""
        if self not in self._limit_functor:
            self._limit_functor[self] = limit_functor(self)
        return self._limit_functor[self]

    def name(self) -> str:
        return f"Limits({self._shape!r})"

    def __repr__(self) -> str:
        return f"{self.narrowing_base()!r}.Limits({self._shape!r})"


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
            return presenting_family(self).presentation(self).diagram

        def index_category(self) -> Category:
            return presenting_family(self).presentation(self).diagram.domain()

        def cone(self) -> NaturalTransformation:
            """The product cone ``constant(self) => diagram``, whose components are the projections."""
            return presenting_family(self).presentation(self).transformation

        def product_projection(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            """``pi_i: self -> X_i`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            data = presenting_family(self).presentation(self)
            return data.transformation.component(vertex_of(data.diagram.domain(), index))

        def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismCategory.ObjectType:
            """The mediating morphism from the apex of another cone over the same diagram."""
            data = presenting_family(self).presentation(self)
            assert candidate_cone.codomain() is data.diagram, f"{candidate_cone!r} is not a cone over {data.diagram!r}"
            return data.mediator(candidate_cone)

    def diagrams(self, shape: Category) -> Category:
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        return Fun(shape, self.narrowing_base())

    def _sequence_diagram(self, sequence: tuple[CategoryOfCategories.ElementType, ...]) -> Functor:
        """The sequence diagram on objects of ``C``, retained per sequence."""
        ambient = self.narrowing_base()
        for member_object in sequence:
            assert member_object in ambient, f"{member_object!r} is not an object of {ambient!r}"
        return from_sequence(ambient, sequence)

    def __call__(
        self,
        family: Functor | tuple[CategoryOfCategories.ElementType, ...],
    ) -> CategoryOfCategories.ElementType:
        """``C.Products()(diagram)`` for a diagram over ``Discrete(S)``; ``C.Products()((X_0, ..., X_n))`` for the sequence form."""
        diagram = family if family in self.universe().morphism_category(1) else self._sequence_diagram(tuple(family))
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self.narrowing_base().limit_construction(shape))

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
        return self._retain(apex, UniversalData(apex, diagram, limiting_cone, mediator))

    def name(self) -> str:
        return "Products"

    def __repr__(self) -> str:
        return f"{self.narrowing_base()!r}.Products()"


class ColimitsCategory(ApexCategory):
    """``C.Colimits(I)``: chosen colimits of diagrams of one shape ``I``."""

    # The universal property of a colimit describes the morphisms *out* of the apex, so
    # it fixes nothing about a point of it.  That is the asymmetry with ``LimitsCategory``.
    class ElementType:
        """A point of a chosen colimit, which its universal property leaves unconstrained."""

    class MorphismType:
        """A morphism of ``C`` between two chosen colimits."""

    class ObjectType:
        """A chosen colimit: an object of ``C`` whose family retains its diagram, colimiting cocone, and mediator rule."""

        def diagram(self) -> Functor:
            return presenting_family(self).presentation(self).diagram

        def index_category(self) -> Category:
            return presenting_family(self).presentation(self).diagram.domain()

        def cocone(self) -> NaturalTransformation:
            """The colimiting cocone ``diagram => constant(self)``."""
            return presenting_family(self).presentation(self).transformation

        def injection(self, index: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            """The cocone component ``D(i) -> self``."""
            return presenting_family(self).presentation(self).transformation.component(index)

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismCategory.ObjectType:
            """The mediating morphism to the apex of another cocone under the same diagram."""
            data = presenting_family(self).presentation(self)
            assert candidate_cocone.domain() is data.diagram, f"{candidate_cocone!r} is not a cocone under {data.diagram!r}"
            return data.mediator(candidate_cocone)

    def __init__(self, ambient: Category, shape: Category) -> None:
        self._shape = shape
        self._colimit_functor: MonoDict = MonoDict()
        super().__init__(ambient)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self.narrowing_base())

    def __call__(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        """``C.Colimits(I)(diagram)``: the chosen colimit, through ``C.colimit_construction(I)``."""
        self.accepts(diagram, self._shape)
        return self.chosen(diagram, self.narrowing_base().colimit_construction(self._shape))

    def with_universal_data(
        self,
        diagram: Functor,
        apex: CategoryOfCategories.ElementType,
        colimiting_cocone: NaturalTransformation,
        mediator: Mediator,
    ) -> CategoryOfCategories.ElementType:
        """The chosen colimit from supplied universal data (POL-MATH-037)."""
        assert diagram in self.diagrams()
        assert colimiting_cocone in self.diagrams().morphism_category(1)(diagram, self.diagrams().constant(apex))
        return self._retain(apex, UniversalData(apex, diagram, colimiting_cocone, mediator))

    def colimit_functor(self) -> Functor:
        """``Colim_I: Fun(I, C) -> C``, retained once."""
        if self not in self._colimit_functor:
            self._colimit_functor[self] = colimit_functor(self)
        return self._colimit_functor[self]

    def name(self) -> str:
        return f"Colimits({self._shape!r})"

    def __repr__(self) -> str:
        return f"{self.narrowing_base()!r}.Colimits({self._shape!r})"


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
            return presenting_family(self).presentation(self).diagram

        def index_category(self) -> Category:
            return presenting_family(self).presentation(self).diagram.domain()

        def cocone(self) -> NaturalTransformation:
            """The coproduct cocone ``diagram => constant(self)``, whose components are the injections."""
            return presenting_family(self).presentation(self).transformation

        def coproduct_injection(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            """``iota_i: X_i -> self`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            data = presenting_family(self).presentation(self)
            return data.transformation.component(vertex_of(data.diagram.domain(), index))

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismCategory.ObjectType:
            """The mediating morphism to the apex of another cocone under the same diagram."""
            data = presenting_family(self).presentation(self)
            assert candidate_cocone.domain() is data.diagram, f"{candidate_cocone!r} is not a cocone under {data.diagram!r}"
            return data.mediator(candidate_cocone)

    def diagrams(self, shape: Category) -> Category:
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        return Fun(shape, self.narrowing_base())

    def _sequence_diagram(self, sequence: tuple[CategoryOfCategories.ElementType, ...]) -> Functor:
        """The sequence diagram on objects of ``C``, retained per sequence."""
        ambient = self.narrowing_base()
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
        return self.chosen(diagram, self.narrowing_base().colimit_construction(shape))

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
        assert colimiting_cocone in diagrams.morphism_category(1)(diagram, diagrams.constant(apex))
        return self._retain(apex, UniversalData(apex, diagram, colimiting_cocone, mediator))

    def name(self) -> str:
        return "Coproducts"

    def __repr__(self) -> str:
        return f"{self.narrowing_base()!r}.Coproducts()"


# ``indexed_by(P, family)``: the chosen apex ``P`` is indexed by the family's shape.
indexed_by = Predicate("indexed_by", 2, False)


def _indexed_by_shape(constructed: CategoryOfCategories.ElementType, family: Category) -> Decision:
    if not is_placed(constructed, family.ambient()):
        return Unknown
    diagrams = family.ambient().presenting_diagrams(constructed)
    return any(diagram.domain() is family.shape() for diagram in diagrams)


indexed_by.register_handler(_indexed_by_shape)


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
        super().__init__(products)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return self._ambient.diagrams(self._shape)

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return member(candidate, self._ambient) & indexed_by(candidate, self)

    def lowered(self, diagram: Functor) -> Functor:
        return self._ambient.lowered(diagram)

    def universal_data(self, diagram: Functor) -> UniversalData:
        return self._ambient.universal_data(diagram)

    def presenting_diagrams(self, constructed: CategoryOfCategories.ElementType) -> tuple[Functor, ...]:
        return self._ambient.presenting_diagrams(constructed)

    def presentation(self, constructed: CategoryOfCategories.ElementType) -> UniversalData:
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
        return self._limit_functor[self]

    def name(self) -> str:
        return f"Limits({self._shape!r})"

    def __repr__(self) -> str:
        return f"{self.narrowing_base()!r}.Limits({self._shape!r})"


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

    def universal_data(self, diagram: Functor) -> UniversalData:
        return self._ambient.universal_data(diagram)

    def presenting_diagrams(self, constructed: CategoryOfCategories.ElementType) -> tuple[Functor, ...]:
        return self._ambient.presenting_diagrams(constructed)

    def presentation(self, constructed: CategoryOfCategories.ElementType) -> UniversalData:
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
        return f"{self.narrowing_base()!r}.Colimits({self._shape!r})"


# -- the construction functors -------------------------------------------------------------


def constructed_data(family: Category, diagram: Functor) -> UniversalData:
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
    induced_cone = cone(target.diagram, source.constructed, lambda vertex: transformation.component(vertex) * source.transformation.component(vertex))
    return target.mediator(induced_cone)


def induced_colimit_morphism(family: Category, transformation: NaturalTransformation) -> MorphismCategory.ObjectType:
    """``Colim(eta): L_D -> L_D'`` for ``eta: D => D'``: the mediator of the cocone ``iota'_i after eta_i``."""
    source = constructed_data(family, transformation.domain())
    target = constructed_data(family, transformation.codomain())
    induced_cocone = cocone(source.diagram, target.constructed, lambda vertex: target.transformation.component(vertex) * transformation.component(vertex))
    return source.mediator(induced_cocone)


def limit_functor(family: Category) -> Functor:
    """``Lim_I: Fun(I, C) -> C`` for a limit family: the chosen limit and the induced morphism between two of them."""
    return Fun(family.diagrams(), family.narrowing_base())(
        lambda diagram: family(diagram),
        lambda transformation: induced_limit_morphism(family, transformation),
    )


def colimit_functor(family: Category) -> Functor:
    """``Colim_I: Fun(I, C) -> C`` for a colimit family."""
    return Fun(family.diagrams(), family.narrowing_base())(
        lambda diagram: family(diagram),
        lambda transformation: induced_colimit_morphism(family, transformation),
    )


# -- the families owned once on ``Category`` (POL-CAT-050) ---------------------------


def limits(ambient: Category, shape: Category) -> Category:
    """``C.Limits(I)``: the full subcategory of ``C.Products()`` for a discrete shape, else the general family."""
    if is_discrete(shape):
        return DiscreteLimits(ambient.Products(), shape)
    return LimitsCategory(ambient, shape)


def colimits(ambient: Category, shape: Category) -> Category:
    """``C.Colimits(I)``: the full subcategory of ``C.Coproducts()`` for a discrete shape, else the general family."""
    if is_discrete(shape):
        return DiscreteColimits(ambient.Coproducts(), shape)
    return ColimitsCategory(ambient, shape)
