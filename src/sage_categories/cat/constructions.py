"""Universal constructions as full subcategories of chosen apexes (D02, D10, D16).

For a category ``C`` and a shape ``I in Cat()``, ``C.Limits(I)`` is the full
subcategory of ``C`` whose objects are the chosen limits of diagrams ``I -> C``
(POL-CAT-046).  Its one selected functor is the inclusion
``Fun(C.Limits(I), C).FullyFaithful().inclusion()``, so a chosen apex is an object
of ``C`` with the whole surface of ``C`` and, from its family, its presentation:
the family retains, by identity of the apex, the diagram, the limiting cone (a
natural transformation from the constant diagram at the apex), and the mediator
rule (POL-FUN-008), and by identity of the diagram the apex it chose.  Its
morphisms are the morphisms of ``C`` between chosen apexes.  ``C.Colimits(I)`` is
dual with cocones.

``C.Products()`` is the family of chosen products over every discrete shape, with
the sequence convenience ``(X_0, ..., X_n)`` and ``product_projection(i)``
(POL-CAT-093); ``C.Limits(Discrete(S))`` is its full subcategory on the products
indexed by ``Discrete(S)``, since a limit over a discrete shape is a product by
definition (Mathlib ``CategoryTheory.Limits.HasProduct``: ``HasLimit
(Discrete.functor f)``; inspected 2026-08-26).  ``C.Coproducts()`` and
``C.Colimits(Discrete(S))`` are dual.

Constructing an object of ``C.Limits(I)`` calls the category-owned
``C.limit_construction(I)``, which fails loudly unless ``C`` owns an ``I``-limit
construction; ``with_universal_data`` refines a supplied apex from supplied data,
trusted by the writer (POL-MATH-037).  The construction category exists for every
supplied shape without asserting completeness (POL-CAT-051).

Each family retains its construction functor ``Lim_I: Fun(I, C) -> C``, acting on
a morphism of diagrams by the induced morphism of apexes: the mediator of the
cone whose components are ``eta_i`` after the projections (Mathlib
``CategoryTheory.Limits.limMap``; inspected 2026-08-26).
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import NamedTuple

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.properties import FullSubcategory
from sage_categories.cat.shapes import index_set_of, is_discrete
from sage_categories.kernel.caches import SequenceTable
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate, Proposition
from sage_categories.kernel.refinement import is_placed, is_subcategory, refine
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory, Role

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
    "vertex_of",
]

type Mediator = Callable[[NaturalTransformation], MorphismOfCategory]
type Construction = Callable[[Functor], ObjectOfCategory]


# -- cones and cocones as natural transformations -------------------------------------
#
# A cone over ``D: I -> C`` with apex ``N`` is a natural transformation
# ``constant(N) => D``; a cocone is ``D => constant(N)`` (Mathlib
# ``CategoryTheory.Limits.Cone``, ``Cocone``; inspected 2026-08-26).


def cone(diagram: Functor, apex: ObjectOfCategory, components: Callable[[ObjectOfCategory], MorphismOfCategory]) -> NaturalTransformation:
    """The cone over ``diagram`` with the given apex and components ``i |-> N -> D(i)``."""
    functors = Fun(diagram.domain(), diagram.codomain())
    return functors.morphism_category(1)(functors.constant(apex), diagram)(components)


def cocone(diagram: Functor, apex: ObjectOfCategory, components: Callable[[ObjectOfCategory], MorphismOfCategory]) -> NaturalTransformation:
    """The cocone under ``diagram`` with the given apex and components ``i |-> D(i) -> N``."""
    functors = Fun(diagram.domain(), diagram.codomain())
    return functors.morphism_category(1)(diagram, functors.constant(apex))(components)


def cone_apex(transformation: NaturalTransformation) -> ObjectOfCategory:
    """The apex ``N`` of a cone ``constant(N) => D``: the value of its retained constant domain."""
    constant = transformation.domain()
    return Fun(constant.domain(), constant.codomain()).constant_value(constant)


def cocone_apex(transformation: NaturalTransformation) -> ObjectOfCategory:
    """The apex ``N`` of a cocone ``D => constant(N)``."""
    constant = transformation.codomain()
    return Fun(constant.domain(), constant.codomain()).constant_value(constant)


def vertex_of(shape: Category, index: ObjectOfCategory | Hashable) -> ObjectOfCategory:
    """An object of a discrete shape, given directly or as a datum of its index set."""
    if index in shape:
        return index
    return shape(index_set_of(shape).point(index))


class UniversalData(NamedTuple):
    """What a family retains for one chosen apex: its diagram, its limiting cone or cocone, and its mediator rule."""

    diagram: Functor
    transformation: NaturalTransformation
    mediator: Mediator


# -- the presentation roles ----------------------------------------------------------------
#
# The local object role of a family reads the universal data the family retained
# for the apex (POL-CAT-046).  Each family builds its role once, closed over
# itself, so a chosen apex reaches its own family's tables.


def limit_presentation_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class LimitPresentation(ObjectOfCategory):
        """A chosen limit: an object of ``C`` whose family retains its diagram, limiting cone, and mediator rule."""

        def diagram(self) -> Functor:
            return family.universal_data(self).diagram

        def index_category(self) -> Category:
            return family.universal_data(self).diagram.domain()

        def cone(self) -> NaturalTransformation:
            """The limiting cone ``constant(apex) => diagram``."""
            return family.universal_data(self).transformation

        def projection(self, index: ObjectOfCategory) -> MorphismOfCategory:
            """The cone component ``apex -> D(i)``."""
            return family.universal_data(self).transformation.component(index)

        def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism from the apex of another cone over the same diagram."""
            data = family.universal_data(self)
            assert candidate_cone.codomain() is data.diagram, f"{candidate_cone!r} is not a cone over {data.diagram!r}"
            return data.mediator(candidate_cone)

    return LimitPresentation


