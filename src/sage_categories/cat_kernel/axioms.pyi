from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Axiom as Axiom
from sage_categories.cat.predicates import Proposition as Proposition
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.kernel.compiler import install_on_declaration as install_on_declaration
from sage_categories.kernel.predicates import AxiomLayer as AxiomLayer
from sage_categories.kernel.predicates import install_axiom_layer as install_axiom_layer
from sage_categories.kernel.roles import Role as Role
from sage_categories.kernel.roles import category_of as category_of
from sage_categories.kernel.roles import role_of as role_of

__all__ = ["application_axiom", "generate_application", "install", "install_base_applications", "install_subclass_applications", "subcategory_inclusions"]

def application_axiom(owner: type[CategoryOfCategories.ElementType], name: str) -> Axiom | None: ...
def generate_application(axiom: Axiom) -> None: ...
def install_base_applications(owner: type[CategoryOfCategories.ElementType]) -> None: ...
def install_subclass_applications(declaring_class: type[Category]) -> None: ...
def subcategory_inclusions(subcategory: PropertySubcategory) -> tuple[MorphismCategory.ObjectType, ...]: ...
def install() -> None: ...
