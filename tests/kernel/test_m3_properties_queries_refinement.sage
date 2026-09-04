"""R3 acceptance for properties, typed queries, refinement, pullbacks, and dispatch."""

from __future__ import annotations

from sage_categories.kernel.sage_runtime import Integer

from sage_categories.kernel.sage_runtime import Unknown
from sympy.assumptions import global_assumptions
from sympy.assumptions.assume import AppliedPredicate
from sympy.logic.boolalg import Boolean

from sage_categories.cat.category import Axiom, Cat, Category, Predicate, Proposition, Query, ask, assume
from sage_categories.cat.functors import Fun
import pytest

from sage_categories.cat.predicates import AppliedQuery, UnknownClass, negation, register_handler, retract
from sage_categories.cat.properties import FullSubcategory, PredicateSubcategory
from sage_categories.kernel.predicates import OwnedPredicate
from sage_categories.kernel.refinement import is_placed, is_subcategory
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
class LightEnoughPredicate(Predicate):
    name = "light_enough"


light_enough = LightEnoughPredicate()


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
    assert isinstance(tiny.Special().predicate(), Predicate)
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


def test_each_property_predicate_uses_cats_base_and_its_own_handler() -> None:
    first, second = Tiny(), Tiny()
    first_predicate = first.Special().predicate()
    second_predicate = second.Special().predicate()
    assert isinstance(first_predicate, Predicate)
    assert isinstance(second_predicate, Predicate)
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

    class MarkedPredicate(Predicate):
        name = "marked"

    marked = MarkedPredicate()

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


def test_an_opposite_narrowing_constructs_into_both_opposite_roots() -> None:
    """The intersection of two opposite subcategories constructs through their common opposite base."""
    tiny = Tiny()
    first, second = TinySubcategory(tiny), TinySubcategory(tiny)
    both = tiny.op().intersection((first.op(), second.op()))

    value = both(Integer(5))

    assert value.value() == Integer(5)
    assert value.category() is both
    assert is_placed(value, both)
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


def test_a_second_property_narrows_the_established_placement_rather_than_replacing_it() -> None:
    """Both positive routes land the value in ``C.P().Q()``; neither answers with the ancestor ``C.Q()`` (``POL-CAT-074``, D150)."""
    tokens = Tokens()
    light, tagged = tokens.Light(), tokens.Tagged()

    assumed = light(Integer(3))
    identity = id(assumed)
    assume(assumed.is_tagged())
    assert id(assumed) == identity
    assert assumed.category() is light.Tagged()
    assert assumed in light
    assert assumed in tagged

    exact = tagged(Integer(4))
    assert ask(exact.is_light()) is True
    assert exact.category() is light.Tagged()
    assert exact in light
    assert exact in tagged


def test_a_negative_answer_records_no_placement_and_an_undecided_one_changes_nothing() -> None:
    """Only an exact positive result refines (``specs/property-refinement.md``, "Same-object refinement")."""
    tokens = Tokens()
    light = tokens.Light()

    heavy = tokens(Integer(50))
    assert ask(heavy.is_light()) is False
    assert heavy.category() is tokens
    assert not is_placed(heavy, light)

    undecided = tokens(Integer(-1))
    assert ask(undecided.is_light()) is Unknown
    assert undecided.category() is tokens
    assert not is_placed(undecided, light)


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


class BoxedTokens(FullSubcategory, Tokens):
    """A second declared subcategory of ``Tokens``, incomparable with ``SealedTokens``."""


class SealedBoxedTokens(Tokens):
    """A category selecting two structure functors whose targets both supply ``Tagged``.

    ``Modules(R).Finite()`` means one thing whether ``Finite`` reaches it through a direct
    functor to ``Sets()`` or through one that passes through ``Groups().Commutative()``
    (D159, ``POL-LEAF-081``).  The declaration is the selection and its order; the leaf
    states no property category, no containment, and no placement of its own.
    """

    def __init__(self, first: Tokens, second: Tokens) -> None:
        self._first = first
        self._second = second
        super().__init__()

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        return (
            Fun.full_subcategory_monomorphism(self, self._first),
            Fun.full_subcategory_monomorphism(self, self._second),
        )


