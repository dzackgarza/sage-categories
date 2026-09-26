"""Static consumer for the presented-abelian tensor structure."""

from typing import assert_type

from sage_categories.algebra.abelian import AbelianTensor
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.monoidal import MonoidalStructuresCategory, tensor_morphism
from sage_categories.cat.morphisms import MorphismCategory


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
