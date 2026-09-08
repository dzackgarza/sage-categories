"""Exact finite evaluation of the existing category constructions.

Products and equalizers compute limits in Cat on objects and arrows. Arrow
categories use commuting squares. These are the constructions in Mathlib's
CategoryTheory.Limits.Shapes.Products and CategoryTheory.Arrow, respectively.
This private evaluator supplies finite inputs to the presented colimit engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.cat_constructions import LimitCategory
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.comma import CommaCategory
from sage_categories.cat.declarations import Sets
from sage_categories.cat.functors import Cat, FunctorCategory
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import OppositeCategory, opposite_morphism
from sage_categories.cat.predicates import Unknown, UnknownClass, ask
from sage_categories.kernel.sage_runtime import MonoDict


@dataclass(frozen=True)
class FiniteCategoryData:
    objects: tuple[CategoryOfCategories.ElementType, ...]
    morphisms: tuple[MorphismCategory.ObjectType, ...]


def position[Value: CategoryOfCategories.ElementType](values: tuple[Value, ...], value: Value) -> int:
    for index, candidate in enumerate(values):
        if candidate is value or ask(candidate == value) is True:
            return index
    raise AssertionError(f"{value!r} has no representative in the finite category")


def equal(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> bool:
    if first is second:
        return True
    result = ask(first == second)
    assert result is not Unknown, "finite category evaluation requires decided equality"
    return result is True


_retained: MonoDict = MonoDict()


def finite_category(category: CategoryOfCategories.ElementType) -> FiniteCategoryData | UnknownClass:
    if category in _retained:
        return _retained[category]
    result = _evaluate(category)
    if result is not Unknown:
        _retained[category] = result
    return result


def finite_objects(category: Category) -> tuple[CategoryOfCategories.ElementType, ...] | UnknownClass:
    """The exact finite object family supplied by a presentation or a chosen enumeration."""
    from sage_categories.cat.shapes import DiscreteCategory

    if isinstance(category, FinitePresentedCategory):
        return tuple(category(label) for label in category.labels())
    if isinstance(category, DiscreteCategory):
        points = Sets.finite_points(category.object_set())
        if points is Unknown:
            return Unknown
        return tuple(category.object_at(point) for point in points)
    if isinstance(category, OppositeCategory):
        return finite_objects(category.original())
    data = finite_category(category)
    return Unknown if data is Unknown else data.objects


def _evaluate(category: CategoryOfCategories.ElementType) -> FiniteCategoryData | UnknownClass:
    from sage_categories.cat.indexed import GrothendieckCategory
    from sage_categories.cat.shapes import DiscreteCategory

    if isinstance(category, DiscreteCategory):
        objects = finite_objects(category)
        if objects is Unknown:
            return Unknown
        return FiniteCategoryData(objects, tuple(Mor(category)(value, value).one() for value in objects))
    if isinstance(category, GrothendieckCategory):
        indexed = category.indexed_category()
        base = finite_category(indexed.domain().op())
        if base is Unknown:
            return Unknown
        fibers = {id(value): finite_category(indexed.on_object(value)) for value in base.objects}
        if any(fiber is Unknown for fiber in fibers.values()):
            return Unknown
        objects = tuple(category(value, point) for value in base.objects for point in fibers[id(value)].objects)
        arrows = []
        for arrow in base.morphisms:
            for source, target in product(objects, repeat=2):
                if source.base_object() is not arrow.domain() or target.base_object() is not arrow.codomain():
                    continue
                image = indexed.reindex(arrow).on_object(target.fiber_object())
                for fiber_arrow in fibers[id(arrow.domain())].morphisms:
                    if equal(fiber_arrow.domain(), source.fiber_object()) and equal(fiber_arrow.codomain(), image):
                        arrows.append(category.construct_morphism(source, target, arrow, fiber_arrow))
        return FiniteCategoryData(objects, tuple(arrows))
    if isinstance(category, FinitePresentedCategory):
        arrows = category.finite_morphisms()
        if arrows is Unknown:
            return Unknown
        return FiniteCategoryData(tuple(category(label) for label in category.labels()), arrows)
    if isinstance(category, OppositeCategory):
        original = finite_category(category.original())
        if original is Unknown:
            return Unknown
        return FiniteCategoryData(original.objects, tuple(opposite_morphism(arrow) for arrow in original.morphisms))
    if isinstance(category, FunctorCategory) and category.domain() is Cat().Simplex(1):
        return _arrows(category)
    if isinstance(category, CommaCategory):
        from sage_categories.cat.slices import SliceLikeCategory

        if isinstance(category, SliceLikeCategory):
            return _slice(category)
        return _comma(category)
    if isinstance(category, LimitCategory):
        return _limit(category)
    return Unknown


def _arrows(category: FunctorCategory) -> FiniteCategoryData | UnknownClass:
    target = finite_category(category.codomain())
    if target is Unknown:
        return Unknown
    if not isinstance(category.codomain(), FinitePresentedCategory):
        return Unknown
    from sage_categories.engines import functor_categories

    objects, morphisms = functor_categories.arrow_category(
        category, category.codomain(), target.morphisms
    )
    return FiniteCategoryData(objects, morphisms)


def _limit(category: LimitCategory) -> FiniteCategoryData | UnknownClass:
    from sage_categories.cat.shapes import DiscreteCategory

    shape = finite_category(category.shape())
    if shape is Unknown:
        return Unknown
    vertices = shape.objects
    factors = tuple(finite_category(category.factor(vertex)) for vertex in vertices)
    if any(factor is Unknown for factor in factors):
        return Unknown

    if isinstance(category.shape(), DiscreteCategory) and all(
        isinstance(category.factor(vertex), FinitePresentedCategory) for vertex in vertices
    ):
        from sage_categories.engines import category_products

        factor_categories = tuple(category.factor(vertex) for vertex in vertices)
        concrete_factors = tuple(factor for factor in factors if factor is not Unknown)
        object_components, morphism_components = category_products.finite_product_data(
            factor_categories,
            tuple(factor.objects for factor in concrete_factors),
            tuple(factor.morphisms for factor in concrete_factors),
        )
        objects = tuple(category(components) for components in object_components)
        by_components = {
            tuple(id(component) for component in components): value
            for components, value in zip(object_components, objects, strict=True)
        }
        morphisms = []
        for components in morphism_components:
            domain = by_components[tuple(id(component.domain()) for component in components)]
            codomain = by_components[tuple(id(component.codomain()) for component in components)]
            morphisms.append(category.construct_morphism(domain, codomain, components))
        return FiniteCategoryData(objects, tuple(morphisms))

    from sage_categories.engines import category_limits

    concrete_factors = tuple(factor for factor in factors if factor is not Unknown)
    diagram = category.defining_diagram()
    object_components = category_limits.compatible_families(
        vertices,
        shape.morphisms,
        tuple(factor.objects for factor in concrete_factors),
        lambda arrow, value: diagram.on_morphism(arrow).on_object(value),
        position,
    )
    objects = tuple(category(components) for components in object_components)
    by_components = {
        tuple(id(component) for component in components): value
        for components, value in zip(object_components, objects, strict=True)
    }
    morphism_components = category_limits.compatible_families(
        vertices,
        shape.morphisms,
        tuple(factor.morphisms for factor in concrete_factors),
        lambda arrow, value: diagram.on_morphism(arrow).on_morphism(value),
        position,
    )
    morphisms = tuple(
        category.construct_morphism(
            by_components[tuple(id(component.domain()) for component in components)],
            by_components[tuple(id(component.codomain()) for component in components)],
            components,
        )
        for components in morphism_components
    )
    return FiniteCategoryData(objects, morphisms)


def _slice(category: object) -> FiniteCategoryData | UnknownClass:
    if category._fixed_label != 1 or not isinstance(category.base_of_slice(), FinitePresentedCategory):
        return Unknown
    base = finite_category(category.base_of_slice())
    if base is Unknown:
        return Unknown
    from sage_categories.engines import slice_categories

    objects, morphisms = slice_categories.slice_category(
        category, category.base_of_slice(), base.morphisms
    )
    return FiniteCategoryData(objects, morphisms)


def _comma(category: CommaCategory) -> FiniteCategoryData | UnknownClass:
    from sage_categories.cat.diagrams import cospan_diagram
    from sage_categories.cat.slices import _endpoint_functor, _pair_functor

    first, second = category.comma_functors()
    cospan = Cat().WalkingCospan()
    diagram = cospan_diagram(
        Cat(),
        _pair_functor(first, second),
        _endpoint_functor(first.codomain()),
    )
    pullback = LimitCategory(diagram)
    data = finite_category(pullback)
    if data is Unknown:
        return Unknown

    pair_vertex, arrow_vertex = cospan(0), cospan(1)
    objects = []
    by_components: dict[tuple[int, int, int], CategoryOfCategories.ElementType] = {}
    for value in data.objects:
        pair = value.family_component(pair_vertex)
        arrow = value.family_component(arrow_vertex)
        first_value = pair.family_component(0)
        second_value = pair.family_component(1)
        owned = category.from_arrow(first_value, second_value, arrow)
        objects.append(owned)
        by_components[(id(first_value), id(second_value), id(arrow))] = owned

    morphisms = []
    for value in data.morphisms:
        pair = value.family_component(pair_vertex)
        source_family = value.domain()
        target_family = value.codomain()

        def comma_endpoint(family: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            pair_object = family.family_component(pair_vertex)
            arrow_object = family.family_component(arrow_vertex)
            return by_components[
                (
                    id(pair_object.family_component(0)),
                    id(pair_object.family_component(1)),
                    id(arrow_object),
                )
            ]

        morphisms.append(
            category.morphism_from_pair(
                comma_endpoint(source_family),
                comma_endpoint(target_family),
                pair.family_component(0),
                pair.family_component(1),
            )
        )
    return FiniteCategoryData(tuple(objects), tuple(morphisms))
