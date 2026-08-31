"""Private evaluation engine for the predicate theory of ``Cat``."""

from __future__ import annotations

from inspect import Parameter, signature
from typing import get_origin

from plum import Dispatcher, NotFoundLookupError, Signature as DispatchSignature
from sage.misc.unknown import Unknown
from sage.structure.coerce_dict import MonoDict, TripleDict
from sympy import Dummy, Integer, Predicate as EnginePredicate, Q, S, sympify
from sympy.assumptions import global_assumptions
from sympy.core.basic import Basic
from sympy.logic.boolalg import And, Implies, Not, Or

from sage_categories.cat.predicates import (
    Answer,
    AppliedPredicate,
    AppliedQuery,
    Argument,
    Connective,
    Decision,
    Handler,
    Predicate,
    PropertyPredicate,
    Proposition,
)
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.roles import CategoryPoint


class OwnedPropertyPredicate(EnginePredicate):
    name = "owned_property"


Q.owned_property = OwnedPropertyPredicate()
_engine_symbols: MonoDict = MonoDict()
_predicate_symbols: dict[Predicate, Basic] = {}
_decisions: TripleDict = TripleDict(weak_values=False)


def _engine_symbol(argument: Argument) -> Basic:
    if isinstance(argument, int):
        return Integer(argument)
    assert isinstance(argument, CategoryPoint), f"{argument!r} has no engine symbol"
    if argument not in _engine_symbols:
        _engine_symbols[argument] = Dummy("owned")
    return _engine_symbols[argument]


def _engine_value(proposition: AppliedPredicate | Connective) -> Basic:
    if isinstance(proposition, AppliedPredicate):
        predicate = proposition.predicate()
        symbol = _predicate_symbols.setdefault(predicate, Dummy(predicate.name()))
        return Q.owned_property(symbol, *map(_engine_symbol, proposition.arguments()))
    operator = {"and": And, "or": Or, "not": Not, "implies": Implies}[proposition.operator()]
    return operator(*(_engine_proposition(part) for part in proposition.parts()))


def _engine_proposition(part: Decision | Proposition) -> Basic:
    if part is Unknown:
        return Dummy("undecided")
    if isinstance(part, (AppliedPredicate, Connective)):
        return _engine_value(part)
    return sympify(part)


def _representable(argument: Argument) -> bool:
    return isinstance(argument, (CategoryPoint, int))


def _dispatch_annotation(annotation: object, namespace: dict[str, object]) -> object:
    if annotation is Parameter.empty:
        return object
    if not isinstance(annotation, str):
        return annotation
    if any(role_name in annotation for role_name in (".ObjectType", ".ElementType", ".MorphismType")):
        return object
    if "[" in annotation:
        return CategoryPoint
    try:
        resolved = eval(annotation, namespace)
    except (NameError, AttributeError, TypeError):
        return object
    origin = get_origin(resolved)
    if isinstance(origin, type) and issubclass(origin, CategoryPoint):
        return CategoryPoint
    if isinstance(resolved, type) and issubclass(resolved, CategoryPoint):
        return CategoryPoint
    if hasattr(resolved, "__parameters__") and resolved.__parameters__:
        return CategoryPoint
    return origin or resolved


def _dispatch_signature(handler: Handler) -> DispatchSignature:
    assert hasattr(handler, "__globals__"), f"{handler!r} has no annotation namespace"
    return DispatchSignature(*(
        _dispatch_annotation(parameter.annotation, handler.__globals__)
        for parameter in signature(handler).parameters.values()
    ))


def _resolved_handlers(predicate: Predicate, arguments: tuple[Argument, ...]):
    remaining = []
    for handler in predicate.handlers():
        def invoke(*values, _handler=handler):
            return _handler(*values)

        invoke.__name__ = handler.__name__
        remaining.append((handler, invoke, _dispatch_signature(handler)))
    while remaining:
        dispatcher = Dispatcher()
        _, first_invoke, first_signature = remaining[0]
        function = dispatcher.multi(first_signature)(first_invoke)
        for _, invoke, dispatch_signature in remaining[1:]:
            function.register(invoke, signature=dispatch_signature)
        try:
            implementation, _ = function.resolve_method(arguments)
        except NotFoundLookupError:
            return
        yield implementation
        remaining = [entry for entry in remaining if entry[1] is not implementation]


