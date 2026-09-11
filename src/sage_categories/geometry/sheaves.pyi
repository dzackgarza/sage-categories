from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry.spaces import TopologicalSpacesCategory
from typing import Any
__all__ = ['RingPresheaf', 'RingSheaf', 'ring_presheaf', 'ring_presheaf_from_functor', 'ring_sheaf']

@dataclass(frozen=True, eq=False, slots=True)
class RingPresheaf:
    space: object
    opens: Any
    functor: Functor
    open_object_rule: Callable[[object], CategoryOfCategories.ElementType]
    open_key_rule: Callable[[CategoryOfCategories.ElementType], object]

    def open_object(self, key: object) -> CategoryOfCategories.ElementType:
        ...

    def open_key(self, open_object: CategoryOfCategories.ElementType) -> object:
        ...

    def section_ring(self, open_set: object) -> CategoryOfCategories.ElementType:
        ...

    def restriction(self, larger: object, smaller: object) -> MorphismCategory.ObjectType:
        ...
type GluingRule = Callable[[frozenset[Hashable], tuple[frozenset[Hashable], ...], tuple[CategoryOfCategories.ElementType, ...]], CategoryOfCategories.ElementType]

@dataclass(frozen=True, eq=False, slots=True)
class RingSheaf:
    presheaf: RingPresheaf
    gluing_rule: GluingRule

    def glue(self, open_set: frozenset[Hashable], cover: tuple[frozenset[Hashable], ...], local_sections: tuple[CategoryOfCategories.ElementType, ...]) -> CategoryOfCategories.ElementType:
        ...

def ring_presheaf(space: TopologicalSpacesCategory.ObjectType, sections: Mapping[frozenset[Hashable], CategoryOfCategories.ElementType], restrictions: Mapping[tuple[frozenset[Hashable], frozenset[Hashable]], MorphismCategory.ObjectType]) -> RingPresheaf:
    ...

def ring_presheaf_from_functor(space: object, opens: Any, functor: Functor, open_object_rule: Callable[[object], CategoryOfCategories.ElementType], open_key_rule: Callable[[CategoryOfCategories.ElementType], object]) -> RingPresheaf:
    ...

def ring_sheaf(presheaf: RingPresheaf, gluing_rule: GluingRule) -> RingSheaf:
    ...
