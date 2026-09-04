"""R3 acceptance for properties, typed queries, refinement, pullbacks, and dispatch."""

from __future__ import annotations

from sage_categories.kernel.sage_runtime import Integer

from sage_categories.kernel.sage_runtime import Unknown
from sympy import Predicate as SymPyPredicate
from sympy.assumptions import global_assumptions
from sympy.assumptions.assume import AppliedPredicate
from sympy.logic.boolalg import Boolean

from sage_categories.cat.category import Axiom, Cat, Category, Predicate, Proposition, Query, ask, assume
from sage_categories.cat.functors import Fun
import pytest

from sage_categories.cat.predicates import AppliedQuery, UnknownClass, predicate
from sage_categories.cat.properties import FullSubcategory, PredicateSubcategory
from sage_categories.kernel.refinement import is_placed, is_subcategory, refine
from sage_categories.kernel.roles import CategoryPoint


class Tiny(Category):
    """Minimal set-like fixture with one object property and one typed query."""

    Special = Axiom()

    class ObjectType:
        def __init__(self, value: int | Integer) -> None:
            self._value = value

        def value(self) -> int | Integer:
            return self._value

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self) -> None:
        self.Measure = Query("measure", 1, self)

        def measure(value: CategoryPoint) -> CategoryPoint | UnknownClass:
            return self(abs(value.value())) if value.value() != 99 else Unknown

        self.Measure.register_handler(measure)

    def __call__(self, value: int | Integer) -> CategoryPoint:
        return self.ObjectType(value)


class SpecialTiny(PredicateSubcategory):
    _base_category_class_and_axiom = (Tiny, "Special")

    def _predicate(self, candidate: Tiny.ObjectType, assumptions: Proposition) -> bool | None:
        if candidate.value() == Integer(99):
            return None
        return bool(candidate.value() >= Integer(0))


class TinySubcategory(FullSubcategory, Tiny):
    """A named full subcategory used to prove functorial property inheritance."""


# The predicate a leaf defines when no existing method supplies the proposition, with the
# exact cases it can decide registered through SymPy (``specs/leaves.md``, "Property
# categories"; D143).
light_enough = predicate("light_enough")


class Tokens(Category):
    """A witness in the shape of ``specs/finite-set-minimal-template.py``.

    A category declares each axiom it introduces once, in its class body, by the axiom
    name and the private method returning the proposition that decides membership (D77
    item 4, D142, D148).  ``Light`` names its own predicate; ``Heavy`` is written from
    ``is_light()``, an application the first declaration generated, which is what "in
    terms of methods that already exist on the category" means; ``Tagged`` computes
    nothing and is complete as it stands (D97).
    """

    class ObjectType:
        def __init__(self, weight: Integer) -> None:
            self._weight = weight

        def weight(self) -> Integer:
            return self._weight

    class ElementType:
        pass

    class MorphismType:
        pass

    def _light(self, X: Tokens.ObjectType) -> Boolean:
        """State the proposition deciding membership in ``Tokens().Light()``."""
        return light_enough(X)

    Light = Axiom(_light)

    def _heavy(self, X: Tokens.ObjectType) -> Boolean:
        """State the proposition deciding membership in ``Tokens().Heavy()``."""
        return ~X.is_light()

    Heavy = Axiom(_heavy)

    Tagged = Axiom()

    def __call__(self, weight: Integer) -> CategoryPoint:
        return self.ObjectType(weight)


class SealedTokens(FullSubcategory, Tokens):
    """A declared subcategory that introduces an axiom of its own.

    ``Posets()`` is ``Relations().PartialOrder()`` and declares ``Total`` on the order it
    adds (``specs/ordered-sets.md``, "Total-order refinement").
    """

    Stamped = Axiom()


def _decide_light(candidate: Tokens.ObjectType, assumptions: Proposition) -> bool | None:
    """Decide the weights this leaf knows; every other case falls through to undecided (D143)."""
    match candidate.weight():
        case weight if weight >= Integer(0):
            return bool(weight <= Integer(10))
    return None


light_enough.register_handler(_decide_light)


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


def test_property_subcategory_constructs_through_its_ambient() -> None:
    """``C.P()`` has exactly the constructors of ``C``, and construction places the result (D150)."""
    tiny = Tiny()

    constructed = tiny.Special()(5)

    assert constructed in tiny.Special()
    assert constructed in tiny
    assert isinstance(constructed, tiny.Special().ObjectType)
    assert constructed.value() == 5
    assert ask(constructed.is_special()) is True


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

    value = inverse(7)
    assert value.value() == 7
    assert value in inverse
    assert value in tiny.Special()
    assert value in tiny

    presentation = Cat().Pullbacks().presentation(inverse)
    shape = presentation.diagram().domain()
    assert presentation.diagram().on_object(shape(0)) is tiny
    assert presentation.diagram().on_object(shape(1)) is property_category
    assert presentation.transformation().component(shape(0)).domain() is inverse
    assert presentation.transformation().component(shape(0)).codomain() is tiny
    assert presentation.transformation().component(shape(1)).domain() is inverse
    assert presentation.transformation().component(shape(1)).codomain() is property_category


