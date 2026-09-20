from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_method as cached_method

__all__ = ["ContravariantFaithfulStructureCategory", "FaithfulStructureCategory", "LeafCategory", "MorphismDataCategory", "ParameterizedThinCategory"]

class LeafCategory[ObjectRole = Category.ObjectType, ElementRole = Category.ElementType, MorphismRole = Category.MorphismType](
    Category[..., ..., ObjectRole, ElementRole, MorphismRole]
):
    def assemble_object(self, data: object) -> CategoryOfCategories.ElementType: ...
    def assemble_morphism(self, domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...

class MorphismDataCategory[ObjectRole = LeafCategory.ObjectType, ElementRole = LeafCategory.ElementType, MorphismRole = LeafCategory.MorphismType](
    LeafCategory[ObjectRole, ElementRole, MorphismRole]
):
    def construct_identity(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...
    def composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType: ...

class FaithfulStructureCategory[ObjectRole = MorphismDataCategory.ObjectType, ElementRole = MorphismDataCategory.ElementType, MorphismRole = MorphismDataCategory.MorphismType](
    MorphismDataCategory[ObjectRole, ElementRole, MorphismRole]
): ...
class ContravariantFaithfulStructureCategory[
    ObjectRole = FaithfulStructureCategory.ObjectType,
    ElementRole = FaithfulStructureCategory.ElementType,
    MorphismRole = FaithfulStructureCategory.MorphismType,
](FaithfulStructureCategory[ObjectRole, ElementRole, MorphismRole]): ...

class ParameterizedThinCategory[ObjectRole = MorphismDataCategory.ObjectType, ElementRole = MorphismDataCategory.ElementType, MorphismRole = MorphismDataCategory.MorphismType](
    MorphismDataCategory[ObjectRole, ElementRole, MorphismRole]
):
    def __init__(self, *parameters: object) -> None: ...
    def parameter(self, position: int) -> object: ...
    def construct_morphism(
        self, domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType, *args: object, **kwargs: object
    ) -> MorphismCategory.ObjectType: ...
