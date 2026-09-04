"""SymPy predicates, typed queries, and property axioms in ``Cat``."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING

from sympy import And, Implies, Not, Or, ask as sympy_ask
from sympy.logic.boolalg import Boolean

from sage_categories.kernel.predicates import (
    AppliedPredicate,
    OwnedPredicate as Predicate,
    ask_query,
    assume_property,
    axiom_layer,
    bind_property_predicate,
    owned_predicate,
    register_declared_case,
    register_predicate_handler,
    register_query_handler,
)
from sage_categories.kernel.sage_runtime import MonoDict, Unknown, UnknownClass, cached_method, uncamelcase

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
    "DecidingProposition",
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
    "declared_axiom",
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

# The private method an axiom declaration carries: the proposition that decides
# membership in ``C.P()``, written on the declaring category class in terms of methods
# that already exist there (D142, D148).  It is unbound when the class body reads it,
# so its first parameter is the declaring category.
type DecidingProposition = Callable[[Category, CategoryOfCategories.ElementType], Proposition]


def predicate(name: str) -> Predicate:
    """Construct one mathematical predicate as a native SymPy predicate.

    A category that needs a predicate no existing method supplies applies one of these
    (``specs/undecidable-properties.md``, "Public propositions").  The SymPy class behind
    it is the kernel's: applying it converts each owned argument to its private identity
    atom and returns the three-valued application.
    """
    return owned_predicate(name)


def property_predicate(name: str, category: Category) -> Predicate:
    """Construct the SymPy predicate owned by one property subcategory."""
    owner = predicate(name)
    bind_property_predicate(owner, category)
    return owner


def register_handler(owner: Predicate, handler: PredicateHandler) -> None:
    """Register an exact handler on a SymPy predicate."""
    register_predicate_handler(owner, handler)


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
        return ask_query(application)
    decision = sympy_ask(application)
    return Unknown if decision is None else decision


def established(application: Decision | Proposition) -> bool:
    """Whether an exact decision establishes ``application`` as true."""
    return ask(application) is True


def assume(proposition: Proposition) -> None:
    """Record a SymPy proposition and apply its positive property refinement."""
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

    ``Finite = Axiom(_finite)`` in the body of ``SetsCategory`` gives every value of that
    class the accessor ``Finite()``, whose value is the property subcategory
    ``Sets().Finite()``, and makes the private method ``_finite`` the proposition that
    decides membership in it (D142, D148; ``specs/finite-set-minimal-template.py``).  That
    method is written in terms of methods that already exist on the declaring category,
    ``X.cardinality() < aleph0``, and it returns a proposition rather than a decision:
    only ``ask()`` evaluates it, and it is registered as the exact case of the property's
    predicate on the objects of the declaring category.

    An axiom that carries no such method, ``Monomorphisms = Axiom()``, is complete as it
    stands: it makes the subcategory available, a value enters it by construction,
    declaration, or assumption, and membership is decided from that placement.  Deciding
    and declaring are two independent mechanisms and neither needs the other (D97), so
    an axiom carries the deciding proposition exactly when its mathematics computes one.

    A category ``D`` declared as a subcategory of ``C`` derives ``D.Finite()`` from that
    one declaration, as the inverse image of ``C.Finite()`` along its subcategory
    monomorphism; it states no class, predicate, constructor, or transport of its own
    (POL-CAT-084, D83).  This reaches every category ``C`` supplies the axiom to,
    ``C.P()`` among them: an axiom is a descriptor on the class that declares it, and a
    subcategory of ``C`` is not a value of that class, so ``CategoryDeclaration`` resolves
    the declaration along the ambient chain (``declared_axiom``, D77 item 4).

    A regressive functorial construction is an axiom too: ``X`` is a chosen product
    exactly when it lies in the image of the nontrivial product functor, so ``Products``,
    ``Coproducts``, ``Limits``, and ``Colimits`` are declared once on the base category
    class and every category receives them (D31, D89; Sage
    ``RegressiveCovariantConstructionCategory``, ``sage/categories/covariant_functorial_construction.py``,
    inspected 2026-09-02).  An axiom may take parameters, and its subcategory is retained
    once per category and parameter values.

    A parameter is a value of ``Cat()``, an object or a morphism of it.  ``C.Limits(J)``
    supplies the shape, an object; ``D.EssentialImage(F)`` supplies the functor whose
    essential image it is, a morphism.  D168 states the second: being a product is an
    axiom, equivalent to membership in the essential image of the nontrivial product
    functor, and axioms can be parameterized.  So the parameter that an essential image
    turns on is the functor itself, and retention by identity is what such a parameter
    needs.

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

    def __init__(
        self,
        deciding: DecidingProposition | None = None,
        *,
        full_subcategory_of: tuple[Axiom, ...] = (),
    ) -> None:
        self._deciding = deciding
        self._full_subcategory_of = full_subcategory_of
        self._implementation: type[PropertySubcategory] | None = None
        # Retained per category and parameter values, by identity (POL-SAGE-013).
        self._constructed: dict[tuple[tuple[int, CategoryOfCategories.ElementType], ...], Category] = {}

    def __set_name__(self, declaring_class: type[Category], name: str) -> None:
        self._declaring_class = declaring_class
        self._name = name
        axiom_layer().generate_application(self)

    def application_name(self) -> str:
        """``is_p()``: the application generated from this axiom's identifier and nothing else (D89, POL-CAT-060)."""
        return _application_name(self._name)

    def application_owner(self) -> type[CategoryOfCategories.ElementType] | None:
        """The role class the application is written onto: the object declaration of the declaring category class.

        A role *is* the name a category class writes for that mathematical kind
        (``Category.local_role_class``, POL-KERNEL-028), so this reads that one
        declaration.  ``Mor(C)`` writes ``MorphismOfCategory``, because an object of it is
        a morphism of an arbitrary ``C``; ``Fun`` writes ``Cat().MorphismType``; ``Cat()``
        writes ``CategoryDeclaration``.

        ``None`` for the base category class, which declares no object role of its own:
        the objects of an arbitrary category are the points of ``Cat()`` (POL-CAT-058),
        whose declaration is written after the base class exists, so its axioms install
        when that declaration is created (``AxiomLayer.install_base_applications``).
        """
        for declaring in self._declaring_class.__mro__:
            declared = vars(declaring).get("ObjectType")
            if declared is not None:
                return declared
        return None

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

    def subcategory(self, category: Category, *parameters: CategoryOfCategories.ElementType) -> Category:
        """``category.P(*parameters)``: one property subcategory per category and parameter values."""
        key = _retention_key(category, *parameters)
        if key not in self._constructed:
            self._constructed[key] = self._construct(category, *parameters)
        return self._constructed[key]

    def is_constructed(self, category: Category, *parameters: CategoryOfCategories.ElementType) -> bool:
        """Whether ``category.P(*parameters)`` is already retained; asking never constructs it.

        A construction that has to place its result in ``C.P()`` only when that
        subcategory exists asks here.  ``cat/images.py`` retains a public functor image in
        ``D.EssentialImage(F)`` for each ``F`` whose essential image someone asked for, and
        constructing one for every functor instead would build a property subcategory per
        functor application.
        """
        return _retention_key(category, *parameters) in self._constructed

    def _construct(self, category: Category, *parameters: CategoryOfCategories.ElementType) -> Category:
        """The inverse image along a declared subcategory's monomorphism, else the implementation of this axiom.

        A subcategory receives the axioms its ambient supplies and constructs the ones it
        declares itself, so the branch asks which of the two this is (D77 item 4, D83).
        ``Posets()`` is ``Relations().PartialOrder()`` and declares ``Total`` on the order
        it adds (``specs/ordered-sets.md``, "Total-order refinement"): the ambient
        supplies no such axiom, so that declaration reaches the second branch, where it
        has an owner to be constructed at.
        """
        if category.has_ambient():
            defining_functor = category.subcategory_monomorphism()
            if declared_axiom(defining_functor.codomain(), self._name) is self:
                return defining_functor.inverse_image(self._declared_on(defining_functor.codomain(), *parameters))
        containing = tuple(axiom._declared_on(category) for axiom in self._full_subcategory_of)
        constructed = (self._implementation or _property_subcategory())(category, self._name, containing, *parameters)
        if self._deciding is not None:
            self._register_deciding_proposition(constructed, category)
        return constructed

    def _register_deciding_proposition(self, subcategory: Category, category: Category) -> None:
        """Make the declared proposition the exact case of this property's predicate (D142, D148).

        The declaration supplies the semantic domain: an axiom of ``C`` is a property of
        the objects of ``C``, which is the same declaration the generated ``is_p()`` is
        written onto, so nothing reads the method's own annotation and neither can
        disagree with the other.  The method returns a proposition, so the case evaluates
        it; an undecided proposition leaves membership undecided, and a positive one
        refines the same value (``kernel/predicates.py``).
        """
        owner = self.application_owner()
        assert owner is not None, f"{self!r} decides membership of the objects of a category that declares none"
        deciding = self._deciding.__get__(category)

        def decide(candidate: CategoryOfCategories.ElementType, assumptions: Proposition) -> PredicateDecision:
            decision = ask(deciding(candidate))
            return None if decision is Unknown else decision

        decide.__name__ = self._deciding.__name__
        register_declared_case(subcategory.predicate(), owner, decide)

    def _declared_on(self, category: Category, *parameters: CategoryOfCategories.ElementType) -> Category:
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