def product_presentation_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class ProductPresentation(ObjectOfCategory):
        """A chosen product over a discrete shape: an object of ``C`` whose family retains its projections and mediator rule."""

        def diagram(self) -> Functor:
            return family.universal_data(self).diagram

        def index_category(self) -> Category:
            return family.universal_data(self).diagram.domain()

        def cone(self) -> NaturalTransformation:
            """The product cone ``constant(apex) => diagram``, whose components are the projections."""
            return family.universal_data(self).transformation

        def product_projection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """``pi_i: apex -> X_i`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            data = family.universal_data(self)
            return data.transformation.component(vertex_of(data.diagram.domain(), index))

        def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism from the apex of another cone over the same diagram."""
            data = family.universal_data(self)
            assert candidate_cone.codomain() is data.diagram, f"{candidate_cone!r} is not a cone over {data.diagram!r}"
            return data.mediator(candidate_cone)

        def subobject_projection(self, monomorphism: MorphismOfCategory, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """The component ``pi_i after j`` of a subobject ``j: S -> apex``: the composition rule of POL-CAT-094."""
            assert monomorphism.codomain() is self, f"{monomorphism!r} does not present a subobject of {self!r}"
            assert monomorphism in family.apex_category().morphism_category(1).Monomorphisms(), f"{monomorphism!r} is not a monomorphism"
            return self.product_projection(index) * monomorphism

    return ProductPresentation


def colimit_presentation_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class ColimitPresentation(ObjectOfCategory):
        """A chosen colimit: an object of ``C`` whose family retains its diagram, colimiting cocone, and mediator rule."""

        def diagram(self) -> Functor:
            return family.universal_data(self).diagram

        def index_category(self) -> Category:
            return family.universal_data(self).diagram.domain()

        def cocone(self) -> NaturalTransformation:
            """The colimiting cocone ``diagram => constant(apex)``."""
            return family.universal_data(self).transformation

        def injection(self, index: ObjectOfCategory) -> MorphismOfCategory:
            """The cocone component ``D(i) -> apex``."""
            return family.universal_data(self).transformation.component(index)

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism to the apex of another cocone under the same diagram."""
            data = family.universal_data(self)
            assert candidate_cocone.domain() is data.diagram, f"{candidate_cocone!r} is not a cocone under {data.diagram!r}"
            return data.mediator(candidate_cocone)

    return ColimitPresentation


def coproduct_presentation_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class CoproductPresentation(ObjectOfCategory):
        """A chosen coproduct over a discrete shape: an object of ``C`` whose family retains its injections and mediator rule."""

        def diagram(self) -> Functor:
            return family.universal_data(self).diagram

        def index_category(self) -> Category:
            return family.universal_data(self).diagram.domain()

        def cocone(self) -> NaturalTransformation:
            """The coproduct cocone ``diagram => constant(apex)``, whose components are the injections."""
            return family.universal_data(self).transformation

        def coproduct_injection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """``iota_i: X_i -> apex`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            data = family.universal_data(self)
            return data.transformation.component(vertex_of(data.diagram.domain(), index))

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism to the apex of another cocone under the same diagram."""
            data = family.universal_data(self)
            assert candidate_cocone.domain() is data.diagram, f"{candidate_cocone!r} is not a cocone under {data.diagram!r}"
            return data.mediator(candidate_cocone)

    return CoproductPresentation


# -- construction families --------------------------------------------------------------------


class ApexCategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):
    """A full subcategory of ``C`` on chosen apexes; it retains their universal data by identity."""

    def __init__(self, apex_category: Category[MorphismData, TwoMorphismData]) -> None:
        self._apex_category = apex_category
        self._data: MonoDict = MonoDict()
        self._apexes: MonoDict = MonoDict()
        self._lowered: MonoDict = MonoDict()
        self._object_role = self.presentation_role()
        super().__init__(apex_category)

    def apex_category(self) -> Category[MorphismData, TwoMorphismData]:
        """The category ``C`` in which the apexes live."""
        return self._apex_category

    def presentation_role(self) -> type[ObjectOfCategory]:
        raise AssertionError(f"{self!r} declares no presentation role")

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        if role is Role.OBJECT:
            return self._object_role
        return super().local_role_class(role)

    def accepts(self, diagram: Functor, shape: Category) -> None:
        """A diagram of shape ``shape`` into ``C`` or into a subcategory of ``C`` (a diagram into ``Sets().Uncountable()`` is a diagram into ``Sets()``)."""
        assert diagram in self.category().morphism_category(1) and diagram.domain() is shape, f"{diagram!r} is not a diagram of shape {shape!r}"
        assert is_subcategory(diagram.codomain(), self._apex_category), f"{diagram!r} does not land in {self._apex_category!r}"

    def lowered(self, diagram: Functor) -> Functor:
        """The diagram as a diagram in ``C``: itself, or its composite with the inclusion of its codomain, retained per diagram."""
        codomain = diagram.codomain()
        if codomain is self._apex_category:
            return diagram
        assert is_subcategory(codomain, self._apex_category), f"{codomain!r} is not a declared subcategory of {self._apex_category!r}"
        if diagram not in self._lowered:
            self._lowered[diagram] = Fun(codomain, self._apex_category).FullyFaithful().inclusion() * diagram
        return self._lowered[diagram]

    # -- the retained universal data --------------------------------------------------

    def retains(self, apex: ObjectOfCategory) -> bool:
        return apex in self._data

    def universal_data(self, apex: ObjectOfCategory) -> UniversalData:
        """The diagram, cone or cocone, and mediator rule retained for a chosen apex."""
        assert apex in self._data, f"{self!r} retains no universal data for {apex!r}"
        return self._data[apex]

    def has_chosen_apex(self, diagram: Functor) -> bool:
        return diagram in self._apexes

    def chosen_apex(self, diagram: Functor) -> ObjectOfCategory:
        """The apex this family chose for ``diagram``."""
        assert diagram in self._apexes, f"{self!r} retains no chosen apex for {diagram!r}"
        return self._apexes[diagram]

    def chosen(self, diagram: Functor, construction: Construction) -> ObjectOfCategory:
        """The chosen apex of ``diagram``, constructed once; the diagram and its lowering share it."""
        if not self.has_chosen_apex(diagram):
            construction(diagram)
            lowered = self.lowered(diagram)
            if lowered is not diagram:
                self._apexes[diagram] = self.chosen_apex(lowered)
        return self.chosen_apex(diagram)

    def _retain(self, apex: ObjectOfCategory, data: UniversalData) -> ObjectOfCategory:
        """Retain the universal data of ``apex`` and refine the same value into this family."""
        assert apex in self._apex_category, f"{apex!r} is not an object of {self._apex_category!r}"
        assert data.diagram not in self._apexes, f"{self!r} already chose an apex for {data.diagram!r}"
        assert apex not in self._data, f"{self!r} already retains universal data for {apex!r}"
        self._apexes[data.diagram] = apex
        self._data[apex] = data
        refine(apex, self)
        return apex


class LimitsCategory(ApexCategory):
    """``C.Limits(I)``: chosen limits of diagrams of one shape ``I``."""

    def __init__(self, apex_category: Category, shape: Category) -> None:
        self._shape = shape
        self._limit_functor: MonoDict = MonoDict()
        super().__init__(apex_category)

    def presentation_role(self) -> type[ObjectOfCategory]:
        return limit_presentation_role(self)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self._apex_category)

    def __call__(self, diagram: Functor) -> ObjectOfCategory:
        """``C.Limits(I)(diagram)``: the chosen limit, through ``C.limit_construction(I)``."""
        self.accepts(diagram, self._shape)
        return self.chosen(diagram, self._apex_category.limit_construction(self._shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        """The chosen limit from supplied universal data; the writer asserts the universal property (POL-MATH-037)."""
        assert diagram in self.diagrams()
        assert limiting_cone in self.diagrams().morphism_category(1)(self.diagrams().constant(apex), diagram)
        return self._retain(apex, UniversalData(diagram, limiting_cone, mediator))

    def limit_functor(self) -> Functor:
        """``Lim_I: Fun(I, C) -> C``, retained once."""
        if self not in self._limit_functor:
            self._limit_functor[self] = limit_functor(self)
        return self._limit_functor[self]

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Limits({self._shape!r})"


class ProductsCategory(ApexCategory):
    """``C.Products()``: chosen products over every discrete shape (D16)."""

    def __init__(self, apex_category: Category) -> None:
        self._sequences = SequenceTable()
        super().__init__(apex_category)

    def presentation_role(self) -> type[ObjectOfCategory]:
        return product_presentation_role(self)

    def diagrams(self, shape: Category) -> Category:
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        return Fun(shape, self._apex_category)

    def _sequence_diagram(self, sequence: tuple[ObjectOfCategory, ...]) -> Functor:
        """The sequence diagram on objects of ``C``, retained per sequence."""
        if sequence not in self._sequences:
            for member_object in sequence:
                assert member_object in self._apex_category, f"{member_object!r} is not an object of {self._apex_category!r}"
            self._sequences[sequence] = from_sequence(self._apex_category, sequence)
        return self._sequences[sequence]

    def __call__(self, family: Functor | tuple[ObjectOfCategory, ...]) -> ObjectOfCategory:
        """``C.Products()(diagram)`` for a diagram over ``Discrete(S)``; ``C.Products()((X_0, ..., X_n))`` for the sequence form."""
        diagram = family if family in self.category().morphism_category(1) else self._sequence_diagram(tuple(family))
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self._apex_category.limit_construction(shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        """The chosen product from supplied universal data (POL-MATH-037)."""
        diagrams = self.diagrams(diagram.domain())
        assert diagram in diagrams
        assert limiting_cone in diagrams.morphism_category(1)(diagrams.constant(apex), diagram)
        return self._retain(apex, UniversalData(diagram, limiting_cone, mediator))

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Products()"


class ColimitsCategory(ApexCategory):
    """``C.Colimits(I)``: chosen colimits of diagrams of one shape ``I``."""

    def __init__(self, apex_category: Category, shape: Category) -> None:
        self._shape = shape
        self._colimit_functor: MonoDict = MonoDict()
        super().__init__(apex_category)

    def presentation_role(self) -> type[ObjectOfCategory]:
        return colimit_presentation_role(self)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self._apex_category)

    def __call__(self, diagram: Functor) -> ObjectOfCategory:
        """``C.Colimits(I)(diagram)``: the chosen colimit, through ``C.colimit_construction(I)``."""
        self.accepts(diagram, self._shape)
        return self.chosen(diagram, self._apex_category.colimit_construction(self._shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        """The chosen colimit from supplied universal data (POL-MATH-037)."""
        assert diagram in self.diagrams()
        assert colimiting_cocone in self.diagrams().morphism_category(1)(diagram, self.diagrams().constant(apex))
        return self._retain(apex, UniversalData(diagram, colimiting_cocone, mediator))

    def colimit_functor(self) -> Functor:
        """``Colim_I: Fun(I, C) -> C``, retained once."""
        if self not in self._colimit_functor:
            self._colimit_functor[self] = colimit_functor(self)
        return self._colimit_functor[self]

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Colimits({self._shape!r})"


class CoproductsCategory(ApexCategory):
    """``C.Coproducts()``: chosen coproducts over every discrete shape (D16)."""

    def __init__(self, apex_category: Category) -> None:
        self._sequences = SequenceTable()
        super().__init__(apex_category)

    def presentation_role(self) -> type[ObjectOfCategory]:
        return coproduct_presentation_role(self)

    def diagrams(self, shape: Category) -> Category:
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        return Fun(shape, self._apex_category)

    def _sequence_diagram(self, sequence: tuple[ObjectOfCategory, ...]) -> Functor:
        """The sequence diagram on objects of ``C``, retained per sequence."""
        if sequence not in self._sequences:
            for member_object in sequence:
                assert member_object in self._apex_category, f"{member_object!r} is not an object of {self._apex_category!r}"
            self._sequences[sequence] = from_sequence(self._apex_category, sequence)
        return self._sequences[sequence]

    def __call__(self, family: Functor | tuple[ObjectOfCategory, ...]) -> ObjectOfCategory:
        """``C.Coproducts()(diagram)`` for a diagram over ``Discrete(S)``; ``C.Coproducts()((X_0, ..., X_n))`` for the sequence form."""
        diagram = family if family in self.category().morphism_category(1) else self._sequence_diagram(tuple(family))
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self._apex_category.colimit_construction(shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        """The chosen coproduct from supplied universal data (POL-MATH-037)."""
        diagrams = self.diagrams(diagram.domain())
        assert diagram in diagrams
        assert colimiting_cocone in diagrams.morphism_category(1)(diagram, diagrams.constant(apex))
        return self._retain(apex, UniversalData(diagram, colimiting_cocone, mediator))

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Coproducts()"


# ``indexed_by(P, family)``: the chosen apex ``P`` is indexed by the family's shape.
indexed_by = Predicate("indexed_by", 2, False)


def _indexed_by_shape(apex: CategoryPoint, family: Category) -> Decision:
    if not is_placed(apex, family.ambient()):
        return Unknown
    return apex.diagram().domain() is family.shape()


indexed_by.register_handler(_indexed_by_shape)


class DiscreteLimits(FullSubcategory[[MorphismOfCategory], []]):
    """``C.Limits(Discrete(S))``: the full subcategory of ``C.Products()`` on the products indexed by ``Discrete(S)``."""

    def __init__(self, products: ProductsCategory, shape: Category) -> None:
        self._shape = shape
        self._limit_functor: MonoDict = MonoDict()
        super().__init__(products)

    def shape(self) -> Category:
        return self._shape

    def apex_category(self) -> Category:
        return self._ambient.apex_category()

    def diagrams(self) -> Category:
        return self._ambient.diagrams(self._shape)

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return member(candidate, self._ambient) & indexed_by(candidate, self)

    def __call__(self, diagram: Functor) -> ObjectOfCategory:
        self._ambient.accepts(diagram, self._shape)
        apex = self._ambient(diagram)
        refine(apex, self)
        return apex

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        assert diagram in self.diagrams()
        self._ambient.with_universal_data(diagram, apex, limiting_cone, mediator)
        refine(apex, self)
        return apex

    def limit_functor(self) -> Functor:
        """``Lim_{Discrete(S)}: Fun(Discrete(S), C) -> C``, retained once."""
        if self not in self._limit_functor:
            self._limit_functor[self] = limit_functor(self)
        return self._limit_functor[self]

    def __repr__(self) -> str:
        return f"{self.apex_category()!r}.Limits({self._shape!r})"


class DiscreteColimits(FullSubcategory[[MorphismOfCategory], []]):
    """``C.Colimits(Discrete(S))``: the full subcategory of ``C.Coproducts()`` on the coproducts indexed by ``Discrete(S)``."""

    def __init__(self, coproducts: CoproductsCategory, shape: Category) -> None:
        self._shape = shape
        self._colimit_functor: MonoDict = MonoDict()
        super().__init__(coproducts)

    def shape(self) -> Category:
        return self._shape

    def apex_category(self) -> Category:
        return self._ambient.apex_category()

    def diagrams(self) -> Category:
        return self._ambient.diagrams(self._shape)

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return member(candidate, self._ambient) & indexed_by(candidate, self)

    def __call__(self, diagram: Functor) -> ObjectOfCategory:
        self._ambient.accepts(diagram, self._shape)
        apex = self._ambient(diagram)
        refine(apex, self)
        return apex

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        assert diagram in self.diagrams()
        self._ambient.with_universal_data(diagram, apex, colimiting_cocone, mediator)
        refine(apex, self)
        return apex

    def colimit_functor(self) -> Functor:
        """``Colim_{Discrete(S)}: Fun(Discrete(S), C) -> C``, retained once."""
        if self not in self._colimit_functor:
            self._colimit_functor[self] = colimit_functor(self)
        return self._colimit_functor[self]

    def __repr__(self) -> str:
        return f"{self.apex_category()!r}.Colimits({self._shape!r})"


# -- the construction functors -------------------------------------------------------------


def induced_limit_morphism(family: Category, transformation: NaturalTransformation) -> MorphismOfCategory:
    """``Lim(eta): Lim D -> Lim D'`` for ``eta: D => D'``: the mediator of the cone ``eta_i after pi_i``."""
    source, target = family(transformation.domain()), family(transformation.codomain())
    induced_cone = cone(transformation.codomain(), source, lambda vertex: transformation.component(vertex) * source.cone().component(vertex))
    return target.universal_morphism(induced_cone)


def induced_colimit_morphism(family: Category, transformation: NaturalTransformation) -> MorphismOfCategory:
    """``Colim(eta): Colim D -> Colim D'`` for ``eta: D => D'``: the mediator of the cocone ``iota'_i after eta_i``."""
    source, target = family(transformation.domain()), family(transformation.codomain())
    induced_cocone = cocone(transformation.domain(), target, lambda vertex: target.cocone().component(vertex) * transformation.component(vertex))
    return source.universal_morphism(induced_cocone)


def limit_functor(family: Category) -> Functor:
    """``Lim_I: Fun(I, C) -> C`` for a limit family: the chosen apex and the induced morphism of apexes."""
    return Fun(family.diagrams(), family.apex_category())(
        lambda diagram: family(diagram),
        lambda transformation: induced_limit_morphism(family, transformation),
    )


def colimit_functor(family: Category) -> Functor:
    """``Colim_I: Fun(I, C) -> C`` for a colimit family."""
    return Fun(family.diagrams(), family.apex_category())(
        lambda diagram: family(diagram),
        lambda transformation: induced_colimit_morphism(family, transformation),
    )


# -- the families owned once on ``Category`` (D02, POL-CAT-050) ---------------------------


def limits(apex_category: Category, shape: Category) -> Category:
    """``C.Limits(I)``: the full subcategory of ``C.Products()`` for a discrete shape, else the general family."""
    if is_discrete(shape):
        return DiscreteLimits(apex_category.Products(), shape)
    return LimitsCategory(apex_category, shape)


def colimits(apex_category: Category, shape: Category) -> Category:
    """``C.Colimits(I)``: the full subcategory of ``C.Coproducts()`` for a discrete shape, else the general family."""
    if is_discrete(shape):
        return DiscreteColimits(apex_category.Coproducts(), shape)
    return ColimitsCategory(apex_category, shape)
