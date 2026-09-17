from _typeshed import Incomplete
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from functools import cache
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import cocone as cocone, cocones as cocones
from sage_categories.cat.declarations import Sets as Sets, omega as omega
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.predicates import Predicate as Predicate, Proposition as Proposition, register_handler as register_handler
from sage_categories.cat.shapes import Thin as Thin
from sage_categories.geometry.spaces import TopologicalSpaces as TopologicalSpaces, TopologicalSpacesCategory as TopologicalSpacesCategory

@dataclass(frozen=True, slots=True)
class ComplexProjectivePoint:
    coordinates: tuple[complex, ...]

def complex_projective_point(*coordinates: complex) -> ComplexProjectivePoint:
    ...

@dataclass(frozen=True, eq=False, slots=True)
class CWOpen:
    stage: int
    name: Hashable
    contains: Callable[[ComplexProjectivePoint], bool]
    subset_rule: Callable[[CWOpen], bool | None] | None = ...

    def included_in(self, other: CWOpen) -> bool | None:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class _WeakCWOpen:
    presentation: ProjectiveInfinityPresentation
    stage_open_rule: Callable[[int], CWOpen]
    name: Hashable
    subset_rule: Callable[[_WeakCWOpen], bool | None] | None = ...

    def stage_open(self, stage: int) -> CWOpen:
        ...

    def included_in(self, other: _WeakCWOpen) -> bool | None:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class ProjectiveSpacePresentation:
    stage: int
    space: TopologicalSpacesCategory.ObjectType[CWOpen]
    empty_open: CWOpen
    whole_open: CWOpen

    def cells(self) -> tuple[int, ...]:
        ...

    def open(self, value: CWOpen) -> CategoryOfCategories.ElementType:
        ...

    def complex_conjugation(self) -> TopologicalSpacesCategory.MorphismType:
        ...

@cache
def projective_space(stage: int) -> ProjectiveSpacePresentation:
    ...

@dataclass(frozen=True, eq=False, slots=True)
class ProjectiveInfinityPresentation:
    diagram: Functor
    space: TopologicalSpacesCategory.ObjectType[_WeakCWOpen]
    weak_opens: CategoryOfCategories.ElementType
    empty_open: _WeakCWOpen
    whole_open: _WeakCWOpen

    def finite_skeleton(self, stage: int) -> ProjectiveSpacePresentation:
        ...

    def structure_map(self, stage: int) -> TopologicalSpacesCategory.MorphismType:
        ...

    def open(self, value: _WeakCWOpen) -> CategoryOfCategories.ElementType:
        ...

    def complex_conjugation(self) -> TopologicalSpacesCategory.MorphismType:
        ...

@cache
def projective_infinity() -> ProjectiveInfinityPresentation:
    ...
