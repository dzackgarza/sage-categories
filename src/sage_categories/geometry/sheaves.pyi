from collections.abc import Hashable, Mapping

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry.spaces import TopologicalSpacesCategory

class RingPresheaf:
    space: TopologicalSpacesCategory.ObjectType
    functor: Functor
    sections: Mapping[frozenset[Hashable], CategoryOfCategories.ElementType]
    def section_ring(self, open_set: frozenset[Hashable]) -> CategoryOfCategories.ElementType: ...
    def restriction(self, larger: frozenset[Hashable], smaller: frozenset[Hashable]) -> MorphismCategory.ObjectType: ...

def ring_presheaf(space: TopologicalSpacesCategory.ObjectType, sections: Mapping[frozenset[Hashable], CategoryOfCategories.ElementType], restrictions: Mapping[tuple[frozenset[Hashable], frozenset[Hashable]], MorphismCategory.ObjectType]) -> RingPresheaf: ...
