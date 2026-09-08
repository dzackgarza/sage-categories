"""Cat().Concrete(): concreteness decided from the declared faithful structure functors, and the composite they build."""

from sage_categories.all import Cat, Cartesian, Mor, Sets, Unknown, ask
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import AdditiveMagmas, AdditiveMonoids, Magmas, Monoids


def test_sets_is_concrete_by_its_identity() -> None:
    assert ask(Sets.is_concrete()) is True
    assert Sets in Cat().Concrete()
    identity = Sets.functor_to_sets()
    assert identity.domain() is Sets and identity.codomain() is Sets
    carrier = Sets((0, 1, 2))
    assert Sets.underlying_set(carrier) is carrier


def test_a_structure_category_is_concrete_along_its_declared_functor() -> None:
    structure = Cartesian(Sets())
    magmas = Magmas(structure)
    assert ask(magmas.is_concrete()) is True
    carrier = Sets((0, 1, 2))
    square = binary_product_data(Sets(), carrier, carrier).apex()
    operation = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % 3)
    magma = magmas.algebra(carrier, operation)

    forgetful = magmas.functor_to_sets()
    assert forgetful.domain() is magmas and forgetful.codomain() is Sets
    assert magmas.underlying_set(magma) is carrier
    # The composite is the functor the declaration already states, not a second one.
    assert magmas.underlying_set(magma) is magmas.forgetful().on_object(magma)

    doubling = Mor(Sets)(carrier, carrier)(lambda value: (2 * value) % 3)
    homomorphism = magmas.homomorphism(magma, magma, doubling)
    assert magmas.underlying_map(homomorphism) is doubling


def test_a_two_step_tower_never_names_sets() -> None:
    structure = Cartesian(Sets())
    monoids, magmas = AdditiveMonoids(structure), AdditiveMagmas(structure)
    # Each category declares one faithful structure functor, to the category below it.
    assert monoids.to_named_magmas().codomain() is magmas
    assert magmas.to_carrier().codomain() is Sets
    # Each category on the tower is concrete for the same reason, and asking places it.
    assert ask(monoids.is_concrete()) is True
    assert ask(magmas.is_concrete()) is True

    carrier = Sets((0, 1, 2))
    square = binary_product_data(Sets(), carrier, carrier).apex()
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % 3)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    additive = monoids.renamed(Monoids(structure)(addition, zero))

    composite = monoids.functor_to_sets()
    assert composite.domain() is monoids and composite.codomain() is Sets
    assert monoids.underlying_set(additive) is carrier
    # The composite factors through the category the declaration names.
    assert monoids.underlying_set(additive) is magmas.underlying_set(monoids.to_named_magmas().on_object(additive))
    # It is the carrier the points of the object are transported to.
    assert additive.index_set() is carrier


def test_a_category_with_no_declared_route_stays_undecided() -> None:
    # No faithful route to Sets() is declared out of Cat(), and its absence is not a proof
    # that no faithful functor exists, so concreteness stays open rather than false.
    assert ask(Cat().is_concrete()) is Unknown


test_sets_is_concrete_by_its_identity()
test_a_structure_category_is_concrete_along_its_declared_functor()
test_a_two_step_tower_never_names_sets()
test_a_category_with_no_declared_route_stays_undecided()
