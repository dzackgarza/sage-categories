"""SymPy predicates, typed queries, and property axioms in ``Cat``."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from itertools import count
from typing import TYPE_CHECKING

from sage.categories.category_with_axiom import uncamelcase
from sage.misc.cachefunc import cached_method
from sage.misc.unknown import Unknown, UnknownClass
from sage.structure.coerce_dict import MonoDict
from sympy import And, Implies, Not, Or, Predicate, ask as sympy_ask
from sympy.assumptions.assume import AppliedPredicate as _SymPyAppliedPredicate
from sympy.logic.boolalg import Boolean


class AppliedPredicate(_SymPyAppliedPredicate):
    """An owned predicate application; three-valued, so its Python truth value raises (D131).

    SymPy's own applied predicates take ``object.__bool__``'s default ``True``, which
    lets ``if proposition:`` and list containment silently affirm an undecided
    proposition.  Every application an owned predicate constructs is this subclass,
    and only ``ask()`` evaluates it.
    """

    def __bool__(self) -> bool:
        raise TypeError(f"cannot determine truth value of {self!r}; use ask()")

if TYPE_CHECKING:
    from sage_categories.cat.category import Category, CategoryOfCategories
    from sage_categories.cat.properties import PropertySubcategory

__all__ = [
    "Answer",
    "Axiom",
    "AppliedPredicate",
    "AppliedQuery",
    "Argument",
    "Decision",
    "Predicate",
    "PredicateHandler",
    "Proposition",
    "Query",
    "QueryAnswer",
    "QueryHandler",
    "Unknown",
    "UnknownClass",
    "ask",
    "assume",
    "conjunction",
    "disjunction",
    "established",
    "implication",
    "negation",
    "predicate",
    "property_predicate",
    "register_handler",
    "retract",
]

# What a predicate is applied to: owned values, and the integer convenience of the
# cardinal and ordinal orders (POL-TYPE-004).
type Argument = CategoryOfCategories.ElementType | int
type Decision = bool | UnknownClass
type PredicateDecision = bool | None

# What ``ask`` returns: a decision for a proposition, and an owned object of the
# declared result category for a query such as ``cardinality()``. Sage
# ``Unknown`` is the one unresolved answer of both and is an object of neither result
# category (``specs/cardinality.md``, "Integration with ``Sets()``").
type QueryAnswer = CategoryOfCategories.ElementType | UnknownClass
type Answer = Decision | CategoryOfCategories.ElementType

# An exact evaluation case on a declared semantic domain; its arity is the
# predicate's, and each owning category declares its exact parameter types.
type PredicateHandler = Callable[..., PredicateDecision]
type QueryHandler = Callable[..., QueryAnswer]
type Proposition = Boolean

_predicate_ids = count()


def _apply_predicate(owner: Predicate, *arguments: Argument) -> AppliedPredicate:
    from sage_categories.kernel.predicates import engine_argument

    return AppliedPredicate(owner, *(engine_argument(argument) for argument in arguments))


def _register_handler(owner: Predicate, handler: PredicateHandler) -> None:
    """Register an exact handler on one repository-owned SymPy predicate."""
    from sage_categories.kernel.predicates import register_predicate_handler

    register_predicate_handler(owner, handler)


def predicate(name: str) -> Predicate:
    """Construct one mathematical predicate as a native SymPy predicate."""
    predicate_type = type(
        f"CatPredicate{next(_predicate_ids)}",
        (Predicate,),
        {"name": name, "__call__": _apply_predicate, "register_handler": _register_handler},
    )
    return predicate_type()


def property_predicate(name: str, category: Category) -> Predicate:
    """Construct the SymPy predicate owned by one property subcategory."""
    owner = predicate(name)
    from sage_categories.kernel.predicates import bind_property_predicate

    bind_property_predicate(owner, category)
    return owner


def register_handler(owner: Predicate, handler: PredicateHandler) -> None:
    """Register an exact handler on a SymPy predicate."""
    _register_handler(owner, handler)


class Query:
    """A typed query with one exact mathematical result category.

    ``cardinality()`` and ``cofinality()`` are the current cases. They are not total
    and exact on their full declared domain. An exact handler returns an object of
    the result category. ``ask()`` returns Sage ``Unknown`` when no handler applies.
    """

    def __init__(self, name: str, arity: int, result_category: Category) -> None:
        self._name = name
        self._arity = arity
        self._result_category = result_category

    def name(self) -> str:
        return self._name

    def register_handler(self, handler: QueryHandler) -> None:
        from sage_categories.kernel.predicates import register_query_handler

        register_query_handler(self, handler)

    def result_category(self) -> Category:
        """The category whose objects are the exact answers of this predicate."""
        return self._result_category

    def __call__(self, *arguments: Argument) -> AppliedQuery:
        assert len(arguments) == self._arity, f"{self._name} has arity {self._arity}"
        return AppliedQuery(self, arguments)

    def __repr__(self) -> str:
        return self._name


class AppliedQuery:
    """A typed query applied to its arguments.

    It has no Boolean engine expression or assumption-context entry.
    """

    def __init__(self, query: Query, arguments: tuple[Argument, ...]) -> None:
        self._query = query
        self._arguments = arguments

    def query(self) -> Query:
        return self._query

    def arguments(self) -> tuple[Argument, ...]:
        return self._arguments

    def __bool__(self) -> bool:
        raise TypeError(f"cannot determine truth value of {self!r}; use ask()")

    def __repr__(self) -> str:
        return f"{self._query}({', '.join(map(repr, self._arguments))})"


def conjunction(parts: Iterable[bool | Proposition]) -> Proposition:
    """Construct a conjunction with SymPy's Boolean operation."""
    return And(*tuple(parts))


