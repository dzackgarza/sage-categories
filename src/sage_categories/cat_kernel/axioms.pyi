from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Axiom
from sage_categories.cat.properties import PropertySubcategory
__all__ = ['application_axiom', 'generate_application', 'install_base_applications', 'install_subclass_applications', 'subcategory_inclusions', 'install']

def application_axiom(owner: type[CategoryOfCategories.ElementType], name: str) -> Axiom | None:
    ...

def generate_application(axiom: Axiom) -> None:
    ...

def install_base_applications(owner: type[CategoryOfCategories.ElementType]) -> None:
    ...

def install_subclass_applications(declaring_class: type[Category]) -> None:
    ...

def subcategory_inclusions(subcategory: PropertySubcategory) -> tuple[MorphismCategory.ObjectType, ...]:
    ...

def install() -> None:
    ...
