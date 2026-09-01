"""R3 acceptance for properties, typed queries, refinement, pullbacks, and dispatch."""

from sage.rings.integer import Integer

from __future__ import annotations

from sage.misc.unknown import Unknown
from sympy import Predicate as SymPyPredicate
from sympy.assumptions import global_assumptions
from sympy.assumptions.assume import AppliedPredicate
from sympy.logic.boolalg import Boolean

from sage_categories.cat.category import Axiom, Cat, Category, Predicate, Query, ask, assume
from sage_categories.cat.functors import Fun
from sage_categories.cat.predicates import AppliedQuery
from sage_categories.cat.properties import FullSubcategory, PredicateSubcategory


class Tiny(Category[[], []]):
    """Minimal set-like fixture with one object property and one typed query."""

    Special = Axiom()

    class ObjectType:
        def __init__(self, value):
            self._value = value
            super().__init__()

        def value(self):
            return self._value

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self):
        self._objects = {}
        super().__init__()
        self.Measure = Query("measure", 1, self)

        def measure(value: Tiny.ObjectType):
            return self(abs(value.value())) if value.value() != 99 else Unknown

        self.Measure.register_handler(measure)

    def __call__(self, value):
        if value not in self._objects:
            self._objects[value] = self.ObjectType(category=self, data=value)
        return self._objects[value]


class SpecialTiny(PredicateSubcategory):
    _base_category_class_and_axiom = (Tiny, "Special")

    def _predicate(self, candidate):
        if candidate.value() == 99:
            return Unknown
        return candidate.value() >= 0


class TinySubcategory(FullSubcategory, Tiny):
    """A named full subcategory used to prove functorial property inheritance."""


def test_generated_property_application_and_three_valued_ask() -> None:
    tiny = Tiny()
    positive, negative, undecided = tiny(3), tiny(-2), tiny(99)
    proposition = positive.is_special()
    assert Predicate is SymPyPredicate
    assert isinstance(proposition, Boolean)
    assert all(isinstance(part, AppliedPredicate) for part in proposition.args)
    assert isinstance(proposition | negative.is_special(), Boolean)
    assert proposition is tiny.Special().membership_proposition(positive)
    assert ask(proposition) is True
    assert ask(negative.is_special()) is False
    assert ask(undecided.is_special()) is Unknown
    assert ask(positive.is_special() | negative.is_special()) is True
    assert ask(~negative.is_special()) is True


def test_positive_evidence_uses_same_object_refinement() -> None:
    tiny = Tiny()

    exact = tiny(4)
    exact_identity = id(exact)
    assert ask(exact.is_special()) is True
    assert id(exact) == exact_identity
    assert exact in tiny.Special()

    assumed = tiny(99)
    assumed_identity = id(assumed)
    proposition = assumed.is_special()
    assert ask(proposition) is Unknown
    assume(proposition)
    assert id(assumed) == assumed_identity
    assert ask(proposition) is True
    assert assumed in tiny.Special()

    constructed = tiny(-5)
    constructed_identity = id(constructed)
    assert tiny.Special()(constructed) is constructed
    assert id(constructed) == constructed_identity
    assert constructed in tiny.Special()


def test_sympy_active_assumptions_own_composite_propositions() -> None:
    tiny = Tiny()
    proposition = tiny(-1).is_special() | tiny(99).is_special()
    assert ask(proposition) is Unknown
    assume(proposition)
    assert proposition in global_assumptions
    assert ask(proposition) is True
    global_assumptions.discard(proposition)


def test_typed_query_has_exact_result_category_and_unknown_is_not_a_value() -> None:
    tiny = Tiny()
    query = tiny.Measure(tiny(-2))
    answer = ask(query)
    assert answer is tiny(2)
    assert answer in tiny
    assert ask(tiny.Measure(tiny(99))) is Unknown
    assert isinstance(query, AppliedQuery)
    assert not isinstance(query, Boolean)


def test_property_monomorphism_and_inverse_image_are_retained_categorical_data() -> None:
    tiny = Tiny()
    property_category = tiny.Special()
    (monomorphism,) = property_category.structure_functors()
    assert monomorphism.domain() is property_category
    assert monomorphism.codomain() is tiny
    assert monomorphism in Fun(property_category, tiny).Monomorphisms().Isofibrations().Full()

    identity = Fun(tiny, tiny)(lambda value: value, lambda morphism: morphism)
    inverse = identity.inverse_image(property_category)
    assert inverse.defining_functor() is identity
    assert inverse.target_subcategory() is property_category

    value = tiny(7)
    identity_before = id(value)
    assert inverse(value) is value
    assert id(value) == identity_before
    assert value in inverse

    presentation = Cat().Pullbacks().presentation(inverse)
    shape = presentation.diagram.domain()
    assert presentation.diagram.on_object(shape(0)) is tiny
    assert presentation.diagram.on_object(shape(1)) is property_category
    assert presentation.transformation.component(shape(0)).domain() is inverse
    assert presentation.transformation.component(shape(0)).codomain() is tiny
    assert presentation.transformation.component(shape(1)).domain() is inverse
    assert presentation.transformation.component(shape(1)).codomain() is property_category


def test_inherited_property_is_the_inverse_image_along_the_defining_functor() -> None:
    tiny = Tiny()
    subcategory = TinySubcategory(tiny)
    defining_functor = subcategory.structure_functors()[0]
    inherited = subcategory.Special()
    assert inherited.defining_functor() is defining_functor
    assert inherited.target_subcategory() is tiny.Special()
    assert inherited.subcategory_monomorphism().domain() is inherited
    assert inherited.subcategory_monomorphism().codomain() is subcategory
    assert inherited.target_projection().domain() is inherited
    assert inherited.target_projection().codomain() is tiny.Special()


def test_sympy_owns_each_property_predicate_and_its_handler() -> None:
    first, second = Tiny(), Tiny()
    first_predicate = first.Special().predicate()
    second_predicate = second.Special().predicate()
    assert isinstance(first_predicate, SymPyPredicate)
    assert isinstance(second_predicate, SymPyPredicate)
    assert first_predicate is not second_predicate

    positive = first_predicate(first(1))
    negative = second_predicate(second(-1))
    assert isinstance(positive, AppliedPredicate)
    assert isinstance(negative, AppliedPredicate)
    assert positive.function is first_predicate
    assert negative.function is second_predicate
    assert ask(positive) is True
    assert ask(negative) is False


for name, value in tuple(globals().items()):
    if name.startswith("test_"):
        value()