def test_two_structure_functors_supplying_one_axiom_give_one_property_category() -> None:
    """``D.P()`` is the pullback along each selected functor whose target supplies ``P`` (D159, ``POL-LEAF-081``)."""
    for order in (0, 1):
        tokens = Tokens()
        subcategories = (SealedTokens(tokens), BoxedTokens(tokens))
        first, second = subcategories[order], subcategories[1 - order]
        both = SealedBoxedTokens(first, second)
        along_first, along_second = both.selected_functors()
        assert both.ambient() is first

        tagged = both.Tagged()
        assert tagged is along_first.inverse_image(first.Tagged())
        assert tagged is along_second.inverse_image(second.Tagged())

        pullbacks = Cat().Pullbacks()
        squares = pullbacks.presenting_diagrams(tagged)
        assert len(squares) == 2
        for square, functor in ((squares[0], along_first), (squares[1], along_second)):
            target = functor.codomain()
            shape = square.domain()
            assert square.on_object(shape(0)) is both
            assert square.on_object(shape(1)) is target.Tagged()
            assert square.on_object(shape(2)) is target
            cone = pullbacks.universal_data(square).transformation()
            assert cone.component(shape(0)).codomain() is both
            assert cone.component(shape(1)).codomain() is target.Tagged()


def test_property_containment_in_each_target_is_a_declared_monomorphism() -> None:
    """Containment is the declaration, not a consequence read off the predicates (D83, D170)."""
    tokens = Tokens()
    sealed, boxed = SealedTokens(tokens), BoxedTokens(tokens)
    both = SealedBoxedTokens(sealed, boxed)
    tagged = both.Tagged()

    for target in (both, tokens.Tagged(), sealed.Tagged(), boxed.Tagged()):
        (declared,) = tuple(functor for functor in tagged.structure_functors() if functor.codomain() is target)
        assert declared in Fun(tagged, target).Monomorphisms().Isofibrations()
        assert is_subcategory(tagged, target)


def test_a_pullback_property_category_places_what_it_constructs() -> None:
    """The retained square routes construction and assumption; the leaf declares only its functors (``POL-LEAF-066``)."""
    tokens = Tokens()
    sealed, boxed = SealedTokens(tokens), BoxedTokens(tokens)
    both = SealedBoxedTokens(sealed, boxed)

    constructed = both.Tagged()(Integer(4))
    assert is_placed(constructed, both.Tagged())
    for category in (both, sealed.Tagged(), boxed.Tagged(), tokens.Tagged()):
        assert constructed in category

    assumed = both(Integer(6))
    identity = id(assumed)
    assume(assumed.is_tagged())
    assert id(assumed) == identity
    assert is_placed(assumed, both.Tagged())
    assert assumed in sealed.Tagged()
    assert assumed in boxed.Tagged()


class BalancedPredicate(Predicate):
    """The predicate a category defines when no existing method supplies its proposition.

    ``specs/leaves.md`` "Property categories" and ``specs/poset-minimal-template.py`` write
    it as this class statement on the predicate base that ``Cat`` exports.  Applying it
    to an owned value enters that value in the SymPy expression as its private identity
    atom, and nothing at the application site converts it.
    """

    name = "balanced"


balanced = BalancedPredicate()


def _decide_balanced(candidate: Tokens.ObjectType, assumptions: Proposition) -> bool | None:
    """A token of nonnegative weight is balanced when that weight is even (D143)."""
    match candidate.weight():
        case weight if weight >= Integer(0):
            return bool(weight % Integer(2) == Integer(0))
    return None


register_handler(balanced, _decide_balanced)


