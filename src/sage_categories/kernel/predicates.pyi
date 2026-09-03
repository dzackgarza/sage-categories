from collections.abc import Callable as Callable
from dataclasses import dataclass
from plum import Function as Function
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Answer as Answer, AppliedQuery as AppliedQuery, Argument as Argument, Axiom as Axiom, PredicateHandler as PredicateHandler, Proposition as Proposition, Query as Query, QueryHandler as QueryHandler
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.kernel.refinement import is_placed as is_placed, refine as refine
from sage_categories.kernel.roles import CategoryPoint as CategoryPoint, category_universal_class as category_universal_class
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict, Unknown as Unknown
from sympy import Predicate
from sympy.core.basic import Basic
from sympy.core.expr import AtomicExpr

@dataclass(frozen=True, slots=True)
class AxiomLayer:
    generate_application: Callable[[Axiom], None]
    install_base_applications: Callable[[type[CategoryOfCategories.ElementType]], None]
    subcategory_inclusions: Callable[[PropertySubcategory], tuple[MorphismCategory.ObjectType, ...]]

def install_axiom_layer(layer: AxiomLayer) -> None:
    ...

def axiom_layer() -> AxiomLayer:
    ...

class _OwnedValueAtom(AtomicExpr):
    is_commutative: bool

    def __new__(cls, identity: int) -> _OwnedValueAtom:
        ...

def engine_argument(argument: Argument) -> Basic:
    ...

def bind_property_predicate(owner: Predicate, category: Category) -> None:
    ...

def mark_identity_predicate(owner: Predicate) -> None:
    ...

def register_predicate_handler(owner: Predicate, handler: PredicateHandler) -> None:
    ...

def register_query_handler(query: Query, handler: QueryHandler) -> None:
    ...

def ask_query(application: AppliedQuery) -> Answer:
    ...

def assume_property(proposition: Proposition) -> None:
    ...
