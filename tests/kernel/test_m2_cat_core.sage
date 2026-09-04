"""R2 acceptance for the owned Cat core, using only Cat-level constructions."""

from sage_categories.kernel.sage_runtime import Integer

import pytest

from sage_categories.cat.category import Axiom, Cat, Category, CategoryOfCategories, OnMorphism, OnObject, ask, is_placed, is_subcategory
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import Op, op_squared_isomorphism
from sage_categories.cat.predicates import Proposition, Unknown, register_handler


class Tokens(Category):
    """A category written from D77's closed list: three declarations, one constructor, two axioms."""

    Marked = Axiom()
    Tagged = Axiom()

    class ObjectType:
        def __init__(self, token: str) -> None:
            self._token = token

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, token: str) -> None:
            self._token = token

    def __call__(self, token: str) -> CategoryOfCategories.ElementType:
        return self.ObjectType(token)


TOKENS = Tokens()


class Marks(Category):
    """A second category from the same closed list, so a declaration between endpoints has two of them."""

    class ObjectType:
        def __init__(self, token: str) -> None:
            self._token = token

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, token: str) -> None:
            self._token = token

    def __call__(self, token: str) -> CategoryOfCategories.ElementType:
        return self.ObjectType(token)


class Runes(Category):
    """A third, so the two zero-argument declarations use two endpoint pairs.

    One identity-on-values functor exists per pair (``POL-FUN-027``), so two declarations
    on one pair would narrow one value twice and say nothing about either spelling.
    """

    class ObjectType:
        def __init__(self, token: str) -> None:
            self._token = token

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, token: str) -> None:
            self._token = token

    def __call__(self, token: str) -> CategoryOfCategories.ElementType:
        return self.ObjectType(token)


MARKS = Marks()
RUNES = Runes()


def _identity_functor(category: Category) -> Functor:
    return Fun(category, category)(lambda x: x, lambda f: f)


def _identity_transformation(functor: Functor) -> NaturalTransformation:
    category = functor.codomain()
    return Fun(functor.domain(), category).morphism_category(1)(functor, functor)(
        lambda x: category.morphism_category(1)(functor.on_object(x), functor.on_object(x)).one()
    )


def test_the_three_role_types_a_functor_and_a_transformation_are_one_tower() -> None:
    """The five types a writer names are five nodes of one tower (R2 criterion 1).

    ``Mor(n, C).ObjectType`` is ``Mor(n-1, C).MorphismType``: one implementation type, one
    value, two placements (``specs/functor.md``, "The ``Mor(n, C)`` tower").  ``Cat()`` is
    that same tower at the top, so a functor is an object of ``Mor(Cat())`` and a natural
    transformation an object of ``Mor(2, Cat())``, which is the morphism type of the
    functor category holding it.  ``isinstance`` decides against each of the five, so the
    writer never needs a class the compiler owns to say what a value is (D130, D173).
    """
    a, b = TOKENS("a"), TOKENS("b")
    arrow = Mor(TOKENS)(a, b)("f")

    # The three role types of one category are three declarations, not one.
    assert len({TOKENS.ObjectType, TOKENS.ElementType, TOKENS.MorphismType}) == 3
    assert isinstance(a, TOKENS.ObjectType)
    assert isinstance(arrow, TOKENS.MorphismType)

    # The level identity, at the two levels a 1-category has.
    assert Mor(0, TOKENS) is TOKENS
    assert Mor(TOKENS) is Mor(1, TOKENS)
    assert Mor(2, TOKENS) is Mor(Mor(TOKENS))
    assert Mor(TOKENS).ObjectType is TOKENS.MorphismType
    assert Mor(2, TOKENS).ObjectType is Mor(TOKENS).MorphismType
    assert isinstance(arrow, Mor(TOKENS).ObjectType)

    # A functor is an object of ``Mor(Cat())`` and of the fixed-endpoint category.
    functors = Fun(TOKENS, TOKENS)
    identity = _identity_functor(TOKENS)
    assert Mor(Cat()).ObjectType is Cat().MorphismType
    assert isinstance(identity, Cat().MorphismType)
    assert isinstance(identity, functors.ObjectType)

    # A natural transformation is an object of ``Mor(2, Cat())``, which is the morphism
    # type of the functor category it is a morphism of.
    eta = _identity_transformation(identity)
    assert Mor(functors).ObjectType is functors.MorphismType
    assert Mor(2, Cat()).ObjectType is Mor(Cat()).MorphismType
    assert isinstance(eta, functors.MorphismType)
    assert isinstance(eta, Mor(2, Cat()).ObjectType)

    # Every value of the tower is a point ``* -> K``, the one root it has (POL-CAT-058).
    for value in (a, arrow, TOKENS, identity, eta):
        assert isinstance(value, Cat().ElementType)


