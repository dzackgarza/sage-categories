"""Sets presented by finite data or membership propositions, and total functions.

The primitive constructions follow Sage's finite enumerated sets and
Mathlib's CategoryTheory.Limits.Types. General finite limits and colimits
are inherited from the product/equalizer calculus in Cat.
"""

from __future__ import annotations

__all__ = ["SetsCategory", "Sets", "FiniteSets"]

from collections.abc import Callable, Hashable, Iterable, Iterator
from functools import cache
from typing import Literal, overload

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, Fun, Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.cones import cone, cocone, cone_apex, cocone_apex
from sage_categories.cat.predicates import Axiom, Predicate, Proposition, ask, register_handler
from sympy import true, false
from sage_categories.sets._finite import cartesian, quotient

type Map = Callable[[Hashable], Hashable]
type MembershipRule = Callable[[Hashable], Proposition]


class FinitePredicate(Predicate):
    name = "finite_set"


class SetMembershipPredicate(Predicate):
    name = "set_membership"


finite_set = FinitePredicate()
set_membership = SetMembershipPredicate()


def _equal_datum(first: Hashable, second: Hashable) -> bool:
    if first is second:
        return True
    if isinstance(first, CategoryOfCategories.ElementType):
        return (
            isinstance(second, CategoryOfCategories.ElementType)
            and ask(first == second) is True
        )
    if isinstance(first, tuple):
        return (
            isinstance(second, tuple)
            and len(first) == len(second)
            and all(_equal_datum(a, b) for a, b in zip(first, second))
        )
    return first == second


def _representative(values: tuple[Hashable, ...], datum: Hashable) -> Hashable:
    for value in values:
        if _equal_datum(value, datum):
            return value
    raise AssertionError(f"{datum!r} is outside the finite codomain")


