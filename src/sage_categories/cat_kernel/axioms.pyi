from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Axiom
from sage_categories.cat.properties import PropertySubcategory
__all__ = ['generate_application', 'install_base_applications', 'subcategory_inclusions', 'install']

def generate_application(axiom: Axiom) -> None:
    ...

def install_base_applications(owner: type[CategoryOfCategories.ElementType]) -> None:
    ...

def subcategory_inclusions(subcategory: PropertySubcategory) -> tuple[MorphismCategory.ObjectType, ...]:
    ...

def install() -> None:
    ...
