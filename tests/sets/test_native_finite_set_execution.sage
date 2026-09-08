"""Finite set algorithms execute through the retained native finite realization."""

from sage_categories.all import Mor, Sets, ask


def test_native_finite_map_algorithms_preserve_owned_labels() -> None:
    source = Sets(("a", "b", "c"))
    target = Sets((10, 20))
    arrow = Mor(Sets)(source, target)({"a": 10, "b": 20, "c": 10})

    assert len(Sets.hom_morphisms(source, target)) == 8
    factor, inclusion = Sets.image_factorization(arrow)
    assert tuple(point.datum() for point in factor.codomain()) == (10, 20)
    assert ask(inclusion * factor == arrow) is True

    ambient = Sets((10, 20, 30))
    mono = Mor(Sets)(target, ambient).Monomorphisms()({10: 10, 20: 30})
    through = Mor(Sets)(source, ambient)({"a": 10, "b": 30, "c": 10})
    lift = Sets.factor_through_monomorphism(mono, through)
    assert lift is not False
    assert tuple(lift(point).datum() for point in source) == (10, 20, 10)
    assert ask(mono * lift == through) is True

    swap = Mor(Sets)(target, target).Isomorphisms()({10: 20, 20: 10})
    inverse = swap.inverse()
    assert tuple(inverse(point).datum() for point in target) == (20, 10)
    assert ask(inverse * swap == Mor(Sets)(target, target).one()) is True
    assert ask(swap * inverse == Mor(Sets)(target, target).one()) is True


test_native_finite_map_algorithms_preserve_owned_labels()
