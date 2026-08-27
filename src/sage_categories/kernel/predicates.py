"""Owned predicates, applied propositions, ``ask()``, and ``assume()``.

The model is SymPy's split between a ``Predicate``, an applied predicate, and
``ask()`` (``sympy.assumptions``).  Applying a predicate constructs a proposition;
only ``ask()`` decides it (POL-MATH-034).  The active SymPy session is the
assumption context (POL-ASSUME-002/004): every proposition has an engine value
``Q.owned_property(...)`` and ``assume()`` records it in ``global_assumptions``.

``ask(P(x))`` for a property predicate uses this order
(``specs/undecidable-properties.md``, "How ``ask()`` works"):

1. category placement, which already includes the recorded implications because
   an implication is a selected subcategory monomorphism between property categories (POL-FUN-024);
2. the active assumption context;
3. the exact decision cache;
4. the registered exact handlers on their declared semantic domains (POL-MATH-042);
5. ``Unknown``.

Exact ``True`` for a property predicate refines the argument through the
property's constructor (POL-CAT-044, POL-ASSUME-007).

There is one three-valued logic, and it is this one.  A handler composes its
sub-questions as propositions -- ``conjunction``, ``disjunction``, ``negation``,
``implication``, and the ``&``, ``|``, ``~`` operators -- and asks the result once.
``Connective`` carries no truth table: it delegates to ``sympy.logic.boolalg``'s
``And``, ``Or``, ``Not``, and ``Implies``, exactly as an applied predicate delegates to
``Q.owned_property``.  What the wrapper adds over a bare SymPy expression is that the
parts stay owned until ``ask`` decides them, because an exact handler needs the owned
arguments of a leaf and the engine expression has replaced them by dummies.

A part may be a decision rather than a proposition: an exact handler that compares two
private data holds one, since ``==`` on an engine value is exact.  ``ask`` sympifies a
decided part, so the two kinds compose without a caller ever inspecting which it holds.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any

from sage.structure.coerce_dict import MonoDict, TripleDict
from sympy import Dummy, Integer, Predicate as EnginePredicate, Q, S, sympify
from sympy.assumptions import global_assumptions
from sympy.assumptions.assume import AppliedPredicate as EngineApplied
from sympy.core.basic import Basic
from sympy.logic.boolalg import And, Implies, Not, Or

from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.roles import CategoryPoint

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = [
    "AppliedPredicate",
    "Argument",
    "Connective",
    "EqualityPredicate",
    "Predicate",
    "PropertyPredicate",
    "Proposition",
    "ask",
    "assume",
    "conjunction",
    "disjunction",
    "implication",
    "negation",
]

# What a predicate is applied to: owned values, and the integer convenience of the
# cardinal and ordinal orders.  The candidate of an equality proposition enters
# through ``EqualityPredicate`` alone (POL-TYPE-004).
type Argument = CategoryPoint | int

# An exact decision procedure on a declared semantic domain; its arity is the
# predicate's, and each owning category declares its exact parameter types.
type Handler = Callable[..., Decision]


class OwnedPropertyPredicate(EnginePredicate):
    """The one SymPy predicate carrying every owned proposition (POL-ASSUME-003)."""

    name = "owned_property"


Q.owned_property = OwnedPropertyPredicate()

# One SymPy ``Dummy`` per owned value, keyed by identity; dummies are unique by
# identity, so two propositions have equal engine values exactly when they apply
# one predicate to the same owned values.
_engine_symbols: MonoDict = MonoDict()

# Exact decisions already computed by a handler: (predicate, first, second) -> Decision.
_decisions: TripleDict = TripleDict(weak_values=False)


def _engine_symbol(argument: Argument) -> Basic:
    if isinstance(argument, int):
        return Integer(argument)
    assert isinstance(argument, CategoryPoint), f"{argument!r} has no engine symbol"
    if argument not in _engine_symbols:
        _engine_symbols[argument] = Dummy("owned")
    return _engine_symbols[argument]


def _representable(argument: Argument) -> bool:
    """Whether the session can carry the argument: an equality candidate may be neither owned nor an integer."""
    return isinstance(argument, (CategoryPoint, int))


class Predicate:
    """A named predicate of fixed arity; applying it constructs a proposition.

    ``records_decisions`` says whether an exact handler decision is a permanent fact
    of its arguments (equality, element membership, cardinal order) and may be
    cached; a decision that reads current category placement is not.
    """

    def __init__(self, name: str, arity: int, records_decisions: bool) -> None:
        self._name = name
        self._arity = arity
        self._records_decisions = records_decisions
        self._handlers: list[Handler] = []
        self._symbol = Dummy(name)

    def name(self) -> str:
        return self._name

    def arity(self) -> int:
        return self._arity

    def records_decisions(self) -> bool:
        return self._records_decisions

    def register_handler(self, handler: Handler) -> None:
        """Register an exact decision procedure on a declared semantic domain."""
        self._handlers.append(handler)

    def handlers(self) -> tuple[Handler, ...]:
        return tuple(self._handlers)

    def __call__(self, *arguments: Argument) -> AppliedPredicate:
        assert len(arguments) == self._arity, f"{self._name} has arity {self._arity}"
        return AppliedPredicate(self, arguments)

    def __repr__(self) -> str:
        return self._name


class EqualityPredicate(Predicate):
    """The binary equality predicate of a category: ``a == b`` applies it to ``a`` and any candidate (POL-TYPE-004)."""

    def __init__(self, name: str) -> None:
        super().__init__(name, 2, True)

    def __call__(self, first: CategoryPoint, candidate: Any) -> AppliedPredicate:
        return AppliedPredicate(self, (first, candidate))


class PropertyPredicate(Predicate):
    """The unary predicate of one property subcategory; ``ask`` consults placement."""

    def __init__(self, name: str, category: Category) -> None:
        super().__init__(name, 1, True)
        self._category = category

    def category(self) -> Category:
        """The root property subcategory that this predicate defines."""
        return self._category


class Proposition:
    """A proposition whose truth is obtained only through ``ask()``."""

    def __bool__(self) -> bool:
        # SymPy ``Relational.__bool__`` is the mature reference: a proposition has no
        # Python truth value (POL-MATH-035).
        raise TypeError(f"cannot determine truth value of {self!r}; use ask()")

    def __invert__(self) -> Connective:
        return Connective(Not, (self,))

    def __and__(self, other: Decision | Proposition) -> Connective:
        return Connective(And, (self, other))

    def __rand__(self, other: Decision | Proposition) -> Connective:
        return Connective(And, (other, self))

    def __or__(self, other: Decision | Proposition) -> Connective:
        return Connective(Or, (self, other))

    def __ror__(self, other: Decision | Proposition) -> Connective:
        return Connective(Or, (other, self))


class AppliedPredicate(Proposition):
    """One predicate applied to its arguments."""

    def __init__(self, predicate: Predicate, arguments: tuple[Argument, ...]) -> None:
        self._predicate = predicate
        self._arguments = arguments

    def predicate(self) -> Predicate:
        return self._predicate

    def arguments(self) -> tuple[Argument, ...]:
        return self._arguments

    def engine_value(self) -> EngineApplied:
        return Q.owned_property(self._predicate._symbol, *map(_engine_symbol, self._arguments))

    def __repr__(self) -> str:
        return f"{self._predicate}({', '.join(map(repr, self._arguments))})"


class Connective(Proposition):
    """Propositions under one SymPy boolean operator: ``And``, ``Or``, or ``Not``.

    The boolean algebra is SymPy's (``sympy.logic.boolalg``), so this class carries no
    truth table of its own.  What it adds over SymPy's own expression is that its parts
    stay owned propositions until ``ask`` decides them: an exact handler needs the owned
    arguments of a leaf, which the engine expression has already replaced by dummies.

    A part may be a decision instead of a proposition.  A handler that compares two
    private data holds one, since ``==`` on an engine value is exact; ``ask`` sympifies
    it and the connective composes the two kinds uniformly.
    """

    def __init__(self, operator: Callable[..., Basic], parts: tuple[Decision | Proposition, ...]) -> None:
        self._operator = operator
        self._parts = parts

    def operator(self) -> Callable[..., Basic]:
        return self._operator

    def parts(self) -> tuple[Decision | Proposition, ...]:
        return self._parts

    def engine_value(self) -> Basic:
        return self._operator(*(_engine_proposition(part) for part in self._parts))

    def __repr__(self) -> str:
        if self._operator is Not:
            return f"not {self._parts[0]!r}"
        separator = " and " if self._operator is And else (" implies " if self._operator is Implies else " or ")
        return separator.join(map(repr, self._parts))


def _engine_proposition(part: Decision | Proposition) -> Basic:
    """A part as an engine expression, with a decided part as its SymPy truth value."""
    if part is True or part is False:
        return sympify(part)
    if part is Unknown:
        return Dummy("undecided")
    return part.engine_value()


def conjunction(parts: Iterable[Decision | Proposition]) -> Proposition:
    """The conjunction of the parts; the empty conjunction is ``True``."""
    return Connective(And, tuple(parts))


def disjunction(parts: Iterable[Decision | Proposition]) -> Proposition:
    """The disjunction of the parts; the empty disjunction is ``False``."""
    return Connective(Or, tuple(parts))


def negation(part: Decision | Proposition) -> Proposition:
    """The negation of a proposition or of a decided part."""
    return Connective(Not, (part,))


def implication(antecedent: Decision | Proposition, consequent: Decision | Proposition) -> Proposition:
    """``antecedent => consequent``."""
    return Connective(Implies, (antecedent, consequent))


def _session_decision(proposition: AppliedPredicate) -> Decision:
    if not all(map(_representable, proposition.arguments())):
        return Unknown
    engine_value = proposition.engine_value()
    if engine_value in global_assumptions:
        return True
    if Not(engine_value) in global_assumptions:
        return False
    return Unknown


def _cache_key(proposition: AppliedPredicate) -> tuple[Predicate, CategoryPoint, CategoryPoint] | None:
    """The identity key of a recordable decision: the predicate and its one or two owned arguments."""
    arguments = proposition.arguments()
    if not proposition.predicate().records_decisions():
        return None
    if len(arguments) not in (1, 2):
        return None
    first, second = arguments[0], arguments[-1]
    if not isinstance(first, CategoryPoint) or not isinstance(second, CategoryPoint):
        return None
    return proposition.predicate(), first, second


def _ask_applied(proposition: AppliedPredicate) -> Decision:
    predicate = proposition.predicate()
    arguments = proposition.arguments()
    if isinstance(predicate, PropertyPredicate) and is_placed(arguments[0], predicate.category()):
        return True
    session = _session_decision(proposition)
    if session is not Unknown:
        return session
    key = _cache_key(proposition)
    if key is not None and key in _decisions:
        return _decisions[key]
    for handler in predicate.handlers():
        decision = handler(*arguments)
        if decision is Unknown:
            continue
        if key is not None:
            _decisions[key] = decision
        if decision is True and isinstance(predicate, PropertyPredicate):
            refine(arguments[0], predicate.category())
        return decision
    return Unknown


def _decided(proposition: Decision | Proposition) -> Basic:
    """The engine value of ``proposition`` with every decided leaf replaced by its truth value.

    An undecided leaf stays its own engine expression, which is unique to its predicate
    and arguments, so SymPy's boolean algebra combines the parts: it reads ``True or P``
    as ``True`` and leaves ``P or Q`` undecided.  That algebra is the only truth table
    involved, and it is SymPy's.
    """
    if proposition is True or proposition is False:
        return sympify(proposition)
    if proposition is Unknown:
        return Dummy("undecided")
    match proposition:
        case Connective():
            operator = proposition.operator()
            if operator is not And and operator is not Or:
                return operator(*(_decided(part) for part in proposition.parts()))
            # A conjunction stops at ``False`` and a disjunction at ``True``.  This is not
            # an optimization: a guarded proposition such as "``f`` is a morphism of ``C``
            # and its endpoints are ``A, B``" states that the later parts are asked only
            # once the earlier ones hold, and its handlers require that.
            absorbing = S.false if operator is And else S.true
            values: list[Basic] = []
            for part in proposition.parts():
                value = _decided(part)
                if value is absorbing:
                    return absorbing
                values.append(value)
            return operator(*values)
        case AppliedPredicate():
            decision = _ask_applied(proposition)
            return proposition.engine_value() if decision is Unknown else sympify(decision)
    raise TypeError(f"{proposition!r} is not a proposition")


def ask(proposition: Decision | Proposition) -> Decision:
    """Decide ``proposition`` as ``True``, ``False``, or Sage ``Unknown``.

    ``ask`` is total on decisions as well: ``a == b`` returns a proposition for an owned
    value and a decision for an engine value, and asking an already decided one is
    idempotent, so a caller never inspects which of the two it holds (POL-MATH-034).
    """
    value = _decided(proposition)
    if value is S.true:
        return True
    if value is S.false:
        return False
    return Unknown


def assume(proposition: Proposition) -> None:
    """Record ``proposition`` in the active session and refine positively (POL-ASSUME-007)."""
    match proposition:
        case Connective() if proposition.operator() is And:
            for part in proposition.parts():
                assume(part)
            return
        case AppliedPredicate() | Connective():
            global_assumptions.add(proposition.engine_value())
    if isinstance(proposition, AppliedPredicate) and isinstance(proposition.predicate(), PropertyPredicate):
        refine(proposition.arguments()[0], proposition.predicate().category())
