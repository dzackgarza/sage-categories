"""Arbitrary maps and universal constructions in the owned Sets category."""

from sage.rings.integer import Integer as SageInteger

from sage_categories.abstract_categories.functors import is_functor
from sage_categories.all import *
from sage_categories.theories.posets import PosetElement, PosetElements
from sage_categories.theories.sets import (
    CoproductElements,
    ProductElements,
    is_colimits_of_sets_category,
    is_coproducts_of_sets_category,
    is_limits_of_sets_category,
    is_products_of_sets_category,
)


def constant_natural(rational: SetElement) -> SetElement:
    assert QQ.contains_rational(rational)
    return NN[int(1)]


def rational_floor(rational: SetElement) -> SetElement:
    assert QQ.contains_rational(rational)
    return rational.floor()


def integer_to_natural(integer: SetElement) -> SetElement:
    assert ZZ.contains_integer(integer)
    return NN[int(abs(int(integer)) + 1)]


def is_even(integer: SetElement) -> bool:
    assert ZZ.contains_integer(integer)
    return int(integer) % 2 == 0


def is_prime(integer: SetElement) -> bool:
    assert ZZ.contains_integer(integer)
    return SageInteger(int(integer)).is_prime()


def is_undecided(integer: SetElement) -> Decision:
    assert ZZ.contains_integer(integer)
    return UNKNOWN


def is_equal(left: PosetElement, right: PosetElement) -> bool:
    return left == right


def test_arbitrary_set_maps_have_exact_endpoints() -> None:
    rational = QQ(int(7), int(3))
    rational_to_natural = Sets().Hom(QQ, NN)(constant_natural)
    rational_to_integer = Sets().Hom(QQ, ZZ)(rational_floor)
    integer_to_natural_morphism = Sets().Hom(ZZ, NN)(integer_to_natural)
    composite = Sets().compose(
        integer_to_natural_morphism,
        rational_to_integer,
    )
    assert Sets().contains_set_morphism(composite)
    real_plane = RR.cartesian_product(RR)

    def diagonal(real: SetElement) -> SetElement:
        assert RR.contains_real(real)
        return real_plane.element(lambda index: real)

    real_diagonal = Sets().Hom(RR, real_plane)(diagonal)
    real = RR(int(3))
    point = real_diagonal(real)

    assert rational_to_natural.domain() is QQ
    assert rational_to_natural.codomain() is NN
    assert rational_to_natural(rational) is NN[int(1)]
    assert rational_to_integer(rational) is ZZ(int(2))
    assert composite(rational) is NN[int(3)]
    assert real_diagonal.domain() is RR
    assert real_diagonal.codomain() is real_plane
    assert ProductElements().contains_product_element(point)
    assert all(point[index] is real for index in real_plane.index_set())


def test_predicates_construct_infinite_subobjects() -> None:
    even_integers = ZZ.subset_from(is_even, cardinality=aleph0)
    prime_integers = ZZ.subset_from(is_prime, cardinality=aleph0)
    undecided_integers = ZZ.subset_from(is_undecided)

    assert ZZ(int(2)) in even_integers
    assert ZZ(int(3)) not in even_integers
    assert ZZ(int(2)) in prime_integers
    assert ZZ(int(4)) not in prime_integers
    assert undecided_integers.membership(ZZ(int(0))) is UNKNOWN

    assert even_integers.inclusion().domain() is even_integers.object()
    assert even_integers.inclusion().codomain() is ZZ
    assert prime_integers.inclusion().domain() is prime_integers.object()
    assert prime_integers.inclusion().codomain() is ZZ
    assert even_integers.inclusion() in Sets().MonomorphismArrowCategory()
    assert prime_integers.inclusion() in Sets().MonomorphismArrowCategory()
    assert even_integers.object().cardinality() == aleph0
    assert prime_integers.object().cardinality() == aleph0


