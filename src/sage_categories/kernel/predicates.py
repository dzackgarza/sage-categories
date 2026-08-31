"""Implement owned predicates, propositions, typed queries, and evaluation."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from inspect import Parameter, signature
from typing import TYPE_CHECKING, Any, get_origin

from plum import Dispatcher, NotFoundLookupError, Signature as DispatchSignature

from sage.categories.category_with_axiom import uncamelcase
from sage.misc.cachefunc import cached_method
from sage.structure.coerce_dict import MonoDict, TripleDict
from sympy import Dummy, Integer, Predicate as EnginePredicate, Q, S, sympify
from sympy.assumptions import global_assumptions
from sympy.assumptions.assume import AppliedPredicate as EngineApplied
from sympy.core.basic import Basic
from sympy.logic.boolalg import And, Implies, Not, Or

from sage_categories.kernel.compiler import install_on_declaration
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.refinement import is_placed, refine
from sage_categories.kernel.roles import CategoryPoint, Role, category_of, role_of

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.cat.properties import PropertySubcategory

__all__ = [
    "Answer",
    "Axiom",
    "Applied",
    "AppliedPredicate",
    "AppliedQuery",
    "Argument",
    "Connective",
    "EqualityPredicate",
    "Predicate",
    "PropertyPredicate",
    "Proposition",
    "Query",
    "ask",
    "assume",
    "conjunction",
    "disjunction",
    "established",
    "implication",
    "negation",
    "retract",
]

# What a predicate is applied to: owned values, and the integer convenience of the
# cardinal and ordinal orders.  The candidate of an equality proposition enters
# through ``EqualityPredicate`` alone (POL-TYPE-004).
type Argument = CategoryPoint | int

# What ``ask`` returns: a decision for a proposition, and an owned object of the
# declared result category for a query such as ``cardinality()``. Sage
# ``Unknown`` is the one unresolved answer of both and is an object of neither result
# category (``specs/cardinality.md``, "Integration with ``Sets()``").
type Answer = Decision | CategoryPoint

# An exact evaluation case on a declared semantic domain; its arity is the
# predicate's, and each owning category declares its exact parameter types.
type Handler = Callable[..., Answer]


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


def _dispatch_annotation(annotation: object, namespace: dict[str, object]) -> object:
    """Resolve one exact-handler annotation for Plum when it is runtime-visible.

    Theory-facing names deliberately kept under ``TYPE_CHECKING`` are not imported into
    the kernel merely for dispatch; those cases remain unrestricted and validate their
    mathematical domain in the handler itself.
    """
    if annotation is Parameter.empty:
        return object
    if not isinstance(annotation, str):
        return annotation
    if any(role_name in annotation for role_name in (".ObjectType", ".ElementType", ".MorphismType")):
        return object
    if annotation.split(".", 1)[0] not in namespace:
        return object
    if "[" in annotation:
        return namespace[annotation.split("[", 1)[0]]
    resolved = eval(annotation, namespace)
    if hasattr(resolved, "__parameters__") and resolved.__parameters__:
        return CategoryPoint
    return get_origin(resolved) or resolved


def _dispatch_signature(handler: Handler) -> DispatchSignature:
    parameters = signature(handler).parameters.values()
    assert hasattr(handler, "__globals__"), f"{handler!r} is not a function with a runtime annotation namespace"
    namespace = handler.__globals__
    return DispatchSignature(*(_dispatch_annotation(parameter.annotation, namespace) for parameter in parameters))


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
        self._handlers: list[tuple[Handler, Handler, DispatchSignature]] = []
        self._symbol = Dummy(name)

    def name(self) -> str:
        return self._name

    def arity(self) -> int:
        return self._arity

    def records_decisions(self) -> bool:
        return self._records_decisions

    def register_handler(self, handler: Handler) -> None:
        """Register an exact case; Plum owns specificity and ambiguity at evaluation."""
        def invoke(*arguments):
            return handler(*arguments)

        assert hasattr(handler, "__name__"), f"{handler!r} is not a named exact case"
        invoke.__name__ = handler.__name__
        self._handlers.append((handler, invoke, _dispatch_signature(handler)))

    def handlers(self) -> tuple[Handler, ...]:
        return tuple(handler for handler, _, _ in self._handlers)

    def resolved_handlers(self, arguments: tuple[Argument, ...]):
        """Yield Plum-selected cases, retrying only when a selected case declines.

        ``Unknown`` means the selected exact case declines. The caller then asks this
        generator for another case; the one declined implementation has been removed,
        and Plum resolves among the remaining signatures again. The kernel never compares
        signatures or resolves an ambiguity itself.
        """
        remaining = list(self._handlers)
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

    @cached_method
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


class Query(Predicate):
    """A typed query with one exact mathematical result category.

    ``cardinality()`` and ``cofinality()`` are the current cases. They are not total
    and exact on their full declared domain. An exact handler returns an object of
    the result category. ``ask()`` returns Sage ``Unknown`` when no handler applies.
    """

    def __init__(self, name: str, arity: int, records_decisions: bool, result_category: Category) -> None:
        super().__init__(name, arity, records_decisions)
        self._result_category = result_category

    def result_category(self) -> Category:
        """The category whose objects are the exact answers of this predicate."""
        return self._result_category

    def __call__(self, *arguments: Argument) -> AppliedQuery:
        assert len(arguments) == self.arity(), f"{self.name()} has arity {self.arity()}"
        return AppliedQuery(self, arguments)


class Applied:
    """An unevaluated proposition or typed query."""

    def __bool__(self) -> bool:
        # SymPy ``Relational.__bool__`` is the reference for an unevaluated proposition.
        raise TypeError(f"cannot determine truth value of {self!r}; use ask()")


class Proposition(Applied):
    """A truth-valued application."""

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


class AppliedQuery(Applied):
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

    def __repr__(self) -> str:
        return f"{self._query}({', '.join(map(repr, self._arguments))})"


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
    if part is Unknown:
        return Dummy("undecided")
    if isinstance(part, Proposition):
        return part.engine_value()
    return sympify(part)


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


def _cache_key(applied: AppliedPredicate | AppliedQuery) -> tuple[Predicate, CategoryPoint, CategoryPoint] | None:
    """The identity key of a recordable answer."""
    arguments = applied.arguments()
    owner = applied.predicate() if isinstance(applied, AppliedPredicate) else applied.query()
    if not owner.records_decisions():
        return None
    if len(arguments) not in (1, 2):
        return None
    first, second = arguments[0], arguments[-1]
    if not isinstance(first, CategoryPoint) or not isinstance(second, CategoryPoint):
        return None
    return owner, first, second


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
    for handler in predicate.resolved_handlers(arguments):
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
    """The engine value of ``proposition`` with every decided leaf replaced by its truth value.

    An undecided leaf stays its own engine expression, which is unique to its predicate
    and arguments, so SymPy's boolean algebra combines the parts: it reads ``True or P``
    as ``True`` and leaves ``P or Q`` undecided.  That algebra is the only truth table
    involved, and it is SymPy's.
    """
    representable = isinstance(proposition, Connective) or (
        isinstance(proposition, AppliedPredicate) and all(map(_representable, proposition.arguments()))
    )
    if representable and proposition.engine_value() in global_assumptions:
        return S.true
    if proposition is Unknown:
        return Dummy("undecided")
    match proposition:
        case bool():
            return sympify(proposition)
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
            if decision is not Unknown:
                return sympify(decision)
            if not all(map(_representable, proposition.arguments())):
                # An equality candidate may be neither owned nor an integer
                # (``POL-TYPE-004``), and the session carries no symbol for it, so the
                # leaf is undecided in the same way an ``Unknown`` part is.
                return Dummy("undecided")
            return proposition.engine_value()
    raise TypeError(f"{proposition!r} is not a proposition")


def _ask_query(applied: AppliedQuery) -> Answer:
    """Return the first exact answer, or Sage ``Unknown``."""
    query = applied.query()
    key = _cache_key(applied)
    if key is not None and key in _decisions:
        return _decisions[key]
    for handler in query.resolved_handlers(applied.arguments()):
        value = handler(*applied.arguments())
        if value is Unknown:
            continue
        assert value in query.result_category(), (
            f"an exact case answered {applied!r} with {value!r}, which is not an object of {query.result_category()!r}"
        )
        if key is not None:
            _decisions[key] = value
        return value
    return Unknown


def ask(application: Decision | Proposition | AppliedQuery) -> Answer:
    """Evaluate a proposition or typed query."""
    if isinstance(application, AppliedQuery):
        return _ask_query(application)
    value = _decided(application)
    if value is S.true:
        return True
    if value is S.false:
        return False
    return Unknown


def established(proposition: Decision | Proposition) -> bool:
    """Whether ``proposition`` is decided affirmatively, which is what fires an exact rule.

    Not the mathematical question: that is ``ask(proposition)``, and it can be
    ``Unknown``.  A rule whose hypothesis is a theorem's premise fires only where that
    premise is established, and an undecided hypothesis does not supply it, so the
    procedure falls through to its next rule and finally to ``Unknown``.  Whether a
    premise is established is two-valued by construction (POL-ASSUME-015), in the same
    way category placement is.

    A caller that must have an answer asks instead and asserts the answer is decided
    (POL-ASSUME-014); a caller that composes answers builds one proposition and asks it
    once (POL-ASSUME-013).  This is neither: it selects a rule.
    """
    decision = ask(proposition)
    return isinstance(decision, bool) and decision


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


def retract(proposition: AppliedPredicate) -> None:
    """Withdraw ``proposition`` from the active session, so ``ask`` decides it from the mathematics alone.

    This is the inverse of ``assume`` for a hypothesis that records no category
    placement, which is what a global set-theoretic hypothesis such as the generalized
    continuum hypothesis is.  A property assumption also refines its argument into the
    property's category, and placement is permanent, so it does not retract.
    """
    assert not isinstance(proposition.predicate(), PropertyPredicate), f"{proposition!r} refined a category, which no retraction undoes"
    global_assumptions.discard(proposition.engine_value())


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
    one declaration, as the narrowing of ``D`` by ``C.Finite()``; it states no class,
    predicate, constructor, or transport of its own (POL-CAT-084).

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
        self._constructed: MonoDict = MonoDict()

    def __set_name__(self, declaring_class: type[Category], name: str) -> None:
        self._declaring_class = declaring_class
        self._name = name
        _derive_application(self)

    def application_name(self) -> str:
        """``is_p()``: the application generated from this axiom's identifier and nothing else (D89, POL-CAT-060)."""
        return _application_name(self._name)

    def application_owner(self) -> type[CategoryPoint]:
        """The role class the application is written onto: the object declaration of the declaring category class.

        A role *is* the name a category class writes for that mathematical kind
        (``Category.local_role_class``, POL-KERNEL-028), so this reads that one
        declaration.  ``Mor(C)`` writes ``MorphismOfCategory``, because an object of it is
        a morphism of an arbitrary ``C``; ``Fun`` writes ``Cat().MorphismType``; ``Cat()``
        writes ``CategoryDeclaration``.
        """
        assert hasattr(self._declaring_class, Role.OBJECT.value), (
            f"{self._declaring_class.__name__} writes no {Role.OBJECT.value} declaration"
        )
        declared = getattr(self._declaring_class, Role.OBJECT.value)
        assert declared is not None, (
            f"{self._declaring_class.__name__} writes no {Role.OBJECT.value} declaration, so {self!r} has no role "
            f"class to write {self.application_name()}() onto (POL-CAT-057)"
        )
        return declared

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

    def subcategory(self, category: Category) -> Category:
        """``category.P()``: one property subcategory per category value."""
        if category not in self._constructed:
            self._constructed[category] = self._construct(category)
        return self._constructed[category]

    def _construct(self, category: Category) -> Category:
        """The narrowing of a declared subcategory, else the implementation of this axiom."""
        if category.has_ambient():
            defining_functor = category.structure_functors()[0]
            return defining_functor.inverse_image(self._declared_on(defining_functor.codomain()))
        containing = tuple(axiom._declared_on(category) for axiom in self._full_subcategory_of)
        return (self._implementation or _property_subcategory())(category, self._name, containing)

    def _declared_on(self, category: Category) -> Category:
        """``category.P()``, through the accessor that category declares for this axiom.

        A category can build the subcategory itself -- ``Fun`` builds its property
        categories eagerly, before any of them can be constructed on demand -- and that
        declaration is then the one owner of ``C.P()``.  The axiom name is the name the
        category writes, exactly as a role is (``Category.local_role_class``,
        POL-KERNEL-028), so this reads the declaration rather than probing for it.
        """
        return getattr(category, self._name)()

    def __repr__(self) -> str:
        return f"{self._declaring_class.__name__}.{self._name}"


