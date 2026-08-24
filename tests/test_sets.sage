"""Arbitrary maps and universal constructions in the owned Sets category."""

from sage_categories.abstract_categories.functors import is_functor
from sage_categories.all import *
from sage_categories.theories.cardinals import (
    SymbolicCardinal,
    is_cardinal_hom_category,
)
from sage_categories.theories.posets import PosetElement, is_poset_element
from sage_categories.theories.sets import (
    CoproductElements,
    ProductElements,
    SubsetsOfSet,
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
    return integer.is_prime()


def is_undecided(integer: SetElement) -> Decision:
    assert ZZ.contains_integer(integer)
    return UNKNOWN


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
    assert even_integers.object().category() is CountableSets()
    assert prime_integers.object().category() is CountableSets()
    assert undecided_integers.object().category() is Sets()

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

    product_cardinalities = product.factor_cardinalities()
    coproduct_cardinalities = coproduct.cofactor_cardinalities()
    product_index = product.index_category().object(high_index)
    coproduct_index = coproduct.index_category().object(high_index)
    assert product_cardinalities(product_index) == aleph0
    assert coproduct_cardinalities(coproduct_index) == aleph0


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

    poset_index = poset.element(NaturalNumbers()[int(10**4)])
    assert is_poset_element(poset_index)
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
    index_category = DiscreteCategory(RR)
    diagram = Sets().DiagonalFunctor(index_category)(ZZ)
    limits = Sets().Limits(index_category)
    colimits = Sets().Colimits(index_category)
    assert is_limits_of_sets_category(limits)
    assert is_colimits_of_sets_category(colimits)
    limit = limits(diagram)
    colimit = colimits(diagram)
    index_object = index_category.object(RR(int(0)))

    projection = limit.projection(index_object)
    injection = colimit.injection(index_object)

    assert projection.domain() is limit
    assert projection.codomain() is ZZ
    assert injection.domain() is ZZ
    assert injection.codomain() is colimit


def test_finite_equalizers_coequalizers_pullbacks_and_pushouts() -> None:
    # Two arrows that genuinely differ. Both send the first and third members
    # to the same place and disagree on the second, so they agree on exactly
    # two of the three. A construction that ignored its parallel arrows would
    # report three, which a pair of equal arrows could never expose.
    domain = FiniteSet((ZZ(int(0)), ZZ(int(1)), ZZ(int(2))))
    codomain = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    members = tuple(domain)
    below, above = tuple(codomain)

    def to_below(member: SetElement) -> SetElement:
        assert member in domain
        return below

    def raise_the_middle(member: SetElement) -> SetElement:
        assert member in domain
        return above if member == members[int(1)] else below

    constant = Sets().Hom(domain, codomain)(to_below)
    varying = Sets().Hom(domain, codomain)(raise_the_middle)
    equalizer = Sets().equalizer(constant, varying)
    coequalizer = Sets().coequalizer(constant, varying)

    assert equalizer.apex() in Sets()
    assert coequalizer.apex() in Sets()
    assert equalizer.cardinality() == Cardinals()(int(2))

    finite_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    identity = Sets().identity(finite_set)
    pullback = Sets().pullback(
        identity,
        identity,
        cardinality=finite_set.cardinality(),
    )
    pushout = Sets().pushout(identity, identity)

    assert pullback.apex() in Sets()
    assert pushout.apex() in Sets()
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


def test_full_subcategories_are_replete_under_declared_isomorphisms() -> None:
    finite_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    represented_copy = PowerSet(finite_set).from_predicate(
        lambda member: True,
        iterator=lambda: iter(finite_set),
    )
    copied_set = represented_copy.object()

    def copy_member(member: SetElement) -> SetElement:
        return next(
            candidate
            for candidate in copied_set
            if represented_copy.inclusion()(candidate) is member
        )

    inverse = Sets().Hom(finite_set, copied_set)(copy_member)
    isomorphism = declare_isomorphism(represented_copy.inclusion(), inverse)

    assert isomorphism in Sets().IsomorphismArrowCategory()
    assert copied_set in FiniteSets()
    assert copied_set in CountableSets()


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


def test_cardinal_and_ordinal_structure_maps() -> None:
    one = cardinal(int(1))
    two = cardinal(int(2))
    hom_category = Cardinals().Hom(one, two)
    assert is_cardinal_hom_category(hom_category)
    inclusion = hom_category.unique_morphism()
    summed = Cardinals().sum_morphism(inclusion, inclusion)
    powered = Cardinals().power_morphism(inclusion, inclusion)
    kappa = SymbolicCardinal("kappa")
    lam = SymbolicCardinal("lambda")

    assert aleph0.is_aleph()
    assert aleph0.initial_ordinal() == omega0
    assert cardinal(int(3)).initial_ordinal() == ordinal(int(3))
    assert omega0.is_initial()
    assert ordinal(int(3)).is_initial() is False
    assert continuum.is_uncountably_infinite() is True
    assert cardinal(int(3)).sort_key() < aleph0.sort_key()
    assert Cardinals().are_incomparable(kappa, lam) is UNKNOWN

    assert summed.domain() == Cardinals().sum(one, one)
    assert summed.codomain() == Cardinals().sum(two, two)
    assert powered.domain() == Cardinals().power(one, one)
    assert powered.codomain() == Cardinals().power(two, two)


def test_subset_constructions_and_power_set_maps() -> None:
    finite_set = FiniteSet((ZZ(int(0)), ZZ(int(1)), ZZ(int(2))))
    zero = finite_set.element(ZZ(int(0)))
    one = finite_set.element(ZZ(int(1)))
    powerset = PowerSet(finite_set)
    singleton = powerset.from_members(frozenset((zero,)))
    pair = powerset.from_members(frozenset((zero, one)))

    subset_poset = finite_set.subset_poset()
    singleton_in_poset = subset_poset.element(singleton)
    pair_in_poset = subset_poset.element(pair)
    assert singleton_in_poset <= pair_in_poset
    assert (pair_in_poset <= singleton_in_poset) is False

    pairs = finite_set.subsets_of_size(int(2))
    finite_subsets = finite_set.finite_subsets()
    assert pair in pairs
    assert singleton not in pairs
    assert singleton in finite_subsets
    assert pair in finite_subsets

    disjoint_union = finite_set.disjoint_union(finite_set)
    left = disjoint_union.element(next(iter(disjoint_union.index_set())), zero)
    assert left in disjoint_union

    characteristic = singleton.characteristic_morphism()
    recovered = powerset.from_characteristic_morphism(characteristic)
    assert recovered.membership(zero) is True
    assert recovered.membership(one) is False

    identity = Sets().identity(finite_set)
    assert Sets().contains_set_morphism(identity)
    direct_image = powerset.direct_image_morphism(identity)
    image = direct_image(singleton)
    assert SubsetsOfSet(finite_set).contains_subset(image)
    assert image.membership(zero) is True
    assert image.membership(one) is False


def test_standard_set_subcategories_and_order_categories() -> None:
    finite_set = FiniteSet((ZZ(int(0)), ZZ(int(1))))
    labels = FiniteSet((ZZ(int(7)),))
    discrete = DiscreteCategory(labels)

    assert Sets().ℵ[int(1)] == aleph(int(1))
    assert Sets().א[int(1)] == aleph(int(1))
    assert Sets().PartiallyOrdered() is PartiallyOrderedSets()
    assert Sets().TotallyOrdered() is TotallyOrderedSets()
    assert FiniteSets().contains_finite_set(finite_set)
    assert FiniteDiscreteCategories().contains_finite_discrete_category(discrete)


def test_finite_poset_realization_returns_owned_elements() -> None:
    order = finite_ordered_set((ZZ(int(0)), ZZ(int(1)), ZZ(int(2))))
    poset = FiniteTotallyOrderedSets().finite_poset_functor()(order)
    assert FinitePosets().contains_finite_poset(poset)
    inclusion = TotallyOrderedSets().inclusion()
    lower = inclusion.on_element(order, order[int(0)])
    middle = inclusion.on_element(order, order[int(1)])
    upper = inclusion.on_element(order, order[int(2)])
    assert is_poset_element(lower)
    assert is_poset_element(middle)
    assert is_poset_element(upper)

    assert poset.covers(lower, middle)
    assert tuple(poset.lower_covers(middle)) == (lower,)
    assert tuple(poset.upper_covers(middle)) == (upper,)
    assert tuple(poset.common_lower_covers((middle,))) == (lower,)
    assert tuple(poset.common_upper_covers((middle,))) == (upper,)
    assert tuple(poset.open_interval(lower, upper)) == (middle,)
    assert tuple(poset.closed_interval(lower, upper)) == (lower, middle, upper)
    assert tuple(poset.principal_order_ideal(middle)) == (lower, middle)
    assert tuple(poset.principal_order_filter(middle)) == (middle, upper)
    assert tuple(poset.order_ideal((middle,))) == (lower, middle)
    assert tuple(poset.order_filter((middle,))) == (middle, upper)
    assert tuple(poset.minimal_elements()) == (lower,)
    assert tuple(poset.maximal_elements()) == (upper,)
    assert poset.has_bottom()
    assert poset.bottom() is lower
    assert poset.has_top()
    assert poset.top() is upper
    assert poset.is_bounded()
    assert poset.height() == 3
    assert poset.width() == 1
    assert poset.rank(upper) == 2
    assert tuple(tuple(level) for level in poset.level_sets()) == (
        (lower,),
        (middle,),
        (upper,),
    )
    assert poset.is_ranked()
    assert poset.is_graded()
    assert poset.is_chain()
    assert poset.is_chain_of_poset((lower, upper))
    assert poset.is_antichain_of_poset((middle,))

    identity = PartiallyOrderedSets().Hom(poset, poset).identity()
    assert identity.is_order_preserving()
    assert identity.is_order_embedding() is True