def test_inherited_property_is_the_inverse_image_along_the_defining_functor() -> None:
    tiny = Tiny()
    subcategory = TinySubcategory(tiny)
    defining_functor = subcategory.structure_functors()[0]
    inherited = subcategory.Special()
    assert inherited is defining_functor.inverse_image(tiny.Special())
    assert is_subcategory(inherited, subcategory)
    assert is_subcategory(inherited, tiny.Special())

    presentation = Cat().Pullbacks().presentation(inherited)
    shape = presentation.diagram().domain()
    assert presentation.diagram().on_object(shape(0)) is subcategory
    assert presentation.diagram().on_object(shape(1)) is tiny.Special()
    assert presentation.transformation().component(shape(0)).domain() is inherited
    assert presentation.transformation().component(shape(0)).codomain() is subcategory
    assert presentation.transformation().component(shape(1)).domain() is inherited
    assert presentation.transformation().component(shape(1)).codomain() is tiny.Special()


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


def test_each_exact_dispatch_signature_has_one_owning_handler() -> None:
    """A second handler on one exact signature is rejected; the first owner keeps deciding."""
    tiny = Tiny()
    marked = predicate("marked")

    def by_value(candidate: Tiny.ObjectType, assumptions: Proposition) -> bool | None:
        return bool(candidate.value() > Integer(0))

    def by_other_rule(candidate: Tiny.ObjectType, assumptions: Proposition) -> bool | None:
        return None

    marked.register_handler(by_value)
    assert ask(marked(tiny(2))) is True
    with pytest.raises(AssertionError):
        marked.register_handler(by_other_rule)
    assert ask(marked(tiny(2))) is True


def test_construction_families_are_axioms_applied_by_the_kernel() -> None:
    """``Products`` and the parameterized ``Limits`` are declared once on the base class; a declared subcategory's family is the inverse image of its ambient's (D31, D89)."""
    cat = Cat()
    inhabited = cat.Inhabited()
    monomorphism = inhabited.subcategory_monomorphism()
    assert inhabited.Products() is monomorphism.inverse_image(cat.Products())
    assert is_subcategory(inhabited.Products(), cat.Products())
    assert is_subcategory(inhabited.Products(), inhabited)

    shape = cat.Simplex(1)
    assert inhabited.Limits(shape) is monomorphism.inverse_image(cat.Limits(shape))
    assert cat.Limits(shape) is cat.Limits(shape)
    assert cat.Limits(shape) is not cat.Limits(cat.Simplex(2))
    assert is_subcategory(inhabited.Limits(shape), cat.Limits(shape))


def test_one_declaration_compiled_at_two_incomparable_nodes_is_one_owner() -> None:
    """Two opposite nodes each compile ``original`` from the one opposite declaration; their join compiles."""
    tiny = Tiny()
    first, second = TinySubcategory(tiny), TinySubcategory(tiny)
    value = tiny(5)
    first(value)
    second(value)
    refine(value, first.op())
    refine(value, second.op())
    assert is_placed(value, first.op())
    assert is_placed(value, second.op())


def test_one_axiom_declaration_supplies_the_subcategory_its_inclusion_and_its_application() -> None:
    """``Light = Axiom(_light)`` is the whole declaration; ``cat_kernel`` supplies the rest (D148, D170, D175)."""
    tokens = Tokens()
    light = tokens.Light()
    (inclusion,) = light.structure_functors()
    assert inclusion.domain() is light
    assert inclusion.codomain() is tokens
    assert inclusion in Fun(light, tokens).Monomorphisms().Isofibrations()

    small = tokens(Integer(3))
    proposition = small.is_light()
    assert isinstance(proposition, Boolean)
    assert proposition is light.membership_proposition(small)


def test_the_declared_proposition_decides_membership_and_refines_the_same_value() -> None:
    """``ask`` answers from the private method the declaration names, and a positive answer places the value (D142)."""
    tokens = Tokens()
    token = tokens(Integer(2))
    identity = id(token)
    assert not is_placed(token, tokens.Light())
    assert ask(token.is_light()) is True
    assert id(token) == identity
    assert is_placed(token, tokens.Light())
    assert token in tokens.Light()

    assert ask(tokens(Integer(50)).is_light()) is False
    assert ask(tokens(Integer(-1)).is_light()) is Unknown


def test_a_deciding_proposition_is_written_from_the_applications_already_generated() -> None:
    """``_heavy`` is written from ``is_light()``, which the first declaration generated (D148)."""
    tokens = Tokens()
    assert ask(tokens(Integer(50)).is_heavy()) is True
    assert ask(tokens(Integer(2)).is_heavy()) is False
    assert ask(tokens(Integer(-1)).is_heavy()) is Unknown


def test_an_axiom_of_the_ambient_is_an_axiom_of_its_property_subcategory() -> None:
    """``C.P().Q()``: one declaration reaches every category that declares a monomorphism into ``C`` (D77 item 4, D83)."""
    tokens = Tokens()
    light = tokens.Light()
    tagged_light = light.Tagged()
    assert tagged_light is light.property_subcategory(tokens.Tagged())
    assert is_subcategory(tagged_light, light)
    assert is_subcategory(tagged_light, tokens.Tagged())

    constructed = tagged_light(Integer(4))
    assert constructed in tagged_light
    assert constructed in light
    assert constructed in tokens.Tagged()
    assert ask(constructed.is_tagged()) is True

    placed = tokens(Integer(6))
    assume(placed.is_tagged())
    assert placed in tokens.Tagged()


def test_a_declared_subcategory_constructs_the_axiom_it_declares_and_inherits_the_rest() -> None:
    """An axiom has one owner: the category whose class body declares it (D77 item 4, D83)."""
    tokens = Tokens()
    sealed = SealedTokens(tokens)
    assert sealed.Stamped().ambient() is sealed
    assert sealed.Light() is sealed.subcategory_monomorphism().inverse_image(tokens.Light())


for name, value in tuple(globals().items()):
    if name.startswith("test_"):
        value()