def test_a_predicate_written_on_cats_base_applies_to_an_owned_value() -> None:
    """``Cat.Predicate`` owns application, composition, and evaluation of a category's predicate.

    The owned value reaches the expression as its private identity atom, so one value
    gives one atom and two values give two.  ``ask`` then answers from the exact case the
    category registered, and returns ``Unknown`` for SymPy's ``None`` alone: a decided
    ``False`` stays ``False`` (criteria 2 and 6).
    """
    tokens = Tokens()
    even, odd, unsigned = tokens(Integer(4)), tokens(Integer(5)), tokens(Integer(-1))

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


def test_an_error_sympy_raises_is_not_an_undecided_answer() -> None:
    """Sage ``Unknown`` is SymPy's ``None`` and nothing else (criterion 6).

    Inconsistent assumptions are SymPy's error, not an answer, and withdrawing them
    restores the exact decision the category's own case supplies.
    """
    tokens = Tokens()
    proposition = balanced(tokens(Integer(7)))

    assume(proposition)
    assume(negation(proposition))
    with pytest.raises(ValueError):
        ask(proposition)

    retract(proposition)
    retract(negation(proposition))
    assert ask(proposition) is False


def test_equality_uses_the_exact_category_owned_predicate() -> None:
    """``a == b`` applies the equality predicate of the category that decides it (criterion 4).

    Each category owns one, and the SymPy class behind every owned predicate is the
    kernel's, so ``Cat`` states no engine construction of its own (D125).
    """
    tokens, other = Tokens(), Tokens()
    here, there = tokens(Integer(2)), other(Integer(2))

    assert isinstance(tokens.equality(), OwnedPredicate)
    assert isinstance(tokens.Light().predicate(), OwnedPredicate)
    assert tokens.equality() is not other.equality()
    assert (here == there).function is tokens.equality()
    assert (there == here).function is other.equality()

    assert ask(here == here) is True
    assert ask(here != here) is False
    assert ask(here == there) is Unknown


def test_a_nontrivial_discrete_limit_family_declares_its_containment_in_products() -> None:
    """``C.Limits(J) -> C.Products()`` is the statement of the containment, not a consequence of the two predicates (D83).

    ``C.Products()`` is the union of the full images of the ``Lim_J`` for nontrivial
    discrete ``J`` (``specs/functor.md``, "Diagram shapes and universal constructions"),
    and ``C.Limits(J)`` is the full image of ``Lim_J``, so the mathematics says
    ``C.Limits(J)`` is a full subcategory of ``C.Products()``.  A shape that is not known
    to be nontrivial discrete declares none.
    """
    cat = Cat()
    discrete = cat.Products()((cat.Simplex(1), cat.Simplex(2))).index_category()
    limits, products = cat.Limits(discrete), cat.Products()

    (declared,) = tuple(functor for functor in limits.structure_functors() if functor.codomain() is products)
    assert declared in Fun(limits, products).Monomorphisms().Isofibrations()
    assert is_subcategory(limits, products)
    assert not is_subcategory(cat.Limits(cat.Terminal()), products)
    assert not is_subcategory(cat.Limits(cat.WalkingCospan()), products)

    colimits, coproducts = cat.Colimits(discrete), cat.Coproducts()
    (codeclared,) = tuple(functor for functor in colimits.structure_functors() if functor.codomain() is coproducts)
    assert codeclared in Fun(colimits, coproducts).Monomorphisms().Isofibrations()
    assert is_subcategory(colimits, coproducts)


def test_a_chosen_product_reaches_products_through_that_one_declaration() -> None:
    """The apex is placed once, in its shape family; membership in ``C.Products()`` follows the declared monomorphism."""
    cat = Cat()
    apex = cat.Products()((cat.Simplex(1), cat.Simplex(2)))
    discrete = apex.index_category()

    assert apex.category() is cat.Limits(discrete)
    assert is_placed(apex, cat.Products())
    assert ask(apex.is_products()) is True
    assert apex in cat.Products()
    assert cat.Products().presenting_family(apex) is cat.Limits(discrete)
    assert ask(cat.Simplex(1).is_products()) is False


