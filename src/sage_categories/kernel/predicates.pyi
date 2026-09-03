from plum import Function as Function
from sage_categories.cat.category import Category as Category
from sage_categories.cat.predicates import Answer as Answer, AppliedQuery as AppliedQuery, Argument as Argument, Axiom as Axiom, PredicateHandler as PredicateHandler, Proposition as Proposition, Query as Query, QueryAnswer as QueryAnswer, QueryHandler as QueryHandler
from sage_categories.kernel.compiler import install_on_declaration as install_on_declaration
from sage_categories.kernel.refinement import is_placed as is_placed, refine as refine
from sage_categories.kernel.roles import CategoryPoint as CategoryPoint, Role as Role, category_of as category_of, role_of as role_of
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict, Unknown as Unknown
from sympy import Predicate
from sympy.core.basic import Basic
from sympy.core.expr import AtomicExpr

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

def axiom_application_owner(axiom: Axiom) -> type[CategoryPoint] | None:
    ...

def install_axiom_application(axiom: Axiom) -> None:
    ...

def install_base_axiom_applications(owner: type[CategoryPoint]) -> None:
    ...
