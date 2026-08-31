"""The constructions ``Cat()`` owns (POL-CAT-050, POL-MATH-037): the strict limit of a diagram of categories, the coproduct over a discrete shape, and the exponential.

Each construction line carries its inspected citation (POL-MATH-040); the
universal property of each is a trusted declaration attached to the
constructor (POL-MATH-037, POL-MATH-036).

- The strict limit of ``D: I -> Cat()`` has as objects the ``I``-indexed families
  of objects that ``D`` carries to one another, given by rule, and as morphisms
  the componentwise families with the same compatibility: limits in ``Cat`` are
  computed on objects and on morphisms (Mathlib
  ``CategoryTheory.Cat.HasLimits.limitCone``, whose apex has as objects the
  compatible families of objects; inspected 2026-08-26).  The compatibility is
  decided by ``ask``: identity first, ``Unknown`` for two distinct rule-defined
  values (POL-MATH-034).  Its projection at ``i`` reads the component there.

  A discrete shape has no generating morphism, so it imposes no compatibility and
  the limit is the product of the family (Mathlib ``CategoryTheory.pi``; the
  binary case ``CategoryTheory.prod``; inspected 2026-08-26); ``L(2, 2)`` gives
  the fibre product.  A product is the fibre product over the terminal category,
  so the two are one construction at two shapes, and the projections of each are
  indexed by the objects of its shape (POL-CAT-092).
- The coproduct has as objects the tagged objects ``(i, x)`` with ``x`` in the
  ``i``-th category and as morphisms the morphisms within one tag (Mathlib
  ``CategoryTheory.Sigma.sigma``; the binary case ``CategoryTheory.sum``;
  inspected 2026-08-26).  ``coproduct_injection(i)`` tags.
- The exponential ``D ** C`` is ``Fun(C, D)`` (Mathlib ``CategoryTheory.Cat.exp_obj``;
  inspected 2026-08-26).

``Cat().Limits(I)`` and ``Cat().Colimits(I)`` for any other shape exist
(POL-CAT-051); constructing an object in them fails loudly, naming the missing
owned construction.

Each of these categories retains one object per construction datum -- one tagged
object per ``(i, x)``, one family per rule -- because a category has one object
per datum, and each functor image cache identifies images by it
(POL-CAT-066).  A universal object is unique up to unique isomorphism
and has one construction, so a second call with the same data returns the same
object; the projections, injections, and functor images of that construction are
likewise one morphism each, retained by the functor and the limiting cone that own
them (``cat/functors.py``; POL-CAT-012).
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sage.misc.cachefunc import cached_method
from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.cat.category import Category, member
from sage_categories.cat.constructions import cocone, cocone_apex, cone, cone_apex, vertex_of
from sage_categories.cat.declarations import Sets
from sage_categories.cat.diagrams import sequence_position
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.shapes import Discrete, DiscreteCategory
from sage_categories.cat.predicates import Decision, Unknown, UnknownClass
from sage_categories.cat.predicates import Predicate, Proposition, ask, conjunction
from sage_categories.kernel.refinement import is_placed

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = [
    "CoproductCategory",
    "LimitCategory",
    "coproduct_of_categories",
    "limit_of_categories",
    "product_of_categories",
    "pullback_of_categories",
]

type ObjectRule = Callable[["CategoryOfCategories.ElementType"], "CategoryOfCategories.ElementType"]
type MorphismRule = Callable[["CategoryOfCategories.ElementType"], MorphismCategory.ObjectType]


def _sequence_rule[Value](sequence: tuple[Value, ...]) -> Callable[[DiscreteCategory.ObjectType], Value]:
    """The rule of a sequence over ``Discrete([n])``, the convenience form of a family (POL-CAT-092)."""
    return lambda vertex: sequence[sequence_position(vertex)]


# -- the strict limit of a diagram of categories --------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class FamilyObjectData:
    """The local state introduced by an object of a strict limit."""

    rule: ObjectRule


@dataclass(frozen=True, eq=False, slots=True)
class FamilyMorphismData:
    """The local state introduced by a morphism of a strict limit."""

    rule: MorphismRule


# ``components_agree(family, L)``: the diagram carries the components of the family to
# one another, so the family is an object (or a morphism) of the strict limit ``L``.
components_agree = Predicate("components_agree", 2, False)


def _components_agree_along_diagram(candidate: CategoryOfCategories.ElementType, limit: Category) -> Decision:
    if not is_placed(candidate, limit):
        return Unknown
    return ask(limit._agrees(candidate.component))


components_agree.register_handler(_components_agree_along_diagram)


class LimitCategory(Category[[MorphismRule | tuple[MorphismCategory.ObjectType, ...]], []]):
    """The strict limit of a diagram of categories: the families its morphisms carry to one another."""

    class ObjectType:
        """An object of a strict limit: a family of objects by rule, one in each factor."""

        def __init__(self, data: FamilyObjectData) -> None:
            self._rule = data.rule
            super().__init__()
            self._shape = self.category().shape()

        def component(self, index: CategoryOfCategories.ElementType | Hashable) -> CategoryOfCategories.ElementType:
            """The object at ``i``, for ``i`` an object of the shape or a datum of its object set."""
            return self._rule(vertex_of(self._shape, index))

        def __repr__(self) -> str:
            return f"family in {self.category()!r}"

    class MorphismType:
        """A morphism of a strict limit: a componentwise family of morphisms."""

        def __init__(self, data: FamilyMorphismData) -> None:
            self._rule = data.rule
            super().__init__()
            self._shape = self.base_category().shape()

        def component(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            return self._rule(vertex_of(self._shape, index))

        def __repr__(self) -> str:
            return f"family morphism in {self.base_category()!r}"

    class ElementType:
        """A generalized element of a family; no local operation."""

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        self._finite_data: MonoDict = MonoDict()
        super().__init__()
        self._equality.register_handler(self._equal)

    def shape(self) -> Category:
        return self._diagram.domain()

    def factor(self, index: CategoryOfCategories.ElementType | Hashable) -> Category:
        return self._diagram.on_object(vertex_of(self.shape(), index))

    # -- the compatibility the diagram imposes ---------------------------------------
    #
    # A family is an object of the limit when the diagram carries each of its components
    # to the next; the shape's generating morphisms state that condition, so a discrete
    # shape imposes none and the limit is the product.  ``ask`` decides each equation:
    # identity first, ``Unknown`` for two distinct rule-defined values (POL-MATH-034).

    def _generators(self) -> tuple[MorphismCategory.ObjectType, ...]:
        edges = self.shape().generating_morphisms()
        assert edges is not Unknown, f"{self.shape()!r} names no generating morphisms, so the compatibility of a family over it is unstated"
        return edges

    def _agrees(self, rule: ObjectRule | MorphismRule) -> Proposition:
        """``D(u)(v_i) == v_j`` for every generating morphism ``u: i -> j`` of the shape."""
        return conjunction(self._diagram.on_morphism(edge)(rule(edge.domain())) == rule(edge.codomain()) for edge in self._generators())

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        return member(candidate, self) & components_agree(candidate, self)

    # -- the sets of objects and of morphisms (specs/functor.md, "Diagram shapes and universal constructions") --
    #
    # The families are the product, over the objects of the shape, of the factors' own
    # sets; the limit's set is the subobject of that product the compatibility cuts out,
    # which is the whole product when the shape has no generating morphism.

    def _positions(self) -> Category:
        """``Discrete(Ob(I))``: the index of the family products, one position per object of the shape."""
        return Discrete(self.shape().object_set())

    def _families(
        self,
        kind: str,
        factor_set: Callable[[Category], CategoryOfCategories.ElementType],
    ) -> CategoryOfCategories.ElementType:
        if kind not in self._finite_data:
            shape = self.shape()
            diagram = Fun(self._positions(), Sets).from_object_rule(lambda position: factor_set(self.factor(shape.object_at(position.point()))))
            self._finite_data[kind] = Sets.Products()(diagram)
        return self._finite_data[kind]

    def _component_at(
        self,
        families: CategoryOfCategories.ElementType,
        point: CategoryOfCategories.ElementType,
        vertex: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        """The point of the factor's set that a point of the family product names at one object of the shape."""
        return families.product_projection(self._positions()(self.shape().object_point(vertex)))(point)

    def _object_rule(
        self,
        families: CategoryOfCategories.ElementType,
        point: CategoryOfCategories.ElementType,
    ) -> ObjectRule:
        return lambda vertex: self.factor(vertex).object_at(self._component_at(families, point, vertex))

    def _morphism_rule(
        self,
        families: CategoryOfCategories.ElementType,
        point: CategoryOfCategories.ElementType,
    ) -> MorphismRule:
        return lambda vertex: self.factor(vertex).morphism_at(self._component_at(families, point, vertex))

    def object_set(self) -> CategoryOfCategories.ElementType:
        families = self._families("objects", lambda factor: factor.object_set())
        if not self._generators():
            return families
        if "object set" not in self._finite_data:
            self._finite_data["object set"] = families.subset_from(lambda datum: ask(self._agrees(self._object_rule(families, families.point(datum)))))
        return self._finite_data["object set"]

    def object_at(self, point: CategoryOfCategories.ElementType) -> LimitCategory.ObjectType:
        return self(self._object_rule(self._families("objects", lambda factor: factor.object_set()), point))

    def _chosen_morphism_set(self) -> CategoryOfCategories.ElementType | UnknownClass:
        vertices = self._vertices()
        if vertices is Unknown:
            return Unknown
        if any(ask(self.factor(vertex).morphism_set()) is Unknown for vertex in vertices):
            return Unknown
        families = self._families("morphisms", lambda factor: ask(factor.morphism_set()))
        if not self._generators():
            return families
        if "morphism set" not in self._finite_data:
            self._finite_data["morphism set"] = families.subset_from(lambda datum: ask(self._agrees(self._morphism_rule(families, families.point(datum)))))
        return self._finite_data["morphism set"]

    def morphism_at(self, point: CategoryOfCategories.ElementType) -> LimitCategory.MorphismType:
        rule = self._morphism_rule(self._families("morphisms", lambda factor: ask(factor.morphism_set())), point)
        return self.construct_morphism(
            self(lambda vertex: rule(vertex).domain()),
            self(lambda vertex: rule(vertex).codomain()),
            rule,
        )

    def _vertices(self) -> tuple[CategoryOfCategories.ElementType, ...] | UnknownClass:
        """The objects of the shape in its chosen enumeration, or ``Unknown`` when it chooses none."""
        shape, objects, finite = self.shape(), self.shape().object_set(), Sets.Finite()
        if not finite.has_chosen_enumeration(objects):
            return Unknown
        return tuple(shape.object_at(objects.point(datum)) for datum in finite.chosen_enumeration(objects))

    # -- construction ------------------------------------------------------------------

    def __call__(
        self,
        family: ObjectRule | tuple[CategoryOfCategories.ElementType, ...],
    ) -> LimitCategory.ObjectType:
        """``L(rule)`` for a family by rule; ``L((X_0, ..., X_n))`` for the sequence convenience over ``Discrete([n])``, retained per tuple."""
        if not callable(family):
            return self._from_sequence(tuple(family))
        rule = family
        assert ask(self._agrees(rule)) is not False, f"{family!r} is no family that {self._diagram!r} carries to itself"
        return self.ObjectType(category=self, data=FamilyObjectData(rule))

    @cached_method(key=lambda self, sequence: tuple((id(member_object), member_object) for member_object in sequence))
    def _from_sequence(self, sequence: tuple[CategoryOfCategories.ElementType, ...]) -> LimitCategory.ObjectType:
        rule = _sequence_rule(sequence)
        assert ask(self._agrees(rule)) is not False, f"{sequence!r} is no family that {self._diagram!r} carries to itself"
        for position, member_object in enumerate(sequence):
            assert member_object in self.factor(position), f"{member_object!r} is not an object of {self.factor(position)!r}"
        return self.ObjectType(category=self, data=FamilyObjectData(rule))

    def construct_morphism(
        self,
        domain: LimitCategory.ObjectType,
        codomain: LimitCategory.ObjectType,
        family: MorphismRule | tuple[MorphismCategory.ObjectType, ...],
    ) -> LimitCategory.MorphismType:
        rule = family if callable(family) else _sequence_rule(tuple(family))
        assert ask(self._agrees(rule)) is not False, f"{family!r} is no family of morphisms that {self._diagram!r} carries to itself"
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=domain,
            codomain=codomain,
            data=FamilyMorphismData(rule),
        )

    def construct_identity(self, member_object: LimitCategory.ObjectType) -> LimitCategory.MorphismType:
        def component_identity(vertex: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            component = member_object.component(vertex)
            return component.category().morphism_category(1)(component, component).one()

        return self.MorphismType(
            category=self.morphism_category(1),
            domain=member_object,
            codomain=member_object,
            data=FamilyMorphismData(component_identity),
        )

    def composite(self, second: LimitCategory.MorphismType, first: LimitCategory.MorphismType) -> LimitCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=first.domain(),
            codomain=second.codomain(),
            data=FamilyMorphismData(lambda vertex: second.component(vertex) * first.component(vertex)),
        )

    def _equal(self, first: CategoryOfCategories.ElementType, candidate: Any) -> Decision:
        """Two families (of objects or of morphisms) over a finitely enumerated shape are equal when every component is."""
        morphisms = self.morphism_category(1)
        if not ((first in self and candidate in self) or (first in morphisms and candidate in morphisms)):
            return Unknown
        vertices = self._vertices()
        if vertices is Unknown:
            return Unknown
        return ask(conjunction(first.component(vertex) == candidate.component(vertex) for vertex in vertices))

    def __repr__(self) -> str:
        return f"Limit({self._diagram!r})"