def disjunction(parts: Iterable[bool | Proposition]) -> Proposition:
    """Construct a disjunction with SymPy's Boolean operation."""
    return Or(*tuple(parts))


def negation(proposition: bool | Proposition) -> Proposition:
    """Construct a negation with SymPy's Boolean operation."""
    return Not(proposition)


def implication(antecedent: bool | Proposition, consequent: bool | Proposition) -> Proposition:
    """Construct an implication with SymPy's Boolean operation."""
    return Implies(antecedent, consequent)


def ask(application: Decision | Proposition | AppliedQuery) -> Answer:
    """Evaluate a proposition or typed query."""
    if isinstance(application, AppliedQuery):
        from sage_categories.kernel.predicates import ask_query

        return ask_query(application)
    decision = sympy_ask(application)
    return Unknown if decision is None else decision


def established(application: Decision | Proposition) -> bool:
    """Whether an exact decision establishes ``application`` as true."""
    return ask(application) is True


def assume(proposition: Proposition) -> None:
    """Record a SymPy proposition and apply its positive property refinement."""
    from sage_categories.kernel.predicates import assume_property
    from sympy.assumptions import global_assumptions

    global_assumptions.add(proposition)
    assume_property(proposition)


def retract(proposition: Proposition) -> None:
    """Withdraw a proposition from SymPy's active assumption context."""
    from sympy.assumptions import global_assumptions

    global_assumptions.discard(proposition)


def _property_subcategory() -> type[PropertySubcategory]:
    """The default implementation of a generated property subcategory.

    An axiom is declared in the body of a category class, and ``Cat()``'s own class is
    one of them, so this module stands below ``cat/properties.py`` rather than beside it
    (``cat/category.py``, ``Cat().Inhabited()``).  The class it returns is read on first
    construction, which is after that module is imported.
    """
    from sage_categories.cat.properties import PropertySubcategory

    return PropertySubcategory


