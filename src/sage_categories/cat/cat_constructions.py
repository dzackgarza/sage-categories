"""The constructions ``Cat()`` owns (D02): products and coproducts of categories over a discrete shape, the strict pullback, and the exponential.

Each construction line carries its inspected citation (POL-MATH-040); the
universal property of each is a trusted declaration attached to the
constructor (POL-MATH-037, D14).

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
  two distinct rule-defined sets (D17).
- The exponential ``D ** C`` is ``Fun(C, D)`` (Mathlib ``CategoryTheory.Cat.exp_obj``;
  inspected 2026-08-26).

``Cat().Limits(I)`` and ``Cat().Colimits(I)`` for any other shape exist and
constructing an object in them fails loudly in this unit.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import Any

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.constructions import cocone, cone, vertex_of
from sage_categories.cat.diagrams import sequence_position
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.shapes import DiscreteObject, index_set_of
from sage_categories.kernel.caches import SequenceTable
from sage_categories.kernel.decisions import Decision, Unknown, decision_and
from sage_categories.kernel.predicates import Predicate, Proposition, ask
from sage_categories.kernel.refinement import is_placed
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.category import Sets

__all__ = [
    "CoproductCategory",
    "ProductCategory",
    "PullbackCategory",
    "coproduct_of_categories",
    "product_of_categories",
    "pullback_of_categories",
]

type ObjectRule = Callable[[DiscreteObject], ObjectOfCategory]
type MorphismRule = Callable[[DiscreteObject], MorphismOfCategory]


def _sequence_rule[Value](sequence: tuple[Value, ...]) -> Callable[[DiscreteObject], Value]:
    return lambda vertex: sequence[sequence_position(vertex)]


# -- products of categories ---------------------------------------------------------------


class FamilyObject(ObjectOfCategory):
    """An object of a product category: an ``S``-indexed family of objects by rule."""

    def __init__(self, category: Category, rule: ObjectRule) -> None:
        ObjectOfCategory.__init__(self, category)
        self._rule = rule

    def component(self, index: ObjectOfCategory | Hashable) -> ObjectOfCategory:
        """The object at ``i``, for ``i`` an object of the index category or a datum of the index set."""
        return self._rule(vertex_of(self.category().shape(), index))

    def __repr__(self) -> str:
        return f"family in {self.category()!r}"


class FamilyMorphism(MorphismOfCategory):
    """A morphism of a product category: a componentwise family of morphisms."""

    def __init__(self, category: Category, domain: FamilyObject, codomain: FamilyObject, rule: MorphismRule) -> None:
        MorphismOfCategory.__init__(self, category, domain, codomain)
        self._rule = rule

    def component(self, index: ObjectOfCategory | Hashable) -> MorphismOfCategory:
        return self._rule(vertex_of(self.base_category().shape(), index))

    def __repr__(self) -> str:
        return f"family morphism in {self.base_category()!r}"


class ProductCategory(Category[[MorphismRule | tuple[MorphismOfCategory, ...]], []]):
    """The product of an ``S``-indexed family of categories."""

    ObjectType = FamilyObject
    MorphismType = FamilyMorphism

    class ElementType(ElementOfObject):
        """A generalized element of a family; no local operation."""

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        self._sequences = SequenceTable()
        super().__init__()
        self._equality.register_handler(self._equal)

    def shape(self) -> Category:
        return self._diagram.domain()

    def factor(self, index: ObjectOfCategory | Hashable) -> Category:
        return self._diagram.on_object(vertex_of(self.shape(), index))

    def __call__(self, family: ObjectRule | tuple[ObjectOfCategory, ...]) -> FamilyObject:
        """``P(rule)`` for a family by rule; ``P((X_0, ..., X_n))`` for the external tuple, retained per tuple."""
        if callable(family):
            return self.ObjectType(self, family)
        sequence = tuple(family)
        if sequence not in self._sequences:
            for position, member_object in enumerate(sequence):
                assert member_object in self.factor(position), f"{member_object!r} is not an object of {self.factor(position)!r}"
            self._sequences[sequence] = self.ObjectType(self, _sequence_rule(sequence))
        return self._sequences[sequence]

    def construct_morphism(self, domain: FamilyObject, codomain: FamilyObject, family: MorphismRule | tuple[MorphismOfCategory, ...]) -> FamilyMorphism:
        rule = family if callable(family) else _sequence_rule(tuple(family))
        return self.MorphismType(self.morphism_category(1), domain, codomain, rule)

    def construct_identity(self, member_object: FamilyObject) -> FamilyMorphism:
        return self.MorphismType(self.morphism_category(1), member_object, member_object, lambda vertex: member_object.component(vertex).identity())

    def composite(self, second: FamilyMorphism, first: FamilyMorphism) -> FamilyMorphism:
        assert first.codomain() is second.domain()
        return self.MorphismType(self.morphism_category(1), first.domain(), second.codomain(), lambda vertex: second.component(vertex) * first.component(vertex))

    def element_from_defining_morphism(self, defining_morphism: FamilyMorphism) -> ElementOfObject:
        assert defining_morphism in self.morphism_category(1)
        return self.ElementType(defining_morphism)

    def _equal(self, first: CategoryPoint, candidate: Any) -> Decision:
        """Two families over a finitely enumerated index are equal when every component is."""
        if first not in self or candidate not in self:
            return Unknown
        index_set, finite = index_set_of(self.shape()), Sets().Finite()
        if not finite.has_chosen_enumeration(index_set):
            return Unknown
        return decision_and(*(ask(first.component(datum) == candidate.component(datum)) for datum in finite.chosen_enumeration(index_set)))

    def __repr__(self) -> str:
        return f"Product({self._diagram!r})"


def product_of_categories(diagram: Functor) -> ObjectOfCategory:
    """``Cat().Products()(diagram)`` for a diagram over ``Discrete(S)``."""
    product = ProductCategory(diagram)
    projections: MonoDict = MonoDict()

    def projection(vertex: DiscreteObject) -> Functor:
        if vertex not in projections:
            projections[vertex] = Fun(product, diagram.on_object(vertex))(
                lambda family: family.component(vertex),
                lambda morphism: morphism.component(vertex),
            )
        return projections[vertex]

    def mediator(candidate_cone: NaturalTransformation) -> Functor:
        source = _cone_apex(candidate_cone)
        return Fun(source, product)(
            lambda member_object: product(lambda vertex: candidate_cone.component(vertex).on_object(member_object)),
            lambda morphism: product.construct_morphism(
                product(lambda vertex: candidate_cone.component(vertex).on_object(morphism.domain())),
                product(lambda vertex: candidate_cone.component(vertex).on_object(morphism.codomain())),
                lambda vertex: candidate_cone.component(vertex).on_morphism(morphism),
            ),
        )

    return Cat().Products().with_universal_data(diagram, product, cone(diagram, product, projection), mediator)


def _cone_apex(transformation: NaturalTransformation) -> ObjectOfCategory:
    """The apex of a cone ``constant(N) => D``: the value of its retained constant domain."""
    constant = transformation.domain()
    return Fun(constant.domain(), constant.codomain()).constant_value(constant)


def _cocone_apex(transformation: NaturalTransformation) -> ObjectOfCategory:
    """The apex of a cocone ``D => constant(N)``."""
    constant = transformation.codomain()
    return Fun(constant.domain(), constant.codomain()).constant_value(constant)


# -- coproducts of categories --------------------------------------------------------------


class TaggedObject(ObjectOfCategory):
    """An object of a coproduct category: an object of one summand, tagged by its index."""

    def __init__(self, category: Category, tag: DiscreteObject, member_object: ObjectOfCategory) -> None:
        ObjectOfCategory.__init__(self, category)
        self._tag = tag
        self._member = member_object

    def tag(self) -> DiscreteObject:
        return self._tag

    def member(self) -> ObjectOfCategory:
        return self._member

    def __repr__(self) -> str:
        return f"({self._tag!r}, {self._member!r})"


class TaggedMorphism(MorphismOfCategory):
    """A morphism of a coproduct category: a morphism within one summand."""

    def __init__(self, category: Category, domain: TaggedObject, codomain: TaggedObject, morphism: MorphismOfCategory) -> None:
        MorphismOfCategory.__init__(self, category, domain, codomain)
        self._morphism = morphism

    def morphism(self) -> MorphismOfCategory:
        return self._morphism

    def __repr__(self) -> str:
        return f"({self.domain().tag()!r}, {self._morphism!r})"


class CoproductCategory(Category[[MorphismOfCategory], []]):
    """The coproduct of an ``S``-indexed family of categories."""

    ObjectType = TaggedObject
    MorphismType = TaggedMorphism

    class ElementType(ElementOfObject):
        """A generalized element of a tagged object; no local operation."""

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        self._objects: TripleDict = TripleDict(weak_values=False)
        super().__init__()

    def shape(self) -> Category:
        return self._diagram.domain()

    def summand(self, index: ObjectOfCategory | Hashable) -> Category:
        return self._diagram.on_object(vertex_of(self.shape(), index))

    def __call__(self, index: ObjectOfCategory | Hashable, member_object: ObjectOfCategory) -> TaggedObject:
        """``Q(i, x)``: the object of the ``i``-th summand tagged by ``i``, retained per pair."""
        tag = vertex_of(self.shape(), index)
        assert member_object in self.summand(tag), f"{member_object!r} is not an object of {self.summand(tag)!r}"
        key = (tag, member_object, self)
        if key not in self._objects:
            self._objects[key] = self.ObjectType(self, tag, member_object)
        return self._objects[key]

    def construct_morphism(self, domain: TaggedObject, codomain: TaggedObject, morphism: MorphismOfCategory) -> TaggedMorphism:
        assert domain.tag() is codomain.tag(), f"{domain!r} and {codomain!r} lie in different summands"
        assert morphism in self.summand(domain.tag()).morphism_category(1)(domain.member(), codomain.member())
        return self.MorphismType(self.morphism_category(1), domain, codomain, morphism)

    def construct_identity(self, member_object: TaggedObject) -> TaggedMorphism:
        return self.MorphismType(self.morphism_category(1), member_object, member_object, member_object.member().identity())

    def composite(self, second: TaggedMorphism, first: TaggedMorphism) -> TaggedMorphism:
        assert first.codomain() is second.domain()
        return self.MorphismType(self.morphism_category(1), first.domain(), second.codomain(), second.morphism() * first.morphism())

    def element_from_defining_morphism(self, defining_morphism: TaggedMorphism) -> ElementOfObject:
        assert defining_morphism in self.morphism_category(1)
        return self.ElementType(defining_morphism)

    def __repr__(self) -> str:
        return f"Coproduct({self._diagram!r})"


def coproduct_of_categories(diagram: Functor) -> ObjectOfCategory:
    """``Cat().Coproducts()(diagram)`` for a diagram over ``Discrete(S)``."""
    coproduct = CoproductCategory(diagram)
    injections: MonoDict = MonoDict()

    def injection(vertex: DiscreteObject) -> Functor:
        if vertex not in injections:
            injections[vertex] = Fun(diagram.on_object(vertex), coproduct)(
                lambda member_object: coproduct(vertex, member_object),
                lambda morphism: coproduct.construct_morphism(coproduct(vertex, morphism.domain()), coproduct(vertex, morphism.codomain()), morphism),
            )
        return injections[vertex]

    def mediator(candidate_cocone: NaturalTransformation) -> Functor:
        target = _cocone_apex(candidate_cocone)
        return Fun(coproduct, target)(
            lambda tagged: candidate_cocone.component(tagged.tag()).on_object(tagged.member()),
            lambda morphism: candidate_cocone.component(morphism.domain().tag()).on_morphism(morphism.morphism()),
        )

    return Cat().Coproducts().with_universal_data(diagram, coproduct, cocone(diagram, coproduct, injection), mediator)


# -- the strict pullback ----------------------------------------------------------------


class PairObject(ObjectOfCategory):
    """An object of a strict pullback: a pair ``(a, b)``."""

    def __init__(self, category: Category, first: ObjectOfCategory, second: ObjectOfCategory) -> None:
        ObjectOfCategory.__init__(self, category)
        self._first = first
        self._second = second

    def first(self) -> ObjectOfCategory:
        return self._first

    def second(self) -> ObjectOfCategory:
        return self._second

    def __repr__(self) -> str:
        return f"({self._first!r}, {self._second!r})"


class PairMorphism(MorphismOfCategory):
    """A morphism of a strict pullback: a pair of morphisms with identical images."""

    def __init__(self, category: Category, domain: PairObject, codomain: PairObject, first: MorphismOfCategory, second: MorphismOfCategory) -> None:
        MorphismOfCategory.__init__(self, category, domain, codomain)
        self._first = first
        self._second = second

    def first(self) -> MorphismOfCategory:
        return self._first

    def second(self) -> MorphismOfCategory:
        return self._second

    def __repr__(self) -> str:
        return f"({self._first!r}, {self._second!r})"


# ``images_agree(pair, pullback)``: the two functors agree on the pair, ``F(a) == G(b)``.
images_agree = Predicate("images_agree", 2, False)


def _images_agree_by_equality(candidate: CategoryPoint, pullback: Category) -> Decision:
    if not is_placed(candidate, pullback):
        return Unknown
    return ask(pullback.first_functor().on_object(candidate.first()) == pullback.second_functor().on_object(candidate.second()))


images_agree.register_handler(_images_agree_by_equality)


class PullbackCategory(Category[[tuple[MorphismOfCategory, MorphismOfCategory]], []]):
    """The strict pullback ``A *_C B`` of ``F: A -> C`` and ``G: B -> C``."""

    ObjectType = PairObject
    MorphismType = PairMorphism

    class ElementType(ElementOfObject):
        """A generalized element of a pair; no local operation."""

    def __init__(self, first_functor: Functor, second_functor: Functor) -> None:
        assert first_functor.codomain() is second_functor.codomain()
        self._first_functor = first_functor
        self._second_functor = second_functor
        self._pairs = SequenceTable()
        super().__init__()

    def first_functor(self) -> Functor:
        return self._first_functor

    def second_functor(self) -> Functor:
        return self._second_functor

    def membership_proposition(self, candidate: CategoryPoint) -> Proposition:
        """A constructed pair is a member exactly when its two images are one object."""
        return member(candidate, self) & images_agree(candidate, self)

    def __call__(self, pair: tuple[ObjectOfCategory, ObjectOfCategory]) -> PairObject:
        """``PB((a, b))``: the pair, retained per pair; rejected only when the images are decidedly distinct."""
        first, second = pair
        assert first in self._first_functor.domain() and second in self._second_functor.domain()
        assert ask(self._first_functor.on_object(first) == self._second_functor.on_object(second)) is not False
        if pair not in self._pairs:
            self._pairs[pair] = self.ObjectType(self, first, second)
        return self._pairs[pair]

    def construct_morphism(self, domain: PairObject, codomain: PairObject, pair: tuple[MorphismOfCategory, MorphismOfCategory]) -> PairMorphism:
        first, second = pair
        assert first in self._first_functor.domain().morphism_category(1)(domain.first(), codomain.first())
        assert second in self._second_functor.domain().morphism_category(1)(domain.second(), codomain.second())
        assert ask(self._first_functor.on_morphism(first) == self._second_functor.on_morphism(second)) is not False
        return self.MorphismType(self.morphism_category(1), domain, codomain, first, second)

    def construct_identity(self, member_object: PairObject) -> PairMorphism:
        return self.MorphismType(self.morphism_category(1), member_object, member_object, member_object.first().identity(), member_object.second().identity())

    def composite(self, second: PairMorphism, first: PairMorphism) -> PairMorphism:
        assert first.codomain() is second.domain()
        return self.MorphismType(self.morphism_category(1), first.domain(), second.codomain(), second.first() * first.first(), second.second() * first.second())

    def element_from_defining_morphism(self, defining_morphism: PairMorphism) -> ElementOfObject:
        assert defining_morphism in self.morphism_category(1)
        return self.ElementType(defining_morphism)

    def __repr__(self) -> str:
        return f"Pullback({self._first_functor!r}, {self._second_functor!r})"


def pullback_of_categories(diagram: Functor) -> ObjectOfCategory:
    """``Cat().Pullbacks()(diagram)`` for a diagram ``L(2, 2) -> Cat()``: the strict pullback of ``D(0 -> 2)`` and ``D(1 -> 2)``."""
    cospan = Cat().Horn(2, 2)
    first_functor, second_functor = diagram.on_morphism(cospan.generator("0->2")), diagram.on_morphism(cospan.generator("1->2"))
    pullback = PullbackCategory(first_functor, second_functor)
    first_projection = Fun(pullback, first_functor.domain())(lambda pair: pair.first(), lambda morphism: morphism.first())
    second_projection = Fun(pullback, second_functor.domain())(lambda pair: pair.second(), lambda morphism: morphism.second())
    legs = {0: first_projection, 1: second_projection, 2: first_functor * first_projection}

    def mediator(candidate_cone: NaturalTransformation) -> Functor:
        source = _cone_apex(candidate_cone)
        to_first, to_second = candidate_cone.component(cospan(0)), candidate_cone.component(cospan(1))
        return Fun(source, pullback)(
            lambda member_object: pullback((to_first.on_object(member_object), to_second.on_object(member_object))),
            lambda morphism: pullback.construct_morphism(
                pullback((to_first.on_object(morphism.domain()), to_second.on_object(morphism.domain()))),
                pullback((to_first.on_object(morphism.codomain()), to_second.on_object(morphism.codomain()))),
                (to_first.on_morphism(morphism), to_second.on_morphism(morphism)),
            ),
        )

    return Cat().Pullbacks().with_universal_data(diagram, pullback, cone(diagram, pullback, lambda vertex: legs[cospan.label(vertex)]), mediator)
