"""Finite sets and total functions.

The primitive constructions follow Sage's finite enumerated sets and
Mathlib's CategoryTheory.Limits.Types. General finite limits and colimits
are inherited from the product/equalizer calculus in Cat.
"""

from __future__ import annotations

__all__ = ["FiniteSetsCategory", "FiniteSets"]

from collections.abc import Callable, Hashable, Iterable, Iterator
from functools import cache
from typing import Literal

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Cat, Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.cones import cone, cocone, cone_apex, cocone_apex
from sage_categories.cat.predicates import Proposition, ask, register_handler
from sage_categories.sets._finite import cartesian, quotient

type Map = Callable[[Hashable], Hashable]


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


class FiniteSetsCategory(Category[[Map], []]):
    class ObjectType:
        def __init__(self, values: tuple[Hashable, ...]) -> None:
            self._values = values
            self._lookup = {value: value for value in values}

        def representative(self, datum: Hashable) -> Hashable:
            try:
                return self._lookup[datum]
            except KeyError:
                return _representative(self._values, datum)

        @cache
        def point(self, datum: Hashable) -> FiniteSetsCategory.ElementType:
            datum = self.representative(datum)
            defining = Mor(FiniteSets)(FiniteSets.Terminal(), self)(lambda value: datum)
            return FiniteSets.ElementType(defining, data=datum)

        def __iter__(self) -> Iterator[FiniteSetsCategory.ElementType]:
            return (self.point(value) for value in self._values)

        def __len__(self) -> int:
            return len(self._values)

        def __contains__(self, point: CategoryOfCategories.ElementType) -> bool:
            return point.parent() is self

        def __repr__(self) -> str:
            return f"FiniteSet({self._values!r})"

    class ElementType:
        def __init__(self, datum: Hashable) -> None:
            self._datum = datum

        def datum(self) -> Hashable:
            return self._datum

    class MorphismType:
        def __init__(self, pairs: tuple[tuple[Hashable, Hashable], ...]) -> None:
            self._table = dict(pairs)

        def __call__(
            self, point: CategoryOfCategories.ElementType
        ) -> FiniteSetsCategory.ElementType:
            assert point in self.domain()
            return self.codomain().point(self._table[point.datum()])

    def _equal_objects(
        self,
        first: FiniteSetsCategory.ObjectType,
        second: FiniteSetsCategory.ObjectType,
        assumptions: Proposition,
    ) -> bool:
        return len(first) == len(second) and all(
            any(_equal_datum(a, b) for b in second._values) for a in first._values
        )

    def _equal_morphisms(
        self,
        first: FiniteSetsCategory.MorphismType,
        second: FiniteSetsCategory.MorphismType,
        assumptions: Proposition,
    ) -> bool:
        return (
            first.domain() is second.domain()
            and first.codomain() is second.codomain()
            and all(
                _equal_datum(first._table[value], second._table[value])
                for value in first.domain()._values
            )
        )

    def _equal_points(
        self,
        first: FiniteSetsCategory.ElementType,
        second: FiniteSetsCategory.ElementType,
        assumptions: Proposition,
    ) -> bool:
        return first.parent() is second.parent() and _equal_datum(
            first.datum(), second.datum()
        )

    def __call__(self, values: Iterable[Hashable]) -> FiniteSetsCategory.ObjectType:
        return self.ObjectType(tuple(dict.fromkeys(values)))

    def Terminal(self) -> FiniteSetsCategory.ObjectType:
        return self(((),))

    def element_from_defining_morphism(
        self, arrow: MorphismCategory.ObjectType
    ) -> FiniteSetsCategory.ElementType:
        assert arrow.domain() is self.Terminal()
        return arrow.codomain().point(arrow._table[()])

    def construct_morphism(
        self,
        source: CategoryOfCategories.ElementType,
        target: CategoryOfCategories.ElementType,
        action: Map,
    ) -> MorphismCategory.ObjectType:
        pairs = tuple(
            (value, target.representative(action(value))) for value in source._values
        )
        return self.MorphismType(domain=source, codomain=target, data=pairs)

    def construct_identity(
        self, value: CategoryOfCategories.ElementType
    ) -> MorphismCategory.ObjectType:
        return self.construct_morphism(value, value, lambda datum: datum)

    def composite(
        self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType
    ) -> MorphismCategory.ObjectType:
        return self.construct_morphism(
            first.domain(),
            second.codomain(),
            lambda value: second._table[first._table[value]],
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
                    candidate.component(vertex)._table[value] for vertex in vertices
                )
            )
        else:
            arrows = shape.generating_morphisms()
            first, second = (diagram.on_morphism(arrow) for arrow in arrows)
            apex = self(
                value
                for value in first.domain()._values
                if first._table[value] == second._table[value]
            )
            legs = lambda vertex: Mor(self)(apex, diagram.on_object(vertex))(
                lambda value: (
                    value if vertex is arrows[0].domain() else first._table[value]
                )
            )
            lift = lambda candidate: Mor(self)(cone_apex(candidate), apex)(
                lambda value: candidate.component(arrows[0].domain())._table[value]
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
                lambda value: candidate.component(vertices[value[0]])._table[value[1]]
            )
        else:
            arrows = shape.generating_morphisms()
            first, second = (diagram.on_morphism(arrow) for arrow in arrows)
            classes = quotient(
                first.codomain()._values,
                (
                    (first._table[value], second._table[value])
                    for value in first.domain()._values
                ),
            )
            apex = self(classes.values())
            legs = lambda vertex: Mor(self)(diagram.on_object(vertex), apex)(
                lambda value: (
                    classes[first._table[value]]
                    if vertex is arrows[0].domain()
                    else classes[value]
                )
            )
            descent = lambda candidate: Mor(self)(apex, cocone_apex(candidate))(
                lambda value: candidate.component(arrows[0].codomain())._table[
                    next(iter(value))
                ]
            )
        return self.Colimits(shape).with_universal_data(
            diagram, apex, cocone(diagram, apex, legs), descent
        )

    def image_factorization(
        self, arrow: MorphismCategory.ObjectType
    ) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
        """The surjection onto the image and its inclusion into the codomain."""
        image = self(arrow._table.values())
        return Mor(self)(arrow.domain(), image)(lambda value: arrow._table[value]), Mor(
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
            lambda value: inverse[arrow._table[value]]
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


FiniteSets: FiniteSetsCategory = FiniteSetsCategory()
register_handler(FiniteSets.equality(), FiniteSets._equal_objects)
register_handler(FiniteSets.equality(), FiniteSets._equal_morphisms)
register_handler(FiniteSets.equality(), FiniteSets._equal_points)
