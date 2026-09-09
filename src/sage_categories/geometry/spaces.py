"""Represented topological spaces and continuous maps with retained inverse image on opens."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass

from sympy import false, true

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method
from sage_categories.order.posets import BinaryRelations, Posets, Thin

__all__ = ["TopologicalSpaces", "TopologicalSpacesCategory"]


@dataclass(frozen=True, eq=False, slots=True)
class _TopologyData:
    carrier: CategoryOfCategories.ElementType
    opens: CategoryOfCategories.ElementType


class TopologicalSpacesCategory(Category[[MorphismCategory.ObjectType], []]):
    """Represented topological spaces; the first executable domain is a finite topology."""

    class ObjectType:
        def __init__(self, data: _TopologyData) -> None:
            self._carrier = data.carrier
            self._opens = data.opens
            self._open_category = Thin.on_object(data.opens)
            self._open_points = {
                point.datum(): point for point in data.opens.carrier()
            }

        def carrier(self) -> CategoryOfCategories.ElementType:
            return self._carrier

        def opens(self) -> CategoryOfCategories.ElementType:
            """The inclusion poset of represented open subsets."""
            return self._opens

        def open_category(self) -> Category:
            """The thin category ``O(X)`` of represented opens and inclusions."""
            return self._open_category

        def open_point(self, subset: frozenset[Hashable]) -> CategoryOfCategories.ElementType:
            assert subset in self._open_points, f"{subset!r} is not a represented open"
            return self._open_points[subset]

        def open_object(self, subset: frozenset[Hashable]) -> CategoryOfCategories.ElementType:
            return self._open_category(self.open_point(subset))

    class ElementType:
        pass

    class MorphismType:
        def __init__(
            self,
            data: tuple[MorphismCategory.ObjectType, Functor],
        ) -> None:
            self._underlying_map, self._inverse_image = data

        def underlying_map(self) -> MorphismCategory.ObjectType:
            return self._underlying_map

        def inverse_image(self) -> Functor:
            """The contravariant functor ``O(Y) -> O(X)`` induced by this map ``X -> Y``."""
            return self._inverse_image

    @cached_method
    def to_sets(self) -> Functor:
        return Fun(self, Sets).Faithful()(
            lambda space: space.carrier(),
            lambda arrow: arrow.underlying_map(),
        )

    def structure_functors(self) -> tuple[Functor, ...]:
        return (*super().structure_functors(), self.to_sets())

    def __call__(
        self,
        carrier: CategoryOfCategories.ElementType,
        opens: tuple[frozenset[Hashable], ...],
    ) -> TopologicalSpacesCategory.ObjectType:
        """The finite topology on ``carrier`` with exactly the supplied open subsets."""
        values = frozenset(point.datum() for point in carrier)
        family = tuple(dict.fromkeys(opens))
        assert frozenset() in family and values in family
        assert all(open_set <= values for open_set in family)
        assert all(first | second in family for first in family for second in family)
        assert all(first & second in family for first in family for second in family)
        open_carrier = Sets(family)
        relation = BinaryRelations().from_predicate(
            open_carrier,
            lambda first, second: true if first.datum() <= second.datum() else false,
        )
        open_poset = Posets()(relation.relation())
        return self.ObjectType(_TopologyData(carrier, open_poset))

    def _inverse_image_functor(
        self,
        source: TopologicalSpacesCategory.ObjectType,
        target: TopologicalSpacesCategory.ObjectType,
        underlying: MorphismCategory.ObjectType,
    ) -> Functor:
        source_data = tuple(point.datum() for point in source.carrier())
        target_opens = target.open_category()
        source_opens = source.open_category()

        def inverse_subset(target_open: CategoryOfCategories.ElementType) -> frozenset[Hashable]:
            subset = target_open.point().datum()
            return frozenset(
                datum
                for datum in source_data
                if underlying(source.carrier().point(datum)).datum() in subset
            )

        def on_object(target_open: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            return source.open_object(inverse_subset(target_open))

        def on_morphism(inclusion: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            domain, codomain = on_object(inclusion.domain()), on_object(inclusion.codomain())
            return Mor(source_opens)(domain, codomain)()

        inverse = Fun(target_opens, source_opens)(on_object, on_morphism)
        for point in target.opens().carrier():
            target_open = target_opens(point)
            source.open_point(inverse_subset(target_open))
        return inverse

    def construct_morphism(
        self,
        source: TopologicalSpacesCategory.ObjectType,
        target: TopologicalSpacesCategory.ObjectType,
        underlying: MorphismCategory.ObjectType,
    ) -> TopologicalSpacesCategory.MorphismType:
        assert underlying.domain() is source.carrier() and underlying.codomain() is target.carrier()
        inverse = self._inverse_image_functor(source, target, underlying)
        return self.MorphismType(domain=source, codomain=target, data=(underlying, inverse))

    def construct_identity(
        self,
        member_object: TopologicalSpacesCategory.ObjectType,
    ) -> TopologicalSpacesCategory.MorphismType:
        return self.construct_morphism(
            member_object,
            member_object,
            Mor(Sets)(member_object.carrier(), member_object.carrier()).one(),
        )

    def composite(
        self,
        second: TopologicalSpacesCategory.MorphismType,
        first: TopologicalSpacesCategory.MorphismType,
    ) -> TopologicalSpacesCategory.MorphismType:
        return self.construct_morphism(
            first.domain(),
            second.codomain(),
            second.underlying_map() * first.underlying_map(),
        )

    def __repr__(self) -> str:
        return "TopologicalSpaces"


@cached_function(key=identity_key)
def TopologicalSpaces() -> TopologicalSpacesCategory:
    return TopologicalSpacesCategory()
