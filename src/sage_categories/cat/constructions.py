"""Universal constructions as categories of presentations (POL-CAT-046, POL-CAT-050, POL-FUN-019, POL-FUN-029).

For a category ``C`` and a shape ``I in Cat()``, ``C.Limits(I)`` is the category
of chosen limit presentations of diagrams ``I -> C``.  Each diagram ``D`` gets its
own presentation ``P_D``, retained by identity of ``D``: it retains ``D``, its
canonical apex ``A_D``, the limiting cone (a natural transformation from the
constant diagram at ``A_D``), and the mediator rule (POL-FUN-008).  Distinct
diagrams have distinct presentations even when their canonical apexes are
identical, since one apex cannot retain two projection families (POL-CAT-046).

The one selected functor is the apex functor ``Fun(C.Limits(I), C).Faithful()``
sending ``P_D`` to ``A_D``.  It is not an inclusion: ``P_D`` is not an object of
``C``.  ``P_D`` reaches the whole surface of ``C`` through it by ordinary
inheritance, ``P_D.f() := A_D.f()``, which is how a chosen set product receives
``cardinality()`` with no product-specific method.  The morphisms of the family
are the morphisms of ``C`` between the canonical apexes.  ``C.Colimits(I)`` is
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
construction; ``with_universal_data`` presents a supplied apex from supplied data,
trusted by the writer (POL-MATH-037).  The construction category exists for every
supplied shape without asserting completeness (POL-CAT-051).

Each family retains its construction functor ``Lim_I: Fun(I, C) -> C``, acting on
a morphism of diagrams by the induced morphism of apexes: the mediator of the
cone whose components are ``eta_i`` after the projections (Mathlib
``CategoryTheory.Limits.limMap``; inspected 2026-08-26).
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from typing import NamedTuple

from sage.misc.cachefunc import cached_method
from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.properties import FullSubcategory
from sage_categories.cat.shapes import index_set_of, is_discrete
from sage_categories.kernel.caches import SequenceTable
from sage_categories.kernel.construction import (
    MorphismConstructionInput,
    ObjectConstructionInput,
    retained_input,
)
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed, is_subcategory, refine
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role

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
    """What one presentation retains: its canonical apex, its diagram, its limiting cone or cocone, and its mediator rule."""

    apex: ObjectOfCategory
    diagram: Functor
    transformation: NaturalTransformation
    mediator: Mediator


@dataclass(frozen=True, eq=False, slots=True)
class PresentationMorphismData:
    """The local state of a presentation morphism: the morphism of ``C`` between the two canonical apexes."""

    apex_morphism: MorphismOfCategory


class PresentationElement(ElementOfObject):
    """A generalized element of a presentation; no local operation."""


# When the ambient category is ``Cat()`` itself the compiled presentation role
# stands on ``Cat().ObjectType``, which is ``Category``: a presentation of a
# product of categories is therefore a category, canonically isomorphic to its
# canonical apex and carrying no declaration of its own.  Its mathematics is the
# presentation surface plus the ``Cat()`` surface it inherits through the apex
# functor.


class PresentedCategoryObject(ObjectOfCategory):
    """An object of a presented category; no local operation."""


class PresentedCategoryElement(ElementOfObject):
    """A generalized element of a presented category; no local operation."""


class PresentedCategoryMorphism(MorphismOfCategory):
    """A morphism of a presented category; no local operation."""


class PresentationMorphism(MorphismOfCategory):
    """A morphism of presentations: a morphism ``A_D -> A_E`` of ``C`` between their canonical apexes."""

    def __init__(self, data: PresentationMorphismData) -> None:
        self._apex_morphism = data.apex_morphism
        super().__init__()

    def apex_morphism(self) -> MorphismOfCategory:
        """The morphism of ``C`` this presentation morphism is (POL-FUN-019)."""
        return self._apex_morphism

    def __repr__(self) -> str:
        return f"presented {self._apex_morphism!r}"


# -- the presentation roles ----------------------------------------------------------------
#
# ``P_D`` is a value of its own, distinct from its canonical apex ``A_D``
# (POL-CAT-046, POL-FUN-019): distinct diagrams have distinct presentations even
# when their canonical apexes are identical, because one apex cannot retain two
# projection families.  Each presentation retains its own universal data, and the
# family's selected apex functor carries it to ``A_D`` in ``C``.  The compiler
# copies a declaration's own class body onto the compiled role, so each family's
# role states its complete surface.


def limit_presentation_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class LimitPresentation(ObjectOfCategory):
        """A chosen limit presentation: its diagram, canonical apex, limiting cone, and mediator rule."""

        DeclaredObjectType = PresentedCategoryObject
        DeclaredElementType = PresentedCategoryElement
        DeclaredMorphismType = PresentedCategoryMorphism

        def __init__(self, data: UniversalData) -> None:
            self._presentation = data
            super().__init__()

        def apex(self) -> ObjectOfCategory:
            """``A_D``: the canonical apex in ``C``, the image of this presentation under the apex functor."""
            return self._presentation.apex

        def diagram(self) -> Functor:
            return self._presentation.diagram

        def index_category(self) -> Category:
            return self._presentation.diagram.domain()

        def cone(self) -> NaturalTransformation:
            """The limiting cone ``constant(A_D) => diagram``."""
            return self._presentation.transformation

        def projection(self, index: ObjectOfCategory) -> MorphismOfCategory:
            """The cone component ``A_D -> D(i)``."""
            return self._presentation.transformation.component(index)

        def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism from the apex of another cone over the same diagram."""
            data = self._presentation
            assert candidate_cone.codomain() is data.diagram, f"{candidate_cone!r} is not a cone over {data.diagram!r}"
            return data.mediator(candidate_cone)

        def __repr__(self) -> str:
            return repr(self._presentation.apex)

    return LimitPresentation


