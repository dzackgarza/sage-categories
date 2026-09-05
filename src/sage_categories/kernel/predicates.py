"""Private SymPy adapter for owned values and typed-query evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from inspect import get_annotations, signature
from itertools import count
from typing import TYPE_CHECKING, Annotated, get_origin

from beartype.vale import Is
from plum import Dispatcher, Function, NotFoundLookupError
from sympy import And, Integer, Predicate
from sympy.assumptions.assume import AppliedPredicate as _SymPyAppliedPredicate
from sympy.core.basic import Basic
from sympy.core.expr import AtomicExpr
from sympy.core.sympify import converter

from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.roles import CategoryPoint, category_universal_class
from sage_categories.kernel.sage_runtime import MonoDict, Unknown

if TYPE_CHECKING:
    from collections.abc import Callable

    from sage_categories.cat.category import Category, CategoryOfCategories
    from sage_categories.cat.morphisms import MorphismCategory
    from sage_categories.cat.predicates import (
        Answer,
        AppliedQuery,
        Argument,
        Axiom,
        PredicateHandler,
        Proposition,
        Query,
        QueryHandler,
    )
    from sage_categories.cat.properties import PropertySubcategory


@dataclass(frozen=True, slots=True)
class AxiomLayer:
    """What ``cat_kernel`` supplies for an axiom, and neither layer below supplies alone (D175).

    Generating ``is_p()`` needs the axiom's declaration, which is ``Cat``'s, and the
    compiler's installer, which is the kernel's; building a property subcategory's
    inclusion ``C.P() -> C`` needs the declaration and the placement graph the same way
    (D148, D150, ``POL-CAT-038``).  ``cat_kernel`` is the layer that has both, and it
    installs itself here because ``Cat`` declares its first axiom while it is loading,
    which is before ``cat_kernel`` can import it (``specs/resolution.md``, "The closed
    kernel surface").
    """

    generate_application: Callable[[Axiom], None]
    install_base_applications: Callable[[type[CategoryOfCategories.ElementType]], None]
    subcategory_inclusions: Callable[[PropertySubcategory], tuple[MorphismCategory.ObjectType, ...]]


_axiom_layer: AxiomLayer | None = None


def install_axiom_layer(layer: AxiomLayer) -> None:
    """Install ``cat_kernel``'s axiom layer (D175)."""
    global _axiom_layer
    _axiom_layer = layer


def axiom_layer() -> AxiomLayer:
    """The installed axiom layer, which ``sage_categories`` installs before ``Cat`` is loaded."""
    assert _axiom_layer is not None, "cat_kernel installs the axiom layer before Cat is loaded"
    return _axiom_layer


class _OwnedValueAtom(AtomicExpr):
    """A private SymPy atom that retains one owned value by Python identity."""

    is_commutative = True

    def __new__(cls, identity: int) -> _OwnedValueAtom:
        return AtomicExpr.__new__(cls, Integer(identity))


_atoms: MonoDict = MonoDict()
_values: dict[int, Argument] = {}
_atom_types: dict[type, type[_OwnedValueAtom]] = {}
_property_categories: dict[OwnedPredicate, Category] = {}
_identity_predicates: set[OwnedPredicate] = set()
_query_dispatchers: dict[Query, tuple[Dispatcher, Function]] = {}


def _atom_type(domain: type) -> type[_OwnedValueAtom]:
    if domain in _atom_types:
        return _atom_types[domain]
    from sage_categories.kernel.compiler import runtime_semantic_bases

    semantic_bases = runtime_semantic_bases(domain) or domain.__bases__
    inherited = tuple(_atom_type(base) for base in semantic_bases)
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


def _owned_atom(value: Argument) -> _OwnedValueAtom:
    if value not in _atoms:
        identity = id(value)
        _values[identity] = value
        _atoms[value] = _atom_type(type(value))(identity)
    return _atoms[value]


# An owned value entering any SymPy expression becomes its private identity atom
# (``specs/undecidable-properties.md``, "Public propositions").  ``converter`` is the
# registry SymPy documents for exactly this -- the key is the class, the value converts an
# instance to a ``Basic``, and ``sympify`` walks the MRO of every argument through it,
# ``strict`` included (``sympy/core/sympify.py`` lines 302-313 and 414-425, SymPy 1.14.0,
# inspected 2026-09-04).  Stating the rule here rather than at each application site is
# what lets a predicate a category defines as a SymPy ``Predicate`` subclass apply to an
# owned value: SymPy converts the argument, and no caller converts anything.
converter[CategoryPoint] = _owned_atom


class AppliedPredicate(_SymPyAppliedPredicate):
    """An owned predicate application; three-valued, so its Python truth value raises (D131).

    SymPy's own applied predicates take ``object.__bool__``'s default ``True``, which
    lets ``if proposition:`` and list containment silently affirm an undecided
    proposition.  Every application an owned predicate constructs is this subclass,
    and only ``ask()`` evaluates it.
    """

    def __bool__(self) -> bool:
        raise TypeError(f"cannot determine truth value of {self!r}; use ask()")


class OwnedPredicate(Predicate):
    """The SymPy ``Predicate`` subclass every owned predicate is an instance of.

    SymPy keeps a predicate's handler dispatcher on its class and dispatches on argument
    types, so a predicate that can be evaluated is a subclass with an instance
    (``sympy/assumptions/assume.py``, ``PredicateMeta`` and ``Predicate``, SymPy 1.14.0,
    inspected 2026-09-04).  This base adds the one thing SymPy's predicate does not:
    application returns the three-valued ``AppliedPredicate`` above.  Argument conversion
    is SymPy's, through the ``converter`` entry above.
    """

    def __call__(self, *arguments: Argument) -> AppliedPredicate:
        return AppliedPredicate(self, *arguments)

    def register_handler(self, handler: PredicateHandler) -> None:
        """Register one owned exact case on this predicate."""
        register_predicate_handler(self, handler)


_predicate_classes = count()


def owned_predicate(name: str) -> OwnedPredicate:
    """Construct one owned predicate, as its own subclass so it carries its own dispatcher."""
    return type(f"OwnedPredicate{next(_predicate_classes)}", (OwnedPredicate,), {"name": name})()


def _owned_argument(argument: Basic) -> Argument:
    if isinstance(argument, _OwnedValueAtom):
        return _values[int(argument.args[0])]
    if isinstance(argument, Integer):
        return int(argument)
    raise TypeError(f"{argument!r} is not an owned predicate argument")


def _handler_domains(handler: PredicateHandler | QueryHandler) -> tuple[type, ...]:
    annotations = get_annotations(handler)
    function = handler.__func__ if hasattr(handler, "__func__") else handler
    namespace = dict(function.__globals__)
    domains: list[type] = []
    for parameter in signature(handler).parameters.values():
        if parameter.name == "assumptions":
            continue
        annotation = annotations.get(parameter.name)
        assert annotation is not None, f"{handler!r} must declare an exact semantic domain for {parameter.name}"
        if isinstance(annotation, str):
            annotation = _evaluated_domain(handler, annotation, namespace)
        domain = get_origin(annotation) or annotation
        assert isinstance(domain, type), f"{handler!r} has non-type domain {domain!r}"
        domains.append(domain)
    return tuple(domains)


def _matches_handler_domain(domain: type, argument: Argument) -> bool:
    """Whether an argument has ``domain`` directly or through the retained compiler relation."""
    if isinstance(argument, domain):
        return True
    if not isinstance(argument, CategoryPoint):
        return False
    from sage_categories.kernel.compiler import runtime_semantic_bases

    semantic_bases = runtime_semantic_bases(type(argument))
    return semantic_bases is not None and domain in semantic_bases


def _evaluated_domain(
    handler: PredicateHandler | QueryHandler,
    annotation: str,
    namespace: dict[str, type],
) -> type:
    """Evaluate a handler's string annotation in its own module's namespace.

    The module that writes a handler can hold the name its annotation uses under
    ``TYPE_CHECKING``, so the name is absent at runtime.  The class ``Cat()`` writes is
    the one the bootstrap handed the kernel, so the string resolves from that rather than
    from a ``Cat`` import (D173).  Adding it is second because a handler registered while
    ``Cat`` is still importing resolves from its own module and the bootstrap has not run.
    """
    try:
        return eval(annotation, namespace)
    except NameError:
        universal = category_universal_class()
        namespace[universal.__name__] = universal
    try:
        return eval(annotation, namespace)
    except NameError as error:
        raise AssertionError(f"{handler!r} has unresolved semantic domain {annotation!r}") from error


def _predicate_domains(handler: PredicateHandler) -> tuple[type, ...]:
    return tuple(
        Integer if domain is int else domain if issubclass(domain, Basic) else _atom_type(domain)
        for domain in _handler_domains(handler)
    )


def bind_property_predicate(owner: OwnedPredicate, category: Category) -> None:
    """Bind one SymPy predicate to the property category it decides."""
    _property_categories[owner] = category

    def placed(argument: _OwnedValueAtom, assumptions: Proposition) -> bool | None:
        return True if is_placed(_owned_argument(argument), category) else None

    owner.register(_OwnedValueAtom)(placed)


def mark_identity_predicate(owner: OwnedPredicate) -> None:
    """Make object identity the generic exact positive case of an equality predicate."""
    _identity_predicates.add(owner)

    def identical(first: _OwnedValueAtom, second: _OwnedValueAtom, assumptions: Proposition) -> bool | None:
        return True if _owned_argument(first) is _owned_argument(second) else None

    owner.register(_OwnedValueAtom, _OwnedValueAtom)(identical)


def register_predicate_handler(owner: OwnedPredicate, handler: PredicateHandler) -> None:
    """Register one owned exact case whose semantic domains its own annotations declare."""
    _register_exact_case(owner, _predicate_domains(handler), handler)


def register_declared_case(owner: OwnedPredicate, domain: type, handler: PredicateHandler) -> None:
    """Register the one exact case an axiom declaration supplies, on the objects of its declaring category.

    The declaration already names that semantic domain -- it is the role class the
    generated ``is_p()`` is written onto -- so the case is dispatched from it rather than
    from an annotation the leaf writes a second time.
    """
    _register_exact_case(owner, (_atom_type(domain),), handler)


def _register_exact_case(owner: OwnedPredicate, domains: tuple[type, ...], handler: PredicateHandler) -> None:
    """Register one owned exact case on SymPy's predicate dispatcher.

    Each exact dispatch signature has one owner.  SymPy's dispatcher silently keeps
    the last registration for a repeated signature, which would discard the earlier
    handler without any failure, so a collision is rejected here instead.
    """
    existing = owner.handler.funcs.get(domains)
    assert existing is None, (
        f"{handler.__name__!r} collides with the registered exact handler {existing.__name__!r} "
        f"on {owner!r}: both dispatch on {domains!r}, so one would silently replace the other. "
        f"Declare exact leaf domains for each handler (POL-TYPE-019)."
    )

    def evaluate(*engine_values, assumptions: Proposition):
        arguments = tuple(_owned_argument(value) for value in engine_values)
        property_category = _property_categories.get(owner)
        if property_category is not None and len(arguments) == 1 and is_placed(arguments[0], property_category):
            return True
        if owner in _identity_predicates and len(arguments) == 2 and arguments[0] is arguments[1]:
            return True
        result = handler(*arguments, assumptions=assumptions)
        if result is True and property_category is not None:
            refine(arguments[0], property_category)
        return None if result is Unknown else result

    evaluate.__name__ = handler.__name__
    owner.register(*domains)(evaluate)


def register_query_handler(query: Query, handler: QueryHandler) -> None:
    """Register one exact typed-query evaluator with private Plum dispatch."""
    domains = tuple(
        Annotated[domain | CategoryPoint, Is[partial(_matches_handler_domain, domain)]]
        for domain in _handler_domains(handler)
    )
    assert len(domains) == query._arity, f"{handler!r} has the wrong arity for {query!r}"
    if query not in _query_dispatchers:
        dispatcher = Dispatcher()

        def evaluate(*arguments):
            raise NotFoundLookupError(f"no exact evaluator for {query!r}{arguments!r}")

        evaluate.__name__ = "evaluate"
        evaluator = dispatcher.abstract(evaluate)
        _query_dispatchers[query] = dispatcher, evaluator
    dispatcher, evaluator = _query_dispatchers[query]

    def evaluate(*arguments):
        return handler(*arguments)

    evaluate.__name__ = "evaluate"
    dispatcher.multi(domains)(evaluate)


def ask_query(application: AppliedQuery) -> Answer:
    """Evaluate a category-owned typed query without entering SymPy's Boolean system."""
    query = application.query()
    registered = _query_dispatchers.get(query)
    if registered is None:
        return Unknown
    _, evaluator = registered
    try:
        value = evaluator(*application.arguments())
    except NotFoundLookupError:
        return Unknown
    if value is Unknown:
        return Unknown
    assert value in query.result_category()
    return value


def assume_property(proposition: Proposition) -> None:
    """Apply the same-object refinement attached to a positive property assumption."""
    applications = proposition.args if isinstance(proposition, And) else (proposition,)
    for application in applications:
        if not isinstance(application, AppliedPredicate):
            continue
        category = _property_categories.get(application.function)
        if category is None or len(application.arguments) != 1:
            continue
        argument = _owned_argument(application.arguments[0])
        assert isinstance(argument, CategoryPoint)
        refine(argument, category)