def limit_of_categories(
    diagram: Functor,
    family: Category,
    category_type: Callable[[Functor], LimitCategory] = LimitCategory,
) -> CategoryOfCategories.ElementType:
    """The strict limit of ``diagram``, retained in ``family`` with its cone of projections and its mediator.

    The projection at an object of the shape reads the component there, of a family and
    of a family morphism alike; the mediator of a cone assembles the family of its
    components.  Both are indexed by the shape, so a product and a fibre product are the
    same construction at two shapes (POL-CAT-092).
    """
    limit = category_type(diagram)
    projections: MonoDict = MonoDict()

    def projection(vertex: CategoryOfCategories.ElementType) -> Functor:
        if vertex not in projections:
            projections[vertex] = Fun(limit, diagram.on_object(vertex))(
                lambda member_object: member_object.component(vertex),
                lambda morphism: morphism.component(vertex),
            )
        return projections[vertex]

    def mediator(candidate_cone: NaturalTransformation) -> Functor:
        source = cone_apex(candidate_cone)
        return Fun(source, limit)(
            lambda member_object: limit(lambda vertex: candidate_cone.component(vertex).on_object(member_object)),
            lambda morphism: limit.construct_morphism(
                limit(lambda vertex: candidate_cone.component(vertex).on_object(morphism.domain())),
                limit(lambda vertex: candidate_cone.component(vertex).on_object(morphism.codomain())),
                lambda vertex: candidate_cone.component(vertex).on_morphism(morphism),
            ),
        )

    lowered = family.lowered(diagram)
    return family.with_universal_data(lowered, limit, cone(lowered, limit, projection), mediator)


