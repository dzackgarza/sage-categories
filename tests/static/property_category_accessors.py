"""Source-declared property accessors project to their exact public category types."""

from typing import assert_type

from sage_categories.cat.monoidal import MonoidalStructuresCategory
from sage_categories.cat.properties import InverseImageSubcategory, PropertySubcategory
from sage_categories.cat.structured_objects import (
    AdditiveMagmas,
    AdditiveMonoids,
    GroupsCategory,
    Magmas,
    Monoids,
)


def property_accessor_types(structure: MonoidalStructuresCategory.ObjectType) -> None:
    assert_type(Magmas(structure).Commutative(), PropertySubcategory)
    assert_type(Monoids(structure).Group(), GroupsCategory)
    assert_type(AdditiveMagmas(structure).Commutative(), InverseImageSubcategory)
    assert_type(AdditiveMonoids(structure).Group(), InverseImageSubcategory)
