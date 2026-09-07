"""Inverses of named group homomorphisms retain their mathematical base."""

from sage_categories.algebra import abelian_homomorphism, presented_abelian_group
from sage_categories.all import Mor, ask, assume
from sage_categories.cat.properties import PropertySubcategory


def test_named_group_inverse_retains_base_and_endpoints() -> None:
    cyclic = AdditiveAbelianGroup([5])
    source = presented_abelian_group(cyclic)
    target = presented_abelian_group(cyclic)
    forward = abelian_homomorphism(source, target, lambda x: 2 * x)
    backward = abelian_homomorphism(target, source, lambda x: 3 * x)
    base = forward.base_category()
    base.retain_inverses(forward, backward)

    assert forward.base_category() is base
    assert backward.base_category() is base
    assert forward.domain() is source and forward.codomain() is target
    assert forward.inverse() is backward
    assert backward.inverse() is forward
    assert ask(backward * forward == Mor(base)(source, source).one()) is True
    assert ask(forward * backward == Mor(base)(target, target).one()) is True
    assert ask(forward(source.point(cyclic.gen(0))) == target.point(2 * cyclic.gen(0))) is True


def test_inverse_in_an_intersection_of_full_subcategories() -> None:
    for modulus, reverse in ((5, False), (7, True)):
        cyclic = AdditiveAbelianGroup([modulus])
        source = presented_abelian_group(cyclic)
        target = presented_abelian_group(cyclic)
        forward = abelian_homomorphism(source, target, lambda x: 2 * x)
        backward = abelian_homomorphism(target, source, lambda x: ((modulus + 1) // 2) * x)
        base = forward.base_category()
        base.retain_inverses(forward, backward)
        first = PropertySubcategory(base, "FirstProperty", ())
        second = PropertySubcategory(base, "SecondProperty", ())
        intersection = base.intersection((first, second))
        for category in ((second, first) if reverse else (first, second)):
            assume(category.membership_proposition(source))
            assume(category.membership_proposition(target))
            assume(Mor(category).membership_proposition(forward))

        assert source in first and source in second
        assert target in first and target in second
        assert forward in Mor(first) and forward in Mor(second)
        assert base.intersection((second, first)) is intersection
        assert forward.base_category() is intersection
        assert forward.inverse() is backward
        assert ask(backward * forward == Mor(intersection)(source, source).one()) is True


test_named_group_inverse_retains_base_and_endpoints()
test_inverse_in_an_intersection_of_full_subcategories()
