"""Pinned Catlab/GATlab execution for owned categories, functors, and transformations.

The owned runtime supplies only primitive category operations and primitive functor or
component callbacks.  Catlab retains and executes every composite representation.
"""

from __future__ import annotations

from functools import cache
from importlib import import_module
from pathlib import Path
from typing import Any

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

__all__ = [
    "callable_transformation",
    "compose_functors",
    "compose_transformations",
    "ensure_native_category",
    "ensure_native_functor",
    "ensure_native_transformation",
    "functor_morphism_image",
    "functor_object_image",
    "horizontal_composite",
    "identity_functor",
    "identity_transformation",
    "retain_composite_functor",
    "transformation_component",
    "whisker_left",
    "whisker_right",
]

type FunctorRecipe = tuple[str, tuple[object, ...]]
type TransformationRecipe = tuple[str, tuple[object, ...]]

_functor_recipes: dict[int, tuple[object, FunctorRecipe]] = {}
_transformation_recipes: dict[int, tuple[object, TransformationRecipe]] = {}


def _bridge_source() -> Path:
    return Path(__file__).with_name("SageCategoriesBridge.jl")


@cache
def _bridge() -> Any:
    """Load the pinned Julia bridge through JuliaCall exactly once."""
    juliacall = import_module("juliacall")
    main = juliacall.Main
    main.include(str(_bridge_source()))
    return main.SageCategoriesBridge


def _retain_functor_recipe(
    value: MorphismCategory.ObjectType, recipe: FunctorRecipe
) -> None:
    identifier = id(value)
    if identifier in _functor_recipes:
        retained, existing = _functor_recipes[identifier]
        assert retained is value and existing == recipe
        return
    _functor_recipes[identifier] = (value, recipe)


def _functor_recipe(value: MorphismCategory.ObjectType) -> FunctorRecipe | None:
    identifier = id(value)
    if identifier not in _functor_recipes:
        return None
    retained, recipe = _functor_recipes[identifier]
    assert retained is value
    return recipe


def _retain_transformation_recipe(
    value: MorphismCategory.ObjectType, recipe: TransformationRecipe
) -> None:
    identifier = id(value)
    if identifier in _transformation_recipes:
        retained, _ = _transformation_recipes[identifier]
        assert retained is value
        assert not has_native_transformation(value), (
            f"{value!r} already materialized its Catlab transformation"
        )
        _transformation_recipes[identifier] = (value, recipe)
        return
    _transformation_recipes[identifier] = (value, recipe)


def _transformation_recipe(
    value: MorphismCategory.ObjectType,
) -> TransformationRecipe | None:
    identifier = id(value)
    if identifier not in _transformation_recipes:
        return None
    retained, recipe = _transformation_recipes[identifier]
    assert retained is value
    return recipe


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
    recipe = _functor_recipe(functor)
    match recipe:
        case ("identity", (owner,)):
            native = bridge.identity_functor(ensure_native_category(owner))
        case ("compose", (first, second)):
            native = bridge.compose_functors(
                ensure_native_functor(first), ensure_native_functor(second)
            )
        case None:
            native = bridge.callable_functor(
                functor._on_object,
                functor._on_morphism,
                ensure_native_category(source),
                ensure_native_category(target),
            )
        case _:
            raise AssertionError(f"unknown Catlab functor recipe {recipe!r}")
    retain_native_functor(functor, source, target, native)
    return native


def functor_object_image(functor: MorphismCategory.ObjectType, value: object) -> object:
    return _bridge().functor_object_image(ensure_native_functor(functor), value)


def functor_morphism_image(
    functor: MorphismCategory.ObjectType, value: object
) -> object:
    return _bridge().functor_morphism_image(ensure_native_functor(functor), value)


def compose_functors(
    first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType
) -> object:
    return _bridge().compose_functors(
        ensure_native_functor(first), ensure_native_functor(second)
    )


def retain_composite_functor(
    value: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> None:
    _retain_functor_recipe(value, ("compose", (first, second)))


def identity_functor(value: MorphismCategory.ObjectType, owner: Category) -> None:
    _retain_functor_recipe(value, ("identity", (owner,)))


def _retain_transformation(
    value: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
    native: object,
) -> object:
    retain_native_transformation(value, source, target, native)
    return native


def callable_transformation(
    value: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
    component: object,
) -> None:
    _retain_transformation_recipe(value, ("callable", (source, target, component)))


def _native_transformation(value: MorphismCategory.ObjectType) -> object:
    assert has_native_transformation(value), (
        f"{value!r} has no retained native transformation"
    )
    return retained_native_transformation(value).native


def ensure_native_transformation(value: MorphismCategory.ObjectType) -> object:
    if has_native_transformation(value):
        return retained_native_transformation(value).native
    recipe = _transformation_recipe(value)
    if recipe is None:
        recipe = (
            "callable",
            (value.source_functor(), value.target_functor(), value._assignment),
        )
    bridge = _bridge()
    match recipe:
        case ("callable", (source, target, component)):
            native = bridge.callable_transformation(
                component,
                ensure_native_functor(source),
                ensure_native_functor(target),
            )
        case ("identity", (functor,)):
            source = target = functor
            native = bridge.identity_transformation(ensure_native_functor(functor))
        case ("compose", (first, second, source, target)):
            native = bridge.compose_transformations(
                ensure_native_transformation(first),
                ensure_native_transformation(second),
            )
        case ("whisker_left", (functor, transformation, source, target)):
            native = bridge.whisker_left(
                ensure_native_functor(functor),
                ensure_native_transformation(transformation),
            )
        case ("whisker_right", (transformation, functor, source, target)):
            native = bridge.whisker_right(
                ensure_native_transformation(transformation),
                ensure_native_functor(functor),
            )
        case ("horizontal", (first, second, source, target)):
            native = bridge.horizontal_composite(
                ensure_native_transformation(first),
                ensure_native_transformation(second),
            )
        case _:
            raise AssertionError(f"unknown Catlab transformation recipe {recipe!r}")
    return _retain_transformation(value, source, target, native)


def transformation_component(
    value: MorphismCategory.ObjectType, member_object: object
) -> object:
    return _bridge().transformation_component(
        ensure_native_transformation(value), member_object
    )


def identity_transformation(
    value: MorphismCategory.ObjectType,
    functor: MorphismCategory.ObjectType,
) -> None:
    _retain_transformation_recipe(value, ("identity", (functor,)))


def compose_transformations(
    value: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
) -> None:
    _retain_transformation_recipe(value, ("compose", (first, second, source, target)))


def whisker_left(
    value: MorphismCategory.ObjectType,
    functor: MorphismCategory.ObjectType,
    transformation: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
) -> None:
    _retain_transformation_recipe(
        value, ("whisker_left", (functor, transformation, source, target))
    )


def whisker_right(
    value: MorphismCategory.ObjectType,
    transformation: MorphismCategory.ObjectType,
    functor: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
) -> None:
    _retain_transformation_recipe(
        value, ("whisker_right", (transformation, functor, source, target))
    )


def horizontal_composite(
    value: MorphismCategory.ObjectType,
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
    source: MorphismCategory.ObjectType,
    target: MorphismCategory.ObjectType,
) -> None:
    _retain_transformation_recipe(
        value, ("horizontal", (first, second, source, target))
    )