def product_of_categories(diagram: Functor) -> CategoryOfCategories.ElementType:
    """``Cat().Products()(diagram)`` for a diagram over ``Discrete(S)``: the limit imposes no condition there."""
    return limit_of_categories(diagram, Cat().Products())


def pullback_of_categories(diagram: Functor) -> CategoryOfCategories.ElementType:
    """``Cat().Pullbacks()(diagram)`` for a diagram over the walking cospan ``L(2, 2)``."""
    return limit_of_categories(diagram, Cat().Pullbacks())




# -- coproducts of categories --------------------------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class TaggedObjectData:
    """The local state introduced by a coproduct-category object."""

    tag: DiscreteCategory.ObjectType
    member: CategoryOfCategories.ElementType


@dataclass(frozen=True, eq=False, slots=True)
class TaggedMorphismData:
    """The local state introduced by a coproduct-category morphism."""

    morphism: MorphismCategory.ObjectType


class CoproductCategory(Category[[MorphismCategory.ObjectType], []]):
    """The coproduct of an ``S``-indexed family of categories."""

    class ObjectType:
        """An object of a coproduct category: an object of one summand, tagged by its index."""

        def __init__(self, data: TaggedObjectData) -> None:
            self._tag = data.tag
            self._member = data.member
            super().__init__()

        def tag(self) -> DiscreteCategory.ObjectType:
            return self._tag

        def member(self) -> CategoryOfCategories.ElementType:
            return self._member

        def __repr__(self) -> str:
            return f"({self._tag!r}, {self._member!r})"

    class MorphismType:
        """A morphism of a coproduct category: a morphism within one summand."""

        def __init__(self, data: TaggedMorphismData) -> None:
            self._morphism = data.morphism
            super().__init__()

        def morphism(self) -> MorphismCategory.ObjectType:
            return self._morphism

        def __repr__(self) -> str:
            return f"({self.domain().tag()!r}, {self._morphism!r})"

    class ElementType:
        """A generalized element of a tagged object; no local operation."""

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        self._objects: TripleDict = TripleDict(weak_values=False)
        super().__init__()
        self._equality.register_handler(self._equal)

    def shape(self) -> Category:
        return self._diagram.domain()

    def summand(self, index: CategoryOfCategories.ElementType | Hashable) -> Category:
        return self._diagram.on_object(vertex_of(self.shape(), index))

    def _equal(self, first: CategoryOfCategories.ElementType, candidate: Any) -> Decision:
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

    def __call__(
        self,
        index: CategoryOfCategories.ElementType | Hashable,
        member_object: CategoryOfCategories.ElementType,
    ) -> CoproductCategory.ObjectType:
        """``Q(i, x)``: the object of the ``i``-th summand tagged by ``i``, retained per pair."""
        tag = vertex_of(self.shape(), index)
        assert member_object in self.summand(tag), f"{member_object!r} is not an object of {self.summand(tag)!r}"
        key = (tag, member_object, self)
        if key not in self._objects:
            self._objects[key] = self.ObjectType(category=self, data=TaggedObjectData(tag, member_object))
        return self._objects[key]

    def construct_morphism(
        self,
        domain: CoproductCategory.ObjectType,
        codomain: CoproductCategory.ObjectType,
        morphism: MorphismCategory.ObjectType,
    ) -> CoproductCategory.MorphismType:
        assert domain.tag() is codomain.tag(), f"{domain!r} and {codomain!r} lie in different summands"
        assert morphism in self.summand(domain.tag()).morphism_category(1)(domain.member(), codomain.member())
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=domain,
            codomain=codomain,
            data=TaggedMorphismData(morphism),
        )

    def construct_identity(self, member_object: CoproductCategory.ObjectType) -> CoproductCategory.MorphismType:
        member = member_object.member()
        return self.MorphismType(
            category=self.morphism_category(1),
            domain=member_object,
            codomain=member_object,
            data=TaggedMorphismData(member.category().morphism_category(1)(member, member).one()),
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


def coproduct_of_categories(diagram: Functor) -> CategoryOfCategories.ElementType:
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
