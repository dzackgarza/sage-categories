"""Private SymPy adapter for owned values and typed-query evaluation."""

from __future__ import annotations

from inspect import get_annotations, signature
from typing import get_origin

from sage.misc.unknown import Unknown
from sage.structure.coerce_dict import MonoDict
from sympy import Integer, Predicate, sympify
from sympy.assumptions.assume import AppliedPredicate
from sympy.core.basic import Basic
from sympy.core.expr import AtomicExpr

from sage_categories.cat.predicates import Answer, AppliedQuery, Argument, Axiom, Handler, Proposition
from sage_categories.kernel.compiler import install_on_declaration
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.roles import CategoryPoint, Role, category_of, role_of


class _OwnedValueAtom(AtomicExpr):
    """A private SymPy atom that retains one owned value by Python identity."""

    is_commutative = True

    def __new__(cls, identity: int) -> _OwnedValueAtom:
        return AtomicExpr.__new__(cls, Integer(identity))


_atoms: MonoDict = MonoDict()
_values: dict[int, CategoryPoint] = {}
_atom_types: dict[type, type[_OwnedValueAtom]] = {}
_property_categories: dict[Predicate, Category] = {}
_identity_predicates: set[Predicate] = set()
_derived_applications: dict[tuple[type[CategoryPoint], str], Axiom] = {}


def _atom_type(domain: type) -> type[_OwnedValueAtom]:
    if domain in _atom_types:
        return _atom_types[domain]
    inherited = tuple(_atom_type(base) for base in domain.__bases__)
    if not inherited:
        result = _OwnedValueAtom
    else:
        bases = tuple(
            base
            for base in inherited
            if not any(other is not base and issubclass(other, base) for other in inherited)
        )
        result = type(f"_{domain.__name__}Atom", bases, {})
    _atom_types[domain] = result
    return result


def _owned_atom(value: CategoryPoint) -> _OwnedValueAtom:
    atom_type = _atom_type(type(value))
    if value not in _atoms or not isinstance(_atoms[value], atom_type):
        identity = id(value)
        _values[identity] = value
        _atoms[value] = atom_type(identity)
    return _atoms[value]


def engine_argument(argument: Argument) -> Basic:
    """Convert an owned predicate argument to its private SymPy value."""
    if isinstance(argument, CategoryPoint):
        return _owned_atom(argument)
    return sympify(argument)


def _owned_argument(argument: Basic) -> Argument:
    if isinstance(argument, _OwnedValueAtom):
        return _values[int(argument.args[0])]
    if isinstance(argument, Integer):
        return int(argument)
    return argument


def _handler_domains(handler: Handler) -> tuple[type, ...]:
    annotations = get_annotations(handler)
    owner = handler.__self__ if hasattr(handler, "__self__") else None
    domains: list[type] = []
    for parameter in signature(handler).parameters.values():
        annotation = annotations.get(parameter.name)
        if annotation is None:
            assert owner is not None and hasattr(owner, "ambient"), (
                f"{handler!r} must declare an exact semantic domain"
            )
            domains.append(_OwnedValueAtom)
            continue
        if isinstance(annotation, str):
            try:
                annotation = eval(annotation, handler.__globals__)
            except NameError:
                domains.append(_OwnedValueAtom)
                continue
        domain = get_origin(annotation) or annotation
        assert isinstance(domain, type), f"{handler!r} has non-type domain {domain!r}"
        if domain is int:
            domains.append(Integer)
        elif issubclass(domain, Basic):
            domains.append(domain)
        else:
            domains.append(_atom_type(domain))
    return tuple(domains)


def bind_property_predicate(owner: Predicate, category: Category) -> None:
    """Bind one SymPy predicate to the property category it decides."""
    _property_categories[owner] = category

    def placed(argument: _OwnedValueAtom, assumptions: Proposition) -> bool | None:
        return True if is_placed(_owned_argument(argument), category) else None

    owner.register(_OwnedValueAtom)(placed)


def mark_identity_predicate(owner: Predicate) -> None:
    """Make object identity the generic exact positive case of an equality predicate."""
    _identity_predicates.add(owner)

    def identical(first: _OwnedValueAtom, second: _OwnedValueAtom, assumptions: Proposition) -> bool | None:
        return True if _owned_argument(first) is _owned_argument(second) else None

    owner.register(_OwnedValueAtom, _OwnedValueAtom)(identical)


def register_predicate_handler(owner: Predicate, handler: Handler) -> None:
    """Register one owned exact case on SymPy's predicate dispatcher."""
    domains = _handler_domains(handler)

    def evaluate(*engine_values, assumptions: Proposition):
        arguments = tuple(_owned_argument(value) for value in engine_values)
        property_category = _property_categories.get(owner)
        if property_category is not None and len(arguments) == 1 and is_placed(arguments[0], property_category):
            return True
        if owner in _identity_predicates and len(arguments) == 2 and arguments[0] is arguments[1]:
            return True
        result = handler(*arguments)
        if result is Unknown:
            return None
        if result is True and property_category is not None:
            refine(arguments[0], property_category)
        return result

    evaluate.__name__ = handler.__name__
    owner.register(*domains)(evaluate)


def ask_query(application: AppliedQuery) -> Answer:
    """Evaluate a category-owned typed query without entering SymPy's Boolean system."""
    query = application.query()
    for handler in query.handlers():
        value = handler(*application.arguments())
        if value is Unknown:
            continue
        assert value in query.result_category()
        return value
    return Unknown


def assume_property(proposition: Proposition) -> None:
    """Apply the same-object refinement attached to a positive property assumption."""
    if not isinstance(proposition, AppliedPredicate):
        return
    category = _property_categories.get(proposition.function)
    if category is None or len(proposition.arguments) != 1:
        return
    argument = _owned_argument(proposition.arguments[0])
    assert isinstance(argument, CategoryPoint)
    refine(argument, category)


def axiom_application_owner(axiom: Axiom) -> type[CategoryPoint]:
    declaring_class = axiom._declaring_class
    assert hasattr(declaring_class, Role.OBJECT.value)
    declared = getattr(declaring_class, Role.OBJECT.value)
    assert declared is not None
    return declared


def install_axiom_application(axiom: Axiom) -> None:
    name, owner = axiom.application_name(), axiom_application_owner(axiom)

    def application(value: CategoryPoint) -> Proposition:
        placement = category_of(value, role_of(value)).narrowing_base()
        return axiom._declared_on(placement).membership_proposition(value)

    application.__name__ = name
    application.__qualname__ = f"{owner.__name__}.{name}"
    known = _derived_applications.get((owner, name))
    assert known is None or known is axiom
    assert known is not None or name not in vars(owner)
    _derived_applications[(owner, name)] = axiom
    install_on_declaration(owner, name, application)