def test_functors_and_two_morphisms_are_owned_and_distinct() -> None:
    category = Cat().Simplex(1)
    first = _identity_functor(category)
    second = _identity_functor(category)
    assert first is not second
    transformation = Fun(category, category).morphism_category(1)(first, second)(
        lambda x: category.morphism_category(1)(x, x).one()
    )
    assert transformation.component(category(0)) is transformation.component(category(0))

    eta = _identity_transformation(first)
    theta = _identity_transformation(second)
    assert eta.whisker_left(first).source_functor().domain() is category
    assert eta.whisker_right(first).source_functor().domain() is category
    assert eta.horizontal(theta).source_functor().domain() is category


def test_walking_arrow_evaluation_acts_on_objects_and_two_morphisms() -> None:
    category = Cat().Simplex(1)
    diagrams = Fun(Cat().Simplex(1), category)
    identity = _identity_functor(category)
    evaluation = diagrams.evaluation(Cat().Simplex(1)(0))
    assert evaluation.on_object(identity) is category(0)
    eta = _identity_transformation(identity)
    assert evaluation.on_morphism(eta) is eta.component(category(0))


def test_products_pullbacks_comma_and_fixed_slices_retain_defining_functors() -> None:
    category = Cat().Simplex(1)
    product = Cat().Products()((category, category))
    assert product.product_projection(0).domain() is product
    assert product.product_projection(1).domain() is product
    assert product.product_factors().domain() is product.index_category()

    identity = _identity_functor(category)
    diagram = cospan_diagram(Cat(), identity, identity)
    pullback = Cat().Pullbacks()(diagram)
    presentation = Cat().Pullbacks().presentation(pullback)
    assert presentation.diagram() is diagram
    assert presentation.transformation().codomain() is diagram

    comma = Cat().Comma(identity, identity)
    assert Cat().Comma(identity, identity) is comma
    assert comma in Cat().Pullbacks()
    assert comma.first_projection().domain() is comma
    assert comma.first_projection().codomain() is category
    assert comma.second_projection().domain() is comma
    assert comma.second_projection().codomain() is category
    transformation = comma.defining_transformation()
    assert transformation.source_functor().factors() == (comma.first_projection(), identity)
    assert transformation.target_functor().factors() == (comma.second_projection(), identity)

    slice_category = category.SliceOver(category(1))
    coslice_category = category.CosliceUnder(category(0))
    for fixed in (slice_category, coslice_category):
        assert fixed.defining_arrow().domain() is fixed
        assert fixed.fixed_projection().domain() is fixed
        assert fixed.fixed_projection().codomain() is category


def test_shape_indexed_functor_properties_exist_at_fixed_endpoints() -> None:
    category = Cat().Simplex(1)
    shape = Cat().Simplex(1)
    functors = Fun(category, category)
    preserves = functors.PreservesLimits(shape)
    creates = functors.CreatesLimits(shape)
    assert preserves.ambient() is functors
    assert creates.ambient() is functors
    assert preserves.shape() is shape
    assert creates.shape() is shape


