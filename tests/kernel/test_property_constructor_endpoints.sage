"""Property constructors retain Hom and Fun parameters through nested narrowing."""

from sage_categories.all import Cartesian, Fun, Monoids, Mor, Sets, binary_product_data


def test_nested_hom_properties_retain_distinct_endpoints() -> None:
    source = Sets((1, 2))
    middle = Sets((3, 4))
    target = Sets((5, 6))
    first_hom = Mor(Sets)(source, middle)
    second_hom = Mor(Sets)(middle, target)

    for narrowed in (
        first_hom.Monomorphisms().Epimorphisms(),
        first_hom.Epimorphisms().Monomorphisms(),
    ):
        first = narrowed(lambda value: value + 2)
        second = second_hom.Monomorphisms().Epimorphisms()(lambda value: value + 2)
        assert first.domain() is source
        assert first.codomain() is middle
        assert second.domain() is middle
        assert second.codomain() is target
        assert first in narrowed
        assert first(source.point(1)) is middle.point(3)
        assert (second * first)(source.point(2)) is target.point(6)


def test_nested_functor_properties_retain_domain_parameters() -> None:
    finite = Sets.Finite()
    source = Sets((1, 2))
    target = Sets((3, 4))
    arrow = Mor(Sets)(source, target)(lambda value: value + 2)

    for domain in (finite, Sets):
        for narrowed in (
            Fun(domain, Sets).Full().Faithful(),
            Fun(domain, Sets).Faithful().Full(),
        ):
            inclusion = narrowed(lambda value: value, lambda morphism: morphism)
            assert inclusion.domain() is domain
            assert inclusion.codomain() is Sets
            assert inclusion in narrowed
            assert inclusion.on_object(source) is source
            assert inclusion.on_morphism(arrow)(source.point(2)) is target.point(4)


def test_nested_algebraic_properties_retain_distinct_monoidal_parameters() -> None:
    bases = (Sets, Sets.Finite())
    structures = tuple(Cartesian(base) for base in bases)
    families = tuple(Monoids(structure) for structure in structures)
    assert structures[0] is not structures[1]
    assert families[0] is not families[1]

    for base, structure, monoids in zip(bases, structures, families):
        carrier = base((0, 1, 2))
        square = binary_product_data(base, carrier, carrier).apex()
        addition = Mor(base)(square, carrier)(lambda pair: (pair[0] + pair[1]) % 3)
        unit = Mor(base)(structure.unit(), carrier)(lambda _: 0)
        for narrowed in (
            monoids.Group().Commutative(),
            monoids.Commutative().Group(),
        ):
            group = narrowed(addition, unit)
            assert group in narrowed
            assert group in monoids
            assert group.operation() is addition
            assert group.unit_morphism() is unit
            assert group.carrier().carrier() is carrier
            assert group.operation()(square.point((2, 2))) is carrier.point(1)
            assert group.unit_morphism()(structure.unit().point(())) is carrier.point(0)


test_nested_hom_properties_retain_distinct_endpoints()
test_nested_functor_properties_retain_domain_parameters()
test_nested_algebraic_properties_retain_distinct_monoidal_parameters()
