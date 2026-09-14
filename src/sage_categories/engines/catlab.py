"""Pinned Catlab/GATlab execution for owned categories, functors, and transformations.

The owned runtime supplies only primitive category operations and primitive functor or
component callbacks.  Catlab retains and executes every composite representation.
"""

from __future__ import annotations

from sage_categories.cat.category import Category
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import (
    has_native_category,
    has_native_functor,
    has_native_transformation,
    retain_native_category,
    retain_native_functor,
    retain_native_transformation,
)
from sage_categories.cat.native import (
    native_category as retained_native_category,
)
from sage_categories.cat.native import (
    native_functor as retained_native_functor,
)
from sage_categories.cat.native import (
    native_transformation as retained_native_transformation,
)
from sage_categories.engines.julia_bridge import catlab_bridge as _bridge
from sage_categories.kernel.refinement import is_placed
from sage_categories.kernel.sage_runtime import MonoDict

__all__ = [
    "compose_transformations",
    "ensure_native_category",
    "ensure_native_functor",
    "ensure_native_transformation",
    "functor_morphism_image",
    "functor_object_image",
    "horizontal_composite",
    "identity_transformation",
    "presented_coproduct",
    "presented_coproduct_data",
    "presented_coproduct_object_image",
    "presented_coproduct_path_image",
    "presented_functor",
    "presented_functor_morphism_image",
    "transformation_component",
    "whisker_left",
    "whisker_right",
]

type TransformationRecipe = tuple[str, tuple[object, ...]]

_transformation_recipes: MonoDict = MonoDict()


def _retain_transformation_recipe(value: MorphismCategory.ObjectType, recipe: TransformationRecipe) -> None:
    if value in _transformation_recipes:
        assert not has_native_transformation(value), f"{value!r} already materialized its Catlab transformation"
    _transformation_recipes[value] = recipe


def ensure_native_category(owner: Category) -> object:
    """Return the Catlab model of this exact owned category."""
    if has_native_category(owner):
        return retained_native_category(owner).native
    bridge = _bridge()
    native = bridge.callable_category(
        lambda arrow: arrow.domain(),
        lambda arrow: arrow.codomain(),
        lambda value: owner.morphism_category(1)(value, value).one(),
        lambda first, second: owner.compose_morphisms(second, first),
    )
    retain_native_category(owner, native)
    return native


def ensure_native_functor(functor: MorphismCategory.ObjectType) -> object:
    """Materialize the retained Catlab representation only when execution asks for it."""
    if has_native_functor(functor):
        return retained_native_functor(functor).native
    source, target = functor.domain(), functor.codomain()
    bridge = _bridge()
    base = functor.base_category()
    if is_placed(functor, base.morphism_category(1).Identity()):
        native = bridge.identity_functor(ensure_native_category(source))
    elif functor.is_composite():
        first, second = functor.factors()
        native = bridge.compose_functors(ensure_native_functor(first), ensure_native_functor(second))
    else:
        native = bridge.callable_functor(
            functor._declared_object_image,
            functor._declared_morphism_image,
            ensure_native_category(source),
            ensure_native_category(target),
        )
    retain_native_functor(functor, source, target, native)
    return native


def functor_object_image(functor: MorphismCategory.ObjectType, value: object) -> object:
    return _bridge().functor_object_image(ensure_native_functor(functor), value)


def functor_morphism_image(functor: MorphismCategory.ObjectType, value: object) -> object:
    return _bridge().functor_morphism_image(ensure_native_functor(functor), value)


def ensure_native_transformation(value: MorphismCategory.ObjectType) -> object:
    if has_native_transformation(value):
        return retained_native_transformation(value).native
    domain, codomain = value.domain(), value.codomain()
    recipe = _transformation_recipes[value] if value in _transformation_recipes else None
    if recipe is None:
        recipe = (
            "callable",
            (value.source_functor(), value.target_functor(), value._declared_component),
        )
    bridge = _bridge()
    match recipe:
        case ("callable", (source, target, component)):
            native = bridge.callable_transformation(
                component,
                ensure_native_functor(source),
                ensure_native_functor(target),
            )
        case ("identity", ()):
            native = bridge.identity_transformation(ensure_native_functor(value.source_functor()))
        case ("compose", (first, second)):
            native = bridge.compose_transformations(
                ensure_native_transformation(first),
                ensure_native_transformation(second),
            )
        case ("whisker_left", (functor, transformation)):
            native = bridge.whisker_left(
                ensure_native_functor(functor),
                ensure_native_transformation(transformation),
            )
        case ("whisker_right", (transformation, functor)):
            native = bridge.whisker_right(
                ensure_native_transformation(transformation),
                ensure_native_functor(functor),
            )
        case ("horizontal", (first, second)):
            native = bridge.horizontal_composite(
                ensure_native_transformation(first),
                ensure_native_transformation(second),
            )
        case _:
            raise AssertionError(f"unknown Catlab transformation recipe {recipe!r}")
    retain_native_transformation(value, domain, codomain, native)
    return native