def test_op_is_an_involution_on_the_four_kinds_it_acts_on() -> None:
    """``X.op().op()`` is ``X`` for a category, a functor, a morphism, and a transformation.

    ``Op: Cat() -> Cat()`` acts on categories and functors and dualizes natural
    transformations, and it retains the isomorphism ``Op * Op ~= Id``
    (``specs/functor.md``, "Opposites and dualization").  Involutivity is by retained
    identity, so the double opposite is the value itself and not a second one equal to it.
    """
    a, b = TOKENS("a"), TOKENS("b")
    arrow = Mor(TOKENS)(a, b)("f")
    source, target = _identity_functor(TOKENS), _identity_functor(TOKENS)
    eta = Fun(TOKENS, TOKENS).morphism_category(1)(source, target)(
        lambda x: Mor(TOKENS)(x, x).one()
    )

    assert TOKENS.op() is Op.on_object(TOKENS)
    assert source.op() is Op.on_morphism(source)
    for value in (TOKENS, source, arrow, eta):
        assert value.op().op() is value

    # ``eta.op(): G.op() => F.op()`` reverses the two functors ``eta`` is a morphism of.
    assert source.op() is not target.op()
    assert eta.op().source_functor() is target.op()
    assert eta.op().target_functor() is source.op()

    # The opposite of a morphism reverses its endpoints in the opposite category.
    assert arrow.op().base_category() is TOKENS.op()
    assert arrow.op().domain() is b
    assert arrow.op().codomain() is a
    assert arrow.op().original() is arrow

    isomorphism = op_squared_isomorphism()
    assert isomorphism.source_functor() is Op * Op
    assert isomorphism.target_functor() is Fun(Cat(), Cat()).one()


def test_the_narrowing_join_of_two_dual_placements_compiles() -> None:
    """One opposite declaration compiled at two incomparable nodes has one owner (issue #24).

    ``C.P().op()`` and ``C.Q().op()`` are incomparable, and each compiles ``original``
    from the one declaration ``OppositeCategory`` writes.  A spelling is owned by the
    declaration that supplies it, so the two nodes are one mathematical operation and
    their narrowing join compiles.
    """
    marked, tagged = TOKENS.Marked().op(), TOKENS.Tagged().op()

    joined = marked.property_subcategory(tagged)

    assert joined.narrowing_base() is TOKENS.op()
    roots = joined.narrowing_roots()
    assert len(roots) == 2
    assert any(root is marked for root in roots)
    assert any(root is tagged for root in roots)


def test_one_equality_predicate_has_a_generic_case_and_one_exact_owner() -> None:
    """Identity decides generically, the word handler owns its exact signature, and a second is refused.

    SymPy's dispatcher keeps the last registration for a repeated signature, which would
    discard the earlier handler with no failure, so the kernel refuses the collision at
    registration instead (``POL-TYPE-019``).  The generic identity case is registered on
    the root atom and the word handler on the exact morphism domain, so the two coexist.
    """
    a, b = TOKENS("a"), TOKENS("b")
    f, g = Mor(TOKENS)(a, b)("f"), Mor(TOKENS)(a, b)("g")
    identity = Mor(TOKENS)(a, a).one()

    assert ask(a == a) is True
    assert ask(a == b) is Unknown
    assert ask(f == f) is True
    assert ask(f == g) is Unknown
    assert ask(identity * identity == identity) is True

    def another_word_rule(
        first: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
        assumptions: Proposition,
    ) -> bool | None:
        return None

    with pytest.raises(AssertionError):
        register_handler((f == f).function, another_word_rule)

    assert ask(f == f) is True
    assert ask(f == g) is Unknown


def test_canonical_shapes_are_retained() -> None:
    cat = Cat()
    assert cat.Initial() is cat.Initial()
    assert cat.Terminal() is cat.Terminal()
    assert cat.Simplex(1) is cat.Simplex(1)
    assert cat.WalkingParallelPair() is cat.WalkingParallelPair()
    assert cat.WalkingIsomorphism() is cat.WalkingIsomorphism()


