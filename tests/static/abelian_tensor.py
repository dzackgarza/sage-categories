"""Static consumer for the presented-abelian tensor structure."""

from typing import assert_type

from sage_categories.algebra.abelian import (
    AbelianBimoduleTensor,
    AbelianTensor,
    relative_tensor_bifunctor,
)
from sage_categories.cat.bimodules import BimoduleCategory
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.monoidal import MonoidalStructuresCategory, tensor_morphism
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory


def abelian_tensor_types(
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    triple: CategoryOfCategories.ElementType,
    first_map: MorphismCategory.ObjectType,
    second_map: MorphismCategory.ObjectType,
) -> None:
    structure = AbelianTensor()
    assert_type(structure, MonoidalStructuresCategory.ObjectType)
    tensor = structure.tensor()
    assert_type(tensor, Functor)
    assert_type(tensor_morphism(tensor, first_map, second_map), MorphismCategory.ObjectType)
    assert_type(structure.left_unitor(), NaturalTransformation)
    assert_type(structure.right_unitor(), NaturalTransformation)
    assert_type(structure.associator(), NaturalTransformation)
    assert_type(structure.left_unitor().component(first), MorphismCategory.ObjectType)
    assert_type(structure.right_unitor().component(first), MorphismCategory.ObjectType)
    assert_type(
        structure.associator().component(triple),
        MorphismCategory.ObjectType,
    )


def relative_tensor_wrapper_types[
    LeftScalar: MonoidCategory.ObjectType,
    MiddleScalar: MonoidCategory.ObjectType,
    RightScalar: MonoidCategory.ObjectType,
](
    left_scalars: LeftScalar,
    middle_scalars: MiddleScalar,
    right_scalars: RightScalar,
    arrow: MorphismCategory.ObjectType,
) -> None:
    tensor = relative_tensor_bifunctor(
        left_scalars,
        middle_scalars,
        right_scalars,
    )
    assert_type(
        tensor.codomain(),
        BimoduleCategory[LeftScalar, RightScalar, Category],
    )
    assert_type(tensor.on_morphism(arrow), BimoduleCategory.MorphismType)
    bimodule_tensor = AbelianBimoduleTensor(left_scalars)
    assert_type(
        bimodule_tensor.underlying_category(),
        BimoduleCategory[LeftScalar, LeftScalar, Category],
    )
