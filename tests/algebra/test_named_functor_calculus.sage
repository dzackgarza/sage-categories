"""Named operation categories retain renaming isomorphisms and their composites."""

from sage_categories.all import Cartesian, Fun, Mor, Sets, ask
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.structured_objects import AdditiveGroups, AdditiveMagmas, AdditiveMonoids, Groups, Monoids, Semirings


def test_named_restriction_retains_renaming_and_both_actions() -> None:
    structure = Cartesian(Sets())
    named_monoids = AdditiveMonoids(structure)
    named_magmas = AdditiveMagmas(structure)
    projection = named_monoids.product_projection(0)
    magma_projection = named_magmas.product_projection(0)
    assert projection in Fun(named_monoids, Monoids(structure)).Isomorphisms()
    section = projection.inverse()
    assert ask(projection * section == Fun(Monoids(structure), Monoids(structure)).one()) is True
    assert ask(section * projection == Fun(named_monoids, named_monoids).one()) is True
    assert Fun.declares_inheritance(projection)

    restriction = named_monoids.to_named_magmas()
    neutral_restriction = Monoids(structure).to_magmas()
    assert restriction is magma_projection.inverse() * neutral_restriction * projection
    assert named_magmas.to_carrier() is named_magmas.neutral_category().forgetful() * magma_projection
    assert named_monoids.Commutative() is projection.inverse_image(Monoids(structure).Commutative())
    assert named_monoids.Group() is projection.inverse_image(Monoids(structure).Group())

    carrier = Sets((0, 1, 2))
    square = binary_product_data(Sets(), carrier, carrier).apex()
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % 3)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    neutral = Monoids(structure)(addition, zero)
    named = named_monoids.renamed(neutral)
    assert section.on_object(neutral) is named
    assert projection.on_object(named) is neutral
    assert restriction.on_object(named) is named_magmas.renamed(neutral_restriction.on_object(neutral))
    assert ask(named.is_commutative()) is True
    assert ask(named.is_group()) is True

    doubling = Mor(Sets)(carrier, carrier)(lambda value: (2 * value) % 3)
    neutral_map = Monoids(structure).homomorphism(neutral, neutral, doubling)
    named_map = named_monoids.homomorphism(named, named, neutral_map)
    image = restriction.on_morphism(named_map)
    assert magma_projection.on_morphism(image) is neutral_restriction.on_morphism(neutral_map)
    assert image.domain() is restriction.on_object(named)
    assert image.codomain() is restriction.on_object(named)
    assert image(image.domain().point(1)).datum() == 2
    composed = restriction.on_morphism(named_map * named_map)
    assert ask(composed == image * image) is True

    groups = AdditiveGroups(structure)
    named_group = groups.renamed(neutral)
    to_monoids = groups.to_named_monoids()
    assert to_monoids is projection.inverse() * Groups(structure).subcategory_monomorphism() * groups.product_projection(0)
    assert to_monoids.on_object(named_group) is named
    group_map = groups.homomorphism(named_group, named_group, neutral_map)
    assert to_monoids.on_morphism(group_map) is named_map
    assert (-named_group.point(1)).datum() == 2


def test_named_operations_keep_their_images_after_refinement() -> None:
    structure = Cartesian(Sets())
    carrier = Sets((0, 1, 2))
    square = binary_product_data(Sets(), carrier, carrier).apex()
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % 3)
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % 3)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    semirings = Semirings(Sets())
    field = semirings(addition, zero, multiplication, one)
    additive = semirings.to_additive().on_object(field)
    multiplicative = semirings.to_multiplicative().on_object(field)
    first, second = field.point(1), field.point(2)
    assert (first + first).datum() == 2
    assert (first * second).datum() == 2
    assert ask(semirings.is_concrete()) is True
    assert semirings.to_additive().on_object(field) is additive
    assert semirings.to_multiplicative().on_object(field) is multiplicative
    assert field.addition() is addition
    assert field.multiplication() is multiplication
    assert (first + second).datum() == 0
    assert (first * second).datum() == 2
    assert field.zero().datum() == 0
    assert field.one().datum() == 1


test_named_restriction_retains_renaming_and_both_actions()
test_named_operations_keep_their_images_after_refinement()
