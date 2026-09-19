"""Represented topological spaces and continuous maps with retained inverse image on opens."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from typing import Any, cast

from sympy import false, true

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.choices import SelectedChoice
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Fun, Functor
from sage_categories.cat.leaf_categories import MorphismDataCategory
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.order.posets import BinaryRelations, Posets, Thin

__all__ = ["TopologicalSpaces", "TopologicalSpacesCategory"]

_QUOTIENT_PROJECTIONS: SelectedChoice[MorphismCategory.ObjectType] = SelectedChoice()


def _topological_space_projection(source: Category) -> Functor:
    """Forget a structured topological category through its retained space/map accessors."""
    return Fun(source, TopologicalSpaces())(
        lambda value: cast(Any, value).space(),
        lambda arrow: cast(Any, arrow).continuous_map(),
    )


@dataclass(frozen=True, eq=False, slots=True)
class _TopologyData[OpenKey: Hashable]:
    carrier: CategoryOfCategories.ElementType
    opens: CategoryOfCategories.ElementType
    open_category: Category
    open_point_rule: Callable[[OpenKey], CategoryOfCategories.ElementType]
    open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType]


class TopologicalSpacesCategory(MorphismDataCategory):
    """Represented topological spaces; the first executable domain is a finite topology."""

    class ObjectType[OpenKey: Hashable = Hashable]:
        def __init__(self, data: _TopologyData[OpenKey]) -> None:
            self._carrier = data.carrier
            self._opens = data.opens
            self._open_category = data.open_category
            self._open_point_rule = data.open_point_rule
            self._open_object_rule = data.open_object_rule

        def carrier(self) -> CategoryOfCategories.ElementType:
            return self._carrier

        def opens(self) -> CategoryOfCategories.ElementType:
            """The inclusion poset of represented open subsets."""
            return self._opens

        def open_category(self) -> Category:
            """The thin category ``O(X)`` of represented opens and inclusions."""
            return self._open_category

        def open_point(self, key: OpenKey) -> CategoryOfCategories.ElementType:
            return self._open_point_rule(key)

        def open_object(self, key: OpenKey) -> CategoryOfCategories.ElementType:
            return self._open_object_rule(key)

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

    def to_sets(self) -> Functor:
        return next(functor for functor in self.selected_functors() if functor.codomain() is Sets)

    def structure_functors(self) -> tuple[Functor, ...]:
        underlying = Fun(self, Sets).Faithful().Isofibrations()(
            lambda space: space.carrier(),
            lambda arrow: arrow.underlying_map(),
        )
        return (*super().structure_functors(), underlying)

    def __call__(
        self,
        carrier: CategoryOfCategories.ElementType,
        opens: tuple[frozenset[Hashable], ...],
    ) -> TopologicalSpacesCategory.ObjectType[frozenset[Hashable]]:
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
        open_category = Thin.on_object(open_poset)
        open_points = {key: open_poset.point(key) for key in family}

        def open_point(key: frozenset[Hashable]) -> CategoryOfCategories.ElementType:
            assert key in open_points, f"{key!r} is not a represented open"
            return open_points[key]

        return self.ObjectType(
            _TopologyData(
                carrier,
                open_poset,
                open_category,
                open_point,
                lambda key: open_category(open_point(key)),
            )
        )

    def from_open_category[OpenKey: Hashable](
        self,
        carrier: CategoryOfCategories.ElementType,
        opens: CategoryOfCategories.ElementType,
        open_category: Category,
        open_point_rule: Callable[[OpenKey], CategoryOfCategories.ElementType],
        open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType],
    ) -> TopologicalSpacesCategory.ObjectType[OpenKey]:
        """Retain a topology whose opens and inclusion category are represented without enumeration."""
        return self.ObjectType(
            _TopologyData(
                carrier,
                opens,
                open_category,
                open_point_rule,
                open_object_rule,
            )
        )

    def quotient_from_open_category[OpenKey: Hashable](
        self,
        ambient: CategoryOfCategories.ElementType,
        equivalent: Callable[
            [CategoryOfCategories.ElementType, CategoryOfCategories.ElementType],
            object,
        ],
        opens: CategoryOfCategories.ElementType,
        open_category: Category,
        open_point_rule: Callable[[OpenKey], CategoryOfCategories.ElementType],
        open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType],
    ) -> TopologicalSpacesCategory.ObjectType[OpenKey]:
        """Form a represented quotient topology from an owned equivalence relation.

        ``Sets`` owns the quotient carrier and projection; ``TopologicalSpaces``
        owns the resulting represented topology. The caller supplies only the
        mathematical equivalence relation and the represented open category.
        """
        quotient, projection = Sets.quotient(ambient, equivalent)
        space = self.from_open_category(
            quotient,
            opens,
            open_category,
            open_point_rule,
            open_object_rule,
        )
        _QUOTIENT_PROJECTIONS.select(self, (space,), projection)
        return space

    def quotient_projection(
        self,
        space: TopologicalSpacesCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        """The retained set quotient map underlying a quotient topology."""
        return _QUOTIENT_PROJECTIONS.selected(self, (space,))

    def quotient_chart_morphism[SourceKey: Hashable, TargetKey: Hashable](
        self,
        source: TopologicalSpacesCategory.ObjectType[SourceKey],
        target: TopologicalSpacesCategory.ObjectType[TargetKey],
        tag_rule: Callable[[Hashable], Hashable],
        preimage_rule: Callable[
            [CategoryOfCategories.ElementType], CategoryOfCategories.ElementType
        ],
    ) -> TopologicalSpacesCategory.MorphismType:
        """The continuous chart map into a represented quotient topology."""
        projection = self.quotient_projection(target)
        ambient = projection.domain()
        assert projection.codomain() is target.carrier()

        def point_image(value: Hashable) -> Hashable:
            return projection(cast(Any, ambient).point(tag_rule(value))).datum()

        underlying = Mor(Sets)(source.carrier(), target.carrier())(point_image)
        target_opens = target.open_category()
        source_opens = source.open_category()
        inverse = Fun(target_opens, source_opens)(
            preimage_rule,
            lambda inclusion: Mor(source_opens)(
                preimage_rule(inclusion.domain()),
                preimage_rule(inclusion.codomain()),
            )(),
        )
        return self.morphism_with_inverse_image(source, target, underlying, inverse)

    def quotient_mediator[SourceKey: Hashable, TargetKey: Hashable](
        self,
        source: TopologicalSpacesCategory.ObjectType[SourceKey],
        target: TopologicalSpacesCategory.ObjectType[TargetKey],
        chart_maps: tuple[TopologicalSpacesCategory.MorphismType, ...],
        representative_rule: Callable[
            [CategoryOfCategories.ElementType],
            tuple[int, CategoryOfCategories.ElementType],
        ],
        assemble_open: Callable[
            [tuple[CategoryOfCategories.ElementType, ...]],
            CategoryOfCategories.ElementType,
        ],
    ) -> TopologicalSpacesCategory.MorphismType:
        """The universal continuous map induced by compatible chart maps."""

        def point_image(value: Hashable) -> Hashable:
            point = source.carrier().point(value)
            chart_index, chart_point = representative_rule(point)
            image = chart_maps[chart_index].underlying_map()(chart_point)
            return image.datum()

        underlying = Mor(Sets)(source.carrier(), target.carrier())(point_image)
        target_opens = target.open_category()
        source_opens = source.open_category()

        def preimage(
            open_object: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            return assemble_open(
                tuple(
                    mapping.inverse_image().on_object(open_object)
                    for mapping in chart_maps
                )
            )

        inverse = Fun(target_opens, source_opens)(
            preimage,
            lambda inclusion: Mor(source_opens)(
                preimage(inclusion.domain()),
                preimage(inclusion.codomain()),
            )(),
        )
        return self.morphism_with_inverse_image(source, target, underlying, inverse)

    def _inverse_image_functor(
        self,
        source: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]],
        target: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]],
        underlying: MorphismCategory.ObjectType,
    ) -> Functor:
        source_data = tuple(point.datum() for point in source.carrier())
        target_opens = target.open_category()
        source_opens = source.open_category()

        def inverse_subset(
            target_open: CategoryOfCategories.ElementType,
        ) -> frozenset[Hashable]:
            subset = target_open.point().datum()
            return frozenset(datum for datum in source_data if underlying(source.carrier().point(datum)).datum() in subset)

        def on_object(
            target_open: CategoryOfCategories.ElementType,
        ) -> CategoryOfCategories.ElementType:
            return source.open_object(inverse_subset(target_open))

        def on_morphism(
            inclusion: MorphismCategory.ObjectType,
        ) -> MorphismCategory.ObjectType:
            domain, codomain = (
                on_object(inclusion.domain()),
                on_object(inclusion.codomain()),
            )
            return Mor(source_opens)(domain, codomain)()

        inverse = Fun(target_opens, source_opens)(on_object, on_morphism)
        for point in target.opens().carrier():
            open_key = point.datum()
            assert isinstance(open_key, frozenset)
            target_open = target.open_object(open_key)
            source.open_point(inverse_subset(target_open))
        return inverse

    def construct_morphism(
        self,
        source: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]],
        target: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]],
        underlying: MorphismCategory.ObjectType,
    ) -> TopologicalSpacesCategory.MorphismType:
        assert underlying.domain() is source.carrier() and underlying.codomain() is target.carrier()
        inverse = self._inverse_image_functor(source, target, underlying)
        return self.morphism_with_inverse_image(source, target, underlying, inverse)

    def morphism_with_inverse_image[SourceKey: Hashable, TargetKey: Hashable](
        self,
        source: TopologicalSpacesCategory.ObjectType[SourceKey],
        target: TopologicalSpacesCategory.ObjectType[TargetKey],
        underlying: MorphismCategory.ObjectType,
        inverse: Functor,
    ) -> TopologicalSpacesCategory.MorphismType:
        """Retain a continuous map from its exact underlying map and inverse-image functor."""
        assert underlying.domain() is source.carrier() and underlying.codomain() is target.carrier()
        assert inverse.domain() is target.open_category()
        assert inverse.codomain() is source.open_category()
        return self._morphism_from_data(source, target, (underlying, inverse))

    def _identity_data[OpenKey: Hashable](
        self,
        member_object: TopologicalSpacesCategory.ObjectType[OpenKey],
    ) -> tuple[MorphismCategory.ObjectType, Functor]:
        return (
            Mor(Sets)(member_object.carrier(), member_object.carrier()).one(),
            Fun(member_object.open_category(), member_object.open_category()).one(),
        )

    def _composite_data(
        self,
        second: TopologicalSpacesCategory.MorphismType,
        first: TopologicalSpacesCategory.MorphismType,
    ) -> tuple[MorphismCategory.ObjectType, Functor]:
        return (
            second.underlying_map() * first.underlying_map(),
            first.inverse_image() * second.inverse_image(),
        )

    def __repr__(self) -> str:
        return "TopologicalSpaces"


def TopologicalSpaces() -> TopologicalSpacesCategory:
    return _TOPOLOGICAL_SPACES


_TOPOLOGICAL_SPACES = TopologicalSpacesCategory()
