"""Universal constructions as categories of chosen apexes with their presentations (D02, D10, D16).

For a category ``C`` and a shape ``I in Cat()``, ``C.Limits(I)`` is the construction
category whose objects are chosen limits of diagrams ``I -> C``: each object
retains its diagram, its apex, its limiting cone (a natural transformation from
the constant diagram at the apex), and its mediator rule (POL-CAT-046,
POL-FUN-008).  Its morphisms are morphisms of apexes.  Its one selected functor
is the apex functor ``Fun(C.Limits(I), C)``, so a presentation inherits the whole
surface of ``C`` (POL-FUN-011).  ``C.Colimits(I)`` is dual with cocones.

``C.Products()`` is the category of chosen products over every discrete shape,
with the sequence convenience ``(X_0, ..., X_n)`` and ``product_projection(i)``
(POL-CAT-093); ``C.Limits(Discrete(S))`` is its full subcategory on the products
indexed by ``Discrete(S)``, since a limit over a discrete shape is a product by
definition (Mathlib ``CategoryTheory.Limits.HasProduct``: ``HasLimit
(Discrete.functor f)``; inspected 2026-08-26).  ``C.Coproducts()`` and
``C.Colimits(Discrete(S))`` are dual.

Constructing an object of ``C.Limits(I)`` calls the category-owned
``C.limit_construction(I)``, which fails loudly unless ``C`` owns an ``I``-limit
construction; ``with_universal_data`` constructs from supplied data, trusted by
the writer (POL-MATH-037).  The construction category exists for every supplied
shape without asserting completeness (POL-CAT-051).

Each family retains its construction functor ``Lim_I: Fun(I, C) -> C``, acting on
a morphism of diagrams by the induced morphism of apexes: the mediator of the
cone whose components are ``eta_i`` after the projections (Mathlib
``CategoryTheory.Limits.limMap``; inspected 2026-08-26).
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import TYPE_CHECKING, Any

from sage.structure.coerce_dict import MonoDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.diagrams import from_sequence
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.properties import FullSubcategory
from sage_categories.cat.shapes import index_set_of, is_discrete
from sage_categories.kernel.caches import SequenceTable
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed, is_subcategory, refine
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory

if TYPE_CHECKING:
    from sage_categories.cat.shapes import DiscreteObject

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


def declares_subcategory(category: Category, ambient: Category) -> bool:
    """Whether ``category`` is ``ambient`` or declared a full subcategory of it, directly or through its ambients (D08)."""
    return category is ambient or any(declares_subcategory(declared, ambient) for declared in category.inclusion_ambient())


# -- presentation roles ------------------------------------------------------------------


def vertex_of(shape: Category, index: ObjectOfCategory | Hashable) -> ObjectOfCategory:
    """An object of a discrete shape, given directly or as a datum of its index set."""
    if index in shape:
        return index
    return shape(index_set_of(shape).point(index))


class LimitPresentation(ObjectOfCategory):
    """A chosen limit: its diagram, apex, limiting cone, and mediator rule."""

    def __init__(self, category: Category, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> None:
        ObjectOfCategory.__init__(self, category)
        self._diagram = diagram
        self._apex = apex
        self._cone = limiting_cone
        self._mediator = mediator

    def diagram(self) -> Functor:
        return self._diagram

    def index_category(self) -> Category:
        return self._diagram.domain()

    def apex(self) -> ObjectOfCategory:
        return self._apex

    def cone(self) -> NaturalTransformation:
        """The limiting cone ``constant(apex) => diagram``."""
        return self._cone

    def projection(self, index: ObjectOfCategory) -> MorphismOfCategory:
        """The cone component ``apex -> D(i)``."""
        return self._cone.component(index)

    def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismOfCategory:
        """The mediating morphism from the apex of another cone over the same diagram."""
        assert candidate_cone.codomain() is self._diagram, f"{candidate_cone!r} is not a cone over {self._diagram!r}"
        return self._mediator(candidate_cone)

    def __repr__(self) -> str:
        return f"Limit({self._diagram!r})"


class ProductPresentation(ObjectOfCategory):
    """A chosen product over a discrete shape: its diagram, apex, projections, and mediator rule."""

    def __init__(self, category: Category, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> None:
        ObjectOfCategory.__init__(self, category)
        self._diagram = diagram
        self._apex = apex
        self._cone = limiting_cone
        self._mediator = mediator

    def diagram(self) -> Functor:
        return self._diagram

    def index_category(self) -> Category:
        return self._diagram.domain()

    def apex(self) -> ObjectOfCategory:
        return self._apex

    def cone(self) -> NaturalTransformation:
        """The product cone ``constant(apex) => diagram``, whose components are the projections."""
        return self._cone

    def product_projection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
        """``pi_i: apex -> X_i`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
        return self._cone.component(vertex_of(self.index_category(), index))

    def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismOfCategory:
        """The mediating morphism from the apex of another cone over the same diagram."""
        assert candidate_cone.codomain() is self._diagram, f"{candidate_cone!r} is not a cone over {self._diagram!r}"
        return self._mediator(candidate_cone)

    def subobject_projection(self, monomorphism: MorphismOfCategory, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
        """The component ``pi_i after j`` of a subobject ``j: S -> apex`` (POL-CAT-094).

        The objects of ``C.Products().Subobjects()`` carry this composite as their own
        ``product_projection(i)``.
        """
        assert monomorphism.codomain() is self._apex, f"{monomorphism!r} does not present a subobject of {self._apex!r}"
        assert monomorphism in self._apex.category().morphism_category(1).Monomorphisms(), f"{monomorphism!r} is not a monomorphism"
        return self.product_projection(index) * monomorphism

    def __repr__(self) -> str:
        return f"Product({self._diagram!r})"


class ColimitPresentation(ObjectOfCategory):
    """A chosen colimit: its diagram, apex, colimiting cocone, and mediator rule."""

    def __init__(self, category: Category, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> None:
        ObjectOfCategory.__init__(self, category)
        self._diagram = diagram
        self._apex = apex
        self._cocone = colimiting_cocone
        self._mediator = mediator

    def diagram(self) -> Functor:
        return self._diagram

    def index_category(self) -> Category:
        return self._diagram.domain()

    def apex(self) -> ObjectOfCategory:
        return self._apex

    def cocone(self) -> NaturalTransformation:
        """The colimiting cocone ``diagram => constant(apex)``."""
        return self._cocone

    def injection(self, index: ObjectOfCategory) -> MorphismOfCategory:
        """The cocone component ``D(i) -> apex``."""
        return self._cocone.component(index)

    def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismOfCategory:
        """The mediating morphism to the apex of another cocone under the same diagram."""
        assert candidate_cocone.domain() is self._diagram, f"{candidate_cocone!r} is not a cocone under {self._diagram!r}"
        return self._mediator(candidate_cocone)

    def __repr__(self) -> str:
        return f"Colimit({self._diagram!r})"


class CoproductPresentation(ObjectOfCategory):
    """A chosen coproduct over a discrete shape: its diagram, apex, injections, and mediator rule."""

    def __init__(self, category: Category, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> None:
        ObjectOfCategory.__init__(self, category)
        self._diagram = diagram
        self._apex = apex
        self._cocone = colimiting_cocone
        self._mediator = mediator

    def diagram(self) -> Functor:
        return self._diagram

    def index_category(self) -> Category:
        return self._diagram.domain()

    def apex(self) -> ObjectOfCategory:
        return self._apex

    def cocone(self) -> NaturalTransformation:
        """The coproduct cocone ``diagram => constant(apex)``, whose components are the injections."""
        return self._cocone

    def coproduct_injection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
        """``iota_i: X_i -> apex`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
        return self._cocone.component(vertex_of(self.index_category(), index))

    def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismOfCategory:
        """The mediating morphism to the apex of another cocone under the same diagram."""
        assert candidate_cocone.domain() is self._diagram, f"{candidate_cocone!r} is not a cocone under {self._diagram!r}"
        return self._mediator(candidate_cocone)

    def __repr__(self) -> str:
        return f"Coproduct({self._diagram!r})"


