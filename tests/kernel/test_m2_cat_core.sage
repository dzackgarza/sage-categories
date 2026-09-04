"""R2 acceptance for the owned Cat core, using only Cat-level constructions."""

from sage_categories.kernel.sage_runtime import Integer

import pytest

from sage_categories.cat.category import Axiom, Cat, Category, CategoryOfCategories, OnMorphism, OnObject, ask, is_placed, is_subcategory
from sage_categories.cat.diagrams import cospan_diagram
from sage_categories.cat.functors import Fun, Functor, NaturalTransformation
from sage_categories.cat.images import full_image, strict_image
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


# A category ``Cat`` declares, and the class that implements it: the identity functor of
# the declaration, selected first, is the whole implementation declaration (D156).
GLYPHS = Cat().declare("Glyphs")
GLYPHS_ORDINAL = GLYPHS.ordinal()


class GlyphsCategory(Category):
    """A category from D77's closed list, implementing the declaration ``Glyphs``."""

    class ObjectType:
        def __init__(self, glyph: str) -> None:
            self._glyph = glyph

        def glyph(self) -> str:
            return self._glyph

    class ElementType:
        pass

    class MorphismType:
        def __init__(self, glyph: str) -> None:
            self._glyph = glyph

    def __call__(self, glyph: str) -> CategoryOfCategories.ElementType:
        return self.ObjectType(glyph)

    def to_tokens(self) -> Functor:
        """The structure functor to ``TOKENS``, written against ``self`` as a leaf writes one."""

        def on_object(X: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            return TOKENS(X.glyph())

        def on_morphism(f: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            source, target = on_object(f.domain()), on_object(f.codomain())
            return Mor(TOKENS)(source, target)(f._glyph)

        return Fun(self, TOKENS)(on_object, on_morphism)

    def structure_functors(self) -> tuple[Functor, ...]:
        """The identity of ``Glyphs``, then the structure functor this leaf defines.

        The second entry is the shape every real leaf has (``specs/poset-minimal-template.py``):
        a functor whose domain is ``self``, defined with its two actions.  It is
        constructed when this declaration is read, which is why the read happens on the
        value under construction and not on the class.
        """
        return (Fun(GLYPHS, GLYPHS).one(), self.to_tokens())


Cat().implement(GlyphsCategory)


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


def test_a_composite_is_placed_by_both_of_its_factors() -> None:
    """``g * f`` lands in the strongest category both factors are morphisms of, in either order.

    A morphism placed in ``Mor(C.P())`` states that both of its endpoints lie in the full
    subcategory ``C.P()``, so ``g * f`` is a morphism of ``C.P()`` when both factors are
    and a morphism of ``C`` when one of them is not.  Composition therefore reads both
    factors, exactly as the product of two objects does (``POL-CAT-088``), and the
    composite is constructed into the strongest category its factors establish (D21,
    ``POL-CAT-020``, ``POL-CAT-081``).

    ``1_X`` for ``X`` in ``C.P()`` is placed in a narrowing of ``Mor(C)`` carrying
    ``Mor(C.P())`` among its roots, so that narrowing's base is ``C.P()`` and not ``C``:
    reading an ancestor there is the weakening ``POL-CAT-074`` forbids.  Placement is a
    sufficient route to ``True`` and never the definition (``POL-CAT-068``), so the two
    answers are read together: they agree on the composites of ``C.P()`` and agree again
    on the composite whose far endpoint ``C.P()`` does not hold.
    """
    marked = TOKENS.Marked()
    source, target = marked("marked source"), marked("marked target")
    arrow = Mor(marked)(source, target)("marked arrow")
    source_identity = Mor(marked)(source, source).one()
    target_identity = Mor(marked)(target, target).one()

    # The identity of an object of ``C.P()`` is a morphism of ``C.P()``, which is what its
    # placement says and what composition reads from it.
    assert is_placed(source_identity, Mor(marked))
    assert source_identity.base_category() is marked

    for name, composite in (("f * 1_X", arrow * source_identity), ("1_Y * f", target_identity * arrow)):
        assert is_placed(composite, Mor(marked)), name
        assert ask(Mor(marked).membership_proposition(composite)) is True, name
        assert ask(composite == arrow) is True, name

    # The far endpoint decides the other direction: ``h`` starts outside ``C.P()``, so
    # ``f * h`` is a morphism of ``C`` alone and neither answer claims otherwise.
    outside = TOKENS("ambient source")
    entering = Mor(TOKENS)(outside, source)("entering arrow")
    leaving = arrow * entering

    assert is_placed(leaving, Mor(TOKENS))
    assert not is_placed(leaving, Mor(marked))
    assert ask(Mor(marked).membership_proposition(leaving)) is Unknown


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


def test_a_functor_is_its_exact_endpoints_and_its_two_ordinary_actions() -> None:
    """A functor is declared by two endpoints and two ordinary actions, and by nothing else (R2 criterion 2).

    The two actions are the complete writer input (D08, D123): each is ordinary Python
    that ends by calling a public constructor of the target, ``D(datum)`` for an object and
    ``Mor(D)(F(X), F(Y))(datum)`` for a morphism (``specs/functor.md``, "Functor actions are
    concrete constructors").  The endpoints are exact: the functor is an object of
    ``Fun(C, D)`` for the two categories the writer named, and every application checks
    both actions against them, so a functor written with one action or with an action that
    leaves the named codomain is refused (D56).
    """

    def on_object(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return MARKS(member_object._token)

    def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        source = on_object(morphism.domain())
        target = on_object(morphism.codomain())
        return Mor(MARKS)(source, target)(morphism._token)

    functor = Fun(TOKENS, MARKS)(on_object, on_morphism)
    assert functor.domain() is TOKENS
    assert functor.codomain() is MARKS
    assert is_placed(functor, Fun(TOKENS, MARKS))
    assert functor in Fun(TOKENS, MARKS)
    assert not is_placed(functor, Fun(MARKS, TOKENS))

    a, b = TOKENS("a"), TOKENS("b")
    arrow = Mor(TOKENS)(a, b)("f")

    # The object action returns an object of the named codomain, built by that category's
    # own constructor, and the morphism action a morphism of the exact target hom category.
    image = functor.on_object(a)
    assert isinstance(image, MARKS.ObjectType)
    assert image in MARKS
    assert image._token == "a"
    arrow_image = functor.on_morphism(arrow)
    assert arrow_image in Mor(MARKS)(functor.on_object(a), functor.on_object(b))
    assert arrow_image._token == "f"

    # One action is not a functor.
    with pytest.raises(TypeError):
        Fun(TOKENS, MARKS)(on_object)

    # Endpoints the actions do not respect are refused where the action breaks them: the
    # same two actions declared ``TOKENS -> TOKENS`` leave the codomain they named.
    with pytest.raises(AssertionError):
        Fun(TOKENS, TOKENS)(on_object, on_morphism).on_object(a)

    def wrong_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        other = MARKS("elsewhere")
        return Mor(MARKS)(other, other)("f")

    with pytest.raises(AssertionError):
        Fun(TOKENS, MARKS)(on_object, wrong_morphism).on_morphism(arrow)

    # An argument outside the named domain is refused too.
    with pytest.raises(AssertionError):
        functor.on_object(MARKS("a"))


def test_a_natural_transformation_is_a_morphism_of_its_exact_functor_category() -> None:
    """A natural transformation is a morphism of ``Fun(C, D)`` for the exact endpoints of its two functors (R2 criterion 3).

    ``Mor(Fun(C, D))(F, G)(assignment)`` is the one spelling, and the assignment is a rule
    ``X |-> eta_X`` returning a morphism ``F(X) -> G(X)`` of ``D``; naturality is trusted
    (``specs/functor.md``, "Functor actions are concrete constructors").  The endpoints are
    exact in both directions: the transformation is placed in ``Mor(Fun(C, D))`` and in the
    fixed-endpoint category on its two functors, in no other functor category, and a pair
    of functors whose endpoints differ has no transformation between them at all (D56).
    """

    def marked(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return MARKS(member_object._token)

    def marked_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        return Mor(MARKS)(marked(morphism.domain()), marked(morphism.codomain()))(morphism._token)

    def shifted(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return MARKS(f"{member_object._token}'")

    def shifted_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        return Mor(MARKS)(shifted(morphism.domain()), shifted(morphism.codomain()))(morphism._token)

    source = Fun(TOKENS, MARKS)(marked, marked_morphism)
    target = Fun(TOKENS, MARKS)(shifted, shifted_morphism)

    def assignment(member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        return Mor(MARKS)(source.on_object(member_object), target.on_object(member_object))("shift")

    transformation = Mor(Fun(TOKENS, MARKS))(source, target)(assignment)
    assert transformation.source_functor() is source
    assert transformation.target_functor() is target

    # Its owning category is the functor category of the exact endpoints, and no other.
    functors = Fun(source.domain(), source.codomain())
    assert functors is Fun(TOKENS, MARKS)
    assert is_placed(transformation, Mor(functors))
    assert is_placed(transformation, Mor(functors)(source, target))
    assert transformation in Mor(functors)
    assert not is_placed(transformation, Mor(Fun(TOKENS, TOKENS)))
    assert not is_placed(transformation, Mor(Fun(MARKS, TOKENS)))

    # Its components are morphisms of the codomain, each in the exact hom category.
    a = TOKENS("a")
    component = transformation.component(a)
    assert component in Mor(MARKS)
    assert component in Mor(MARKS)(source.on_object(a), target.on_object(a))
    assert component._token == "shift"

    # Functors with mismatched endpoints have no transformation between them.
    with pytest.raises(AssertionError):
        Mor(Fun(TOKENS, MARKS))(source, _identity_functor(TOKENS))

    # A component that is not a morphism of the codomain is refused when it is read.
    stray = Mor(Fun(TOKENS, MARKS))(source, target)(lambda member_object: Mor(TOKENS)(a, a).one())
    with pytest.raises(AssertionError):
        stray.component(a)


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


def test_an_axiom_parameterized_by_a_functor_is_the_essential_image() -> None:
    """``D.EssentialImage(F)`` is an axiom of ``D`` whose parameter is a functor (D168, POL-LEAF-064).

    Being a product is an axiom, equivalent to membership in the essential image of the
    nontrivial product functor, and axioms can be parameterized (D168).  So the essential
    image is the general shape that row states in one case, and what it turns on is the
    functor: a morphism of ``Cat()`` rather than an object of it, as ``C.Limits(I)`` turns
    on a shape.  ``Category`` declares the axiom once and the declaration owns the name,
    the retention, and the generated application; nothing spells ``"EssentialImage"`` at a
    construction site (D89, D133 shape (2), D148, D175).
    """

    def token_actions(prefix: str) -> tuple[OnObject, OnMorphism]:
        def on_object(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            return TOKENS(prefix + member_object._token)

        def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            source = on_object(morphism.domain())
            target = on_object(morphism.codomain())
            return Mor(TOKENS)(source, target)(morphism._token)

        return on_object, on_morphism

    first = Fun(MARKS, TOKENS)(*token_actions("first "))
    second = Fun(MARKS, TOKENS)(*token_actions("second "))

    # One subcategory per target and defining functor, retained by the declaration; the
    # two functors share their endpoints and have different essential images.
    image = TOKENS.EssentialImage(first)
    assert TOKENS.EssentialImage(first) is image
    assert TOKENS.EssentialImage(second) is not image
    assert image.ambient() is TOKENS
    assert image.defining_functor() is first

    # The name is the declaration's, and the application is compiled from that identifier
    # and nothing else: ``EssentialImage`` gives ``is_essential_image`` (D89, POL-CAT-060).
    assert image.name() == "EssentialImage"
    assert Category.EssentialImage.application_name() == "is_essential_image"

    # The generated application decides, and it takes the parameter the axiom does.
    inside = first.on_object(MARKS("a"))
    assert ask(inside.is_essential_image(first)) is True
    assert inside in image
    assert ask(inside.is_essential_image(second)) is Unknown

    # Membership records only the existential property, so an object nobody exhibited as a
    # value of ``first`` is undecided rather than excluded (``specs/functor.md``, "Strict,
    # full, and essential images").
    assert ask(TOKENS("unrelated").is_essential_image(first)) is Unknown

    # The factorization the specification states: an essentially surjective factor onto
    # the image, then the fully faithful inclusion that ``cat_kernel`` builds for the
    # axiom's subcategory (D175).
    factor, inclusion = image.factorization()
    assert factor.domain() is MARKS and factor.codomain() is image
    assert ask(factor.is_essentially_surjective())
    assert inclusion.domain() is image and inclusion.codomain() is TOKENS
    assert ask(inclusion.is_fully_faithful())

    # Asking whether the subcategory exists constructs none: every public object image of
    # every functor passes through the retention that reads this.
    third = Fun(MARKS, TOKENS)(*token_actions("third "))
    assert not Category.EssentialImage.is_constructed(TOKENS, third)
    third.on_object(MARKS("a"))
    assert not Category.EssentialImage.is_constructed(TOKENS, third)


def test_strict_and_full_image_inclusions_are_the_direct_zero_argument_call() -> None:
    """A strict or full image inclusion is exactly ``Fun(S, T).P()()`` on its own placement (POL-LEAF-070).

    Neither image is replete in general -- the essential image is the replete one, and it
    is a different class (D168) -- so neither inclusion carries ``Isofibrations()`` (D169).
    The strict image states only monicity; the full image states monicity and fullness
    together, and not through ``Fun.full_subcategory_monomorphism``, which declares
    ``Isofibrations()`` too and would misstate repleteness here.  ``_construct_inclusion``
    writes no action for either, so it retains the one identity-on-values functor for its
    endpoint pair (POL-FUN-027), the same object the named property category builds
    directly with no arguments.
    """

    def token_actions(prefix: str) -> tuple[OnObject, OnMorphism]:
        def on_object(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            return TOKENS(prefix + member_object._token)

        def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            source = on_object(morphism.domain())
            target = on_object(morphism.codomain())
            return Mor(TOKENS)(source, target)(morphism._token)

        return on_object, on_morphism

    defining = Fun(MARKS, TOKENS)(*token_actions("image "))

    strict = strict_image(TOKENS, defining)
    strict_inclusion = strict.inclusion_functor()
    assert strict_inclusion is Fun(strict, TOKENS).Monomorphisms()()
    assert is_placed(strict_inclusion, Fun(strict, TOKENS).Monomorphisms())
    assert ask(Fun.Isofibrations().membership_proposition(strict_inclusion)) is Unknown

    full = full_image(TOKENS, defining)
    full_inclusion = full.inclusion_functor()
    assert full_inclusion is Fun(full, TOKENS).FullyFaithful().Monomorphisms()()
    assert is_placed(full_inclusion, Fun(full, TOKENS).Monomorphisms())
    assert is_placed(full_inclusion, Fun(full, TOKENS).FullyFaithful())
    assert ask(Fun.Isofibrations().membership_proposition(full_inclusion)) is Unknown


def test_a_class_says_which_declared_category_it_implements_by_that_category_identity_functor() -> None:
    """The identity structure functor is the whole implementation declaration (D156, POL-LEAF-080).

    A category ``Cat`` declared exists before any class is written for it, and the class
    that implements it says so by selecting that category's identity functor first among
    its structure functors.  There is no binding field and no name written as a string,
    which is the shape ``POL-LEAF-077`` names a red flag.  ``Cat().implement`` constructs
    the class to read that declaration, because the structure functors beside the identity
    are written against ``self`` as ``to_tokens`` is; the construction then stops at the
    declaration and strengthens the declared value in place, ordinal kept, instead of
    building a second category.
    """
    # The declared object is the final object: its class is strengthened in place, it
    # keeps its ordinal, and it is no longer open work.
    assert type(GLYPHS) is GlyphsCategory
    assert GLYPHS.ordinal() == GLYPHS_ORDINAL
    assert Cat().open_declaration(GLYPHS) is None

    # The identity functor is what said which category, and it is the first selected.
    assert GLYPHS.selected_functors()[0] is Fun(GLYPHS, GLYPHS).one()

    # The functor written against ``self`` was built over the declared value, not over a
    # second one: this is what a read taken off the class instead of the construction
    # cannot do.
    assert GLYPHS.selected_functors()[1].domain() is GLYPHS
    assert GLYPHS.selected_functors()[1].on_object(GLYPHS("a")) is TOKENS("a")

    # The class's mathematics reaches the value every earlier reference already holds.
    assert GLYPHS("a").glyph() == "a"

    # The identity functor is the only thing that says "I implement that one": a class
    # selecting an ordinary structure functor first declares its own category, and the
    # declaration it names as a codomain is untouched.
    class SelectsNoIdentity(Category):
        """A class whose only structure functor is the inclusion every subcategory selects."""

        class ObjectType:
            pass

        class ElementType:
            pass

        class MorphismType:
            pass

        def structure_functors(self) -> tuple[Functor, ...]:
            return (Fun(self, GLYPHS).Monomorphisms().Isofibrations()(),)

    its_own = SelectsNoIdentity()
    assert its_own is not GLYPHS
    assert its_own.ambient() is GLYPHS
    assert type(GLYPHS) is GlyphsCategory

    # An identity naming a category Cat declared nothing for is refused rather than
    # silently adopted.
    class ImplementsNoDeclaration(Category):
        """A class selecting the identity of a category no declaration of Cat awaits."""

        class ObjectType:
            pass

        class ElementType:
            pass

        class MorphismType:
            pass

        def structure_functors(self) -> tuple[Functor, ...]:
            return (Fun(TOKENS, TOKENS).one(),)

    with pytest.raises(AssertionError):
        Cat().implement(ImplementsNoDeclaration)


def test_the_core_functor_target_is_implemented_through_that_same_declaration() -> None:
    """``Groupoids`` is the declaration ``cat/core.py`` claims by this route (D99, D156).

    The one implementation in the tree of a category ``Cat`` declares reaches it the way
    the row states: the identity functor first, then the inclusion the core states, and
    the declared value carries the implementing class.
    """
    from sage_categories.cat.core import U, Groupoids, GroupoidsCategory

    assert type(Groupoids) is GroupoidsCategory
    assert Cat().open_declaration(Groupoids) is None
    assert Groupoids.selected_functors() == (Fun(Groupoids, Groupoids).one(), U)


def test_the_core_constructs_its_morphisms_through_the_isomorphisms_of_its_ambient() -> None:
    """``Mor(C.Core())(A, B)(data)`` is the trusted constructor ``Mor(C)(A, B).Isomorphisms()(data)`` (D99, POL-MATH-037).

    A morphism of ``C.Core()`` is an isomorphism of ``C``, and that containment is the
    only thing the core adds to ``C``.  It is declared, not induced (D83), so the hom
    category the call places its result in lies inside the isomorphisms of ``C`` between
    the same two objects, and the call keeps the stronger of the two placements rather
    than finding them incomparable (D21, ``POL-CAT-074``).  The core owns its identities
    and its composites for the same reason its monomorphism is not full, so each lands in
    the core's own hom category: ``Mor(C).Isomorphisms()`` is a declared ancestor of
    ``Mor(C.Core())``, and answering there is the ancestor ``POL-CAT-074`` forbids.
    """
    A, B, D = TOKENS("core-domain"), TOKENS("core-middle"), TOKENS("core-codomain")
    core = TOKENS.Core()
    isomorphisms_between = Mor(TOKENS)(A, B).Isomorphisms()

    morphism = Mor(core)(A, B)("core-arrow")

    assert morphism.category() is Mor(core)(A, B)
    assert is_subcategory(Mor(core)(A, B), isomorphisms_between)
    assert is_placed(morphism, isomorphisms_between)
    assert morphism.domain() is A and morphism.codomain() is B
    assert morphism in Mor(TOKENS).Isomorphisms()

    second = Mor(core)(B, D)("core-arrow-on")
    composite = second * morphism
    assert is_placed(composite, Mor(core))
    assert is_placed(composite, Mor(core)(A, D))
    assert is_placed(Mor(core)(A, A).one(), Mor(core)(A, A))


def test_the_restriction_of_a_functor_places_its_images_in_the_core_it_was_declared_into() -> None:
    """``Core.on_morphism(F)`` returns its images in the exact target hom category (R2 criterion 2).

    A functor action returns an actual morphism built through the exact target hom
    category (``specs/functor.md``, "Functor actions are concrete constructors";
    ``specs/leaves.md``, "Structure functors"), and the codomain this action was declared
    with is ``D.Core()``.  ``F(f)`` is an isomorphism of ``D`` because ``F(f⁻¹)`` is
    retained as its inverse, and that is exactly the theorem making it a morphism of the
    core, so the restriction places it there (D21, ``POL-CAT-081``): ``Mor(D)`` and its
    isomorphisms are declared ancestors of ``Mor(D.Core())``, and answering in one of them
    is the ancestor ``POL-CAT-074`` forbids.  Composition is what the placement decides:
    ``g * f`` is composed by the least category holding both factors, so an image left in
    the ambient makes ``(F g) * (F f)``, a composite of two morphisms of ``D.Core()``,
    leave the core.

    Inversion is the same statement about the core's own defining operation: a groupoid is
    a category in which every morphism is invertible, so ``f⁻¹`` is a morphism of the core
    and ``f⁻¹ * f`` is the core's identity, reduced by the inverse pair the ambient
    retains and the core reads back.
    """
    from sage_categories.cat.core import Core

    def on_object(member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        return MARKS(member_object._token)

    def on_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        source = on_object(morphism.domain())
        target = on_object(morphism.codomain())
        return Mor(MARKS)(source, target)(morphism._token)

    functor = Fun(TOKENS, MARKS)(on_object, on_morphism)
    restricted = Core.on_morphism(functor)
    assert restricted.domain() is TOKENS.Core()
    assert restricted.codomain() is MARKS.Core()

    X, Y, Z = TOKENS("restricted-domain"), TOKENS("restricted-middle"), TOKENS("restricted-codomain")
    source_core, target_core = TOKENS.Core(), MARKS.Core()
    arrow = Mor(source_core)(X, Y)("restricted-arrow")
    onward = Mor(source_core)(Y, Z)("restricted-arrow-on")

    image = restricted.on_morphism(arrow)
    between = Mor(target_core)(functor.on_object(X), functor.on_object(Y))
    assert image.category() is between
    assert is_placed(image, between)
    assert is_placed(image, Mor(target_core))
    assert image in between
    assert image in Mor(target_core)

    # The image is an isomorphism of ``D`` with ``F(f⁻¹)`` retained as its inverse, which
    # is what the ambient placements state; the core placement narrows them and keeps them.
    assert is_placed(image, Mor(MARKS)(functor.on_object(X), functor.on_object(Y)).Isomorphisms())
    assert image in Mor(MARKS).Isomorphisms()
    assert restricted.on_morphism(arrow.inverse()) is image.inverse()
    assert image.inverse().inverse() is image

    # The core is closed under the operation that defines a groupoid, so the inverse of one
    # of its morphisms is one of its morphisms and the round trip is its own identity.
    assert is_placed(arrow.inverse(), Mor(source_core)(Y, X))
    assert is_placed(arrow.inverse() * arrow, Mor(source_core)(X, X))
    assert ask(arrow.inverse() * arrow == Mor(source_core)(X, X).one()) is True

    # Two images compose inside the core, because the core is the category that holds both.
    composite = restricted.on_morphism(onward) * image
    assert is_placed(composite, Mor(target_core))
    assert is_placed(composite, Mor(target_core)(functor.on_object(X), functor.on_object(Z)))


for name, value in tuple(globals().items()):
    if name.startswith("test_"):
        value()