class SetsCategory(Category[[Map], []]):
    def __repr__(self) -> str:
        return "Sets"

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(Sets, Sets).one(),)

    def _finite(self, value: SetsCategory.ObjectType) -> Proposition:
        return finite_set(value)

    Finite = Axiom(_finite)

    class ObjectType:
        def __init__(self, presentation: tuple[Hashable, ...] | MembershipRule) -> None:
            self._presentation = presentation
            if isinstance(presentation, tuple):
                self._lookup = {value: value for value in presentation}

        @property
        def _values(self) -> tuple[Hashable, ...]:
            assert isinstance(self._presentation, tuple), "this set has no chosen enumeration"
            return self._presentation

        def representative(self, datum: Hashable) -> Hashable:
            if isinstance(self._presentation, tuple):
                if datum in self._lookup:
                    return self._lookup[datum]
                return _representative(self._presentation, datum)
            assert ask(self._presentation(datum)) is True, "set membership is not established"
            return datum

        @cache
        def point(self, datum: Hashable) -> SetsCategory.ElementType:
            datum = self.representative(datum)
            defining = Mor(Sets)(Sets.Terminal(), self)(lambda value: datum)
            return Sets.ElementType(defining, data=datum)

        def __iter__(self) -> Iterator[SetsCategory.ElementType]:
            return (self.point(value) for value in self._values)

        def __len__(self) -> int:
            return len(self._values)

        def __contains__(self, point: CategoryOfCategories.ElementType) -> bool:
            return ask(self.membership_proposition(point)) is True

        def membership_proposition(self, point: CategoryOfCategories.ElementType) -> Proposition:
            return set_membership(self, point)

        def __repr__(self) -> str:
            return f"Set({self._presentation!r})"

    class ElementType:
        def __init__(self, datum: Hashable) -> None:
            self._datum = datum

        def datum(self) -> Hashable:
            return self._datum

    class MorphismType:
        def __init__(self, action: Map) -> None:
            self._action = action

        @property
        def _table(self) -> dict[Hashable, Hashable]:
            return {value: self._action(value) for value in self.domain()._values}

        def __call__(
            self, point: CategoryOfCategories.ElementType
        ) -> SetsCategory.ElementType:
            assert point in self.domain()
            return self.codomain().point(self._action(point.datum()))

    def _equal_objects(
        self,
        first: SetsCategory.ObjectType,
        second: SetsCategory.ObjectType,
        assumptions: Proposition,
    ) -> bool | None:
        if not isinstance(first._presentation, tuple) or not isinstance(second._presentation, tuple):
            return None
        return len(first) == len(second) and all(
            any(_equal_datum(a, b) for b in second._values) for a in first._values
        )

    def _equal_morphisms(
        self,
        first: SetsCategory.MorphismType,
        second: SetsCategory.MorphismType,
        assumptions: Proposition,
    ) -> bool | None:
        if not isinstance(first.domain()._presentation, tuple):
            return None
        return (
            first.domain() is second.domain()
            and first.codomain() is second.codomain()
            and all(
                _equal_datum(first._action(value), second._action(value))
                for value in first.domain()._values
            )
        )

    def _equal_points(
        self,
        first: SetsCategory.ElementType,
        second: SetsCategory.ElementType,
        assumptions: Proposition,
    ) -> bool:
        return first.parent() is second.parent() and _equal_datum(
            first.datum(), second.datum()
        )

    @overload
    def __call__(self) -> SetsCategory: ...

    @overload
    def __call__(self, values: Iterable[Hashable]) -> SetsCategory.ObjectType: ...

    def __call__(self, values: Iterable[Hashable] | None = None) -> SetsCategory | SetsCategory.ObjectType:
        if values is None:
            return self
        return self.ObjectType(tuple(dict.fromkeys(values)))

    def from_membership(self, rule: MembershipRule) -> SetsCategory.ObjectType:
        """Represent a set by its membership proposition, without choosing an enumeration."""
        return self.ObjectType(rule)

    def constant(self, source: SetsCategory.ObjectType, point: SetsCategory.ElementType) -> SetsCategory.MorphismType:
        """The total constant map with the supplied value."""
        return self.MorphismType(domain=source, codomain=point.parent(), data=lambda datum: point.datum())

    def Initial(self) -> SetsCategory.ObjectType:
        return self(())

    def subobjects_type(self) -> type[SetSubobjects]:
        return SetSubobjects

    def Terminal(self) -> SetsCategory.ObjectType:
        return self(((),))

    def element_from_defining_morphism(
        self, arrow: MorphismCategory.ObjectType
    ) -> SetsCategory.ElementType:
        assert arrow.domain() is self.Terminal()
        return arrow.codomain().point(arrow._action(()))

    def construct_morphism(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        action: Map,
    ) -> MorphismCategory.ObjectType:
        pairs = tuple(
            (value, target.representative(action(value))) for value in source._values
        )
        return self.MorphismType(domain=source, codomain=target, data=dict(pairs).__getitem__)

    def construct_identity(
        self, value: CategoryOfCategories.ElementType
    ) -> MorphismCategory.ObjectType:
        return self.MorphismType(domain=value, codomain=value, data=lambda datum: datum)

    def composite(
        self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType:
        return self.MorphismType(
            domain=first.domain(),
            codomain=second.codomain(),
            data=lambda value: second._action(first._action(value)),
        )

    def limit_construction(
        self, shape: Category
    ) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        if (
            shape.is_discrete()
            or shape is Cat().WalkingParallelPair()
            or shape.op() is Cat().WalkingParallelPair()
        ):
            return self._primitive_limit
        return Category.limit_construction(self, shape)

    def colimit_construction(
        self, shape: Category
    ) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        if (
            shape.is_discrete()
            or shape is Cat().WalkingParallelPair()
            or shape.op() is Cat().WalkingParallelPair()
        ):
            return self._primitive_colimit
        return Category.colimit_construction(self, shape)

    def _primitive_limit(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        from sage_categories.cat.finite_categories import finite_category

        shape = diagram.domain()
        vertices = finite_category(shape).objects
        if shape.is_discrete():
            apex = self(
                cartesian(diagram.on_object(vertex)._values for vertex in vertices)
            )
            position = {id(vertex): index for index, vertex in enumerate(vertices)}
            legs = lambda vertex: Mor(self)(apex, diagram.on_object(vertex))(
                lambda value: value[position[id(vertex)]]
            )
            lift = lambda candidate: Mor(self)(cone_apex(candidate), apex)(
                lambda value: tuple(
                    candidate.component(vertex)._action(value) for vertex in vertices
                )
            )
        else:
            arrows = shape.generating_morphisms()
            first, second = (diagram.on_morphism(arrow) for arrow in arrows)
            apex = self(
                value
                for value in first.domain()._values
                if first._action(value) == second._action(value)
            )
            legs = lambda vertex: Mor(self)(apex, diagram.on_object(vertex))(
                lambda value: (
                    value if vertex is arrows[0].domain() else first._action(value)
                )
            )
            lift = lambda candidate: Mor(self)(cone_apex(candidate), apex)(
                lambda value: candidate.component(arrows[0].domain())._action(value)
            )
        return self.Limits(shape).with_universal_data(
            diagram, apex, cone(diagram, apex, legs), lift
        )

    def _primitive_colimit(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        from sage_categories.cat.finite_categories import finite_category

        shape = diagram.domain()
        vertices = finite_category(shape).objects
        if shape.is_discrete():
            position = {id(vertex): index for index, vertex in enumerate(vertices)}
            apex = self(
                (index, value)
                for index, vertex in enumerate(vertices)
                for value in diagram.on_object(vertex)._values
            )
            legs = lambda vertex: Mor(self)(diagram.on_object(vertex), apex)(
                lambda value: (position[id(vertex)], value)
            )
            descent = lambda candidate: Mor(self)(apex, cocone_apex(candidate))(
                lambda value: candidate.component(vertices[value[0]])._action(value[1])
            )
        else:
            arrows = shape.generating_morphisms()
            first, second = (diagram.on_morphism(arrow) for arrow in arrows)
            classes = quotient(
                first.codomain()._values,
                (
                    (first._action(value), second._action(value))
                    for value in first.domain()._values
                ),
            )
            apex = self(classes.values())
            legs = lambda vertex: Mor(self)(diagram.on_object(vertex), apex)(
                lambda value: (
                    classes[first._action(value)]
                    if vertex is arrows[0].domain()
                    else classes[value]
                )
            )
            descent = lambda candidate: Mor(self)(apex, cocone_apex(candidate))(
                lambda value: candidate.component(arrows[0].codomain())._action(next(iter(value)))
            )
        return self.Colimits(shape).with_universal_data(
            diagram, apex, cocone(diagram, apex, legs), descent
        )

    def image_factorization(
        self, arrow: MorphismCategory.ObjectType
    ) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
        """The surjection onto the image and its inclusion into the codomain."""
        image = self(arrow._table.values())
        return Mor(self)(arrow.domain(), image)(lambda value: arrow._action(value)), Mor(
            self
        )(image, arrow.codomain()).Monomorphisms()(lambda value: value)

    def factor_through_monomorphism(
        self, mono: MorphismCategory.ObjectType, arrow: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType | Literal[False]:
        assert mono.codomain() is arrow.codomain()
        inverse = {image: value for value, image in mono._table.items()}
        if not all(image in inverse for image in arrow._table.values()):
            return False
        return Mor(self)(arrow.domain(), mono.domain())(
            lambda value: inverse[arrow._action(value)]
        )

    @cache
    def hom_morphisms(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
    ) -> tuple[MorphismCategory.ObjectType, ...]:
        return tuple(
            Mor(self)(source, target)(dict(zip(source._values, images)).__getitem__)
            for images in cartesian(target._values for _ in source._values)
        )


def _finite_presentation(value: SetsCategory.ObjectType, assumptions: Proposition) -> bool | None:
    if isinstance(value._presentation, tuple):
        return True
    return None


def _set_member(
    value: SetsCategory.ObjectType,
    point: SetsCategory.ElementType,
    assumptions: Proposition,
) -> bool:
    return point.parent() is value


from sage_categories.cat.slices import SliceProperty, SliceLikeCategory


class SetSubobjects(SliceProperty):
    class ObjectType:
        """A set with its inclusion into the fixed set."""

    class ElementType:
        """A point inherited from the slice."""

    class MorphismType:
        """A commuting triangle of set inclusions."""

    def from_predicate(
        self, predicate: Callable[[SetsCategory.ElementType], Proposition]
    ) -> SliceLikeCategory.ObjectType:
        ambient = self.ambient().fixed_object()
        decisions = tuple((point, ask(predicate(point))) for point in ambient)
        assert all(decision is True or decision is False for _, decision in decisions), (
            "the finite predicate subset needs decided membership"
        )
        subset = Sets(point.datum() for point, decision in decisions if decision is True)
        inclusion = Mor(Sets)(subset, ambient).Monomorphisms()(lambda datum: datum)
        return self(inclusion)


Cat().implement(SetsCategory)
register_handler(finite_set, _finite_presentation)
register_handler(set_membership, _set_member)
FiniteSets = Sets.Finite()
register_handler(Sets.equality(), Sets._equal_objects)
register_handler(Sets.equality(), Sets._equal_morphisms)
register_handler(Sets.equality(), Sets._equal_points)