class PresentationMorphism(MorphismOfCategory):
    """A morphism of presentations: a morphism of their apexes."""

    def __init__(self, category: Category, domain: ObjectOfCategory, codomain: ObjectOfCategory, apex_morphism: MorphismOfCategory) -> None:
        MorphismOfCategory.__init__(self, category, domain, codomain)
        self._apex_morphism = apex_morphism

    def apex_morphism(self) -> MorphismOfCategory:
        return self._apex_morphism

    def __repr__(self) -> str:
        return f"PresentationMorphism({self._apex_morphism!r})"


# -- construction categories --------------------------------------------------------------


class ApexCategory(Category[[MorphismOfCategory], []]):
    """A category of chosen apexes with their presentations; morphisms are morphisms of apexes."""

    MorphismType = PresentationMorphism

    class ElementType(ElementOfObject):
        """A generalized element of a presentation; no local operation."""

    def __init__(self, apex_category: Category) -> None:
        self._apex_category = apex_category
        self._presentations: MonoDict = MonoDict()
        self._apexes: MonoDict = MonoDict()
        self._lowered: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(self._morphisms_equal)

    def apex_category(self) -> Category:
        """The category ``C`` in which the apexes live."""
        return self._apex_category

    def structure_functors(self) -> tuple[Functor, ...]:
        """The apex functor ``Fun(self, C)``: the retained apex and the morphism of apexes."""
        return (Fun(self, self._apex_category)(lambda presentation: presentation.apex(), lambda morphism: morphism.apex_morphism()),)

    def member_in_apex_category(self, value: ObjectOfCategory) -> ObjectOfCategory:
        """A member of a sequence form as an object of ``C``: itself when its category declares
        itself a subcategory of ``C``, else the apex it presents (it reached ``C`` through an
        apex functor), so that ``(X * Y) * Z`` is a product of the apex of ``X * Y`` with ``Z``."""
        if declares_subcategory(value.category(), self._apex_category):
            return value
        assert value in self._apex_category, f"{value!r} is not an object of {self._apex_category!r}"
        return self.member_in_apex_category(value.apex())

    # The apex functor is fully faithful, so the universal constructions of a
    # category of presentations are those of its apex category applied to apexes;
    # an inherited operation on a presentation is the operation on its apex (D18).

    def Products(self) -> Category:
        return self._apex_category.Products()

    def Coproducts(self) -> Category:
        return self._apex_category.Coproducts()

    def Limits(self, shape: Category) -> Category:
        return self._apex_category.Limits(shape)

    def Colimits(self, shape: Category) -> Category:
        return self._apex_category.Colimits(shape)

    def exponential(self, exponent: ObjectOfCategory, base: ObjectOfCategory) -> ObjectOfCategory:
        return self._apex_category.exponential(self.member_in_apex_category(exponent), self.member_in_apex_category(base))

    def accepts(self, diagram: Functor, shape: Category) -> None:
        """A diagram of shape ``shape`` into ``C`` or into a subcategory of ``C`` (a diagram into ``Sets().Uncountable()`` is a diagram into ``Sets()``)."""
        assert diagram in self.category().morphism_category(1) and diagram.domain() is shape, f"{diagram!r} is not a diagram of shape {shape!r}"
        assert is_subcategory(diagram.codomain(), self._apex_category), f"{diagram!r} does not land in {self._apex_category!r}"

    def lowered(self, diagram: Functor) -> Functor:
        """The diagram as a diagram in ``C``: itself, or its composite with the inclusion of its codomain, retained per diagram."""
        codomain = diagram.codomain()
        if codomain is self._apex_category:
            return diagram
        assert declares_subcategory(codomain, self._apex_category), f"{codomain!r} is not a declared subcategory of {self._apex_category!r}"
        if diagram not in self._lowered:
            self._lowered[diagram] = Fun(codomain, self._apex_category).FullyFaithful().inclusion() * diagram
        return self._lowered[diagram]

    def has_presentation(self, diagram: Functor) -> bool:
        return diagram in self._presentations

    def presentation(self, diagram: Functor) -> ObjectOfCategory:
        """The chosen presentation retained for ``diagram``."""
        assert diagram in self._presentations, f"{self!r} retains no presentation of {diagram!r}"
        return self._presentations[diagram]

    def chosen(self, diagram: Functor, construction: Construction) -> ObjectOfCategory:
        """The chosen presentation of ``diagram``, constructed once; the diagram and its lowering share it."""
        if not self.has_presentation(diagram):
            construction(diagram)
            lowered = self.lowered(diagram)
            if lowered is not diagram:
                self._presentations[diagram] = self.presentation(lowered)
        return self.presentation(diagram)

    def _retain(self, presentation: ObjectOfCategory) -> ObjectOfCategory:
        diagram = presentation.diagram()
        assert diagram not in self._presentations, f"{self!r} already retains a presentation of {diagram!r}"
        self._presentations[diagram] = presentation
        self._apexes[presentation.apex()] = presentation
        return presentation

    def presentation_of_apex(self, apex: ObjectOfCategory) -> ObjectOfCategory:
        """The chosen presentation whose apex is the given object."""
        assert apex in self._apexes, f"{apex!r} is not the apex of a presentation retained by {self!r}"
        return self._apexes[apex]

    def construct_morphism(self, domain: ObjectOfCategory, codomain: ObjectOfCategory, apex_morphism: MorphismOfCategory) -> PresentationMorphism:
        assert apex_morphism in self._apex_category.morphism_category(1)(domain.apex(), codomain.apex())
        return self.MorphismType(self.morphism_category(1), domain, codomain, apex_morphism)

    def construct_identity(self, presentation: ObjectOfCategory) -> PresentationMorphism:
        return self.MorphismType(self.morphism_category(1), presentation, presentation, presentation.apex().identity())

    def composite(self, second: PresentationMorphism, first: PresentationMorphism) -> PresentationMorphism:
        assert first.codomain() is second.domain()
        return self.MorphismType(self.morphism_category(1), first.domain(), second.codomain(), second.apex_morphism() * first.apex_morphism())

    def element_from_defining_morphism(self, defining_morphism: PresentationMorphism) -> ElementOfObject:
        assert defining_morphism in self.morphism_category(1)
        return self.ElementType(defining_morphism)

    def _morphisms_equal(self, first: CategoryPoint, candidate: Any) -> Decision:
        morphisms = self.morphism_category(1)
        if first in morphisms and candidate in morphisms:
            return ask(first.apex_morphism() == candidate.apex_morphism())
        return Unknown


