from collections.abc import Callable, Iterable
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.sage_runtime import Unknown as Unknown, UnknownClass as UnknownClass
from sympy import Predicate as Predicate
from sympy.assumptions.assume import AppliedPredicate as _SymPyAppliedPredicate
from sympy.logic.boolalg import Boolean
__all__ = ['Predicate', 'Unknown', 'UnknownClass', 'AppliedPredicate', 'Argument', 'Decision', 'QueryAnswer', 'Answer', 'PredicateHandler', 'QueryHandler', 'Proposition', 'DecidingProposition', 'predicate', 'property_predicate', 'register_handler', 'Query', 'AppliedQuery', 'conjunction', 'disjunction', 'negation', 'implication', 'ask', 'established', 'assume', 'retract', 'Axiom', 'declared_axiom']

class AppliedPredicate(_SymPyAppliedPredicate):

    def __bool__(self) -> bool:
        ...
type Argument = CategoryOfCategories.ElementType | int
type Decision = bool | UnknownClass
type PredicateDecision = bool | None
type QueryAnswer = CategoryOfCategories.ElementType | UnknownClass
type Answer = Decision | CategoryOfCategories.ElementType
type PredicateHandler = Callable[..., PredicateDecision]
type QueryHandler = Callable[..., QueryAnswer]
type Proposition = Boolean
type DecidingProposition = Callable[[Category, CategoryOfCategories.ElementType], Proposition]

def predicate(name: str) -> Predicate:
    ...

def property_predicate(name: str, category: Category) -> Predicate:
    ...

def register_handler(owner: Predicate, handler: PredicateHandler) -> None:
    ...

class Query:

    def __init__(self, name: str, arity: int, result_category: Category) -> None:
        ...

    def name(self) -> str:
        ...

    def register_handler(self, handler: QueryHandler) -> None:
        ...

    def result_category(self) -> Category:
        ...

    def __call__(self, *arguments: Argument) -> AppliedQuery:
        ...

class AppliedQuery:

    def __init__(self, query: Query, arguments: tuple[Argument, ...]) -> None:
        ...

    def query(self) -> Query:
        ...

    def arguments(self) -> tuple[Argument, ...]:
        ...

    def __bool__(self) -> bool:
        ...

def conjunction(parts: Iterable[bool | Proposition]) -> Proposition:
    ...

def disjunction(parts: Iterable[bool | Proposition]) -> Proposition:
    ...

def negation(proposition: bool | Proposition) -> Proposition:
    ...

def implication(antecedent: bool | Proposition, consequent: bool | Proposition) -> Proposition:
    ...

def ask(application: Decision | Proposition | AppliedQuery) -> Answer:
    ...

def established(application: Decision | Proposition) -> bool:
    ...

def assume(proposition: Proposition) -> None:
    ...

def retract(proposition: Proposition) -> None:
    ...

class Axiom:

    def __init__(self, deciding: DecidingProposition | None = None, *, full_subcategory_of: tuple[Axiom, ...]=()) -> None:
        ...

    def __set_name__(self, declaring_class: type[Category], name: str) -> None:
        ...

    def application_name(self) -> str:
        ...

    def application_owner(self) -> type[CategoryOfCategories.ElementType] | None:
        ...

    def __get__(self, category: Category | None, owner: type[Category]) -> Axiom | Callable[[], Category]:
        ...

    def name(self) -> str:
        ...

    def implemented_by(self, implementation: type[PropertySubcategory]) -> None:
        ...

    def subcategory(self, category: Category, *parameters: CategoryOfCategories.ElementType) -> Category:
        ...

    def is_constructed(self, category: Category, *parameters: CategoryOfCategories.ElementType) -> bool:
        ...

def declared_axiom(category: Category, name: str) -> Axiom | None:
    ...
