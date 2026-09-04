import abc
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition
from sage_categories.cat.properties import PropertySubcategory
__all__ = ['StrictImageCategory', 'FullImageCategory', 'EssentialImageCategory', 'retain_object_image', 'retain_morphism_image', 'strict_image', 'register_full_image', 'full_image', '_ImageObjectPredicate@67', '_ImageMorphismPredicate@70']

class ImageMorphismCategory[**MorphismData, **TwoMorphismData](MorphismCategory[MorphismData, TwoMorphismData]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

class ImageCategory[**MorphismData, **TwoMorphismData](Category[MorphismData, TwoMorphismData], metaclass=abc.ABCMeta):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, defining_functor: Functor) -> None:
        ...

    def defining_functor(self) -> Functor:
        ...

    def target(self) -> Category:
        ...

    def equality(self) -> Predicate:
        ...

    def morphism_category_type(self) -> type[ImageMorphismCategory[MorphismData, TwoMorphismData]]:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def morphism_membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def object_image(self, source: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def morphism_image(self, source: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def factor_functor(self) -> Functor:
        ...

    def inclusion_functor(self) -> Functor:
        ...

    def factorization(self) -> tuple[Functor, Functor]:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def construct_identity(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def compose_morphisms(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

class StrictImageCategory[**MorphismData, **TwoMorphismData](ImageCategory[MorphismData, TwoMorphismData]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

class FullImageCategory[**MorphismData, **TwoMorphismData](ImageCategory[MorphismData, TwoMorphismData]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

class EssentialImageCategory[**MorphismData, **TwoMorphismData](PropertySubcategory[MorphismData, TwoMorphismData]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category, name: str, full_subcategory_of: tuple[Category, ...], defining_functor: Functor) -> None:
        ...

    def defining_functor(self) -> Functor:
        ...

    def object_image(self, source: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def morphism_image(self, source: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def factor_functor(self) -> Functor:
        ...

    def inclusion_functor(self) -> Functor:
        ...

    def factorization(self) -> tuple[Functor, Functor]:
        ...

def retain_object_image(defining_functor: Functor, image: CategoryOfCategories.ElementType) -> None:
    ...

def retain_morphism_image(defining_functor: Functor, image: MorphismCategory.ObjectType) -> None:
    ...

def strict_image(target: Category, defining_functor: Functor) -> StrictImageCategory:
    ...

def register_full_image(defining_functor: Functor, image: Category) -> None:
    ...

def full_image(target: Category, defining_functor: Functor) -> Category:
    ...