def test_a_construction_family_carries_the_name_its_axiom_declares() -> None:
    """One axiom, one name: the family reads the declaration and spells no name of its own (D89, ``POL-LEAF-079``)."""
    cat = Cat()
    discrete = cat.Products()((cat.Simplex(1), cat.Simplex(2))).index_category()

    assert cat.Products().name() == "Products"
    assert cat.Coproducts().name() == "Coproducts"
    assert cat.Limits(discrete).name() == "Limits"
    assert cat.Colimits(discrete).name() == "Colimits"

    assert repr(cat.Limits(discrete)) == f"{cat!r}.Limits({discrete!r})"
    assert repr(cat.Colimits(discrete)) == f"{cat!r}.Colimits({discrete!r})"
    assert repr(cat.Products()) == f"{cat!r}.Products()"


def test_a_parameterized_construction_family_is_retained_per_parameter_value() -> None:
    """``C.Limits(J)`` is one category per category and shape, each retaining its own universal data (D168)."""
    cat = Cat()
    first, second = cat.Simplex(1), cat.Simplex(2)

    assert cat.Limits(first) is cat.Limits(first)
    assert cat.Limits(first) is not cat.Limits(second)
    assert cat.Limits(first).shape() is first
    assert cat.Limits(second).shape() is second
    assert cat.Limits(first).limit_functor() is not cat.Limits(second).limit_functor()
    assert cat.Colimits(first) is not cat.Colimits(second)


def test_limit_functor_preserves_the_retained_identity() -> None:
    apex = Cat().Products()((Cat().Simplex(1), Cat().Simplex(2)))
    family = apex.category()
    diagram = family.presentation(apex).diagram()
    identity = family.diagrams().morphism_category(1)(diagram, diagram).one()

    assert family.limit_functor().on_morphism(identity) is Cat().morphism_category(1)(apex, apex).one()


def test_two_structure_functors_supply_the_construction_families_and_their_containment() -> None:
    """A category that declares only its structure functors receives every family and the containment along each (D31, D83, D159)."""
    tokens = Tokens()
    sealed, boxed = SealedTokens(tokens), BoxedTokens(tokens)
    both = SealedBoxedTokens(sealed, boxed)
    along_first, along_second = both.selected_functors()
    shape = Cat().Products()((Cat().Simplex(1), Cat().Simplex(2))).index_category()

    products = both.Products()
    assert products is along_first.inverse_image(sealed.Products())
    assert products is along_second.inverse_image(boxed.Products())

    limits = both.Limits(shape)
    assert limits is along_first.inverse_image(sealed.Limits(shape))
    assert limits is along_second.inverse_image(boxed.Limits(shape))
    assert is_subcategory(limits, tokens.Limits(shape))
    assert is_subcategory(limits, tokens.Products())
    comparison = limits._subcategory_comparison(products)
    assert comparison is not None
    assert limits._subcategory_comparison(products) is comparison
    assert comparison in Fun(limits, products).Monomorphisms().Isofibrations().Full()
    assert is_subcategory(limits, products)