class LimitsCategory(ApexCategory):
    """``C.Limits(I)``: chosen limits of diagrams of one shape ``I``."""

    ObjectType = LimitPresentation

    def __init__(self, apex_category: Category, shape: Category) -> None:
        self._shape = shape
        self._limit_functor: MonoDict = MonoDict()
        super().__init__(apex_category)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self._apex_category)

    def __call__(self, diagram: Functor) -> LimitPresentation:
        """``C.Limits(I)(diagram)``: the chosen limit, through ``C.limit_construction(I)``."""
        self.accepts(diagram, self._shape)
        return self.chosen(diagram, self._apex_category.limit_construction(self._shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> LimitPresentation:
        """The chosen limit from supplied universal data; the writer asserts the universal property (POL-MATH-037)."""
        assert diagram in self.diagrams() and apex in self._apex_category
        assert limiting_cone in self.diagrams().morphism_category(1)(self.diagrams().constant(apex), diagram)
        return self._retain(self.ObjectType(self, diagram, apex, limiting_cone, mediator))

    def limit_functor(self) -> Functor:
        """``Lim_I: Fun(I, C) -> C``, retained once."""
        if self not in self._limit_functor:
            self._limit_functor[self] = limit_functor(self)
        return self._limit_functor[self]

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Limits({self._shape!r})"


class ProductsCategory(ApexCategory):
    """``C.Products()``: chosen products over every discrete shape (D16)."""

    ObjectType = ProductPresentation

    def __init__(self, apex_category: Category) -> None:
        self._sequences = SequenceTable()
        super().__init__(apex_category)

    def diagrams(self, shape: Category) -> Category:
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        return Fun(shape, self._apex_category)

    def _sequence_diagram(self, sequence: tuple[ObjectOfCategory, ...]) -> Functor:
        """The sequence diagram on the canonical images of the members in ``C``, retained per sequence."""
        if sequence not in self._sequences:
            self._sequences[sequence] = from_sequence(self._apex_category, tuple(map(self.member_in_apex_category, sequence)))
        return self._sequences[sequence]

    def __call__(self, family: Functor | tuple[ObjectOfCategory, ...]) -> ProductPresentation:
        """``C.Products()(diagram)`` for a diagram over ``Discrete(S)``; ``C.Products()((X_0, ..., X_n))`` for the sequence form."""
        diagram = family if family in self.category().morphism_category(1) else self._sequence_diagram(tuple(family))
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self._apex_category.limit_construction(shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> ProductPresentation:
        """The chosen product from supplied universal data (POL-MATH-037)."""
        diagrams = self.diagrams(diagram.domain())
        assert diagram in diagrams and apex in self._apex_category
        assert limiting_cone in diagrams.morphism_category(1)(diagrams.constant(apex), diagram)
        return self._retain(self.ObjectType(self, diagram, apex, limiting_cone, mediator))

    def Subobjects(self) -> Category:
        """``C.Products().Subobjects()``: subobjects of product apexes with their derived component projections (POL-CAT-094)."""
        if "Subobjects" not in self._constructions:
            self._constructions["Subobjects"] = ProductSubobjectsCategory(self)
        return self._constructions["Subobjects"]

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Products()"


class ProductSubobjectPresentation(ObjectOfCategory):
    """A subobject ``j: S -> P`` of a product apex: its apex is ``S`` and each ``product_projection(i)`` is ``pi_i * j``."""

    def __init__(self, category: Category, monomorphism: MorphismOfCategory, product: ProductPresentation) -> None:
        ObjectOfCategory.__init__(self, category)
        self._monomorphism = monomorphism
        self._product = product

    def monomorphism(self) -> MorphismOfCategory:
        """The presenting monomorphism ``j: S -> P`` (POL-FUN-013)."""
        return self._monomorphism

    def product(self) -> ProductPresentation:
        """The product presentation whose apex is ``j.codomain()`` (POL-FUN-014)."""
        return self._product

    def apex(self) -> ObjectOfCategory:
        return self._monomorphism.domain()

    def diagram(self) -> Functor:
        return self._product.diagram()

    def index_category(self) -> Category:
        return self._product.index_category()

    def product_projection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
        """``pi_i * j``: the component of the subobject, derived by composition (POL-CAT-094)."""
        return self._product.subobject_projection(self._monomorphism, index)

    def __repr__(self) -> str:
        return f"Subobject({self._monomorphism!r})"


class ProductSubobjectsCategory(ApexCategory):
    """``C.Products().Subobjects()``: the subobjects of product apexes, each retaining its monomorphism and its product."""

    ObjectType = ProductSubobjectPresentation

    def __init__(self, products: ProductsCategory) -> None:
        self._products = products
        self._subobjects: MonoDict = MonoDict()
        super().__init__(products.apex_category())

    def __call__(self, monomorphism: MorphismOfCategory) -> ProductSubobjectPresentation:
        """The subobject presented by ``j: S -> P`` for a retained product apex ``P``: the trusted constructor of ``Monomorphisms()`` on ``j`` (POL-MATH-037), rejected only when decided false."""
        morphisms = self._apex_category.morphism_category(1)
        assert monomorphism in morphisms, f"{monomorphism!r} is not a morphism of {self._apex_category!r}"
        assert ask(monomorphism.is_monomorphism()) is not False, f"{monomorphism!r} is not a monomorphism"
        if monomorphism not in self._subobjects:
            morphisms.Monomorphisms()(monomorphism)
            self._subobjects[monomorphism] = self.ObjectType(self, monomorphism, self._products.presentation_of_apex(monomorphism.codomain()))
        return self._subobjects[monomorphism]

    def __repr__(self) -> str:
        return f"{self._products!r}.Subobjects()"


class ColimitsCategory(ApexCategory):
    """``C.Colimits(I)``: chosen colimits of diagrams of one shape ``I``."""

    ObjectType = ColimitPresentation

    def __init__(self, apex_category: Category, shape: Category) -> None:
        self._shape = shape
        self._colimit_functor: MonoDict = MonoDict()
        super().__init__(apex_category)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self._apex_category)

    def __call__(self, diagram: Functor) -> ColimitPresentation:
        """``C.Colimits(I)(diagram)``: the chosen colimit, through ``C.colimit_construction(I)``."""
        self.accepts(diagram, self._shape)
        return self.chosen(diagram, self._apex_category.colimit_construction(self._shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> ColimitPresentation:
        """The chosen colimit from supplied universal data (POL-MATH-037)."""
        assert diagram in self.diagrams() and apex in self._apex_category
        assert colimiting_cocone in self.diagrams().morphism_category(1)(diagram, self.diagrams().constant(apex))
        return self._retain(self.ObjectType(self, diagram, apex, colimiting_cocone, mediator))

    def colimit_functor(self) -> Functor:
        """``Colim_I: Fun(I, C) -> C``, retained once."""
        if self not in self._colimit_functor:
            self._colimit_functor[self] = colimit_functor(self)
        return self._colimit_functor[self]

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Colimits({self._shape!r})"


class CoproductsCategory(ApexCategory):
    """``C.Coproducts()``: chosen coproducts over every discrete shape (D16)."""

    ObjectType = CoproductPresentation

    def __init__(self, apex_category: Category) -> None:
        self._sequences = SequenceTable()
        super().__init__(apex_category)

    def diagrams(self, shape: Category) -> Category:
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        return Fun(shape, self._apex_category)

    def _sequence_diagram(self, sequence: tuple[ObjectOfCategory, ...]) -> Functor:
        """The sequence diagram on the canonical images of the members in ``C``, retained per sequence."""
        if sequence not in self._sequences:
            self._sequences[sequence] = from_sequence(self._apex_category, tuple(map(self.member_in_apex_category, sequence)))
        return self._sequences[sequence]

    def __call__(self, family: Functor | tuple[ObjectOfCategory, ...]) -> CoproductPresentation:
        """``C.Coproducts()(diagram)`` for a diagram over ``Discrete(S)``; ``C.Coproducts()((X_0, ..., X_n))`` for the sequence form."""
        diagram = family if family in self.category().morphism_category(1) else self._sequence_diagram(tuple(family))
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self._apex_category.colimit_construction(shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> CoproductPresentation:
        """The chosen coproduct from supplied universal data (POL-MATH-037)."""
        diagrams = self.diagrams(diagram.domain())
        assert diagram in diagrams and apex in self._apex_category
        assert colimiting_cocone in diagrams.morphism_category(1)(diagram, diagrams.constant(apex))
        return self._retain(self.ObjectType(self, diagram, apex, colimiting_cocone, mediator))

    def __repr__(self) -> str:
        return f"{self._apex_category!r}.Coproducts()"


# ``indexed_by(P, family)``: the presentation ``P`` is indexed by the family's shape.
indexed_by = Predicate("indexed_by", 2, False)


def _indexed_by_shape(presentation: CategoryPoint, family: Category) -> Decision:
    if not is_placed(presentation, family.ambient()):
        return Unknown
    return presentation.diagram().domain() is family.shape()


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

    def __call__(self, diagram: Functor) -> ProductPresentation:
        self._ambient.accepts(diagram, self._shape)
        presentation = self._ambient(diagram)
        refine(presentation, self)
        return presentation

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> ProductPresentation:
        assert diagram in self.diagrams()
        presentation = self._ambient.with_universal_data(diagram, apex, limiting_cone, mediator)
        refine(presentation, self)
        return presentation

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

    def __call__(self, diagram: Functor) -> CoproductPresentation:
        self._ambient.accepts(diagram, self._shape)
        presentation = self._ambient(diagram)
        refine(presentation, self)
        return presentation

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> CoproductPresentation:
        assert diagram in self.diagrams()
        presentation = self._ambient.with_universal_data(diagram, apex, colimiting_cocone, mediator)
        refine(presentation, self)
        return presentation

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
    induced_cone = cone(transformation.codomain(), source.apex(), lambda vertex: transformation.component(vertex) * source.cone().component(vertex))
    return target.universal_morphism(induced_cone)


def induced_colimit_morphism(family: Category, transformation: NaturalTransformation) -> MorphismOfCategory:
    """``Colim(eta): Colim D -> Colim D'`` for ``eta: D => D'``: the mediator of the cocone ``iota'_i after eta_i``."""
    source, target = family(transformation.domain()), family(transformation.codomain())
    induced_cocone = cocone(transformation.domain(), target.apex(), lambda vertex: target.cocone().component(vertex) * transformation.component(vertex))
    return source.universal_morphism(induced_cocone)


def limit_functor(family: Category) -> Functor:
    """``Lim_I: Fun(I, C) -> C`` for a limit family: the chosen apex and the induced morphism of apexes."""
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
