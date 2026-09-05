"""R3 witness for public property, query, refinement, and pullback contracts."""

from __future__ import annotations

import pytest
from sage.all import Unknown
from sympy.assumptions.assume import AppliedPredicate
from sympy.logic.boolalg import Boolean

from sage_categories.cat.category import Axiom, Cat, Category, Predicate, Proposition, Query, ask, assume
from sage_categories.cat.functors import Fun
from sage_categories.cat.predicates import AppliedQuery, negation, retract


class SpecialPredicate(Predicate):
    """The proposition declared by ``Tiny.Special``."""

    name = "special"


special = SpecialPredicate()


class Tiny(Category):
    """A category that declares one object property and one typed query."""

    class ObjectType:
        def __init__(self, value: int) -> None:
            self._value = value

        def value(self) -> int:
            return self._value

        def positive_square_root(self) -> AppliedQuery:
            return self.category()._positive_square_root(self)

    class ElementType:
        pass

    class MorphismType:
        pass

    def _special(self, candidate: "Tiny.ObjectType") -> Boolean:
        return special(candidate)

    Special = Axiom(_special)

    def __init__(self) -> None:
        self._positive_square_root = Query("positive_square_root", 1, self)

        def evaluate(candidate: Tiny.ObjectType) -> Tiny.ObjectType:
            match candidate.value():
                case 4:
                    return self(2)
            return Unknown

        self._positive_square_root.register_handler(evaluate)

    def __call__(self, value: int) -> "Tiny.ObjectType":
        return self.ObjectType(value)


def _decide_special(candidate: Tiny.ObjectType, assumptions: Proposition) -> bool | None:
    match candidate.value():
        case 99:
            return None
        case value if value >= 0:
            return True
    return False


special.register_handler(_decide_special)


class LightEnoughPredicate(Predicate):
    """The predicate declared by ``Tokens.Light``."""

    name = "light_enough"


light_enough = LightEnoughPredicate()


class BalancedPredicate(Predicate):
    """A leaf predicate uses the exported ``Predicate`` base."""

    name = "balanced"


balanced = BalancedPredicate()


class Tokens(Category):
    """A leaf-shaped category with axiom declarations only."""

    class ObjectType:
        def __init__(self, weight: int) -> None:
            self._weight = weight

        def weight(self) -> int:
            return self._weight

    class ElementType:
        pass

    class MorphismType:
        pass

    def _light(self, token: "Tokens.ObjectType") -> Boolean:
        return light_enough(token)

    Light = Axiom(_light)

    def _heavy(self, token: "Tokens.ObjectType") -> Boolean:
        return ~token.is_light()

    Heavy = Axiom(_heavy)
    Tagged = Axiom()

    def __call__(self, weight: int) -> "Tokens.ObjectType":
        return self.ObjectType(weight)


def _decide_light(candidate: Tokens.ObjectType, assumptions: Proposition) -> bool | None:
    match candidate.weight():
        case weight if 0 <= weight <= 10:
            return True
        case weight if weight >= 0:
            return False
    return None


def _decide_balanced(candidate: Tokens.ObjectType, assumptions: Proposition) -> bool | None:
    match candidate.weight():
        case weight if weight >= 0 and weight % 2 == 0:
            return True
        case weight if weight >= 0:
            return False
    return None


light_enough.register_handler(_decide_light)
balanced.register_handler(_decide_balanced)


def test_axiom_application_has_three_valued_public_semantics() -> None:
    tiny = Tiny()
    positive, negative, undecided = tiny(3), tiny(-2), tiny(99)
    proposition = positive.is_special()

    assert isinstance(tiny.Special().predicate(), Predicate)
    assert isinstance(proposition, Boolean)
    assert all(isinstance(part, AppliedPredicate) for part in proposition.args)
    assert proposition is tiny.Special().membership_proposition(positive)
    assert ask(proposition) is True
    assert ask(negative.is_special()) is False
    assert ask(undecided.is_special()) is Unknown
    assert ask(proposition | negative.is_special()) is True


