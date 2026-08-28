"""The constructions ``Cat()`` owns (POL-CAT-050, POL-MATH-037): products and coproducts of categories over a discrete shape, the strict pullback, and the exponential.

Each construction line carries its inspected citation (POL-MATH-040); the
universal property of each is a trusted declaration attached to the
constructor (POL-MATH-037, POL-MATH-036).

- The product of an ``S``-indexed family of categories has as objects the
  ``S``-indexed families of objects given by rule and as morphisms the
  componentwise families of morphisms (Mathlib ``CategoryTheory.pi``; the binary
  case ``CategoryTheory.prod``; inspected 2026-08-26).  ``product_projection(i)``
  is the evaluation functor at ``i``.
- The coproduct has as objects the tagged objects ``(i, x)`` with ``x`` in the
  ``i``-th category and as morphisms the morphisms within one tag (Mathlib
  ``CategoryTheory.Sigma.sigma``; the binary case ``CategoryTheory.sum``;
  inspected 2026-08-26).  ``coproduct_injection(i)`` tags.
- The strict pullback of ``F: A -> C`` and ``G: B -> C`` has as objects the pairs
  ``(a, b)`` with ``F(a)`` and ``G(b)`` one object of ``C``, and as morphisms the
  pairs with identical images: limits in ``Cat`` are computed on objects and on
  morphisms (Mathlib ``CategoryTheory.Cat.HasLimits.limitCone``, whose apex has
  as objects the compatible families of objects; inspected 2026-08-26).  A pair's
  membership is decided by ``ask(F(a) == G(b))``: identity first, ``Unknown`` for
  two distinct rule-defined sets (POL-MATH-034).
- The exponential ``D ** C`` is ``Fun(C, D)`` (Mathlib ``CategoryTheory.Cat.exp_obj``;
  inspected 2026-08-26).

``Cat().Limits(I)`` and ``Cat().Colimits(I)`` for any other shape exist
(POL-CAT-051); constructing an object in them fails loudly, naming the missing
owned construction.

Each of these categories retains one object per construction datum -- one tagged
object per ``(i, x)``, one family per rule, one pair per ``(a, b)`` -- because a
category has one object per datum, and the structural transport caches identify
images by it (POL-CAT-066).  A universal object is unique up to unique isomorphism
and has one construction, so a second call with the same data returns the same
object; the projections, injections, and functor images of that construction are
likewise one morphism each, retained by the functor and the limiting cone that own
them (``cat/functors.py``; POL-CAT-012).
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from typing import Any

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.constructions import cocone, cocone_apex, cone, cone_apex, vertex_of
from sage_categories.cat.declarations import Sets
from sage_categories.cat.diagrams import sequence_position
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.shapes import DiscreteCategory, index_set_of
from sage_categories.kernel.caches import SequenceTable
from sage_categories.kernel.decisions import Decision, Unknown, UnknownClass
from sage_categories.kernel.predicates import Predicate, Proposition, ask, conjunction
from sage_categories.kernel.refinement import is_placed
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory

__all__ = [
    "CoproductCategory",
    "ProductCategory",
    "PullbackCategory",
    "SharedCarrierPullback",
    "coproduct_of_categories",
    "product_of_categories",
    "pullback_of_categories",
    "shared_carrier_pullback",
    "strict_pullback",
]

type ObjectRule = Callable[[DiscreteCategory.ObjectType], ObjectOfCategory]
type MorphismRule = Callable[[DiscreteCategory.ObjectType], MorphismOfCategory]
type Datum = Hashable


def _sequence_rule[Value](sequence: tuple[Value, ...]) -> Callable[[DiscreteCategory.ObjectType], Value]:
    return lambda vertex: sequence[sequence_position(vertex)]


# -- products of categories ---------------------------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class FamilyObjectData:
    """The local state introduced by a product-category object."""

    rule: ObjectRule


@dataclass(frozen=True, eq=False, slots=True)
class FamilyMorphismData:
    """The local state introduced by a product-category morphism."""

    rule: MorphismRule


class ProductCategory(Category[[MorphismRule | tuple[MorphismOfCategory, ...]], []]):
    """The product of an ``S``-indexed family of categories."""

    class ObjectType(ObjectOfCategory):
        """An object of a product category: an ``S``-indexed family of objects by rule."""

        def __init__(self, data: FamilyObjectData) -> None:
            self._rule = data.rule
            super().__init__()
            self._shape = self.category().shape()

        def component(self, index: ObjectOfCategory | Hashable) -> ObjectOfCategory:
            """The object at ``i``, for ``i`` an object of the index category or a datum of the index set."""
            return self._rule(vertex_of(self._shape, index))

        def __repr__(self) -> str:
            return f"family in {self.category()!r}"

    class MorphismType(MorphismOfCategory):
        """A morphism of a product category: a componentwise family of morphisms."""

        def __init__(self, data: FamilyMorphismData) -> None:
            self._rule = data.rule
            super().__init__()
            self._shape = self.base_category().shape()

        def component(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
            return self._rule(vertex_of(self._shape, index))

        def __repr__(self) -> str:
            return f"family morphism in {self.base_category()!r}"

    class ElementType(ElementOfObject):
        """A generalized element of a family; no local operation."""

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        self._sequences = SequenceTable()
        self._finite_data: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(self._equal)

    def shape(self) -> Category:
        return self._diagram.domain()

    def factor(self, index: ObjectOfCategory | Hashable) -> Category:
        return self._diagram.on_object(vertex_of(self.shape(), index))

    # The objects and morphisms are the families of objects and morphisms of the
    # factors: their sets are the set products of the factors' sets (specs/functor.md, "Diagram shapes and universal constructions"), for a
    # sequence-indexed product whose index set is ``[n]``.

    def _positions(self) -> tuple[Datum, ...]:
        enumeration = Sets.Finite().chosen_enumeration(index_set_of(self.shape()))
        assert enumeration == tuple(range(len(enumeration))), f"{self!r} is not indexed by a simplex"
        return enumeration

    def object_set(self) -> ObjectOfCategory:
        if "objects" not in self._finite_data:
            diagram = Fun(self.shape(), Sets).from_object_rule(lambda vertex: self.factor(vertex).object_set())
            self._finite_data["objects"] = Sets.Products()(diagram)
        return self._finite_data["objects"]

    def object_at(self, point: ElementOfObject) -> ProductCategory.ObjectType:
        self.object_set()
        product = self._finite_data["objects"]
        return self(tuple(self.factor(position).object_at(product.product_projection(position)(point)) for position in self._positions()))

    def morphism_set(self) -> ObjectOfCategory | UnknownClass:
        factor_morphisms = tuple(self.factor(position).morphism_set() for position in self._positions())
        if any(morphisms is Unknown for morphisms in factor_morphisms):
            return Unknown
        if "morphisms" not in self._finite_data:
            diagram = Fun(self.shape(), Sets).from_object_rule(lambda vertex: factor_morphisms[sequence_position(vertex)])
            self._finite_data["morphisms"] = Sets.Products()(diagram)
        return self._finite_data["morphisms"]

    def morphism_at(self, point: ElementOfObject) -> ProductCategory.MorphismType:
        product = self._finite_data["morphisms"]
        components = tuple(self.factor(position).morphism_at(product.product_projection(position)(point)) for position in self._positions())
        return self.construct_morphism(
            self(tuple(component.domain() for component in components)),
            self(tuple(component.codomain() for component in components)),
            components,
        )

    def separating_family(self) -> tuple[ProductCategory.ObjectType, ...]:
        """The separator ``(G_i)_i`` when every factor of an enumerated family chooses one separator."""
        index_set, finite = index_set_of(self.shape()), Sets.Finite()
        if not finite.has_chosen_enumeration(index_set):
            return ()
        separators = tuple(self.factor(datum).separating_family() for datum in finite.chosen_enumeration(index_set))
        if any(len(family) != 1 for family in separators):
            return ()
        return (self(tuple(separator for (separator,) in separators)),)

    def __call__(self, family: ObjectRule | tuple[ObjectOfCategory, ...]) -> ProductCategory.ObjectType:
        """``P(rule)`` for a family by rule; ``P((X_0, ..., X_n))`` for the external tuple, retained per tuple."""
        if callable(family):
            return self.ObjectType(category=self, data=FamilyObjectData(family))
        sequence = tuple(family)
        if sequence not in self._sequences:
            for position, member_object in enumerate(sequence):
                assert member_object in self.factor(position), f"{member_object!r} is not an object of {self.factor(position)!r}"
            self._sequences[sequence] = self.ObjectType(category=self, data=FamilyObjectData(_sequence_rule(sequence)))
        return self._sequences[sequence]

    def construct_morphism(self, domain: ProductCategory.ObjectType, codomain: ProductCategory.ObjectType, family: MorphismRule | tuple[MorphismOfCategory, ...]) -> ProductCategory.MorphismType:
        rule = family if callable(family) else _sequence_rule(tuple(family))
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=domain,
            codomain=codomain,
            data=FamilyMorphismData(rule),
        )

    def construct_identity(self, member_object: ProductCategory.ObjectType) -> ProductCategory.MorphismType:
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=member_object,
            codomain=member_object,
            data=FamilyMorphismData(lambda vertex: member_object.component(vertex).identity()),
        )

    def composite(self, second: ProductCategory.MorphismType, first: ProductCategory.MorphismType) -> ProductCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=first.domain(),
            codomain=second.codomain(),
            data=FamilyMorphismData(lambda vertex: second.component(vertex) * first.component(vertex)),
        )

    def _equal(self, first: CategoryPoint, candidate: Any) -> Decision:
        """Two families (of objects or of morphisms) over a finitely enumerated index are equal when every component is."""
        morphisms = self.morphism_category(1)
        if not ((first in self and candidate in self) or (first in morphisms and candidate in morphisms)):
            return Unknown
        index_set, finite = index_set_of(self.shape()), Sets.Finite()
        if not finite.has_chosen_enumeration(index_set):
            return Unknown
        return ask(conjunction(first.component(datum) == candidate.component(datum) for datum in finite.chosen_enumeration(index_set)))

    def __repr__(self) -> str:
        return f"Product({self._diagram!r})"


def product_of_categories(diagram: Functor) -> ObjectOfCategory:
    """``Cat().Products()(diagram)`` for a diagram over ``Discrete(S)``."""
    product = ProductCategory(diagram)
    projections: MonoDict = MonoDict()

    def projection(vertex: DiscreteCategory.ObjectType) -> Functor:
        if vertex not in projections:
            projections[vertex] = Fun(product, diagram.on_object(vertex))(
                lambda family: family.component(vertex),
                lambda morphism: morphism.component(vertex),
            )
        return projections[vertex]

    def mediator(candidate_cone: NaturalTransformation) -> Functor:
        source = cone_apex(candidate_cone)
        return Fun(source, product)(
            lambda member_object: product(lambda vertex: candidate_cone.component(vertex).on_object(member_object)),
            lambda morphism: product.construct_morphism(
                product(lambda vertex: candidate_cone.component(vertex).on_object(morphism.domain())),
                product(lambda vertex: candidate_cone.component(vertex).on_object(morphism.codomain())),
                lambda vertex: candidate_cone.component(vertex).on_morphism(morphism),
            ),
        )

    lowered = Cat().Products().lowered(diagram)
    return Cat().Products().with_universal_data(lowered, product, cone(lowered, product, projection), mediator)






# -- coproducts of categories --------------------------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class TaggedObjectData:
    """The local state introduced by a coproduct-category object."""

    tag: DiscreteCategory.ObjectType
    member: ObjectOfCategory


@dataclass(frozen=True, eq=False, slots=True)
class TaggedMorphismData:
    """The local state introduced by a coproduct-category morphism."""

    morphism: MorphismOfCategory


class CoproductCategory(Category[[MorphismOfCategory], []]):
    """The coproduct of an ``S``-indexed family of categories."""

    class ObjectType(ObjectOfCategory):
        """An object of a coproduct category: an object of one summand, tagged by its index."""

        def __init__(self, data: TaggedObjectData) -> None:
            self._tag = data.tag
            self._member = data.member
            super().__init__()

        def tag(self) -> DiscreteCategory.ObjectType:
            return self._tag

        def member(self) -> ObjectOfCategory:
            return self._member

        def __repr__(self) -> str:
            return f"({self._tag!r}, {self._member!r})"

    class MorphismType(MorphismOfCategory):
        """A morphism of a coproduct category: a morphism within one summand."""

        def __init__(self, data: TaggedMorphismData) -> None:
            self._morphism = data.morphism
            super().__init__()

        def morphism(self) -> MorphismOfCategory:
            return self._morphism

        def __repr__(self) -> str:
            return f"({self.domain().tag()!r}, {self._morphism!r})"

    class ElementType(ElementOfObject):
        """A generalized element of a tagged object; no local operation."""

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        self._objects: TripleDict = TripleDict(weak_values=False)
        super().__init__()
        self._equality.register_handler(self._equal)

    def shape(self) -> Category:
        return self._diagram.domain()

    def summand(self, index: ObjectOfCategory | Hashable) -> Category:
        return self._diagram.on_object(vertex_of(self.shape(), index))

    def _equal(self, first: CategoryPoint, candidate: Any) -> Decision:
        """Two tagged values are equal when they carry one tag and their members are equal.

        A morphism of the coproduct lies within one summand, so equal tags reduce the
        question to the summand's own equality (Mathlib ``CategoryTheory.Sigma.SigmaHom``,
        ``Mathlib/CategoryTheory/Sigma/Basic.lean``: "a morphism ``(i, X) -> (j, Y)`` when
        ``i = j`` is just a morphism ``X -> Y``, and if ``i != j`` then there are no such
        morphisms"; inspected 2026-08-28).
        """
        if first in self and candidate in self:
            return ask((first.tag() == candidate.tag()) & (first.member() == candidate.member()))
        morphisms = self.morphism_category(1)
        if first in morphisms and candidate in morphisms:
            return ask((first.domain().tag() == candidate.domain().tag()) & (first.morphism() == candidate.morphism()))
        return Unknown

    def __call__(self, index: ObjectOfCategory | Hashable, member_object: ObjectOfCategory) -> CoproductCategory.ObjectType:
        """``Q(i, x)``: the object of the ``i``-th summand tagged by ``i``, retained per pair."""
        tag = vertex_of(self.shape(), index)
        assert member_object in self.summand(tag), f"{member_object!r} is not an object of {self.summand(tag)!r}"
        key = (tag, member_object, self)
        if key not in self._objects:
            self._objects[key] = self.ObjectType(category=self, data=TaggedObjectData(tag, member_object))
        return self._objects[key]

    def construct_morphism(self, domain: CoproductCategory.ObjectType, codomain: CoproductCategory.ObjectType, morphism: MorphismOfCategory) -> CoproductCategory.MorphismType:
        assert domain.tag() is codomain.tag(), f"{domain!r} and {codomain!r} lie in different summands"
        assert morphism in self.summand(domain.tag()).morphism_category(1)(domain.member(), codomain.member())
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=domain,
            codomain=codomain,
            data=TaggedMorphismData(morphism),
        )

    def construct_identity(self, member_object: CoproductCategory.ObjectType) -> CoproductCategory.MorphismType:
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=member_object,
            codomain=member_object,
            data=TaggedMorphismData(member_object.member().identity()),
        )

    def composite(self, second: CoproductCategory.MorphismType, first: CoproductCategory.MorphismType) -> CoproductCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=first.domain(),
            codomain=second.codomain(),
            data=TaggedMorphismData(second.morphism() * first.morphism()),
        )

    def __repr__(self) -> str:
        return f"Coproduct({self._diagram!r})"


def coproduct_of_categories(diagram: Functor) -> ObjectOfCategory:
    """``Cat().Coproducts()(diagram)`` for a diagram over ``Discrete(S)``."""
    coproduct = CoproductCategory(diagram)
    injections: MonoDict = MonoDict()

    def injection(vertex: DiscreteCategory.ObjectType) -> Functor:
        if vertex not in injections:
            injections[vertex] = Fun(diagram.on_object(vertex), coproduct)(
                lambda member_object: coproduct(vertex, member_object),
                lambda morphism: coproduct.construct_morphism(coproduct(vertex, morphism.domain()), coproduct(vertex, morphism.codomain()), morphism),
            )
        return injections[vertex]

    def mediator(candidate_cocone: NaturalTransformation) -> Functor:
        target = cocone_apex(candidate_cocone)
        return Fun(coproduct, target)(
            lambda tagged: candidate_cocone.component(tagged.tag()).on_object(tagged.member()),
            lambda morphism: candidate_cocone.component(morphism.domain().tag()).on_morphism(morphism.morphism()),
        )

    lowered = Cat().Coproducts().lowered(diagram)
    return Cat().Coproducts().with_universal_data(lowered, coproduct, cocone(lowered, coproduct, injection), mediator)


# -- the strict pullback ----------------------------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class PairObjectData:
    """The local state introduced by a pullback object."""

    first: ObjectOfCategory
    second: ObjectOfCategory


@dataclass(frozen=True, eq=False, slots=True)
class PairMorphismData:
    """The local state introduced by a pullback morphism."""

    first: MorphismOfCategory
    second: MorphismOfCategory


# ``images_agree(pair, pullback)``: the two functors agree on the pair, ``F(a) == G(b)``.
images_agree = Predicate("images_agree", 2, False)


def _images_agree_by_equality(candidate: CategoryPoint, pullback: Category) -> Decision:
    if not is_placed(candidate, pullback):
        return Unknown
    return ask(pullback.first_functor().on_object(candidate.first()) == pullback.second_functor().on_object(candidate.second()))


images_agree.register_handler(_images_agree_by_equality)


class PullbackCategory(Category[[tuple[MorphismOfCategory, MorphismOfCategory]], []]):
    """The strict pullback ``A *_C B`` of ``F: A -> C`` and ``G: B -> C``."""

    class ObjectType(ObjectOfCategory):
        """An object of a strict pullback: a pair ``(a, b)``."""

        def __init__(self, data: PairObjectData) -> None:
            self._first = data.first
            self._second = data.second
            super().__init__()

        def first(self) -> ObjectOfCategory:
            return self._first

        def second(self) -> ObjectOfCategory:
            return self._second

        def __repr__(self) -> str:
            return f"({self._first!r}, {self._second!r})"

    class MorphismType(MorphismOfCategory):
        """A morphism of a strict pullback: a pair of morphisms with identical images."""

        def __init__(self, data: PairMorphismData) -> None:
            self._first = data.first
            self._second = data.second
            super().__init__()

        def first(self) -> MorphismOfCategory:
            return self._first

        def second(self) -> MorphismOfCategory:
            return self._second

        def __repr__(self) -> str:
            return f"({self._first!r}, {self._second!r})"

    class ElementType(ElementOfObject):
        """A generalized element of a pair; no local operation."""

    def __init__(self, first_functor: Functor, second_functor: Functor) -> None:
        assert first_functor.codomain() is second_functor.codomain()
        self._first_functor = first_functor
        self._second_functor = second_functor
        self._pairs = SequenceTable()
        self._projections: MonoDict = MonoDict()
        self._finite_data: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(self._equal)

    def first_functor(self) -> Functor:
        return self._first_functor

    def second_functor(self) -> Functor:
        return self._second_functor

    def first_projection(self) -> Functor:
        """The pullback projection to the domain of the first functor, retained once."""
        if self._first_functor not in self._projections:
            self._projections[self._first_functor] = Fun(self, self._first_functor.domain())(lambda pair: pair.first(), lambda morphism: morphism.first())
        return self._projections[self._first_functor]

    def second_projection(self) -> Functor:
        """The pullback projection to the domain of the second functor, retained once."""
        if self._second_functor not in self._projections:
            self._projections[self._second_functor] = Fun(self, self._second_functor.domain())(lambda pair: pair.second(), lambda morphism: morphism.second())
        return self._projections[self._second_functor]

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        """A constructed pair is a member exactly when its two images are one object."""
        return member(candidate, self) & images_agree(candidate, self)

    # The objects are the pairs with one image: the subset of the product of the
    # factors' object sets cut out by ``images_agree``; the morphisms likewise (POL-CAT-092, specs/functor.md, "Diagram shapes and universal constructions").

    def object_set(self) -> ObjectOfCategory:
        if "objects" not in self._finite_data:
            first, second = self._first_functor.domain(), self._second_functor.domain()
            pairs = Sets.Products()((first.object_set(), second.object_set()))

            def agree(datum: Datum) -> Decision:
                point = pairs.point(datum)
                left, right = first.object_at(pairs.product_projection(0)(point)), second.object_at(pairs.product_projection(1)(point))
                return ask(self._first_functor.on_object(left) == self._second_functor.on_object(right))

            self._finite_data["objects"] = pairs
            self._finite_data["object set"] = pairs.subset_from(agree)
        return self._finite_data["object set"]

    def object_at(self, point: ElementOfObject) -> PullbackCategory.ObjectType:
        self.object_set()
        pairs = self._finite_data["objects"]
        first, second = self._first_functor.domain(), self._second_functor.domain()
        return self((first.object_at(pairs.product_projection(0)(point)), second.object_at(pairs.product_projection(1)(point))))

    def morphism_set(self) -> ObjectOfCategory | UnknownClass:
        first, second = self._first_functor.domain(), self._second_functor.domain()
        if first.morphism_set() is Unknown or second.morphism_set() is Unknown:
            return Unknown
        if "morphisms" not in self._finite_data:
            pairs = Sets.Products()((first.morphism_set(), second.morphism_set()))

            def agree(datum: Datum) -> Decision:
                point = pairs.point(datum)
                left, right = first.morphism_at(pairs.product_projection(0)(point)), second.morphism_at(pairs.product_projection(1)(point))
                return ask(self._first_functor.on_morphism(left) == self._second_functor.on_morphism(right))

            self._finite_data["morphisms"] = pairs
            self._finite_data["morphism set"] = pairs.subset_from(agree)
        return self._finite_data["morphism set"]

    def morphism_at(self, point: ElementOfObject) -> PullbackCategory.MorphismType:
        pairs = self._finite_data["morphisms"]
        first, second = self._first_functor.domain(), self._second_functor.domain()
        left, right = first.morphism_at(pairs.product_projection(0)(point)), second.morphism_at(pairs.product_projection(1)(point))
        return self.construct_morphism(self((left.domain(), right.domain())), self((left.codomain(), right.codomain())), (left, right))

    def _equal(self, first: CategoryPoint, candidate: Any) -> Decision:
        """Two pairs are equal when both components are."""
        morphisms = self.morphism_category(1)
        if (first in self and candidate in self) or (first in morphisms and candidate in morphisms):
            return ask((first.first() == candidate.first()) & (first.second() == candidate.second()))
        return Unknown

    def __call__(self, pair: tuple[ObjectOfCategory, ObjectOfCategory]) -> PullbackCategory.ObjectType:
        """``PB((a, b))``: the pair, retained per pair; rejected only when the images are decidedly distinct."""
        first, second = pair
        assert first in self._first_functor.domain() and second in self._second_functor.domain()
        assert ask(self._first_functor.on_object(first) == self._second_functor.on_object(second)) is not False
        if pair not in self._pairs:
            self._pairs[pair] = self.ObjectType(category=self, data=PairObjectData(first, second))
        return self._pairs[pair]

    def construct_morphism(self, domain: PullbackCategory.ObjectType, codomain: PullbackCategory.ObjectType, pair: tuple[MorphismOfCategory, MorphismOfCategory]) -> PullbackCategory.MorphismType:
        first, second = pair
        assert first in self._first_functor.domain().morphism_category(1)(domain.first(), codomain.first())
        assert second in self._second_functor.domain().morphism_category(1)(domain.second(), codomain.second())
        assert ask(self._first_functor.on_morphism(first) == self._second_functor.on_morphism(second)) is not False
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=domain,
            codomain=codomain,
            data=PairMorphismData(first, second),
        )

    def construct_identity(self, member_object: PullbackCategory.ObjectType) -> PullbackCategory.MorphismType:
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=member_object,
            codomain=member_object,
            data=PairMorphismData(member_object.first().identity(), member_object.second().identity()),
        )

    def composite(self, second: PullbackCategory.MorphismType, first: PullbackCategory.MorphismType) -> PullbackCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=first.domain(),
            codomain=second.codomain(),
            data=PairMorphismData(second.first() * first.first(), second.second() * first.second()),
        )

    def __repr__(self) -> str:
        return f"Pullback({self._first_functor!r}, {self._second_functor!r})"


class SharedCarrierPullback(PullbackCategory):
    """A strict pullback whose objects carry two structures on one retained ancestor object (POL-FUN-029).

    The constructor asserts with ``is`` that both projections return the same
    ancestor object; the pullback retains that object once with both structures.
    """

    def __call__(self, pair: tuple[ObjectOfCategory, ObjectOfCategory]) -> PullbackCategory.ObjectType:
        first, second = pair
        assert self._first_functor.on_object(first) is self._second_functor.on_object(second), (
            f"{first!r} and {second!r} are structures on distinct carriers"
        )
        return super().__call__(pair)


def cospan_legs(diagram: Functor) -> tuple[Functor, Functor]:
    """The two legs ``D(0 -> 2)`` and ``D(1 -> 2)`` of a diagram over the walking cospan ``L(2, 2)``."""
    cospan = Cat().Horn(2, 2)
    return diagram.on_morphism(cospan.generator("0->2")), diagram.on_morphism(cospan.generator("1->2"))


def pullback_of_categories(diagram: Functor) -> ObjectOfCategory:
    """``Cat().Pullbacks()(diagram)`` for a diagram ``L(2, 2) -> Cat()``: the strict pullback of ``D(0 -> 2)`` and ``D(1 -> 2)``."""
    return strict_pullback(diagram, PullbackCategory(*cospan_legs(diagram)))


def shared_carrier_pullback(diagram: Functor) -> ObjectOfCategory:
    """The strict pullback of two structure functors into a shared ancestor, with the identity precondition on objects."""
    return strict_pullback(diagram, SharedCarrierPullback(*cospan_legs(diagram)))


def strict_pullback(diagram: Functor, pullback: PullbackCategory) -> ObjectOfCategory:
    """The chosen pullback of a cospan of categories with the given apex, retaining both projections and the mediator."""
    cospan = Cat().Horn(2, 2)
    first_functor, second_functor = pullback.first_functor(), pullback.second_functor()
    assert all(leg is functor for leg, functor in zip(cospan_legs(diagram), (first_functor, second_functor))), f"{pullback!r} is not the pullback of {diagram!r}"
    first_projection, second_projection = pullback.first_projection(), pullback.second_projection()
    legs = {0: first_projection, 1: second_projection, 2: first_functor * first_projection}

    def mediator(candidate_cone: NaturalTransformation) -> Functor:
        source = cone_apex(candidate_cone)
        to_first, to_second = candidate_cone.component(cospan(0)), candidate_cone.component(cospan(1))
        return Fun(source, pullback)(
            lambda member_object: pullback((to_first.on_object(member_object), to_second.on_object(member_object))),
            lambda morphism: pullback.construct_morphism(
                pullback((to_first.on_object(morphism.domain()), to_second.on_object(morphism.domain()))),
                pullback((to_first.on_object(morphism.codomain()), to_second.on_object(morphism.codomain()))),
                (to_first.on_morphism(morphism), to_second.on_morphism(morphism)),
            ),
        )

    lowered = Cat().Pullbacks().lowered(diagram)
    return Cat().Pullbacks().with_universal_data(lowered, pullback, cone(lowered, pullback, lambda vertex: legs[cospan.label(vertex)]), mediator)
