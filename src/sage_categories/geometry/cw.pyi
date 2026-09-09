from collections.abc import Callable, Hashable

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.geometry.spaces import TopologicalSpacesCategory

class ComplexProjectivePoint:
    coordinates: tuple[complex, ...]

class CWOpen:
    stage: int
    name: Hashable
    contains: Callable[[ComplexProjectivePoint], bool]
    def included_in(self, other: CWOpen) -> bool | None: ...

class ProjectiveSpacePresentation:
    stage: int
    space: TopologicalSpacesCategory.ObjectType
    empty_open: CWOpen
    whole_open: CWOpen
    def cells(self) -> tuple[int, ...]: ...
    def open(self, value: CWOpen) -> CategoryOfCategories.ElementType: ...
    def complex_conjugation(self) -> TopologicalSpacesCategory.MorphismType: ...

class ProjectiveInfinityPresentation:
    diagram: Functor
    space: TopologicalSpacesCategory.ObjectType
    weak_opens: CategoryOfCategories.ElementType
    def finite_skeleton(self, stage: int) -> ProjectiveSpacePresentation: ...
    def structure_map(self, stage: int) -> TopologicalSpacesCategory.MorphismType: ...
    def complex_conjugation(self) -> TopologicalSpacesCategory.MorphismType: ...

def complex_projective_point(*coordinates: complex) -> ComplexProjectivePoint: ...
def projective_space(stage: int) -> ProjectiveSpacePresentation: ...
def projective_infinity() -> ProjectiveInfinityPresentation: ...