def test_positive_evidence_refines_the_same_public_value() -> None:
    tiny = Tiny()
    exact = tiny(4)
    identity = id(exact)
    assert ask(exact.is_special()) is True
    assert id(exact) == identity
    assert exact.category() is tiny.Special()
    assert exact in tiny.Special()

    undecided = tiny(99)
    identity = id(undecided)
    assume(undecided.is_special())
    assert id(undecided) == identity
    assert undecided.category() is tiny.Special()
    assert undecided in tiny.Special()


def test_property_construction_and_query_use_public_surfaces() -> None:
    tiny = Tiny()
    constructed = tiny.Special()(5)
    query = tiny(4).positive_square_root()
    answer = ask(query)

    assert constructed.value() == 5
    assert constructed.category() is tiny.Special()
    assert constructed in tiny.Special()
    assert answer.category() is tiny
    assert answer.value() == 2

    other = Tiny()
    other_answer = ask(other(4).positive_square_root())
    assert other_answer.category() is other
    assert other_answer.value() == 2
    assert ask(tiny(2).positive_square_root()) is Unknown
    assert isinstance(query, AppliedQuery)
    assert not isinstance(query, Boolean)


def test_predicate_subclassing_uses_owned_sympy_atoms() -> None:
    tokens = Tokens()
    even, odd, unsigned = tokens(4), tokens(5), tokens(-1)
    proposition = balanced(even)

    assert isinstance(proposition, AppliedPredicate)
    assert proposition.function is balanced
    assert proposition == balanced(even)
    assert proposition != balanced(odd)
    assert ask(proposition) is True
    assert ask(balanced(odd)) is False
    assert ask(balanced(unsigned)) is Unknown
    with pytest.raises(TypeError):
        bool(balanced(unsigned))
    assert ask(balanced(even) & ~balanced(odd)) is True


def test_exact_handler_dispatch_and_sympy_errors_keep_their_meaning() -> None:
    tiny = Tiny()

    class MarkedPredicate(Predicate):
        name = "marked"

    marked = MarkedPredicate()

    def positive(candidate: Tiny.ObjectType, assumptions: Proposition) -> bool | None:
        return candidate.value() > 0

    def undecided(candidate: Tiny.ObjectType, assumptions: Proposition) -> bool | None:
        return None

    marked.register_handler(positive)
    assert ask(marked(tiny(2))) is True
    with pytest.raises(AssertionError):
        marked.register_handler(undecided)

    proposition = balanced(Tokens()(7))
    assume(proposition)
    assume(negation(proposition))
    with pytest.raises(ValueError):
        ask(proposition)
    retract(proposition)
    retract(negation(proposition))
    assert ask(proposition) is False


def test_equality_uses_the_category_owned_predicate() -> None:
    tokens, other = Tokens(), Tokens()
    here, there = tokens(2), other(2)

    assert tokens.equality() is not other.equality()
    assert (here == there).function is tokens.equality()
    assert (there == here).function is other.equality()
    assert ask(here == here) is True
    assert ask(here != here) is False
    assert ask(here == there) is Unknown


def test_axioms_propagate_along_retained_structure_functors() -> None:
    tokens = Tokens()
    reached = tokens.Light()
    light = reached.Light()

    assert light is reached
    comparison = next(functor for functor in reached.selected_functors() if functor.codomain() is tokens)
    assert comparison in Fun(reached, tokens).Monomorphisms().Isofibrations().Full()

    token = reached(2)
    assert ask(token.is_light()) is True
    assert token in light
    assert token.category() is light