def test_the_zero_argument_declaration_states_the_property_category_it_names() -> None:
    """The zero-argument call declares an inclusion, and the property category named is the whole declaration (D146, D162).

    A subcategory inclusion computes nothing, so it is written with no action; every other
    functor is written with its two actions (D08, D21).  The call is therefore available
    on a monomorphism subcategory of ``Fun(S, T)`` and refused on every other property
    category of it.  What it declares is what it named: ``Fun(S, T).Monomorphisms()()``
    states that the functor is monic and states nothing more, so placement does not follow
    it, while ``Fun(S, T).Monomorphisms().Isofibrations()()`` is the declaration placement
    follows (``POL-FUN-036``, ``specs/functor.md``, "Declaring one").
    """
    monic = Fun(MARKS, TOKENS).Monomorphisms()()
    assert is_placed(monic, Fun(MARKS, TOKENS).Monomorphisms())
    assert ask(Fun.Monomorphisms().membership_proposition(monic))
    assert ask(Fun.Isofibrations().membership_proposition(monic)) is Unknown
    assert not Fun.declares_subcategory(monic)
    assert not Fun.declares_inheritance(monic)

    inclusion = Fun(RUNES, TOKENS).Monomorphisms().Isofibrations()()
    assert is_placed(inclusion, Fun.Isofibrations())
    assert Fun.declares_subcategory(inclusion)
    assert Fun.declares_inheritance(inclusion)

    for property_category in (
        Fun(MARKS, TOKENS).Full(),
        Fun(MARKS, TOKENS).Faithful(),
        Fun(MARKS, TOKENS).Isofibrations(),
        Fun(MARKS, TOKENS).Fibrations(),
        Fun(MARKS, TOKENS).Opfibrations(),
        Fun(MARKS, TOKENS).Equivalences(),
        Fun(MARKS, TOKENS).PreservesLimits(Cat().Simplex(1)),
    ):
        with pytest.raises(AssertionError):
            property_category()


def test_the_containments_of_funs_property_subcategories_are_retained_monomorphisms() -> None:
    """Each containment among ``Fun``'s property subcategories is the monomorphism presenting it (D83, D169).

    The containment is the statement, and nothing induces it from a relation between the
    predicates: ``ask`` answers a functor's faithfulness from a declared containment where
    one is declared and returns ``Unknown`` where none is (``POL-CAT-091``).  A monic
    functor is faithful and injective on objects, so ``Monomorphisms()`` declares its
    containment in ``Faithful()``.  An isofibration is neither, so ``Isofibrations()``
    declares no containment beyond its inclusion into ``Fun``; the fibrations and
    opfibrations inside it declare theirs.
    """
    for inner, outer in (
        (Fun.Monomorphisms(), Fun.Faithful()),
        (Fun.FullyFaithful(), Fun.Full()),
        (Fun.FullyFaithful(), Fun.Faithful()),
        (Fun.Equivalences(), Fun.FullyFaithful()),
        (Fun.Equivalences(), Fun.EssentiallySurjective()),
        (Fun.Fibrations(), Fun.Isofibrations()),
        (Fun.Opfibrations(), Fun.Isofibrations()),
    ):
        (presenting,) = [functor for functor in inner.selected_functors() if functor.codomain() is outer]
        assert is_placed(presenting, Fun.Monomorphisms())
        assert is_placed(presenting, Fun.Full())
        assert is_subcategory(inner, outer)

    assert tuple(functor.codomain() for functor in Fun.Isofibrations().selected_functors()) == (Fun,)

    def token_actions() -> tuple[OnObject, OnMorphism]:
        """A fresh pair of actions into ``TOKENS``; the four components select the functor (POL-FUN-001)."""

        def on_object(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            return TOKENS(member_object._token)

        def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            image = on_object(morphism.domain())
            return Mor(TOKENS)(image, image).one()

        return on_object, on_morphism

    monomorphism = Fun(MARKS, TOKENS).Monomorphisms()(*token_actions())
    assert ask(monomorphism.is_faithful())
    isofibration = Fun(RUNES, TOKENS).Isofibrations()(*token_actions())
    assert ask(isofibration.is_faithful()) is Unknown


for name, value in tuple(globals().items()):
    if name.startswith("test_"):
        value()