def transformation_component(value: MorphismCategory.ObjectType, member_object: object) -> object:
    return _bridge().transformation_component(ensure_native_transformation(value), member_object)


def identity_transformation(value: MorphismCategory.ObjectType) -> None:
    _retain_transformation_recipe(value, ("identity", ()))


def compose_transformations(
    value: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> None:
    _retain_transformation_recipe(value, ("compose", (first, second)))


def whisker_left(
    value: MorphismCategory.ObjectType,
    functor: MorphismCategory.ObjectType,
    transformation: MorphismCategory.ObjectType,
) -> None:
    _retain_transformation_recipe(value, ("whisker_left", (functor, transformation)))


def whisker_right(
    value: MorphismCategory.ObjectType,
    transformation: MorphismCategory.ObjectType,
    functor: MorphismCategory.ObjectType,
) -> None:
    _retain_transformation_recipe(value, ("whisker_right", (transformation, functor)))


def horizontal_composite(
    value: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> None:
    _retain_transformation_recipe(value, ("horizontal", (first, second)))


def _presented_category_data(
    category: object,
) -> tuple[list[str], list[tuple[str, int, int]], list[tuple[int, list[int], list[int]]]]:
    labels = tuple(category.labels())
    names = tuple(category.generator_names())
    label_positions = {label: index + 1 for index, label in enumerate(labels)}
    generator_positions = {name: index + 1 for index, name in enumerate(names)}
    object_names = [f"o{index}" for index in range(len(labels))]
    generators = [
        (
            f"g{index}",
            label_positions[category.label(category.generator_endpoints(name)[0])],
            label_positions[category.label(category.generator_endpoints(name)[1])],
        )
        for index, name in enumerate(names)
    ]
    relations = []
    for left, right in category.relations():
        witness = left or right
        assert witness, "a defining relation cannot equate two empty paths"
        source = category.label(category.generator_endpoints(witness[0])[0])
        relations.append(
            (
                label_positions[source],
                [generator_positions[name] for name in left],
                [generator_positions[name] for name in right],
            )
        )
    return object_names, generators, relations


def presented_coproduct(categories: tuple[object, ...]) -> object:
    """Native Catlab coproduct of exact finite presentations."""
    return _bridge().presented_coproduct([_presented_category_data(category) for category in categories])


def presented_coproduct_data(
    value: object,
) -> tuple[
    tuple[str, ...],
    tuple[tuple[str, str, str], ...],
    tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
]:
    objects, homs, relations = _bridge().presented_coproduct_data(value)
    return (
        tuple(str(name) for name in objects),
        tuple((str(name), str(source), str(target)) for name, source, target in homs),
        tuple((tuple(str(name) for name in left), tuple(str(name) for name in right)) for left, right in relations),
    )


def presented_coproduct_object_image(value: object, factor: int, object_index: int) -> str:
    return str(_bridge().presented_coproduct_object_image(value, factor + 1, object_index + 1))


def _word_indices(category: object, word: tuple[str, ...]) -> list[int]:
    positions = {name: index + 1 for index, name in enumerate(category.generator_names())}
    return [positions[name] for name in word]


def presented_coproduct_path_image(
    value: object,
    categories: tuple[object, ...],
    factor: int,
    word: tuple[str, ...],
    source: object,
) -> tuple[str, ...]:
    category = categories[factor]
    source_index = tuple(category.labels()).index(category.label(source))
    result = _bridge().presented_coproduct_path_image(
        value,
        factor + 1,
        _word_indices(category, word),
        source_index + 1,
    )
    return tuple(str(name) for name in result)


def presented_functor(
    source: object,
    target: Category,
    object_images: tuple[object, ...],
    generator_images: tuple[object, ...],
) -> object:
    """Native Catlab functor extending supplied images of a finite presentation."""
    return _bridge().presented_functor(
        _presented_category_data(source),
        list(object_images),
        list(generator_images),
        ensure_native_category(target),
    )


def presented_functor_morphism_image(
    functor: object,
    source: object,
    morphism: object,
) -> object:
    source_index = tuple(source.labels()).index(source.label(morphism.domain()))
    return _bridge().presented_functor_morphism_image(
        functor,
        _word_indices(source, morphism.word()),
        source_index + 1,
    )