def test_function_sets_supply_evaluation() -> None:
    functions = ZZ**QQ
    floor = functions(rational_floor)
    rational = QQ(int(7), int(3))
    evaluation = functions.evaluation()
    pairs = evaluation.domain()
    assert Sets().contains_set(pairs)
    product_category = pairs.category()
    assert is_products_of_sets_category(product_category)
    assert product_category.contains_set_product(pairs)

    pair = pairs.element(
        lambda index: floor if pairs.factor(index) is functions else rational,
    )
    assert floor(rational) is ZZ(int(2))
    assert evaluation(pair) is ZZ(int(2))
    assert functions.cardinality() == Cardinals().power(
        ZZ.cardinality(),
        QQ.cardinality(),
    )


def test_infinite_products_and_coproducts_use_direct_indexing() -> None:
    product = CartesianProductOfFamily(NN, lambda index: ZZ)
    coproduct = CoproductOfFamily(NN, lambda index: ZZ)
    high_index = NN[int(10**10)]
    point = product.element(lambda index: ZZ(int(7)))
    term = coproduct.element(high_index, ZZ(int(11)))

    assert point[high_index] is ZZ(int(7))
    assert term.index() is high_index
    assert term.value() is ZZ(int(11))
    assert point in product
    assert term in coproduct
    assert product.cardinality().index_set() is NN
    assert product.cardinality().family()(high_index) == aleph0
    assert coproduct.cardinality().index_set() is NN
    assert coproduct.cardinality().family()(high_index) == aleph0


def test_infinite_product_and_coproduct_functors_act_on_maps() -> None:
    index_category = DiscreteCategory(NN)
    identity = Sets().Hom(ZZ, ZZ).identity()
    product_morphism = CartesianProductMorphismOfFamily(
        index_category,
        lambda index: identity,
    )
    coproduct_morphism = CoproductMorphismOfFamily(
        index_category,
        lambda index: identity,
    )
    high_index = NN[int(10**10)]

    product = product_morphism.domain()
    assert Sets().contains_set(product)
    product_category = product.category()
    assert is_products_of_sets_category(product_category)
    assert product_category.contains_set_product(product)
    product_member = product.element(lambda index: ZZ(int(7)))
    product_image = product_morphism(product_member)
    assert ProductElements().contains_product_element(product_image)
    assert product_image[high_index] is ZZ(int(7))

    coproduct = coproduct_morphism.domain()
    assert Sets().contains_set(coproduct)
    coproduct_category = coproduct.category()
    assert is_coproducts_of_sets_category(coproduct_category)
    assert coproduct_category.contains_set_coproduct(coproduct)
    coproduct_member = coproduct.element(high_index, ZZ(int(11)))
    coproduct_image = coproduct_morphism(coproduct_member)
    assert CoproductElements().contains_coproduct_element(coproduct_image)
    assert coproduct_image.index() is high_index
    assert coproduct_image.value() is ZZ(int(11))


def test_general_infinite_limits_and_colimits_have_universal_maps() -> None:
    countable_order = Sets().Δ.__getitem__(aleph0)
    assert TotallyOrderedSets().contains_total_order(countable_order)
    poset = TotallyOrderedSets().underlying_poset(countable_order)
    index_category = poset.thin_category()
    diagram = Sets().DiagonalFunctor(index_category)(ZZ)
    assert is_functor(diagram)

    limits = Sets().Limits(index_category)
    colimits = Sets().Colimits(index_category)
    assert is_limits_of_sets_category(limits)
    assert is_colimits_of_sets_category(colimits)
    limit = limits(diagram, cardinality=aleph0)
    colimit = colimits(diagram, cardinality=aleph0)

    identity = Sets().identity(ZZ)
    cone = Cone(diagram, ZZ, lambda index: identity)
    cocone = Cocone(diagram, ZZ, lambda index: identity)
    into_limit = limit.universal_morphism(cone)
    from_colimit = colimit.universal_morphism(cocone)

    high_index = countable_order[int(10**4)]
    poset_index = TotallyOrderedSets().inclusion().on_element(
        countable_order,
        high_index,
    )
    assert PosetElements().contains_poset_element(poset_index)
    index_member = index_category.objects().element(poset_index)
    limit_member = into_limit(ZZ(int(5)))
    assert ProductElements().contains_product_element(limit_member)
    colimit_member = colimit.element(index_member, ZZ(int(7)))

    assert limit_member[index_member] is ZZ(int(5))
    assert from_colimit(colimit_member) is ZZ(int(7))
    assert into_limit.domain() is ZZ
    assert into_limit.codomain() is limit
    assert from_colimit.domain() is colimit
    assert from_colimit.codomain() is ZZ
    assert limit.cardinality() == aleph0
    assert colimit.cardinality() == aleph0