def product_presentation_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class ProductPresentation(ObjectOfCategory):
        """A chosen product presentation over a discrete shape: its projections and mediator rule."""

        DeclaredObjectType = PresentedCategoryObject
        DeclaredElementType = PresentedCategoryElement
        DeclaredMorphismType = PresentedCategoryMorphism

        def __init__(self, data: UniversalData) -> None:
            self._presentation = data
            super().__init__()

        def apex(self) -> ObjectOfCategory:
            """``A_D``: the canonical apex in ``C``."""
            return self._presentation.apex

        def diagram(self) -> Functor:
            return self._presentation.diagram

        def index_category(self) -> Category:
            return self._presentation.diagram.domain()

        def cone(self) -> NaturalTransformation:
            """The product cone ``constant(A_D) => diagram``, whose components are the projections."""
            return self._presentation.transformation

        def product_projection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """``pi_i: A_D -> X_i`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            data = self._presentation
            return data.transformation.component(vertex_of(data.diagram.domain(), index))

        def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism from the apex of another cone over the same diagram."""
            data = self._presentation
            assert candidate_cone.codomain() is data.diagram, f"{candidate_cone!r} is not a cone over {data.diagram!r}"
            return data.mediator(candidate_cone)

        def subobject_projection(self, monomorphism: MorphismOfCategory, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """The component ``pi_i after j`` of a subobject ``j: S -> A_D``: the composition rule of POL-CAT-094."""
            assert monomorphism.codomain() is self._presentation.apex, f"{monomorphism!r} does not present a subobject of {self!r}"
            assert monomorphism in family.apex_category().morphism_category(1).Monomorphisms(), f"{monomorphism!r} is not a monomorphism"
            return self.product_projection(index) * monomorphism

        def __repr__(self) -> str:
            return repr(self._presentation.apex)

    return ProductPresentation


def colimit_presentation_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class ColimitPresentation(ObjectOfCategory):
        """A chosen colimit presentation: its diagram, canonical apex, colimiting cocone, and mediator rule."""

        DeclaredObjectType = PresentedCategoryObject
        DeclaredElementType = PresentedCategoryElement
        DeclaredMorphismType = PresentedCategoryMorphism

        def __init__(self, data: UniversalData) -> None:
            self._presentation = data
            super().__init__()

        def apex(self) -> ObjectOfCategory:
            """``A_D``: the canonical apex in ``C``."""
            return self._presentation.apex

        def diagram(self) -> Functor:
            return self._presentation.diagram

        def index_category(self) -> Category:
            return self._presentation.diagram.domain()

        def cocone(self) -> NaturalTransformation:
            """The colimiting cocone ``diagram => constant(A_D)``."""
            return self._presentation.transformation

        def injection(self, index: ObjectOfCategory) -> MorphismOfCategory:
            """The cocone component ``D(i) -> A_D``."""
            return self._presentation.transformation.component(index)

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism to the apex of another cocone under the same diagram."""
            data = self._presentation
            assert candidate_cocone.domain() is data.diagram, f"{candidate_cocone!r} is not a cocone under {data.diagram!r}"
            return data.mediator(candidate_cocone)

        def __repr__(self) -> str:
            return repr(self._presentation.apex)

    return ColimitPresentation


def coproduct_presentation_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class CoproductPresentation(ObjectOfCategory):
        """A chosen coproduct presentation over a discrete shape: its injections and mediator rule."""

        DeclaredObjectType = PresentedCategoryObject
        DeclaredElementType = PresentedCategoryElement
        DeclaredMorphismType = PresentedCategoryMorphism

        def __init__(self, data: UniversalData) -> None:
            self._presentation = data
            super().__init__()

        def apex(self) -> ObjectOfCategory:
            """``A_D``: the canonical apex in ``C``."""
            return self._presentation.apex

        def diagram(self) -> Functor:
            return self._presentation.diagram

        def index_category(self) -> Category:
            return self._presentation.diagram.domain()

        def cocone(self) -> NaturalTransformation:
            """The coproduct cocone ``diagram => constant(A_D)``, whose components are the injections."""
            return self._presentation.transformation

        def coproduct_injection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """``iota_i: X_i -> A_D`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            data = self._presentation
            return data.transformation.component(vertex_of(data.diagram.domain(), index))

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism to the apex of another cocone under the same diagram."""
            data = self._presentation
            assert candidate_cocone.domain() is data.diagram, f"{candidate_cocone!r} is not a cocone under {data.diagram!r}"
            return data.mediator(candidate_cocone)

        def __repr__(self) -> str:
            return repr(self._presentation.apex)

    return CoproductPresentation


# -- construction families --------------------------------------------------------------------


class ApexCategory[**MorphismData, **TwoMorphismData](Category[[MorphismOfCategory], []]):
    """``C.Products()``, ``C.Limits(I)``, and their duals: the category of chosen presentations.

    Its objects are the presentations ``P_D``, one per diagram; its morphisms are
    the morphisms of ``C`` between their canonical apexes.  Its one selected
    functor is the apex functor ``Fun(P, C).Faithful()`` sending ``P_D`` to
    ``A_D``.  That functor is not an inclusion: a presentation is not its apex,
    so ``P_D`` is not an object of ``C`` (POL-CAT-046, POL-FUN-019).  ``P_D``
    reaches the whole surface of ``C`` through it by ordinary inheritance,
    ``P_D.f() := A_D.f()``.
    """

    DeclaredElementType = PresentationElement
    DeclaredMorphismType = PresentationMorphism

    def __init__(self, apex_category: Category[MorphismData, TwoMorphismData]) -> None:
        self._apex_category = apex_category
        self._presentations: MonoDict = MonoDict()
        self._canonical: MonoDict = MonoDict()
        self._lowered: MonoDict = MonoDict()
        self._apex_functor: MonoDict = MonoDict()
        self._object_role = self.presentation_role()
        super().__init__()

    def apex_category(self) -> Category[MorphismData, TwoMorphismData]:
        """The category ``C`` in which the apexes live."""
        return self._apex_category

    def presentation_role(self) -> type[ObjectOfCategory]:
        raise AssertionError(f"{self!r} declares no presentation role")

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        if role is Role.OBJECT:
            return self._object_role
        return super().local_role_class(role)

    # -- the selected apex functor -----------------------------------------------------

    def structure_functors(self) -> tuple[Functor, ...]:
        return (self.apex_functor(),)

    def apex_functor(self) -> Functor:
        """``A: P -> C``, retained once: ``P_D |-> A_D`` on objects, the underlying morphism of ``C`` on morphisms."""
        if self in self._apex_functor:
            return self._apex_functor[self]
        functor = Fun(self, self._apex_category).Faithful()(
            lambda presentation: presentation.apex(),
            lambda morphism: morphism.apex_morphism(),
        )

        def object_input(source: ObjectConstructionInput) -> ObjectConstructionInput:
            return retained_input(source.datum.apex)

        def morphism_input(source: MorphismConstructionInput) -> MorphismConstructionInput:
            return retained_input(source.datum.apex_morphism)

        functor.retain_object_constructor_conversion(object_input)
        functor.retain_morphism_constructor_conversion(morphism_input)
        self._apex_functor[self] = functor
        return functor

    # -- morphisms of presentations ----------------------------------------------------

    def construct_morphism(self, domain: ObjectOfCategory, codomain: ObjectOfCategory, apex_morphism: MorphismOfCategory) -> MorphismOfCategory:
        morphisms = self._apex_category.morphism_category(1)
        assert apex_morphism in morphisms(domain.apex(), codomain.apex()), f"{apex_morphism!r} is not a morphism {domain.apex()!r} -> {codomain.apex()!r}"
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=domain,
            codomain=codomain,
            data=PresentationMorphismData(apex_morphism),
        )

    def construct_identity(self, presentation: ObjectOfCategory) -> MorphismOfCategory:
        return self.construct_morphism(presentation, presentation, presentation.apex().identity())

    def composite(self, second: MorphismOfCategory, first: MorphismOfCategory) -> MorphismOfCategory:
        assert first.codomain() is second.domain()
        return self.construct_morphism(first.domain(), second.codomain(), second.apex_morphism() * first.apex_morphism())

    # -- the diagrams this family accepts ----------------------------------------------

    def accepts(self, diagram: Functor, shape: Category) -> None:
        """A diagram of shape ``shape`` into ``C`` or into a subcategory of ``C`` (a diagram into ``Sets().Uncountable()`` is a diagram into ``Sets()``)."""
        assert diagram in self.universe().morphism_category(1) and diagram.domain() is shape, f"{diagram!r} is not a diagram of shape {shape!r}"
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

    # -- the retained presentations ----------------------------------------------------

    def retains(self, apex: ObjectOfCategory) -> bool:
        return apex in self._canonical

    def has_presentation(self, diagram: Functor) -> bool:
        return diagram in self._presentations

    def presentation(self, diagram: Functor) -> ObjectOfCategory:
        """``P_D``: the presentation this family retains for ``diagram`` (POL-CAT-046, POL-FUN-019)."""
        assert diagram in self._presentations, f"{self!r} retains no presentation for {diagram!r}"
        return self._presentations[diagram]

    def canonical_presentation(self, apex: ObjectOfCategory) -> ObjectOfCategory:
        """The presentation an apex is read through: the first one this family presented onto it."""
        assert apex in self._canonical, f"{self!r} retains no presentation with apex {apex!r}"
        return self._canonical[apex]

    def chosen_apex(self, diagram: Functor) -> ObjectOfCategory:
        """``A_D``: the apex this family chose for ``diagram``."""
        return self.presentation(diagram).apex()

    def chosen(self, diagram: Functor, construction: Construction) -> ObjectOfCategory:
        """``P_D``, constructed once; a diagram and its lowering share one presentation."""
        if not self.has_presentation(diagram):
            construction(diagram)
            lowered = self.lowered(diagram)
            if lowered is not diagram:
                self._presentations[diagram] = self.presentation(lowered)
        return self.presentation(diagram)

    def _retain(self, apex: ObjectOfCategory, data: UniversalData) -> ObjectOfCategory:
        """Construct and retain the presentation of one diagram; return ``P_D``.

        Each diagram gets its own presentation, including when a second diagram
        chooses an apex this family already presented: one apex cannot retain two
        projection families, so the presentations are distinct values with their
        own diagram, defining morphisms, and mediator rule, and their apex images
        are the same canonical object by identity (POL-CAT-046, POL-FUN-019).
        """
        assert apex in self._apex_category, f"{apex!r} is not an object of {self._apex_category!r}"
        assert data.diagram not in self._presentations, f"{self!r} already retains a presentation for {data.diagram!r}"
        presented = self.ObjectType(category=self, data=data)
        self._presentations[data.diagram] = presented
        if apex not in self._canonical:
            self._canonical[apex] = presented
        return presented


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
        return self._retain(apex, UniversalData(apex, diagram, limiting_cone, mediator))

    def limit_functor(self) -> Functor:
        """``Lim_I: Fun(I, C) -> C``, retained once."""
        if self not in self._limit_functor:
            self._limit_functor[self] = limit_functor(self)
        return self._limit_functor[self]

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Limits({self._shape!r})"


class ProductsCategory(ApexCategory):
    """``C.Products()``: chosen products over every discrete shape (POL-CAT-093)."""

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
        diagram = family if family in self.universe().morphism_category(1) else self._sequence_diagram(tuple(family))
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self._apex_category.limit_construction(shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        """The chosen product from supplied universal data (POL-MATH-037)."""
        diagrams = self.diagrams(diagram.domain())
        assert diagram in diagrams
        assert limiting_cone in diagrams.morphism_category(1)(diagrams.constant(apex), diagram)
        return self._retain(apex, UniversalData(apex, diagram, limiting_cone, mediator))

    @cached_method
    def Subobjects(self) -> Category:
        """``C.Products().Subobjects()``: the objects presented by a monomorphism into a chosen product, with their derived component projections (POL-CAT-094)."""
        return ProductSubobjectsCategory(self)

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Products()"


def product_subobject_role(family: ProductSubobjectsCategory) -> type[ObjectOfCategory]:
    class ProductSubobjectPresentation(ObjectOfCategory):
        """An object ``S`` presented by a monomorphism ``j: S -> P`` into a chosen product: each ``product_projection(i)`` is ``pi_i * j``."""

        def monomorphism(self) -> MorphismOfCategory:
            """The presenting monomorphism ``j: S -> P`` (POL-FUN-013)."""
            return family.presenting_monomorphism(self)

        def product(self) -> ObjectOfCategory:
            """``P_D``: the presentation whose canonical apex is the codomain of ``j`` (POL-FUN-014, POL-CAT-094)."""
            return family.presented_product(self)

        def diagram(self) -> Functor:
            return self.product().diagram()

        def index_category(self) -> Category:
            return self.product().index_category()

        def product_projection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """``P_D.product_projection(i) after j``: the component of the subobject (POL-CAT-094)."""
            monomorphism = family.presenting_monomorphism(self)
            return family.presented_product(self).subobject_projection(monomorphism, index)

    return ProductSubobjectPresentation


class ProductSubobjectsCategory(FullSubcategory[[MorphismOfCategory], []]):
    """``C.Products().Subobjects()``: the full subcategory of ``C`` on the objects presented by a monomorphism into a chosen product.

    The presenting monomorphism is retained by identity of its domain; the object
    itself is the domain ``S``, refined into this family (POL-FUN-013/014).
    """

    def __init__(self, products: ProductsCategory) -> None:
        self._products = products
        self._monomorphisms: MonoDict = MonoDict()
        self._object_role = product_subobject_role(self)
        super().__init__(products.apex_category())

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        if role is Role.OBJECT:
            return self._object_role
        return super().local_role_class(role)

    def presenting_monomorphism(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        """The monomorphism ``j: S -> A_D`` retained for ``S``."""
        assert member_object in self._monomorphisms, f"{self!r} retains no presenting monomorphism for {member_object!r}"
        return self._monomorphisms[member_object]

    def presented_product(self, member_object: ObjectOfCategory) -> ObjectOfCategory:
        """``P_D``: the product presentation whose canonical apex is the codomain of ``j`` (POL-CAT-094)."""
        return self._products.canonical_presentation(self.presenting_monomorphism(member_object).codomain())

    def __call__(self, monomorphism: MorphismOfCategory) -> ObjectOfCategory:
        """The object ``S`` presented by ``j: S -> A_D`` for the canonical apex of a chosen product: the trusted constructor of ``Monomorphisms()`` on ``j`` (POL-MATH-037), rejected only when decided false."""
        morphisms = self._ambient.morphism_category(1)
        assert monomorphism in morphisms, f"{monomorphism!r} is not a morphism of {self._ambient!r}"
        assert self._products.retains(monomorphism.codomain()), f"{monomorphism.codomain()!r} is not the canonical apex of a chosen product of {self._products!r}"
        assert ask(monomorphism.is_monomorphism()) is not False, f"{monomorphism!r} is not a monomorphism"
        subobject = monomorphism.domain()
        if subobject not in self._monomorphisms:
            morphisms.Monomorphisms()(monomorphism)
            self._monomorphisms[subobject] = monomorphism
            refine(subobject, self)
        return subobject

    def __repr__(self) -> str:
        return f"{self._products!r}.Subobjects()"


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
        return self._retain(apex, UniversalData(apex, diagram, colimiting_cocone, mediator))

    def colimit_functor(self) -> Functor:
        """``Colim_I: Fun(I, C) -> C``, retained once."""
        if self not in self._colimit_functor:
            self._colimit_functor[self] = colimit_functor(self)
        return self._colimit_functor[self]

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Colimits({self._shape!r})"


class CoproductsCategory(ApexCategory):
    """``C.Coproducts()``: chosen coproducts over every discrete shape (POL-CAT-093)."""

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
        diagram = family if family in self.universe().morphism_category(1) else self._sequence_diagram(tuple(family))
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self._apex_category.colimit_construction(shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        """The chosen coproduct from supplied universal data (POL-MATH-037)."""
        diagrams = self.diagrams(diagram.domain())
        assert diagram in diagrams
        assert colimiting_cocone in diagrams.morphism_category(1)(diagram, diagrams.constant(apex))
        return self._retain(apex, UniversalData(apex, diagram, colimiting_cocone, mediator))

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Coproducts()"


# ``indexed_by(P, family)``: the chosen apex ``P`` is indexed by the family's shape.
indexed_by = Predicate("indexed_by", 2, False)


def _indexed_by_shape(presented: CategoryPoint, family: Category) -> Decision:
    if not is_placed(presented, family.ambient()):
        return Unknown
    return presented.diagram().domain() is family.shape()


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
        presented = self._ambient(diagram)
        refine(presented, self)
        return presented

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        assert diagram in self.diagrams()
        presented = self._ambient.with_universal_data(diagram, apex, limiting_cone, mediator)
        refine(presented, self)
        return presented

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
        presented = self._ambient(diagram)
        refine(presented, self)
        return presented

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        assert diagram in self.diagrams()
        presented = self._ambient.with_universal_data(diagram, apex, colimiting_cocone, mediator)
        refine(presented, self)
        return presented

    def colimit_functor(self) -> Functor:
        """``Colim_{Discrete(S)}: Fun(Discrete(S), C) -> C``, retained once."""
        if self not in self._colimit_functor:
            self._colimit_functor[self] = colimit_functor(self)
        return self._colimit_functor[self]

    def __repr__(self) -> str:
        return f"{self.apex_category()!r}.Colimits({self._shape!r})"


# -- the construction functors -------------------------------------------------------------


def induced_limit_morphism(family: Category, transformation: NaturalTransformation) -> MorphismOfCategory:
    """``Lim(eta): A_D -> A_D'`` for ``eta: D => D'``: the mediator of the cone ``eta_i after pi_i``."""
    source, target = family(transformation.domain()), family(transformation.codomain())
    induced_cone = cone(transformation.codomain(), source.apex(), lambda vertex: transformation.component(vertex) * source.cone().component(vertex))
    return target.universal_morphism(induced_cone)


def induced_colimit_morphism(family: Category, transformation: NaturalTransformation) -> MorphismOfCategory:
    """``Colim(eta): A_D -> A_D'`` for ``eta: D => D'``: the mediator of the cocone ``iota'_i after eta_i``."""
    source, target = family(transformation.domain()), family(transformation.codomain())
    induced_cocone = cocone(transformation.domain(), target.apex(), lambda vertex: target.cocone().component(vertex) * transformation.component(vertex))
    return source.universal_morphism(induced_cocone)


def limit_functor(family: Category) -> Functor:
    """``Lim_I: Fun(I, C) -> C`` for a limit family: the canonical apex and the induced morphism of apexes."""
    return Fun(family.diagrams(), family.apex_category())(
        lambda diagram: family(diagram).apex(),
        lambda transformation: induced_limit_morphism(family, transformation),
    )


def colimit_functor(family: Category) -> Functor:
    """``Colim_I: Fun(I, C) -> C`` for a colimit family."""
    return Fun(family.diagrams(), family.apex_category())(
        lambda diagram: family(diagram).apex(),
        lambda transformation: induced_colimit_morphism(family, transformation),
    )


# -- the families owned once on ``Category`` (POL-CAT-050) ---------------------------


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
