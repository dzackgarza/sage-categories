"""``Sets()`` products, coproducts, and function sets with their cardinality routes.

Oracles: the definition of the product and coproduct of sets (Mathlib
``Limits.Types.productLimitCone``, ``coproductColimitCocone``); the cardinal
identities ``#(X x Y) = #X #Y``, ``#(X + Y) = #X + #Y``, ``#(Y^X) = (#Y)^(#X)``
(POL-SET-020; Mathlib ``Cardinal.mk_pi``, ``mk_sigma``, ``power_def``);
``Cardinal.prod_const'`` and ``Cardinal.power_self_eq`` for the constant product
over a countably infinite index; ``Cardinal.prod_eq_zero`` for an empty factor;
``Cardinal.prod_le_prod`` with ``Cardinal.cantor`` for the uncountable placement;
``instCountableForallOfFinite`` for the countable placement.  The mediator
equations are decided by the finite set-map equality handler (D17); no row proves
a universal property (D14).
"""

from sage_categories.all import *
from sage_categories.cat.constructions import cocone, cone
from sage_categories.cat.diagrams import sequence_position


def _is_prime(datum):
    return type(datum) is int and datum > int(1) and all(datum % divisor for divisor in range(int(2), int(datum**0.5) + int(1)))


def _primes_with_known_cardinal():
    """The primes by rule with the writer's cardinal ``aleph0`` (POL-MATH-037); never enumerated."""
    return Sets().ObjectType(Sets(), _is_prime, aleph0)


def _naturals_with_known_cardinal():
    return Sets().ObjectType(Sets(), lambda datum: type(datum) is int and datum >= int(0), aleph0)


def _sequence_cone(diagram, apex, legs):
    return cone(diagram, apex, lambda vertex: legs[sequence_position(vertex)])


def test_a_binary_product_is_the_chosen_product_with_projections_that_act() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    product = two * three
    first, second = product.product_projection(int(0)), product.product_projection(int(1))

    assert product is Sets().Products()((two, three))
    assert product in Sets().Products()
    assert product in Sets().Limits(Discrete(Sets().Simplex(int(1))))
    assert ask(product.cardinality() == int(6)) is True
    assert first.domain() is product.apex() and first.codomain() is two
    assert second.codomain() is three
    assert first is not second

    points = list(product.apex())
    assert len(points) == int(6)
    chosen = next(point for point in points if ask(first(point) == two.point(int(1))) is True and ask(second(point) == three.point(int(2))) is True)
    assert chosen in product
    assert ask(second(chosen) == three.point(int(2))) is True


def test_the_mediator_satisfies_the_projection_equations_on_finite_sets() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    product = two * three
    parity = Mor(Sets())(four, two)(lambda datum: datum % int(2))
    residue = Mor(Sets())(four, three)(lambda datum: datum % int(3))
    zero = Mor(Sets())(four, three)(lambda datum: int(0))

    mediating = product.universal_morphism(_sequence_cone(product.diagram(), four, {int(0): parity, int(1): residue}))
    assert mediating in Mor(Sets())(four, product.apex())
    assert ask(product.product_projection(int(0)) * mediating == parity) is True
    assert ask(product.product_projection(int(1)) * mediating == residue) is True
    assert ask(product.product_projection(int(1)) * mediating == zero) is False
    assert ask(product.product_projection(int(1))(mediating(four.point(int(2)))) == three.point(int(2))) is True


def test_the_limit_functor_maps_a_natural_transformation_to_the_induced_morphism_of_products() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    source, target = two * three, three * four
    include = Mor(Sets())(two, three)(lambda datum: datum)
    include_again = Mor(Sets())(three, four)(lambda datum: datum)
    components = {int(0): include, int(1): include_again}
    transformation = Mor(Fun(source.index_category(), Sets()))(source.diagram(), target.diagram())(lambda vertex: components[sequence_position(vertex)])
    limit = Sets().Limits(source.index_category()).limit_functor()

    assert limit in Fun(Fun(source.index_category(), Sets()), Sets())
    assert limit.on_object(source.diagram()) is source.apex()
    induced = limit.on_morphism(transformation)
    assert induced in Mor(Sets())(source.apex(), target.apex())
    assert ask(target.product_projection(int(0)) * induced == include * source.product_projection(int(0))) is True
    assert ask(target.product_projection(int(1)) * induced == include_again * source.product_projection(int(1))) is True


def test_the_iterated_binary_product_is_distinct_from_the_flat_product_with_the_same_cardinality() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    flat = Sets().Products()((two, three, four))
    iterated = prod((two, three, four))

    assert flat is not iterated
    assert ask(flat.cardinality() == int(24)) is True
    assert ask(iterated.cardinality() == int(24)) is True
    assert flat.product_projection(int(2)).codomain() is four


def test_a_subobject_of_a_product_derives_its_components_by_composition() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    product = two * three
    same = Mor(Sets())(two, two)(lambda datum: datum)
    include = Mor(Sets())(two, three)(lambda datum: datum)
    diagonal = product.universal_morphism(_sequence_cone(product.diagram(), two, {int(0): same, int(1): include}))

    assert ask(diagonal.is_monomorphism()) is True
    component = product.subobject_projection(diagonal, int(1))
    assert component in Mor(Sets())(two, three)
    assert ask(component == include) is True
    assert ask(component(two.point(int(1))) == three.point(int(1))) is True


