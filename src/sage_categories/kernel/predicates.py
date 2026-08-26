"""Owned predicates, applied propositions, ``ask()``, and ``assume()``.

The model is SymPy's split between a ``Predicate``, an applied predicate, and
``ask()`` (``sympy.assumptions``).  Applying a predicate constructs a proposition;
only ``ask()`` decides it (POL-MATH-034).  The active SymPy session is the
assumption context (POL-ASSUME-002/004): every proposition has an engine value
``Q.owned_property(...)`` and ``assume()`` records it in ``global_assumptions``.

``ask(P(x))`` for a property predicate uses this order
(``specs/undecidable-properties.md``, "How ``ask()`` works"):

1. category placement, which already includes the recorded implications because
   an implication is a selected inclusion between property categories (POL-FUN-024);
2. the active assumption context;
3. the exact decision cache;
4. the registered exact handlers on their declared semantic domains (POL-MATH-042);
5. ``Unknown``.

Exact ``True`` for a property predicate refines the argument through the
property's constructor (POL-CAT-044, POL-ASSUME-007).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from sage.structure.coerce_dict import MonoDict, TripleDict
from sympy import Dummy, Integer, Predicate as EnginePredicate, Q
from sympy.assumptions import global_assumptions
from sympy.assumptions.assume import AppliedPredicate as EngineApplied
from sympy.core.basic import Basic
from sympy.logic.boolalg import And, Not

from sage_categories.kernel.decisions import Decision, Unknown, decision_and, decision_not
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.roles import CategoryPoint

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = [
    "AppliedPredicate",
    "Conjunction",
    "Negation",
    "Predicate",
    "PropertyPredicate",
    "Proposition",
    "ask",
    "assume",
]

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


def _engine_symbol(argument: CategoryPoint | int) -> Basic:
    if isinstance(argument, int):
        return Integer(argument)
    assert isinstance(argument, CategoryPoint), f"{argument!r} has no engine symbol"
    if argument not in _engine_symbols:
        _engine_symbols[argument] = Dummy("owned")
    return _engine_symbols[argument]


def _representable(argument: Any) -> bool:
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

    def __call__(self, *arguments: Any) -> AppliedPredicate:
        assert len(arguments) == self._arity, f"{self._name} has arity {self._arity}"
        return AppliedPredicate(self, arguments)

    def __repr__(self) -> str:
        return self._name


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

    def __invert__(self) -> Negation:
        return Negation(self)

    def __and__(self, other: Proposition) -> Conjunction:
        return Conjunction((self, other))


class AppliedPredicate(Proposition):
    """One predicate applied to its arguments."""

    def __init__(self, predicate: Predicate, arguments: tuple[Any, ...]) -> None:
        self._predicate = predicate
        self._arguments = arguments

    def predicate(self) -> Predicate:
        return self._predicate

    def arguments(self) -> tuple[Any, ...]:
        return self._arguments

    def engine_value(self) -> EngineApplied:
        return Q.owned_property(self._predicate._symbol, *map(_engine_symbol, self._arguments))

    def __repr__(self) -> str:
        return f"{self._predicate}({', '.join(map(repr, self._arguments))})"


class Negation(Proposition):
    def __init__(self, positive: Proposition) -> None:
        self._positive = positive

    def positive(self) -> Proposition:
        return self._positive

    def engine_value(self) -> Basic:
        return Not(self._positive.engine_value())

    def __repr__(self) -> str:
        return f"not {self._positive!r}"


class Conjunction(Proposition):
    def __init__(self, parts: tuple[Proposition, ...]) -> None:
        self._parts = parts

    def parts(self) -> tuple[Proposition, ...]:
        return self._parts

    def engine_value(self) -> Basic:
        return And(*(part.engine_value() for part in self._parts))

    def __repr__(self) -> str:
        return " and ".join(map(repr, self._parts))


def _session_decision(proposition: AppliedPredicate) -> Decision:
    if not all(map(_representable, proposition.arguments())):
        return Unknown
    engine_value = proposition.engine_value()
    if engine_value in global_assumptions:
        return True
    if Not(engine_value) in global_assumptions:
        return False
    return Unknown


def _cache_key(proposition: AppliedPredicate) -> tuple[Predicate, Any, Any] | None:
    arguments = proposition.arguments()
    if not proposition.predicate().records_decisions():
        return None
    if len(arguments) not in (1, 2) or not all(isinstance(a, CategoryPoint) for a in arguments):
        return None
    first, second = arguments[0], arguments[-1]
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


def ask(proposition: Proposition) -> Decision:
    """Decide ``proposition`` as ``True``, ``False``, or Sage ``Unknown``."""
    match proposition:
        case AppliedPredicate():
            return _ask_applied(proposition)
        case Negation():
            return decision_not(ask(proposition.positive()))
        case Conjunction():
            decision: Decision = True
            for part in proposition.parts():
                decision = decision_and(decision, ask(part))
                if decision is False:
                    return False
            return decision
    raise TypeError(f"{proposition!r} is not a proposition")


def assume(proposition: Proposition) -> None:
    """Record ``proposition`` in the active session and refine positively (POL-ASSUME-007)."""
    match proposition:
        case Conjunction():
            for part in proposition.parts():
                assume(part)
            return
        case AppliedPredicate() | Negation():
            global_assumptions.add(proposition.engine_value())
    if isinstance(proposition, AppliedPredicate) and isinstance(proposition.predicate(), PropertyPredicate):
        refine(proposition.arguments()[0], proposition.predicate().category())
