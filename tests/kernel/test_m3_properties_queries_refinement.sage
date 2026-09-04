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

    class ElementType:
        pass

    class MorphismType:
        pass

    def _special(self, candidate: Tiny.ObjectType) -> Boolean:
        return special(candidate)

    Special = Axiom(_special)

    def __call__(self, value: int) -> Tiny.ObjectType:
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

    def _light(self, token: Tokens.ObjectType) -> Boolean:
        return light_enough(token)

    Light = Axiom(_light)

    def _heavy(self, token: Tokens.ObjectType) -> Boolean:
        return ~token.is_light()

    Heavy = Axiom(_heavy)
    Tagged = Axiom()

    def __call__(self, weight: int) -> Tokens.ObjectType:
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
    shape = Cat().Simplex(1)
    query = shape.morphism_set()
    undecided_query = Query("measure", 1, tiny)(tiny(-2))
    answer = ask(query)

    assert constructed.value() == 5
    assert constructed.category() is tiny.Special()
    assert constructed in tiny.Special()
    assert answer in query.query().result_category()
    assert ask(undecided_query) is Unknown
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
    inclusion = Fun(tokens, tokens).Monomorphisms().Isofibrations().Full()(
        lambda value: value,
        lambda morphism: morphism,
    )
    light = inclusion.inverse_image(tokens.Light())

    assert light is inclusion.inverse_image(tokens.Light())
    comparison = next(functor for functor in light.selected_functors() if functor.codomain() is tokens.Light())
    assert comparison in Fun(light, tokens.Light()).Monomorphisms().Isofibrations().Full()

    token = tokens(2)
    assert ask(token.is_light()) is True
    assert token in light
    assert token.category() is light


def test_narrowed_construction_containment_is_retained_and_navigable() -> None:
    cat = Cat()
    apex = cat.Products()((cat.Simplex(1), cat.Simplex(2)))
    shape = apex.index_category()
    limits, products = cat.Limits(shape), cat.Products()

    assert apex.category() is products
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

    coproduct_apex = cat.Coproducts()((cat.Simplex(1), cat.Simplex(2)))
    coproduct_shape = coproduct_apex.index_category()
    colimits, coproducts = cat.Colimits(coproduct_shape), cat.Coproducts()
    comparison = next(functor for functor in colimits.selected_functors() if functor.codomain() is coproducts)
    assert comparison in Fun(colimits, coproducts).Monomorphisms().Isofibrations().Full()
    assert coproduct_apex.category() is coproducts


def test_opposite_narrowing_constructs_into_each_selected_root() -> None:
    tokens = Tokens()
    first, second = tokens.Light(), tokens.Tagged()
    both = tokens.op().intersection((first.op(), second.op()))
    value = both(5)

    assert value.category() is both
    assert value in both
    assert value in first.op()
    assert value in second.op()


def test_functor_property_axioms_have_retained_containments() -> None:
    tiny = Tiny()
    tokens = Tokens()
    inclusion = Fun(tokens, tokens).Monomorphisms().Isofibrations().Full()(
        lambda value: value,
        lambda morphism: morphism,
    )

    identity = Cat().morphism_category(1)(Cat(), Cat()).one()
    assert ask(identity.is_fully_faithful()) is True

    assert ask(inclusion.is_monomorphisms()) is True
    assert ask(inclusion.is_isofibrations()) is True
    assert ask(inclusion.is_full()) is True
    assert ask(inclusion.is_faithful()) is True

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
    functor = functors.CreatesLimits(shape)(lambda value: value, lambda morphism: morphism)
    assert ask(functor.is_creates_limits(shape)) is True
    assert ask(functor.is_creates_limits(other)) is Unknown
    assert ask(functor.is_preserves_limits(shape)) is Unknown


for name, value in tuple(globals().items()):
    if name.startswith("test_"):
        value()