def _cache_key(applied: AppliedPredicate | AppliedQuery):
    arguments = applied.arguments()
    owner = applied.predicate() if isinstance(applied, AppliedPredicate) else applied.query()
    if not owner.records_decisions() or len(arguments) not in (1, 2):
        return None
    first, second = arguments[0], arguments[-1]
    if not isinstance(first, CategoryPoint) or not isinstance(second, CategoryPoint):
        return None
    return owner, first, second


def _ask_applied(proposition: AppliedPredicate) -> Decision:
    predicate, arguments = proposition.predicate(), proposition.arguments()
    if isinstance(predicate, PropertyPredicate) and is_placed(arguments[0], predicate.category()):
        return True
    if all(map(_representable, arguments)):
        engine_value = _engine_value(proposition)
        if engine_value in global_assumptions:
            return True
        if Not(engine_value) in global_assumptions:
            return False
    key = _cache_key(proposition)
    if key is not None and key in _decisions:
        return _decisions[key]
    for handler in _resolved_handlers(predicate, arguments):
        decision = handler(*arguments)
        if decision is Unknown:
            continue
        if key is not None:
            _decisions[key] = decision
        if decision and isinstance(predicate, PropertyPredicate):
            refine(arguments[0], predicate.category())
        return decision
    return Unknown


def _decided(proposition: Decision | Proposition) -> Basic:
    if isinstance(proposition, Connective) and _engine_value(proposition) in global_assumptions:
        return S.true
    if proposition is Unknown:
        return Dummy("undecided")
    if isinstance(proposition, bool):
        return sympify(proposition)
    if isinstance(proposition, Connective):
        operator = {"and": And, "or": Or, "not": Not, "implies": Implies}[proposition.operator()]
        if proposition.operator() not in ("and", "or"):
            return operator(*(_decided(part) for part in proposition.parts()))
        absorbing = S.false if proposition.operator() == "and" else S.true
        values: list[Basic] = []
        for part in proposition.parts():
            value = _decided(part)
            if value is absorbing:
                return absorbing
            values.append(value)
        return operator(*values)
    if isinstance(proposition, AppliedPredicate):
        decision = _ask_applied(proposition)
        if decision is not Unknown:
            return sympify(decision)
        if all(map(_representable, proposition.arguments())):
            return _engine_value(proposition)
        return Dummy("undecided")
    raise TypeError(f"{proposition!r} is not a proposition")


def ask(application: Decision | Proposition | AppliedQuery) -> Answer:
    if isinstance(application, AppliedQuery):
        query, key = application.query(), _cache_key(application)
        if key is not None and key in _decisions:
            return _decisions[key]
        for handler in _resolved_handlers(query, application.arguments()):
            value = handler(*application.arguments())
            if value is Unknown:
                continue
            assert value in query.result_category()
            if key is not None:
                _decisions[key] = value
            return value
        return Unknown
    value = _decided(application)
    return True if value is S.true else False if value is S.false else Unknown


def assume(proposition: Proposition) -> None:
    if isinstance(proposition, Connective) and proposition.operator() == "and":
        for part in proposition.parts():
            assert isinstance(part, Proposition)
            assume(part)
        return
    if isinstance(proposition, (AppliedPredicate, Connective)):
        global_assumptions.add(_engine_value(proposition))
    if isinstance(proposition, AppliedPredicate) and isinstance(proposition.predicate(), PropertyPredicate):
        refine(proposition.arguments()[0], proposition.predicate().category())


def retract(proposition: AppliedPredicate) -> None:
    assert not isinstance(proposition.predicate(), PropertyPredicate)
    global_assumptions.discard(_engine_value(proposition))
