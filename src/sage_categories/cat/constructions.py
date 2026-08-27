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
diagram at the constructed object), and the mediator rule (POL-FUN-008).
Distinct diagrams have distinct universal data even when they construct one
object: a skeletal ambient identifies the products of ``(c_2, c_3)`` and
``(c_6, c_1)``, and the cone of each diagram is still exact.  The object-level
accessors ``product_projection``, ``projection``, ``cone``, and
``universal_morphism`` read the data of the one diagram the object was
constructed from; ``_retain`` rejects a second diagram onto one object, naming
both, so that assumption fails loudly at the construction.

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
from typing import NamedTuple

from sage.misc.cachefunc import cached_method
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
    """What one diagram's construction retains: the constructed object, the diagram, its limiting cone or cocone, and its mediator rule."""

    constructed: ObjectOfCategory
    diagram: Functor
    transformation: NaturalTransformation
    mediator: Mediator


# -- the object roles of the construction families -----------------------------------------
#
# A family is a full subcategory of ``C``, so its compiled object role stands on
# ``C.ObjectType`` and adds the universal surface of the construction.  Each role
# reads the universal data through the family, which retains it per diagram
# (POL-CAT-046, POL-FUN-019).  The compiler copies a declaration's own class body
# onto the compiled role, so each family's role states its complete surface.