# The axiom each derived application was compiled from, by the class and name it was
# installed under.  A second axiom reaching one spelling on one owner is the collision
# ``specs/undecidable-properties.md`` requires the kernel to reject.
_derived_applications: dict[tuple[type[CategoryPoint], str], Axiom] = {}


def _application_name(identifier: str) -> str:
    """``"FullyFaithful"`` gives ``"is_fully_faithful"``."""
    return "is_" + uncamelcase(identifier, "_")


def _derive_application(axiom: Axiom) -> None:
    """Compile ``x.is_P()`` from the axiom's identifier and declaring class (POL-CAT-060, D89).

    The application returns the containment proposition and evaluates nothing; a leaf
    writes no such method and forwards none (``specs/undecidable-properties.md``,
    "The exact architectural rule").

    Which property subcategory it asks is read off the value's own placement.  The
    narrowing base of that placement is the category the axiom is declared on, so a set
    reaches ``Sets().Finite()`` and a morphism ``Mor(C).Isomorphisms()`` from the one
    declaration, and a value already refined into a property reaches the same one
    (POL-CAT-084).  A base that is itself a full subcategory -- ``Mor(C)(A, B)`` is the
    one -- returns a narrowing there, and the property owning the predicate is its root,
    which is what the predicate names.
    """
    name, owner = axiom.application_name(), axiom.application_owner()

    def application(value: CategoryPoint) -> Proposition:
        placement = category_of(value, role_of(value)).narrowing_base()
        return axiom._declared_on(placement).predicate().category().membership_proposition(value)

    application.__name__ = name
    application.__qualname__ = f"{owner.__name__}.{name}"
    application.__doc__ = f"The proposition that this value is an object of ``{axiom!r}()`` (POL-CAT-060)."
    known = _derived_applications.get((owner, name))
    assert known is None or known is axiom, f"{known!r} and {axiom!r} both spell their application {owner.__name__}.{name}; name the two properties distinctly"
    assert known is not None or name not in vars(owner), (
        f"{owner.__name__} declares {name!r} itself, so {axiom!r} cannot compile its application there"
    )
    _derived_applications[(owner, name)] = axiom
    # The kernel writes the compiled method onto the declaration and onto the class of
    # every node already compiled from it, as ``install_level_shift`` writes the
    # point-inherited spellings onto theirs (``kernel/compiler.py``).
    install_on_declaration(owner, name, application)