def declared_axiom(category: Category, name: str) -> Axiom | None:
    """The axiom ``category`` supplies under ``name``, declared on it or reached from its ambient (D77 item 4).

    An axiom is a descriptor on the class that declares it, and a declared subcategory is
    a value of another class: ``C.P()`` is a ``PropertySubcategory`` and the inverse image
    along a structure functor is its own class, so ordinary attribute lookup stops at the
    first of them.  The subcategory monomorphism is what carries the axiom down (D83), so
    the walk follows it, and the name is the one the declaring category writes, exactly as
    a role is (``Category.local_role_class``, ``POL-KERNEL-028``).
    """
    declared = getattr(type(category), name, None)
    if isinstance(declared, Axiom):
        return declared
    if not category.has_ambient():
        return None
    return declared_axiom(category.subcategory_monomorphism().codomain(), name)


def _retention_key(
    category: Category,
    *parameters: CategoryOfCategories.ElementType,
) -> tuple[tuple[int, CategoryOfCategories.ElementType], ...]:
    """The category and its parameter values, by identity, holding each alive (POL-SAGE-013)."""
    return tuple((id(value), value) for value in (category, *parameters))


def _application_name(identifier: str) -> str:
    """``"FullyFaithful"`` gives ``"is_fully_faithful"``."""
    return "is_" + uncamelcase(identifier, "_")