def chosen_limit_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class ChosenLimit(ObjectOfCategory):
        """A chosen limit: an object of ``C`` whose family retains its diagram, limiting cone, and mediator rule."""

        def diagram(self) -> Functor:
            return family.universal_data(self).diagram

        def index_category(self) -> Category:
            return family.universal_data(self).diagram.domain()

        def cone(self) -> NaturalTransformation:
            """The limiting cone ``constant(self) => diagram``."""
            return family.universal_data(self).transformation

        def projection(self, index: ObjectOfCategory) -> MorphismOfCategory:
            """The cone component ``self -> D(i)``."""
            return family.universal_data(self).transformation.component(index)

        def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism from the apex of another cone over the same diagram."""
            data = family.universal_data(self)
            assert candidate_cone.codomain() is data.diagram, f"{candidate_cone!r} is not a cone over {data.diagram!r}"
            return data.mediator(candidate_cone)

    return ChosenLimit


def chosen_product_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class ChosenProduct(ObjectOfCategory):
        """A chosen product over a discrete shape: an object of ``C`` with its projections and mediator rule."""

        def diagram(self) -> Functor:
            return family.universal_data(self).diagram

        def index_category(self) -> Category:
            return family.universal_data(self).diagram.domain()

        def cone(self) -> NaturalTransformation:
            """The product cone ``constant(self) => diagram``, whose components are the projections."""
            return family.universal_data(self).transformation

        def product_projection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """``pi_i: self -> X_i`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            data = family.universal_data(self)
            return data.transformation.component(vertex_of(data.diagram.domain(), index))

        def universal_morphism(self, candidate_cone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism from the apex of another cone over the same diagram."""
            data = family.universal_data(self)
            assert candidate_cone.codomain() is data.diagram, f"{candidate_cone!r} is not a cone over {data.diagram!r}"
            return data.mediator(candidate_cone)

        def subobject_projection(self, monomorphism: MorphismOfCategory, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """The component ``pi_i after j`` of a subobject ``j: S -> self``: the composition rule of POL-CAT-094."""
            assert monomorphism.codomain() is self, f"{monomorphism!r} does not present a subobject of {self!r}"
            assert monomorphism in family.narrowing_base().morphism_category(1).Monomorphisms(), f"{monomorphism!r} is not a monomorphism"
            return self.product_projection(index) * monomorphism

    return ChosenProduct


def chosen_colimit_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class ChosenColimit(ObjectOfCategory):
        """A chosen colimit: an object of ``C`` whose family retains its diagram, colimiting cocone, and mediator rule."""

        def diagram(self) -> Functor:
            return family.universal_data(self).diagram

        def index_category(self) -> Category:
            return family.universal_data(self).diagram.domain()

        def cocone(self) -> NaturalTransformation:
            """The colimiting cocone ``diagram => constant(self)``."""
            return family.universal_data(self).transformation

        def injection(self, index: ObjectOfCategory) -> MorphismOfCategory:
            """The cocone component ``D(i) -> self``."""
            return family.universal_data(self).transformation.component(index)

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism to the apex of another cocone under the same diagram."""
            data = family.universal_data(self)
            assert candidate_cocone.domain() is data.diagram, f"{candidate_cocone!r} is not a cocone under {data.diagram!r}"
            return data.mediator(candidate_cocone)

    return ChosenColimit


def chosen_coproduct_role(family: ApexCategory) -> type[ObjectOfCategory]:
    class ChosenCoproduct(ObjectOfCategory):
        """A chosen coproduct over a discrete shape: an object of ``C`` with its injections and mediator rule."""

        def diagram(self) -> Functor:
            return family.universal_data(self).diagram

        def index_category(self) -> Category:
            return family.universal_data(self).diagram.domain()

        def cocone(self) -> NaturalTransformation:
            """The coproduct cocone ``diagram => constant(self)``, whose components are the injections."""
            return family.universal_data(self).transformation

        def coproduct_injection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """``iota_i: X_i -> self`` for ``i`` an object of the index category or a datum of the index set (POL-CAT-093)."""
            data = family.universal_data(self)
            return data.transformation.component(vertex_of(data.diagram.domain(), index))

        def universal_morphism(self, candidate_cocone: NaturalTransformation) -> MorphismOfCategory:
            """The mediating morphism to the apex of another cocone under the same diagram."""
            data = family.universal_data(self)
            assert candidate_cocone.domain() is data.diagram, f"{candidate_cocone!r} is not a cocone under {data.diagram!r}"
            return data.mediator(candidate_cocone)

    return ChosenCoproduct


# -- construction families --------------------------------------------------------------------


class ApexCategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):
    """``C.Products()``, ``C.Limits(I)``, and their duals: the full subcategory of ``C`` on the chosen apexes.

    Its objects are the constructed objects themselves and its morphisms are the
    morphisms of ``C`` between them; its one selected functor is the retained
    monomorphism ``Fun(P, C).Monomorphisms().Isofibrations().Full()()``, identity on values
    (POL-CAT-046, POL-FUN-019).  The family retains the universal data of each
    diagram it constructed from.
    """

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData]) -> None:
        self._data: MonoDict = MonoDict()
        self._constructed: MonoDict = MonoDict()
        self._source_diagram: MonoDict = MonoDict()
        self._lowered: MonoDict = MonoDict()
        self._object_role = self.chosen_role()
        super().__init__(ambient)

    def chosen_role(self) -> type[ObjectOfCategory]:
        raise AssertionError(f"{self!r} declares no object role")

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        if role is Role.OBJECT:
            return self._object_role
        return super().local_role_class(role)

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

    def chosen_object(self, diagram: Functor) -> ObjectOfCategory:
        """The object this family constructed for ``diagram`` (POL-CAT-046, POL-FUN-019)."""
        assert diagram in self._constructed, f"{self!r} constructed nothing for {diagram!r}"
        return self._constructed[diagram]

    def universal_data(self, constructed: ObjectOfCategory) -> UniversalData:
        """The universal data of the diagram ``constructed`` was constructed from.

        Exact because ``_retain`` admits one diagram per constructed object; the
        authority is the diagram-keyed table, and this is the derived reading that
        an object-level accessor needs.
        """
        assert constructed in self._source_diagram, f"{self!r} constructed no object {constructed!r}"
        return self._data[self._source_diagram[constructed]]

    def chosen(self, diagram: Functor, construction: Construction) -> ObjectOfCategory:
        """The constructed object of ``diagram``, constructed once; a diagram and its lowering share it."""
        if not self.has_construction(diagram):
            construction(diagram)
            lowered = self.lowered(diagram)
            if lowered is not diagram:
                self._constructed[diagram] = self.chosen_object(lowered)
        return self.chosen_object(diagram)

    def _retain(self, constructed: ObjectOfCategory, data: UniversalData) -> ObjectOfCategory:
        """Place ``constructed`` in this family, retain the universal data of its diagram, and return it."""
        ambient = self.narrowing_base()
        assert constructed in ambient, f"{constructed!r} is not an object of {ambient!r}"
        assert data.diagram not in self._data, f"{self!r} already retains the construction of {data.diagram!r}"
        assert constructed not in self._source_diagram, (
            f"{self!r} constructed {constructed!r} from {self._source_diagram[constructed]!r} and again from {data.diagram!r}; "
            "one object cannot answer the projections of two diagrams"
        )
        self._data[data.diagram] = data
        self._constructed[data.diagram] = constructed
        self._source_diagram[constructed] = data.diagram
        refine(constructed, self)
        return constructed


class LimitsCategory(ApexCategory):
    """``C.Limits(I)``: chosen limits of diagrams of one shape ``I``."""

    def __init__(self, ambient: Category, shape: Category) -> None:
        self._shape = shape
        self._limit_functor: MonoDict = MonoDict()
        super().__init__(ambient)

    def chosen_role(self) -> type[ObjectOfCategory]:
        return chosen_limit_role(self)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self.narrowing_base())

    def __call__(self, diagram: Functor) -> ObjectOfCategory:
        """``C.Limits(I)(diagram)``: the chosen limit, through ``C.limit_construction(I)``."""
        self.accepts(diagram, self._shape)
        return self.chosen(diagram, self.narrowing_base().limit_construction(self._shape))

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

    def name(self) -> str:
        return f"Limits({self._shape!r})"

    def __repr__(self) -> str:
        return f"{self.narrowing_base()!r}.Limits({self._shape!r})"


class ProductsCategory(ApexCategory):
    """``C.Products()``: chosen products over every discrete shape (POL-CAT-093)."""

    def __init__(self, ambient: Category) -> None:
        self._sequences = SequenceTable()
        super().__init__(ambient)

    def chosen_role(self) -> type[ObjectOfCategory]:
        return chosen_product_role(self)

    def diagrams(self, shape: Category) -> Category:
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        return Fun(shape, self.narrowing_base())

    def _sequence_diagram(self, sequence: tuple[ObjectOfCategory, ...]) -> Functor:
        """The sequence diagram on objects of ``C``, retained per sequence."""
        ambient = self.narrowing_base()
        if sequence not in self._sequences:
            for member_object in sequence:
                assert member_object in ambient, f"{member_object!r} is not an object of {ambient!r}"
            self._sequences[sequence] = from_sequence(ambient, sequence)
        return self._sequences[sequence]

    def __call__(self, family: Functor | tuple[ObjectOfCategory, ...]) -> ObjectOfCategory:
        """``C.Products()(diagram)`` for a diagram over ``Discrete(S)``; ``C.Products()((X_0, ..., X_n))`` for the sequence form."""
        diagram = family if family in self.universe().morphism_category(1) else self._sequence_diagram(tuple(family))
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self.narrowing_base().limit_construction(shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
        """The chosen product from supplied universal data (POL-MATH-037)."""
        diagrams = self.diagrams(diagram.domain())
        assert diagram in diagrams
        assert limiting_cone in diagrams.morphism_category(1)(diagrams.constant(apex), diagram)
        return self._retain(apex, UniversalData(apex, diagram, limiting_cone, mediator))

    @cached_method
    def ChosenSubobjects(self) -> Category:
        """``C.Products().ChosenSubobjects()``: the objects presented by a chosen monomorphism into a chosen product, with their derived component projections (POL-CAT-094).

        This is a different notion from ``C.Subobjects()``, which is the family of
        monomorphism fibers: ``C.Subobjects()(x)`` collects every monomorphism into ``x``
        (POL-API-011).  "Chosen" names an act that cannot be derived: a subobject is an
        isomorphism class of monomorphisms and no intrinsic representative of it exists, so
        the presenting monomorphism is selected and retained (``specs/functor.md``,
        "Monomorphisms of ``Cat()`` and placement"), as a chosen subset retains its
        monomorphism.
        """
        return ProductSubobjectsCategory(self)

    def name(self) -> str:
        return "Products"

    def __repr__(self) -> str:
        return f"{self.narrowing_base()!r}.Products()"


def product_subobject_role(family: ProductSubobjectsCategory) -> type[ObjectOfCategory]:
    class ProductSubobject(ObjectOfCategory):
        """An object ``S`` presented by a monomorphism ``j: S -> P`` into a chosen product: each ``product_projection(i)`` is ``pi_i * j``."""

        def monomorphism(self) -> MorphismOfCategory:
            """The presenting monomorphism ``j: S -> P`` (POL-FUN-013)."""
            return family.presenting_monomorphism(self)

        def product(self) -> ObjectOfCategory:
            """The chosen product ``P``: the codomain of ``j`` (POL-FUN-014, POL-CAT-094)."""
            return family.presenting_monomorphism(self).codomain()

        def diagram(self) -> Functor:
            return self.product().diagram()

        def index_category(self) -> Category:
            return self.product().index_category()

        def product_projection(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            """``P.product_projection(i) after j``: the component of the subobject (POL-CAT-094)."""
            monomorphism = family.presenting_monomorphism(self)
            return monomorphism.codomain().subobject_projection(monomorphism, index)

    return ProductSubobject


class ProductSubobjectsCategory(FullSubcategory[[MorphismOfCategory], []]):
    """``C.Products().ChosenSubobjects()``: the full subcategory of ``C`` on the objects presented by a chosen monomorphism into a chosen product.

    The presenting monomorphism is retained by identity of its domain; the object
    itself is the domain ``S``, refined into this family (POL-FUN-013/014).
    """

    def __init__(self, products: ProductsCategory) -> None:
        self._products = products
        self._monomorphisms: MonoDict = MonoDict()
        self._object_role = product_subobject_role(self)
        super().__init__(products.narrowing_base())

    def local_role_class(self, role: Role) -> type[CategoryPoint]:
        if role is Role.OBJECT:
            return self._object_role
        return super().local_role_class(role)

    def presenting_monomorphism(self, member_object: ObjectOfCategory) -> MorphismOfCategory:
        """The monomorphism ``j: S -> P`` retained for ``S``."""
        assert member_object in self._monomorphisms, f"{self!r} retains no presenting monomorphism for {member_object!r}"
        return self._monomorphisms[member_object]

    def __call__(self, monomorphism: MorphismOfCategory) -> ObjectOfCategory:
        """The object ``S`` presented by ``j: S -> P`` for a chosen product ``P``: the trusted constructor of ``Monomorphisms()`` on ``j`` (POL-MATH-037), rejected only when decided false."""
        morphisms = self._ambient.morphism_category(1)
        assert monomorphism in morphisms, f"{monomorphism!r} is not a morphism of {self._ambient!r}"
        assert monomorphism.codomain() in self._products, f"{monomorphism.codomain()!r} is not a chosen product of {self._products!r}"
        assert ask(monomorphism.is_monomorphism()) is not False, f"{monomorphism!r} is not a monomorphism"
        subobject = monomorphism.domain()
        if subobject not in self._monomorphisms:
            morphisms.Monomorphisms()(monomorphism)
            self._monomorphisms[subobject] = monomorphism
            refine(subobject, self)
        return subobject

    def name(self) -> str:
        return "Products().ChosenSubobjects"

    def __repr__(self) -> str:
        return f"{self._products!r}.ChosenSubobjects()"


class ColimitsCategory(ApexCategory):
    """``C.Colimits(I)``: chosen colimits of diagrams of one shape ``I``."""

    def __init__(self, ambient: Category, shape: Category) -> None:
        self._shape = shape
        self._colimit_functor: MonoDict = MonoDict()
        super().__init__(ambient)

    def chosen_role(self) -> type[ObjectOfCategory]:
        return chosen_colimit_role(self)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return Fun(self._shape, self.narrowing_base())

    def __call__(self, diagram: Functor) -> ObjectOfCategory:
        """``C.Colimits(I)(diagram)``: the chosen colimit, through ``C.colimit_construction(I)``."""
        self.accepts(diagram, self._shape)
        return self.chosen(diagram, self.narrowing_base().colimit_construction(self._shape))

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

    def name(self) -> str:
        return f"Colimits({self._shape!r})"

    def __repr__(self) -> str:
        return f"{self.narrowing_base()!r}.Colimits({self._shape!r})"


class CoproductsCategory(ApexCategory):
    """``C.Coproducts()``: chosen coproducts over every discrete shape (POL-CAT-093)."""

    def __init__(self, ambient: Category) -> None:
        self._sequences = SequenceTable()
        super().__init__(ambient)

    def chosen_role(self) -> type[ObjectOfCategory]:
        return chosen_coproduct_role(self)

    def diagrams(self, shape: Category) -> Category:
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        return Fun(shape, self.narrowing_base())

    def _sequence_diagram(self, sequence: tuple[ObjectOfCategory, ...]) -> Functor:
        """The sequence diagram on objects of ``C``, retained per sequence."""
        ambient = self.narrowing_base()
        if sequence not in self._sequences:
            for member_object in sequence:
                assert member_object in ambient, f"{member_object!r} is not an object of {ambient!r}"
            self._sequences[sequence] = from_sequence(ambient, sequence)
        return self._sequences[sequence]

    def __call__(self, family: Functor | tuple[ObjectOfCategory, ...]) -> ObjectOfCategory:
        """``C.Coproducts()(diagram)`` for a diagram over ``Discrete(S)``; ``C.Coproducts()((X_0, ..., X_n))`` for the sequence form."""
        diagram = family if family in self.universe().morphism_category(1) else self._sequence_diagram(tuple(family))
        shape = diagram.domain()
        assert is_discrete(shape), f"{shape!r} is not a discrete shape"
        self.accepts(diagram, shape)
        return self.chosen(diagram, self.narrowing_base().colimit_construction(shape))

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
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


def _indexed_by_shape(constructed: CategoryPoint, family: Category) -> Decision:
    if not is_placed(constructed, family.ambient()):
        return Unknown
    return constructed.diagram().domain() is family.shape()


indexed_by.register_handler(_indexed_by_shape)


class DiscreteLimits(FullSubcategory[[MorphismOfCategory], []]):
    """``C.Limits(Discrete(S))``: the full subcategory of ``C.Products()`` on the products indexed by ``Discrete(S)``."""

    def __init__(self, products: ProductsCategory, shape: Category) -> None:
        self._shape = shape
        self._limit_functor: MonoDict = MonoDict()
        super().__init__(products)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return self._ambient.diagrams(self._shape)

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return member(candidate, self._ambient) & indexed_by(candidate, self)

    def __call__(self, diagram: Functor) -> ObjectOfCategory:
        self._ambient.accepts(diagram, self._shape)
        constructed = self._ambient(diagram)
        refine(constructed, self)
        return constructed

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, limiting_cone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
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


class DiscreteColimits(FullSubcategory[[MorphismOfCategory], []]):
    """``C.Colimits(Discrete(S))``: the full subcategory of ``C.Coproducts()`` on the coproducts indexed by ``Discrete(S)``."""

    def __init__(self, coproducts: CoproductsCategory, shape: Category) -> None:
        self._shape = shape
        self._colimit_functor: MonoDict = MonoDict()
        super().__init__(coproducts)

    def shape(self) -> Category:
        return self._shape

    def diagrams(self) -> Category:
        return self._ambient.diagrams(self._shape)

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        return member(candidate, self._ambient) & indexed_by(candidate, self)

    def __call__(self, diagram: Functor) -> ObjectOfCategory:
        self._ambient.accepts(diagram, self._shape)
        constructed = self._ambient(diagram)
        refine(constructed, self)
        return constructed

    def with_universal_data(self, diagram: Functor, apex: ObjectOfCategory, colimiting_cocone: NaturalTransformation, mediator: Mediator) -> ObjectOfCategory:
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


def induced_limit_morphism(family: Category, transformation: NaturalTransformation) -> MorphismOfCategory:
    """``Lim(eta): L_D -> L_D'`` for ``eta: D => D'``: the mediator of the cone ``eta_i after pi_i``."""
    source, target = family(transformation.domain()), family(transformation.codomain())
    induced_cone = cone(transformation.codomain(), source, lambda vertex: transformation.component(vertex) * source.cone().component(vertex))
    return target.universal_morphism(induced_cone)


def induced_colimit_morphism(family: Category, transformation: NaturalTransformation) -> MorphismOfCategory:
    """``Colim(eta): L_D -> L_D'`` for ``eta: D => D'``: the mediator of the cocone ``iota'_i after eta_i``."""
    source, target = family(transformation.domain()), family(transformation.codomain())
    induced_cocone = cocone(transformation.domain(), target, lambda vertex: target.cocone().component(vertex) * transformation.component(vertex))
    return source.universal_morphism(induced_cocone)


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