def test_narrowed_construction_containment_is_retained_and_navigable() -> None:
    cat = Cat()
    apex = cat.Products()((cat.Simplex(1), cat.Simplex(2)))
    shape = apex.index_category()
    limits, products = cat.Limits(shape), cat.Products()

    # The apex is placed once, in its shape family, and reaches the union of product
    # families along the declared containment ``Limits(J) -> Products()``.
    assert apex.category() is limits
    assert apex in products
    comparison = next(functor for functor in limits.selected_functors() if functor.codomain() is products)
    assert comparison in Fun(limits, products).Monomorphisms().Isofibrations().Full()
    assert next(functor for functor in limits.selected_functors() if functor.codomain() is products) is comparison
    assert cat.Limits(shape) is cat.Limits(shape)
    assert cat.Limits(shape) is not cat.Limits(cat.Simplex(2))

    narrowed = cat.Inhabited()
    narrowed_limits, narrowed_products = narrowed.Limits(shape), narrowed.Products()
    comparison = next(
        functor for functor in narrowed_limits.selected_functors() if functor.codomain() is narrowed_products
    )
    assert comparison in Fun(narrowed_limits, narrowed_products).Monomorphisms().Isofibrations().Full()

    narrowed_colimits, narrowed_coproducts = narrowed.Colimits(shape), narrowed.Coproducts()
    comparison = next(
        functor for functor in narrowed_colimits.selected_functors() if functor.codomain() is narrowed_coproducts
    )
    assert comparison in Fun(narrowed_colimits, narrowed_coproducts).Monomorphisms().Isofibrations().Full()

    coproduct_apex = cat.Coproducts()((cat.Simplex(1), cat.Simplex(2)))
    coproduct_shape = coproduct_apex.index_category()
    colimits, coproducts = cat.Colimits(coproduct_shape), cat.Coproducts()
    comparison = next(functor for functor in colimits.selected_functors() if functor.codomain() is coproducts)
    assert comparison in Fun(colimits, coproducts).Monomorphisms().Isofibrations().Full()
    assert coproduct_apex in colimits
    assert coproduct_apex in coproducts


def test_opposite_narrowing_constructs_into_each_selected_root() -> None:
    for dual_first in (True, False):
        tokens = Tokens()
        first, second = tokens.Light(), tokens.Tagged()
        if dual_first:
            both = tokens.op().intersection((first.op(), second.op()))
            original = tokens.intersection((first, second))
        else:
            original = tokens.intersection((first, second))
            both = original.op()
        assert original.op() is both
        assert both.op() is original
        assert tokens.op().intersection((second.op(), first.op())) is both
        value = both(5)
        assert value.weight() == 5
        assert value.category() is both
        assert value in both
        assert value in first.op()
        assert value in second.op()


def test_functor_property_axioms_have_retained_containments() -> None:
    tiny = Tiny()
    identity = Cat().morphism_category(1)(Cat(), Cat()).one()
    proposition = identity.is_fully_faithful()
    assert proposition is Fun(Cat(), Cat()).FullyFaithful().membership_proposition(identity)
    assert ask(proposition) is True

    endofunctors = Fun(tiny, tiny)
    for source, target in (
        (endofunctors.Monomorphisms(), endofunctors.Faithful()),
        (endofunctors.Fibrations(), endofunctors.Isofibrations()),
        (endofunctors.Opfibrations(), endofunctors.Isofibrations()),
    ):
        comparison = next(functor for functor in source.selected_functors() if functor.codomain() is target)
        assert comparison in Fun(source, target).Monomorphisms().Isofibrations().Full()


def test_shape_indexed_functor_properties_are_public_axioms() -> None:
    tiny = Tiny()
    shape, other = Cat().Simplex(1), Cat().Simplex(2)
    preserves, creates = Fun.PreservesLimits(shape), Fun.CreatesLimits(shape)
    functors = Fun(tiny, tiny)

    assert preserves.ambient() is Fun
    assert creates.ambient() is Fun
    assert Fun.PreservesLimits(shape) is preserves
    assert Fun.PreservesLimits(other) is not preserves
    assert functors.CreatesLimits(shape) is creates(tiny, tiny)

    identity = Cat().morphism_category(1)(Cat(), Cat()).one()
    created_at_shape = identity.is_creates_limits(shape)
    created_at_other = identity.is_creates_limits(other)
    assert created_at_shape is Fun(Cat(), Cat()).CreatesLimits(shape).membership_proposition(identity)
    assert created_at_other is Fun(Cat(), Cat()).CreatesLimits(other).membership_proposition(identity)
    assert created_at_shape != created_at_other


for name, value in tuple(globals().items()):
    if name.startswith("test_"):
        value()