def test_an_infinite_indexed_product_is_constructed_by_rule_and_its_projection_at_seven_acts() -> None:
    primes, naturals = _primes_with_known_cardinal(), _naturals_with_known_cardinal()
    shape = Discrete(primes)
    diagram = Fun(shape, Sets()).from_object_rule(lambda vertex: naturals)
    product = Sets().Products()(diagram)
    seven = shape(primes.point(int(7)))
    three_everywhere = cone(diagram, Sets().Terminal(), lambda vertex: naturals.point(int(3)).defining_morphism())

    family = Sets().element_from_defining_morphism(product.universal_morphism(three_everywhere))
    assert family in product.apex()
    assert product.product_projection(seven).domain() is product.apex()
    assert product.product_projection(seven).codomain() is naturals
    assert ask(product.product_projection(seven)(family) == naturals.point(int(3))) is True
    assert ask(product.product_projection(int(7))(family) == naturals.point(int(3))) is True
    assert product.cardinality() is Unknown


def test_construction_cardinality_routes() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    primes, naturals = _primes_with_known_cardinal(), _naturals_with_known_cardinal()
    reals = Sets().Uncountable()(Sets()(lambda datum: type(datum) is float))
    Sets().Countable()(naturals)

    assert ask(Sets().Products()((two, three, four)).cardinality() == int(24)) is True
    assert ask(Sets().Products()((two, Sets().Empty())).cardinality() == int(0)) is True
    assert Sets().Products()(Fun(Discrete(primes), Sets()).constant(naturals)).cardinality() is continuum

    uncountable = Sets().Products()(Fun(Discrete(primes), Sets().Uncountable()).from_object_rule(lambda vertex: reals))
    assert ask(uncountable.is_countable()) is False
    assert uncountable.apex() in Sets().Uncountable()
    assert uncountable.cardinality() is Unknown

    assert Sets().Products()(Fun(Discrete(two), Sets().Countable()).from_object_rule(lambda vertex: naturals)).cardinality() is aleph0

    evens = Sets().Countable()(Sets()(lambda datum: type(datum) is int and datum % int(2) == int(0)))
    countable = Sets().Products()(Fun(Discrete(two), Sets().Countable()).from_object_rule(lambda vertex: evens))
    assert countable.cardinality() is Unknown
    assert ask(countable.is_countable()) is True

    integers, words = Sets()(lambda datum: type(datum) is int), Sets()(lambda datum: type(datum) is str)
    two_prime = primes.point(int(2))
    unplaced = Sets().Products()(Fun(Discrete(primes), Sets()).from_object_rule(lambda vertex: integers if ask(vertex.point() == two_prime) is True else words))
    assert unplaced.cardinality() is Unknown
    assert ask(unplaced.is_countable()) is Unknown


def test_a_coproduct_has_injections_that_tag_and_a_mediator_satisfying_the_injection_equations() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    coproduct = two + three
    into_two, into_three = coproduct.coproduct_injection(int(0)), coproduct.coproduct_injection(int(1))
    include = Mor(Sets())(two, four)(lambda datum: datum)
    shift = Mor(Sets())(three, four)(lambda datum: datum + int(1))

    assert coproduct is Sets().Coproducts()((two, three))
    assert ask(coproduct.cardinality() == int(5)) is True
    assert into_three.domain() is three and into_three.codomain() is coproduct.apex()
    assert into_two is not into_three
    tagged = into_three(three.point(int(2)))
    assert tagged in coproduct.apex()
    assert ask(tagged == into_two(two.point(int(1)))) is False

    mediating = coproduct.universal_morphism(cocone(coproduct.diagram(), four, lambda vertex: {int(0): include, int(1): shift}[sequence_position(vertex)]))
    assert ask(mediating * into_two == include) is True
    assert ask(mediating * into_three == shift) is True
    assert ask(mediating(tagged) == four.point(int(3))) is True

    naturals = _naturals_with_known_cardinal()
    constant = Sets().Coproducts()(Fun(Discrete(_primes_with_known_cardinal()), Sets()).constant(naturals))
    assert constant.cardinality() is aleph0


def test_the_function_set_is_the_exponential_and_the_morphism_category_is_discrete_on_its_points() -> None:
    two, three, four = Sets().Simplex(int(1)), Sets().Simplex(int(2)), Sets().Simplex(int(3))
    function_set = three ** two
    parity, parity_again = Mor(Sets())(four, two)(lambda datum: datum % int(2)), Mor(Sets())(four, two)(lambda datum: (datum + int(2)) % int(2))
    constant = Mor(Sets())(four, two)(lambda datum: int(0))

    assert function_set is Sets().exponential(two, three)
    assert ask(function_set.cardinality() == int(9)) is True
    assert ask((two ** four).cardinality() == int(16)) is True
    assert Sets().name_of(parity) in two ** four
    assert ask(Sets().name_of(parity) == Sets().name_of(parity_again)) is True
    assert ask(Sets().name_of(parity) == Sets().name_of(constant)) is False
    assert parity in Mor(Sets())(four, two)
    assert Mor(Mor(Sets())(four, two))(parity, parity).identity() not in Mor(Mor(Sets())(four, two))(parity, constant)

    evaluation = Sets().evaluation(two, three)
    assert evaluation.domain() is (function_set * two).apex()
    assert evaluation.codomain() is three
