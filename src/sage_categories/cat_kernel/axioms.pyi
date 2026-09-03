from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Axiom
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.roles import CategoryPoint
__all__ = ['generate_application', 'install_base_applications', 'subcategory_inclusions', 'install']

def generate_application(axiom: Axiom) -> None:
    ...

def install_base_applications(owner: type[CategoryPoint]) -> None:
    ...

def subcategory_inclusions(subcategory: PropertySubcategory) -> tuple[MorphismCategory.ObjectType, ...]:
    ...

def install() -> None:
    ...
