from collections.abc import Callable, Hashable, Mapping

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

type GluingRule = Callable[[frozenset[Hashable], tuple[frozenset[Hashable], ...], tuple[CategoryOfCategories.ElementType, ...]], CategoryOfCategories.ElementType]

class RingSheaf:
    presheaf: RingPresheaf
    gluing_rule: GluingRule
    def glue(self, open_set: frozenset[Hashable], cover: tuple[frozenset[Hashable], ...], local_sections: tuple[CategoryOfCategories.ElementType, ...]) -> CategoryOfCategories.ElementType: ...

def ring_presheaf(space: TopologicalSpacesCategory.ObjectType, sections: Mapping[frozenset[Hashable], CategoryOfCategories.ElementType], restrictions: Mapping[tuple[frozenset[Hashable], frozenset[Hashable]], MorphismCategory.ObjectType]) -> RingPresheaf: ...
def ring_sheaf(presheaf: RingPresheaf, gluing_rule: GluingRule) -> RingSheaf: ...
