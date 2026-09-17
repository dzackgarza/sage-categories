from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.cat.predicates import Unknown as Unknown, ask as ask
from sage_categories.geometry.spaces import TopologicalSpacesCategory as TopologicalSpacesCategory

@dataclass(frozen=True, eq=False, slots=True)
class RingPresheaf[OpenKey: Hashable]:
    space: object
    opens: Category
    functor: Functor
    open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType]
    open_key_rule: Callable[[CategoryOfCategories.ElementType], OpenKey]

    def open_object(self, key: OpenKey) -> CategoryOfCategories.ElementType:
        ...

    def open_key(self, open_object: CategoryOfCategories.ElementType) -> OpenKey:
        ...

    def section_ring(self, open_set: OpenKey) -> CategoryOfCategories.ElementType:
        ...

    def restriction(self, larger: OpenKey, smaller: OpenKey) -> MorphismCategory.ObjectType:
        ...
type GluingRule[OpenKey: Hashable] = Callable[[OpenKey, tuple[OpenKey, ...], tuple[CategoryOfCategories.ElementType, ...]], CategoryOfCategories.ElementType]

@dataclass(frozen=True, eq=False, slots=True)
class RingSheaf[OpenKey: Hashable]:
    presheaf: RingPresheaf[OpenKey]
    gluing_rule: GluingRule[OpenKey]

    def glue(self, open_set: frozenset[Hashable], cover: tuple[frozenset[Hashable], ...], local_sections: tuple[CategoryOfCategories.ElementType, ...]) -> CategoryOfCategories.ElementType:
        ...

def ring_presheaf(space: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]], sections: Mapping[frozenset[Hashable], CategoryOfCategories.ElementType], restrictions: Mapping[tuple[frozenset[Hashable], frozenset[Hashable]], MorphismCategory.ObjectType]) -> RingPresheaf[frozenset[Hashable]]:
    ...

def ring_presheaf_from_functor[OpenKey: Hashable](space: TopologicalSpacesCategory.ObjectType[OpenKey], opens: Category, functor: Functor, open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType], open_key_rule: Callable[[CategoryOfCategories.ElementType], OpenKey]) -> RingPresheaf[OpenKey]:
    ...

def ring_sheaf[OpenKey: Hashable](presheaf: RingPresheaf[OpenKey], gluing_rule: GluingRule[OpenKey]) -> RingSheaf[OpenKey]:
    ...