def test_limits_and_colimits_do_not_enumerate_their_index_objects() -> None:
    real_equality_order = PartiallyOrderedSets()(RR, is_equal)
    index_category = real_equality_order.thin_category()
    diagram = Sets().DiagonalFunctor(index_category)(ZZ)
    limits = Sets().Limits(index_category)
    colimits = Sets().Colimits(index_category)
    assert is_limits_of_sets_category(limits)
    assert is_colimits_of_sets_category(colimits)
    limit = limits(diagram)
    colimit = colimits(diagram)
    index_object = real_equality_order.element(RR(int(0)))

    projection = limit.projection(index_object)
    injection = colimit.injection(index_object)

    assert projection.domain() is limit
    assert projection.codomain() is ZZ
    assert injection.domain() is ZZ
    assert injection.codomain() is colimit


def test_finite_equalizers_coequalizers_pullbacks_and_pushouts() -> None:
    finite_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    identity = Sets().identity(finite_set)
    equalizer = Sets().equalizer(identity, identity)
    coequalizer = Sets().coequalizer(identity, identity)
    pullback = Sets().pullback(
        identity,
        identity,
        cardinality=finite_set.cardinality(),
    )
    pushout = Sets().pushout(identity, identity)

    assert equalizer.image() in Sets()
    assert coequalizer.image() in Sets()
    assert pullback.image() in Sets()
    assert pushout.image() in Sets()
    assert equalizer.limit_cone().diagram().codomain() is Sets()
    assert coequalizer.colimit_cocone().diagram().codomain() is Sets()
    assert pullback.limit_cone().diagram().codomain() is Sets()
    assert pushout.colimit_cocone().diagram().codomain() is Sets()


def test_sets_use_their_strongest_known_categories() -> None:
    finite_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    enumeration = finite_set.enumeration_injection()

    assert finite_set.category() is FiniteSets()
    assert NN.category() is CountableSets()
    assert ZZ.category() is CountableSets()
    assert QQ.category() is CountableSets()
    assert RR.category() is UncountableSets()
    assert finite_set in FiniteSets()
    assert finite_set in CountableSets()
    assert finite_set in Sets()
    assert enumeration.domain() is finite_set
    assert enumeration.codomain() is NaturalNumbers()


def test_finite_sets_inherit_closed_products_and_coproducts() -> None:
    labels = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    index_category = DiscreteCategory(labels)
    factor = FiniteSet((ZZ(int(2)), ZZ(int(3))))
    diagram = FiniteSets().DiagonalFunctor(index_category)(factor)

    products = FiniteSets().Products(index_category)
    coproducts = FiniteSets().Coproducts(index_category)
    assert is_products_of_sets_category(products)
    assert is_coproducts_of_sets_category(coproducts)
    product = products(diagram)
    coproduct = coproducts(diagram)

    assert product in FiniteSets()
    assert coproduct in FiniteSets()
    assert product.cardinality().is_finite() is True
    assert coproduct.cardinality().is_finite() is True