class Axiom:
    """A property axiom, declared once in the body of a category class (D77.4, POL-LEAF-059).

    ``Finite = Axiom()`` in the body of ``SetsCategory`` gives every value of that class
    the accessor ``Finite()``, whose value is the property subcategory ``Sets().Finite()``.
    A category ``D`` declared as a subcategory of ``C`` derives ``D.Finite()`` from that
    one declaration, as the inverse image of ``C.Finite()`` along its subcategory
    monomorphism; it states no class, predicate, constructor, or transport of its own
    (POL-CAT-084, D83).

    A regressive functorial construction is an axiom too: ``X`` is a chosen product
    exactly when it lies in the image of the nontrivial product functor, so ``Products``,
    ``Coproducts``, ``Limits``, and ``Colimits`` are declared once on the base category
    class and every category receives them (D31, D89; Sage
    ``RegressiveCovariantConstructionCategory``, ``sage/categories/covariant_functorial_construction.py``,
    inspected 2026-09-02).  An axiom may take parameters, ``C.Limits(J)``, and its
    subcategory is retained once per category and parameter values.

    ``full_subcategory_of`` lists the categories ``C.P()`` is a full subcategory of beyond
    its ambient, by their axioms; each is recorded on the constructed subcategory as the
    monomorphism ``C.P() -> C.Q()`` (D83).

    The declaration is the whole of it.  The identifier supplies the generated
    application: ``Finite`` gives ``is_finite()``, ``FullyFaithful`` gives
    ``is_fully_faithful()``, and ``OfCardinalityExactlyFour`` gives
    ``is_of_cardinality_exactly_four()`` (D89, POL-CAT-060).  The class the axiom is
    written in supplies the role class the application is written onto, its
    ``ObjectType``, because ``C.P()`` is a property of the objects of ``C``.  Nothing
    spells either by hand, so neither can disagree with the axiom that owns it.

    A separate class implements the generated subcategory by naming the declaring
    category class and the axiom in ``_base_category_class_and_axiom``, exactly as Sage
    links ``FiniteSets`` back to ``(Sets, 'Finite')``
    (``sage/categories/category_with_axiom.py`` lines 213-242 and 1886-1953, inspected
    2026-08-29).  In Sage the implementation then *is* the attribute on the base category
    class, ``Groups.Finite``; here that attribute is this declaration, so the declaration
    holds the link and no table records it.

    Sage also deduces the link from the class name when the class sits in the standard
    module location (``base_category_class_and_axiom``, same file, line 1717).  This
    kernel does not: ``specs/undecidable-properties.md`` requires the property class to
    state its mathematics and forbids inferring it from the strings ``"Finite"`` or
    ``"is_finite"`` by name matching, so the link is always the field.
    """

    def __init__(self, full_subcategory_of: tuple[Axiom, ...] = ()) -> None:
        self._full_subcategory_of = full_subcategory_of
        self._implementation: type[PropertySubcategory] | None = None
        # Retained per category and parameter values, by identity (POL-SAGE-013).
        self._constructed: dict[tuple[tuple[int, Category], ...], Category] = {}

    def __set_name__(self, declaring_class: type[Category], name: str) -> None:
        self._declaring_class = declaring_class
        self._name = name
        from sage_categories.kernel.predicates import install_axiom_application

        install_axiom_application(self)

    def application_name(self) -> str:
        """``is_p()``: the application generated from this axiom's identifier and nothing else (D89, POL-CAT-060)."""
        return _application_name(self._name)

    def application_owner(self) -> type[CategoryOfCategories.ElementType]:
        """The role class the application is written onto: the object declaration of the declaring category class.

        A role *is* the name a category class writes for that mathematical kind
        (``Category.local_role_class``, POL-KERNEL-028), so this reads that one
        declaration.  ``Mor(C)`` writes ``MorphismOfCategory``, because an object of it is
        a morphism of an arbitrary ``C``; ``Fun`` writes ``Cat().MorphismType``; ``Cat()``
        writes ``CategoryDeclaration``.
        """
        from sage_categories.kernel.predicates import axiom_application_owner

        return axiom_application_owner(self)

    def __get__(self, category: Category | None, owner: type[Category]) -> Axiom | Callable[[], Category]:
        """``C.P`` on a category value is its accessor; on the class it is the declaration."""
        if category is None:
            return self
        return partial(self.subcategory, category)

    def name(self) -> str:
        return self._name

    def implemented_by(self, implementation: type[PropertySubcategory]) -> None:
        """Record the class that implements this axiom's subcategory; one axiom has one.

        The implementation supplies the subcategory's own class and, when it inherits
        ``PredicateSubcategory``, the predicate that decides membership in it (D97).  It
        supplies no name: the application was compiled from this axiom's identifier when
        the declaring class was created.
        """
        assert self._implementation is None or self._implementation is implementation, (
            f"{self!r} is already implemented by {self._implementation.__name__}, not {implementation.__name__}"
        )
        self._implementation = implementation

    def subcategory(self, category: Category, *parameters: Category) -> Category:
        """``category.P(*parameters)``: one property subcategory per category and parameter values."""
        key = tuple((id(value), value) for value in (category, *parameters))
        if key not in self._constructed:
            self._constructed[key] = self._construct(category, *parameters)
        return self._constructed[key]

    def _construct(self, category: Category, *parameters: Category) -> Category:
        """The inverse image along a declared subcategory's monomorphism, else the implementation of this axiom."""
        if category.has_ambient():
            defining_functor = category.subcategory_monomorphism()
            return defining_functor.inverse_image(self._declared_on(defining_functor.codomain(), *parameters))
        containing = tuple(axiom._declared_on(category) for axiom in self._full_subcategory_of)
        return (self._implementation or _property_subcategory())(category, self._name, containing, *parameters)

    def _declared_on(self, category: Category, *parameters: Category) -> Category:
        """``category.P(*parameters)``, through the accessor that category declares for this axiom.

        A category can build the subcategory itself -- ``Fun`` builds its property
        categories eagerly, before any of them can be constructed on demand -- and that
        declaration is then the one owner of ``C.P()``.  The axiom name is the name the
        category writes, exactly as a role is (``Category.local_role_class``,
        POL-KERNEL-028), so this reads the declaration rather than probing for it.
        """
        return getattr(category, self._name)(*parameters)

    def __repr__(self) -> str:
        return f"{self._declaring_class.__name__}.{self._name}"


def _application_name(identifier: str) -> str:
    """``"FullyFaithful"`` gives ``"is_fully_faithful"``."""
    return "is_" + uncamelcase(identifier, "_")
