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
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Cat, Fun, FunctorCategory
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
    if category not in _retained:
        _retained[category] = _evaluate(category)
    return _retained[category]


def _evaluate(category: CategoryOfCategories.ElementType) -> FiniteCategoryData | UnknownClass:
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
    if isinstance(category, LimitCategory):
        return _limit(category)
    return Unknown


def _arrows(category: FunctorCategory) -> FiniteCategoryData | UnknownClass:
    target = finite_category(category.codomain())
    if target is Unknown:
        return Unknown
    objects = target.morphisms
    arrows: list[MorphismCategory.ObjectType] = []
    for source, destination in product(objects, repeat=2):
        for first, second in product(target.morphisms, repeat=2):
            if not (first.domain() is source.domain() and first.codomain() is destination.domain()
                    and second.domain() is source.codomain() and second.codomain() is destination.codomain()):
                continue
            if equal(destination * first, second * source):
                arrows.append(Mor(category)(source, destination)(
                    lambda vertex, first=first, second=second: first if vertex is Cat().Simplex(1)(0) else second,
                ))
    return FiniteCategoryData(objects, tuple(arrows))


def _limit(category: LimitCategory) -> FiniteCategoryData | UnknownClass:
    shape = finite_category(category.shape())
    if shape is Unknown:
        return Unknown
    vertices = shape.objects
    factors = tuple(finite_category(category.factor(vertex)) for vertex in vertices)
    if any(factor is Unknown for factor in factors):
        return Unknown
    vertex_positions = {id(vertex): index for index, vertex in enumerate(vertices)}

    def agrees(components: tuple[CategoryOfCategories.ElementType, ...], morphisms: bool) -> bool:
        for edge in shape.morphisms:
            functor = category.diagram().on_morphism(edge)
            source = components[vertex_positions[id(edge.domain())]]
            image = functor.on_morphism(source) if morphisms else functor.on_object(source)
            if not equal(image, components[vertex_positions[id(edge.codomain())]]):
                return False
        return True

    families = tuple(components for components in product(*(factor.objects for factor in factors)) if agrees(components, False))
    objects = tuple(category.from_components(lambda vertex, components=components: components[vertex_positions[id(vertex)]]) for components in families)

    def endpoint(components: tuple[CategoryOfCategories.ElementType, ...]) -> CategoryOfCategories.ElementType:
        for index, family in enumerate(families):
            if all(equal(first, second) for first, second in zip(components, family, strict=True)):
                return objects[index]
        raise AssertionError("a compatible arrow family has no endpoint in its limit")

    arrows = tuple(
        category.morphism_from_components(
            endpoint(tuple(arrow.domain() for arrow in components)),
            endpoint(tuple(arrow.codomain() for arrow in components)),
            lambda vertex, components=components: components[vertex_positions[id(vertex)]],
        )
        for components in product(*(factor.morphisms for factor in factors)) if agrees(components, True)
    )
    return FiniteCategoryData(objects, arrows)
