from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry.affine import AffineSchemesCategory

__all__ = [
    "GlobalSections",
    "affine_global_sections_comparison",
    "affine_structure_sheaf_global_map",
    "global_sections",
    "global_sections_map",
    "global_sections_spec_comparison",
]

GlobalSections: Functor

def global_sections(
    scheme: AffineSchemesCategory.ObjectType,
) -> CategoryOfCategories.ElementType: ...
def affine_structure_sheaf_global_map(
    mapping: AffineSchemesCategory.MorphismType,
) -> MorphismCategory.ObjectType: ...
def global_sections_map(
    mapping: AffineSchemesCategory.MorphismType,
) -> MorphismCategory.ObjectType: ...

global_sections_spec_comparison: NaturalTransformation
affine_global_sections_comparison: NaturalTransformation
