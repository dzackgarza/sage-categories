from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import NativeMorphismRealization, NativeObjectRealization
from sage_categories.geometry.affine import AffineOpenCategory, AffineSchemesCategory
from sage_categories.geometry.sheaves import RingPresheaf

class TwoChartGluing:
    left: AffineSchemesCategory.ObjectType
    right: AffineSchemesCategory.ObjectType
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_to_right_pullback: MorphismCategory.ObjectType
    right_to_left_pullback: MorphismCategory.ObjectType

class ProjectiveLinePresentation:
    scheme: SchemesCategory.ObjectType
    left_chart: AffineSchemesCategory.ObjectType
    right_chart: AffineSchemesCategory.ObjectType
    left_coordinate: CategoryOfCategories.ElementType
    right_coordinate: CategoryOfCategories.ElementType
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_inclusion: SchemesCategory.MorphismType
    right_inclusion: SchemesCategory.MorphismType
    chart_swap: SchemesCategory.MorphismType
    structure_sheaf: RingPresheaf
    overlap_swap: MorphismCategory.ObjectType

class SchemesCategory(Category):
    class ObjectType(CategoryOfCategories.ElementType):
        def construction(self) -> object: ...

    class ElementType(CategoryOfCategories.ElementType): ...
    class MorphismType(MorphismCategory.ObjectType): ...

    def affine(self, affine: AffineSchemesCategory.ObjectType) -> ObjectType: ...
    def glue_two_affines(
        self,
        left: AffineSchemesCategory.ObjectType,
        right: AffineSchemesCategory.ObjectType,
        left_open: AffineOpenCategory.ObjectType,
        right_open: AffineOpenCategory.ObjectType,
        left_to_right_pullback: MorphismCategory.ObjectType,
        right_to_left_pullback: MorphismCategory.ObjectType,
    ) -> tuple[ObjectType, MorphismType, MorphismType]: ...
    def gluing_mediator(self, glued: ObjectType, target: ObjectType, left_map: MorphismType, right_map: MorphismType) -> MorphismType: ...
    def chart_map(
        self, source: AffineSchemesCategory.ObjectType, target: ObjectType, target_chart: AffineSchemesCategory.ObjectType, pullback: MorphismCategory.ObjectType
    ) -> MorphismType: ...

def Schemes() -> SchemesCategory: ...
def native_scheme(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[object, object]: ...
def native_scheme_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[object]: ...
def projective_line(field: CategoryOfCategories.ElementType) -> ProjectiveLinePresentation: ...
