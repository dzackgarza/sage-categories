"""Static consumers for bimodule objects and their two-sided morphisms."""

from typing import assert_type

from sage_categories.cat.bimodules import (
    BimoduleCategory,
    Bimodules,
    fixed_tensor_functor,
    induced_left_action,
    induced_right_action,
    relative_left_unitor,
    relative_right_unitor,
    relative_tensor,
    relative_tensor_associator,
    relative_tensor_bifunctor,
    relative_tensor_factor,
    relative_tensor_morphism,
    relative_tensor_preserved_factor,
)
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.monoidal import MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory


class AmbientCategory(Category[[], []]):
    pass


def bimodule_owner_parameters[
    LeftScalar: MonoidCategory.ObjectType,
    RightScalar: MonoidCategory.ObjectType,
](
    left_scalars: LeftScalar,
    right_scalars: RightScalar,
    monoidal: MonoidalStructuresCategory.ObjectType[AmbientCategory],
) -> None:
    bimodules = Bimodules(left_scalars, right_scalars, monoidal)
    assert_type(
        bimodules,
        BimoduleCategory[LeftScalar, RightScalar, AmbientCategory],
    )
    assert_type(bimodules.left_scalars(), LeftScalar)
    assert_type(bimodules.right_scalars(), RightScalar)
    assert_type(bimodules.underlying_category(), AmbientCategory)


def bimodule_object_types(
    bimodules: BimoduleCategory,
    left_action: MorphismCategory.ObjectType,
    right_action: MorphismCategory.ObjectType,
) -> None:
    assert_type(bimodules.left_scalars(), MonoidCategory.ObjectType)
    assert_type(bimodules.right_scalars(), MonoidCategory.ObjectType)
    module = bimodules(left_action, right_action)
    assert_type(module, BimoduleCategory.ObjectType)
    assert_type(module.left_action(), MorphismCategory.ObjectType)
    assert_type(module.right_action(), MorphismCategory.ObjectType)


def bimodule_morphism_types(
    bimodules: BimoduleCategory,
    source: BimoduleCategory.ObjectType,
    target: BimoduleCategory.ObjectType,
    arrow: MorphismCategory.ObjectType,
    left_scalar_map: MorphismCategory.ObjectType,
    right_scalar_map: MorphismCategory.ObjectType,
) -> None:
    assert_type(
        bimodules.homomorphism(source, target, arrow),
        BimoduleCategory.MorphismType,
    )
    assert_type(
        bimodules.restriction(left_scalar_map, right_scalar_map),
        Functor,
    )


def relative_tensor_calculus_types(
    monoidal: MonoidalStructuresCategory.ObjectType,
    left_scalars: MonoidCategory.ObjectType,
    middle_scalars: MonoidCategory.ObjectType,
    right_scalars: MonoidCategory.ObjectType,
    middle: CategoryOfCategories.ElementType,
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    scalars: CategoryOfCategories.ElementType,
    right_action: MorphismCategory.ObjectType,
    left_action: MorphismCategory.ObjectType,
    projection: MorphismCategory.ObjectType,
    target_projection: MorphismCategory.ObjectType,
    first_map: MorphismCategory.ObjectType,
    second_map: MorphismCategory.ObjectType,
    arrow: MorphismCategory.ObjectType,
    preserving: Functor,
) -> None:
    assert_type(
        relative_tensor_bifunctor(
            left_scalars,
            middle_scalars,
            right_scalars,
            monoidal,
        ),
        Functor,
    )
    assert_type(fixed_tensor_functor(monoidal, first, "left"), Functor)
    assert_type(fixed_tensor_functor(monoidal, second, "right"), Functor)
    assert_type(relative_tensor(monoidal, middle, right_action, left_action), MorphismCategory.ObjectType)
    assert_type(relative_tensor_factor(monoidal, projection, arrow), MorphismCategory.ObjectType)
    assert_type(relative_left_unitor(monoidal, projection, left_action, arrow), tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType])
    assert_type(relative_right_unitor(monoidal, projection, right_action, arrow), tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType])
    assert_type(
        relative_tensor_associator(
            monoidal,
            first,
            second,
            scalars,
            projection,
            projection,
            projection,
            projection,
        ),
        tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType],
    )
    assert_type(relative_tensor_preserved_factor(monoidal, projection, preserving, arrow), MorphismCategory.ObjectType)
    assert_type(induced_left_action(monoidal, projection, scalars, second, left_action), MorphismCategory.ObjectType)
    assert_type(induced_right_action(monoidal, projection, first, scalars, right_action), MorphismCategory.ObjectType)
    assert_type(
        relative_tensor_morphism(monoidal, projection, target_projection, first_map, second_map),
        MorphismCategory.ObjectType,
    )