def test_every_property_of_a_functor_is_an_axiom_the_kernel_applies() -> None:
    """``Fun`` declares each of its properties once, and the kernel writes ``is_p()`` for every one (D89, ``POL-CAT-090``, ``POL-LEAF-064``).

    A category that constructs a property subcategory by hand, names it with a string, or
    patches an accessor onto it has no declaration for the kernel to read, so the
    application is missing and the containment is a table rather than a monomorphism.
    Each of these eleven is an ``Axiom`` in the body of ``FunctorsCategory``, so the
    identifier is the whole declaration.
    """
    for name in (
        "Full", "Faithful", "FullyFaithful", "EssentiallySurjective", "Equivalences",
        "Isofibrations", "Monomorphisms", "Fibrations", "Opfibrations",
        "PreservesLimits", "CreatesLimits",
    ):
        assert isinstance(getattr(type(Fun), name), Axiom)

    tiny = Tiny()
    inclusion = TinySubcategory(tiny).subcategory_monomorphism()

    assert ask(inclusion.is_monomorphisms()) is True
    assert ask(inclusion.is_isofibrations()) is True
    assert ask(inclusion.is_full()) is True
    # Faithfulness follows the declared containment ``Monomorphisms -> Faithful`` and is
    # not stated a second time on the functor.
    assert ask(inclusion.is_faithful()) is True
    assert ask(inclusion.is_fibrations()) is Unknown
    assert ask(inclusion.is_opfibrations()) is Unknown
    assert ask(inclusion.is_essentially_surjective()) is Unknown

    # Each containment is the declared monomorphism between the two property categories,
    # and nothing induces one from a relation between the predicates (D83, D169).
    assert is_subcategory(Fun.Monomorphisms(), Fun.Faithful())
    assert is_subcategory(Fun.Fibrations(), Fun.Isofibrations())
    assert is_subcategory(Fun.Opfibrations(), Fun.Isofibrations())
    assert not is_subcategory(Fun.Isofibrations(), Fun.Faithful())

    endofunctors = Fun(Cat(), Cat())
    for source, target in (
        (endofunctors.Monomorphisms(), endofunctors.Faithful()),
        (endofunctors.Fibrations(), endofunctors.Isofibrations()),
        (endofunctors.Opfibrations(), endofunctors.Isofibrations()),
    ):
        comparison = source._subcategory_comparison(target)
        assert comparison is not None
        assert source._subcategory_comparison(target) is comparison
        assert comparison in Fun(source, target).Monomorphisms().Isofibrations().Full()
        assert is_subcategory(source, target)

    # The axiom's identifier names the category too, so nothing spells a name twice.
    assert Fun.Isofibrations().name() == "Isofibrations"
    assert Fun.Monomorphisms().name() == "Monomorphisms"
    assert Fun.Fibrations().name() == "Fibrations"
    assert Fun.Opfibrations().name() == "Opfibrations"


def test_a_shape_indexed_functor_property_is_a_parameterized_axiom_of_Fun() -> None:
    """``Fun.PreservesLimits(I)`` and ``Fun.CreatesLimits(I)`` are property subcategories of ``Fun``, one per shape (D107, D158, D168, ``POL-FUN-039``).

    The shape is the axiom's parameter, so the axiom retains one category per shape and
    supplies its name; the fixed-endpoint category is the narrowing of ``Fun(C, D)`` by
    it, which is what ``Fun.P(I)(C, D)`` spells (``specs/functor.md``, "Functor property
    subcategories").
    """
    tiny = Tiny()
    shape, other = Cat().Simplex(1), Cat().Simplex(2)
    preserves, creates = Fun.PreservesLimits(shape), Fun.CreatesLimits(shape)

    assert preserves.ambient() is Fun
    assert creates.ambient() is Fun
    assert preserves.shape() is shape
    assert preserves.name() == "PreservesLimits"
    assert creates.name() == "CreatesLimits"
    assert Fun.PreservesLimits(shape) is preserves
    assert Fun.PreservesLimits(other) is not preserves
    assert Fun.CreatesLimits(shape) is not preserves

    functors = Fun(tiny, tiny)
    assert functors.CreatesLimits(shape) is creates(tiny, tiny)
    assert functors.PreservesLimits(shape) is preserves(tiny, tiny)

    functor = functors.CreatesLimits(shape)(lambda value: value, lambda morphism: morphism)
    assert ask(functor.is_creates_limits(shape)) is True
    assert ask(functor.is_creates_limits(other)) is Unknown
    assert ask(functor.is_preserves_limits(shape)) is Unknown
